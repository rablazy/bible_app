import logging

from app.db.start.import_version import importer_cls
from app.db.start.init_langs import init_languages
from app.db.start.rules import STANDARD_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial test data")

    init_languages()

    test_bible = {
        "lang": "mg",
        "version": "BMG_1886",
        "src_type": "standard_json",
        "encoding": "utf-8",
        "validation_rules": STANDARD_RULES,  # customize
    }

    importer = importer_cls(**test_bible)
    importer.run_import()

    logger.info("Init test data done !")


if __name__ == "__main__":
    main()
