import logging

from app import crud
from app.db.session import SessionLocal
from app.models.bible import Language

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_languages():
    logger.info("Init languages")
    db = SessionLocal()
    for lg in [
        ("en", "English"),
        ("fr", "French"),
        ("mg", "Malagasy"),
        ("de", "German"),
        ("el", "Greek"),
        ("he", "Hebrew"),
    ]:
        if not crud.language.get_by_code(db, lg[0]):
            language = Language(name=lg[1], code=lg[0])
            crud.language.create(db, language)
            logger.info("Language %s inserted (ok)", language)
        else:
            logger.info("Language %s already in db !", lg[0])

    logger.info("Languages init done")


def main() -> None:
    logger.info("Init languages")
    init_languages()
    logger.info("Languages init done")


if __name__ == "__main__":
    main()
