import enum
import logging
import os
import pathlib

import pydantic_core
from pydash import omit
from sqlalchemy import null, or_

from app import crud
from app.db.constants import BOOK_CODES
from app.db.session import SessionLocal
from app.models.bible import Bible, Book, BookTypeEnum, Chapter, Verse
from app.schemas.bible import BibleItem

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
    COUNT_VERSE_PER_BOOK = "verse_per_book"
    COUNT_ALL_VERSE = "count_all_verse"


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
        """Validate this version by running all defined rules"""
        if self.rules:
            for rule in self.rules:
                logger.debug("Checking rule %s", rule)
                getattr(self, rule[0].value)(*rule[1])

    def book_count(self, expected):
        """Checks numbers of book in this version"""
        assert self._q_book().count() == expected

    def boot_count_by_category(self, category, expected):
        """Compare book count by category to expected"""
        assert self._q_book().filter(Book.category == category).count() == expected

    def book_category(self, rank, expected):
        """assert books placed in right category

        Args:
            rank (int): book rank
            expected (BookTypeEnum): expected category
        """
        assert self._q_book().filter(Book.rank == rank).first().category == expected

    def book_chapter_count(self, book_rank, expected_chapter_count):
        """Check number of chapters in a book"""
        assert (
            self._q_chapter().filter(Book.rank == book_rank).count()
            == expected_chapter_count
        )

    def count_all_verse(self, expected, *book_category):
        """Count all verse based on book_category"""
        q = self._q_verse()
        if book_category:
            q = q.filter(Book.category.in_(book_category))
        assert q.count() == expected

    def count_verse(self, book_rank, chapter_rank, expected):
        """Compare numbers of verses in chapter to expected"""
        assert (
            self._q_verse()
            .filter(Book.rank == book_rank, Chapter.rank == chapter_rank)
            .count()
            == expected
        )

    def verse_text(self, book_rank, chapter_rank, verse_rank, expected):
        """Check if verse content is as excepted"""
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
        """Check if all verses are not empty"""
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

    def verse_per_book(self, expected: dict):
        """Check if verses count per book is ok"""
        books = self._q_book().all()
        for b in books:
            logger.info("Checking book %s, rank:%s", b, b.rank)
            expected_chapters = expected.get(b.rank).get("chapters")
            current_verses = sum([c.verse_count for c in b.chapters])
            expected_verses = expected.get(b.rank).get("verses")

            logger.info(
                "chapters : %s vs expected: %s | verses : %s vs expected: %s",
                b.chapter_count,
                expected_chapters,
                current_verses,
                expected_verses,
            )
            assert b.chapter_count == expected_chapters
            assert current_verses == expected_verses

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
    """Bible importer factory"""
    src_type = kwargs.get("src_type", None)
    if src_type == "standard_json":
        return JsonBible(*args, **kwargs)
    else:
        return BibleImporter(*args, **kwargs)


class BibleImporter:
    """Main class to import bible version"""

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

        self.book_codes = BOOK_CODES

    def import_version(self, bible_item: BibleItem):
        existing_version = self._get_existing_version()
        if existing_version:
            # update to manage later
            self.bible_id = existing_version.id
        else:
            bible = Bible(**(omit(bible_item.__dict__, "books", "lang")))
            bible.lang_id = self.language.id
            crud.bible.create(self.db, bible)

            rank_all = 1

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
                        chapter.code = f"{book.code}.{chapter.rank}"
                        crud.chapter.create(self.db, chapter)

                        if chap.verses:
                            for v in chap.verses:
                                verse = Verse(
                                    **(
                                        omit(
                                            v.__dict__,
                                            "chapter_rank",
                                            "book_rank",
                                            "book_name",
                                            "book_short_name",
                                        )
                                    )
                                )
                                content = verse.content
                                if content and content.startswith("["):
                                    try:
                                        x = content.index("]")
                                        if x:
                                            maybe_subtitle = content[0 : x + 1]  # 0,x+1
                                            maybe_content = content[x + 1 :].strip()
                                            if maybe_content:
                                                verse.content = maybe_content
                                                verse.subtitle = maybe_subtitle
                                    except ValueError:
                                        ...
                                verse.chapter_id = chapter.id
                                verse.code = "%s.%02d.%02d" % (
                                    book.code,
                                    chapter.rank,
                                    verse.rank,
                                )
                                verse.rank_all = rank_all
                                if verse.content and any(
                                    ch.isalpha() for ch in verse.content
                                ):
                                    rank_all += 1
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
