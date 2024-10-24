import logging
import os
import pathlib
import sys

from app import crud
from app.db.session import SessionLocal
from app.models.bible import Bible, Book, Chapter
from app.schemas.bible import BibleItem, BookItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = os.getcwd()


class ReverseData:
    def run(self, vers="all"):

        db = SessionLocal()
        versions = (
            [d for d, in db.query(Bible.version).all()] if vers == "all" else [vers]
        )
        for version in versions:
            logger.info("Reverse %s from db...", version)
            bible = crud.bible.query_by_version(db, version).first()
            if bible:
                b_item = BibleItem.model_validate(bible)

                books = (
                    db.query(Book)
                    .join(Chapter)
                    .order_by(Book.rank)
                    .filter(Book.bible_id == bible.id)
                    .all()
                )
                b_item.books = [BookItem.model_validate(book) for book in books]

                path = os.path.join(ROOT, "export", "bible", bible.lang.code)
                file_name = os.path.join(path, f"{version.upper()}.json")
                abort = False
                try:
                    pathlib.Path(path).mkdir(mode=0o755, parents=True, exist_ok=True)
                except OSError as err:
                    abort = True
                    logger.error("Error: %s", err)

                if not abort:
                    with open(file_name, "w", encoding="utf-8") as fp:
                        fp.write(b_item.model_dump_json())
                    logger.info("Reverse %s done, file saved at %s", version, file_name)
            else:
                logger.error("Bible version %s not found", version)


if __name__ == "__main__":
    if sys.argv and len(sys.argv) > 1:
        version = sys.argv[1]
        if version:
            ReverseData().run(version)
        else:
            logger.error("Give <version> string as param to the script")
