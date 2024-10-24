import logging

from app.db.start.import_version import importer_cls
from app.db.start.init_langs import init_languages
from app.db.start.rules import KJV_RULES, MG_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial test data")

    init_languages()

    test_bibles = [
        # {
        #     "lang": "mg",
        #     "version": "BMG_1886",
        #     "src_type": "standard_json",
        #     "encoding": "utf-8",
        #     "validation_rules": STANDARD_RULES,  # customize
        # },
        {
            "lang": "mg",
            "version": "BMG_1965",
            "description": "Baiboly Malagasy 1965",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": MG_RULES,
        },
        {
            "lang": "en",
            "version": "KJV",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": KJV_RULES,
        },
    ]

    for b in test_bibles:
        importer = importer_cls(**b)
        importer.run_import()

    logger.info("Init test data done !")


if __name__ == "__main__":
    main()
