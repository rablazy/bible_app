import logging

from app.db.start.import_version import importer_cls
from app.db.start.init_langs import init_languages
from app.db.start.rules import EN_RULES, KJV_RULES, MG_RULES, STANDARD_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")

    init_languages()

    bibles = [
        {
            "lang": "mg",
            "version": "BMG_1965",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": MG_RULES,  # customize
        },  # OK
        # {
        #     "lang": "mg",
        #     "version": "BMG_1886",
        #     "src_type": "standard_json",
        #     "encoding": "utf-8",
        #     "validation_rules": MG_RULES,  # customize
        # },  # OK
        {
            "lang": "en",
            "version": "KJV",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": KJV_RULES,
        },  # OK
        {
            "lang": "fr",
            "version": "LSG_21",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": STANDARD_RULES,
        },  # OK
        {
            "lang": "en",
            "version": "ASV_1901",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": EN_RULES,  # change rules
        },  # OK
    ]

    for b in bibles:
        importer = importer_cls(**b)
        importer.run_import()  # validate=False

    logger.info("Init done !")


if __name__ == "__main__":
    main()
