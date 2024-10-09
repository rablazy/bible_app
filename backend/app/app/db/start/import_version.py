import csv
import enum
import logging
import os
import pathlib
import tempfile
from zipfile import ZipFile

import pydantic_core
from pydash import omit
from sqlalchemy import null, or_

from app import crud
from app.db.session import SessionLocal
from app.models.bible import Bible, Book, BookTypeEnum, Chapter, Verse
from app.schemas.bible import BibleItem, BookItem, ChapterItem, VerseItem

ROOT = pathlib.Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RulesEnum(enum.Enum):
    """Validation methods

    Args:
        enum (str): method name to call in validator
    """

    BOOK_COUNT = "book_count"
    BOOK_COUNT_BY_CATEG = "boot_count_by_category"
    BOOK_CATEGORY = "book_category"
    BOOK_CHAPTER_COUNT = "book_chapter_count"
    VERSE_COUNT = "count_verse"
    VERSE_TEXT = "verse_text"
    ALL_VERSE_PRESENT = "all_verse_present"


class BibleValidator:
    """Validator class to validate bible content"""

    def __init__(self, bible_id: int, rules: dict = None) -> None:
        if not bible_id or bible_id <= 0:
            raise ValueError("Set a valid value to bible_id")
        self.db = SessionLocal()
        self.bible_id = bible_id
        self.rules = rules
        self.version_filter = [Book.bible_id == self.bible_id]

    def run(self):
        if self.rules:
            for rule in self.rules:
                logger.debug("Checking rule %s", rule)
                getattr(self, rule[0].value)(*rule[1])

    def book_count(self, expected):
        assert self._q_book().count() == expected

    def boot_count_by_category(self, category, expected):
        assert self._q_book().filter(Book.category == category).count() == expected

    def book_category(self, rank, expected):
        """assert books placed in right category

        Args:
            rank (int): book rank
            expected (BookTypeEnum): expected category
        """
        assert self._q_book().filter(Book.rank == rank).first().category == expected

    def book_chapter_count(self, book_rank, expected_chapter_count):
        assert (
            self._q_chapter().filter(Book.rank == book_rank).count()
            == expected_chapter_count
        )

    def count_verse(self, book_rank, chapter_rank, expected):
        assert (
            self._q_verse()
            .filter(Book.rank == book_rank, Chapter.rank == chapter_rank)
            .count()
            == expected
        )

    def verse_text(self, book_rank, chapter_rank, verse_rank, expected):
        v = (
            self._q_verse()
            .filter(
                Book.rank == book_rank,
                Chapter.rank == chapter_rank,
                Verse.rank == verse_rank,
            )
            .first()
        )
        assert v is not None and v.content == expected

    def all_verse_present(self):
        assert (
            self._q_verse()
            .filter(
                or_(
                    Verse.content.ilike("???"),
                    Verse.content == "",
                    Verse.content == null(),
                )
            )
            .count()
            == 0
        )

    def _q_book(self):
        return self.db.query(Book).filter(*self.version_filter)

    def _q_chapter(self):
        return self.db.query(Chapter).join(Chapter.book).filter(*self.version_filter)

    def _q_verse(self):
        return (
            self.db.query(Verse)
            .join(Chapter)
            .join(Chapter.book)
            .filter(*self.version_filter)
        )


def importer_cls(*args, **kwargs):
    src_type = kwargs.get("src_type", None)
    if src_type == "standard_json":
        return JsonBible(*args, **kwargs)
    elif src_type == "bicaso":
        return BicasoBible(*args, **kwargs)
    else:
        return BibleImporter(*args, **kwargs)


class BibleImporter:
    def __init__(self, lang: str, version: str, validation_rules: dict = {}, **kwargs):
        self.db = SessionLocal()
        self.lang = lang
        self.language = None
        self._init_language()

        self.version = version
        self.bible_id = None
        self.validation_rules = validation_rules

        self.file_path = kwargs.get("file_path", None)
        self.file_name = kwargs.get("file_name", None)
        self.file_encoding = kwargs.get("encoding", "UTF-8")
        self.file_type = None

        self.book_codes = {
            1: "gen_",
            2: "exo_",
            3: "lev_",
            4: "num_",
            5: "deu_",
            6: "josh_",
            7: "jud_",
            8: "rut_",
            9: "1sam_",
            10: "2sam_",
            11: "1kin_",
            12: "2kin_",
            13: "1chr_",
            14: "2chr_",
            15: "ezr_",
            16: "neh_",
            17: "est_",
            18: "job_",
            19: "psa_",
            20: "pro_",
            21: "ecc_",
            22: "song_",
            23: "isa_",
            24: "jer_",
            25: "lam_",
            26: "eze_",
            27: "dan_",
            28: "hos_",
            29: "joe_",
            30: "amos_",
            31: "oba_",
            32: "jon_",
            33: "mic_",
            34: "nah_",
            35: "hab_",
            36: "zep_",
            37: "hag_",
            38: "zec_",
            39: "mal_",
            40: "mat_",
            41: "mar_",
            42: "luk_",
            43: "joh_",
            44: "act_",
            45: "rom_",
            46: "1cor_",
            47: "2cor_",
            48: "gal_",
            49: "eph_",
            50: "phi_",
            51: "col_",
            52: "1the_",
            53: "2the_",
            54: "1tim_",
            55: "2tim_",
            56: "tit_",
            57: "phl_",
            58: "heb_",
            59: "jam_",
            60: "1pet_",
            61: "2pet_",
            62: "1joh_",
            63: "2joh_",
            64: "3joh_",
            65: "jude_",
            66: "rev_",
        }

    def import_version(self, bible_item: BibleItem):
        existing_version = self._get_existing_version()
        if existing_version:
            # update to manage later
            self.bible_id = existing_version.id
        else:
            bible = Bible(**(omit(bible_item.__dict__, "books", "lang")))
            bible.lang_id = self.language.id
            crud.bible.create(self.db, bible)

            self.bible_id = bible.id  # save newly created bible id, used later on
            logger.info("Bible %s inserted, id: %s", self.version, self.bible_id)

            books = bible_item.books
            for b in books:
                book = Book(**(omit(b.__dict__, "chapters", "chapter_count")))
                if not book.short_name:
                    if (
                        book.name[0].isdigit()
                        or book.name.startswith("1")
                        or book.name.startswith("2")
                    ):
                        book.short_name = book.name[:5]
                    else:
                        book.short_name = book.name[:3]
                book.short_name = book.short_name.capitalize()
                book.category = BookTypeEnum(b.category)
                if self.book_codes.get(book.rank, None):
                    book.code = self.book_codes.get(book.rank)
                book.bible_id = bible.id
                crud.book.create(self.db, book)

                if b.chapters:
                    logger.info(
                        "%s Inserting book %s with %s chapters ...",
                        self.version,
                        book,
                        len(b.chapters),
                    )
                    for chap in b.chapters:
                        chapter = Chapter(
                            **(omit(chap.__dict__, "book_rank", "verses"))
                        )  # "book_id",
                        chapter.book_id = book.id
                        crud.chapter.create(self.db, chapter)

                        if chap.verses:
                            for v in chap.verses:
                                verse = Verse(
                                    **(omit(v.__dict__, "chapter_rank", "book_rank"))
                                )
                                verse.chapter_id = chapter.id
                                chapter.verses.append(verse)

            self.db.commit()
            logger.info("%s book inserted.", len(books))

        return self.bible_id

    def run_import(self, validate=True):
        self.import_data()
        if validate:
            self.validate_data()

    def import_data(self):
        raise NotImplementedError

    def validate_data(self):
        """Checking bible content
        You can override this method if you want
        """
        logger.info("Checking bible %s data right now ...", self.version)
        BibleValidator(self.bible_id, self.validation_rules).run()
        logger.info("Checking done !")

    def default_file_path(self):
        """Default file path to look for file to import

        Returns:
            str: full path
        """
        if self.file_name:
            return os.path.join(ROOT, "data", "bible", self.lang, self.file_name)
        else:
            return os.path.join(
                ROOT, "data", "bible", self.lang, f"{self.version}.{self.file_type}"
            )

    def _init_language(self):
        """Checks if lang to be used exists in db

        Raises:
            ValueError: if lang not found
        """
        self.language = crud.language.get_by_code(self.db, self.lang)
        if not self.language:
            raise ValueError(f"Source language {self.lang} not found in db")

    def _get_existing_version(self):
        """Check if same version already exists in db

        Returns:
            int: count
        """
        return crud.bible.query_by_version(self.db, self.version).first()


class JsonBible(BibleImporter):
    """Import bible in json format"""

    def __init__(self, *args, **kwargs):
        super(JsonBible, self).__init__(*args, **kwargs)
        self.file_type = "json"

    def import_data(self):
        """
        Import generic bible with <BibleItem> json format in input
        """
        file_path = self.file_path or self.default_file_path()
        with open(file_path, "r+", encoding=self.file_encoding) as f:
            datas = f.read()
            bible_item = BibleItem.model_validate(pydantic_core.from_json(datas))
            super().import_version(bible_item)


class BicasoBible(BibleImporter):
    """Import bible in zip format from bicaso site"""

    def __init__(self, *args, **kwargs):
        super(BicasoBible, self).__init__(*args, **kwargs)
        self.file_type = "zip"

    def import_data(self):
        zip_file = self.file_path or self.default_file_path()
        zf = ZipFile(zip_file)
        with tempfile.TemporaryDirectory() as tempdir:
            zf.extractall(tempdir)
            chap_file = os.path.join(tempdir, self.version, "Livre_chap.txt")
            entries = list(csv.reader(open(chap_file, "r"), delimiter="\t"))

            books = dict()
            for i, entry in enumerate(entries):
                rank = i + 1
                b = BookItem(
                    rank=rank,
                    name=((entry[0].split("-"))[1]).strip(),
                    classification=entry[4].strip(),
                    chapter_count=int(entry[2]),
                )
                # b.short_name = b.name[:5] if b.name[0].isdigit() else b.name[:3]
                if self.book_codes.get(rank, None):
                    b.code = self.book_codes.get(rank)
                b.chapters = [ChapterItem(rank=0)] * (b.chapter_count)

                if b.rank < 40:
                    b.category = "Old"
                else:
                    if b.rank <= 66:
                        b.category = "New"
                    else:
                        b.category = "Apocryphal"

                books[entry[1]] = b

            for verse_file in [
                os.path.join(tempdir, self.version, f"{self.version}-O.txt"),
                os.path.join(tempdir, self.version, f"{self.version}-N.txt"),
            ]:
                verses = list(
                    csv.reader(
                        open(verse_file, "r", encoding=self.file_encoding),
                        delimiter="\t",
                    )
                )
                for i, verse in enumerate(verses):
                    if len(verse):
                        book_code, chapter_rank, verse_rank, content = (
                            verse[0],
                            int(verse[1]),
                            int(verse[2]),
                            verse[4].strip(),
                        )
                        subtitle = None
                        if content and content.startswith("["):
                            x = content.rfind("]")
                            if x:
                                may_subtitle = content[0 : x + 1]
                                may_content = content[x + 1 :].strip()
                                if may_content:
                                    content = may_content
                                    subtitle = may_subtitle
                        book = books.get(book_code)
                        chap_index = chapter_rank - 1
                        if book.chapters[chap_index].rank == 0:
                            book.chapters[chap_index] = ChapterItem(rank=chapter_rank)
                        book.chapters[chap_index].verses.append(
                            VerseItem(
                                rank=verse_rank, subtitle=subtitle, content=content
                            )
                        )

        bible_item = BibleItem(
            **{
                "src": "bicaso",
                "description": (
                    self.file_name.rsplit(".", 1)[0].split("-", 1)[1]
                ).strip(),
                "src_url": "https://www.bicaso.fr/Bible.html",
                "version": self.version,
                "lang": self.language,
                "books": books.values(),
            }
        )

        # out_file = os.path.join(os.path.dirname(zip_file), f'{self.version}.json')
        # with open(out_file, 'w', encoding="utf-8") as fp:
        #     fp.write(bible_item.model_dump_json(indent=2))

        super().import_version(bible_item)
