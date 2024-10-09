import logging

from app.db.start.import_version import importer_cls
from app.db.start.init_langs import init_languages
from app.db.start.rules import KJV_RULES, STANDARD_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")

    init_languages()

    bibles = [
        {
            "lang": "mg",
            "version": "BMG_1886",
            "src_type": "standard_json",
            "encoding": "utf-8",
            "validation_rules": STANDARD_RULES,  # customize
        },  # OK
        {
            "lang": "en",
            "version": "KJV",
            "src_type": "bicaso",
            "file_name": "KJV - King James Version Bible.zip",
            "encoding": "utf-8-sig",
            "validation_rules": KJV_RULES,
        },  # OK
        {
            "lang": "fr",
            "version": "LSG_21",
            "src_type": "bicaso",
            "file_name": "LSG_21 - Bible Louis Second 21eme siecle.zip",
            "encoding": "utf-8-sig",
            "validation_rules": STANDARD_RULES,
        },  # OK
        {
            "lang": "en",
            "version": "ASV_1901",
            "src_type": "bicaso",
            "encoding": "utf-8-sig",
            "file_name": "ASV_1901 - American Standard Version.zip",
            "validation_rules": STANDARD_RULES,  # change rules
        },  # OK
        # {
        #     "lang" : "mg",
        #     "version" : "BMG_1865",
        #     "src_type": "bicaso",
        #     "file_name": "BMG_1865 - Baiboly Malagasy 1865.zip",
        #     "src_type": "bicaso",
        #     "encoding" : "utf-8-sig",
        #     "validation_rules" : STANDARD_RULES # customize
        # },
        # {
        #     "lang" : "mg",
        #     "version" : "DIEM",
        #     "src_type": "bicaso",
        #     "file_name" : "DIEM - Dikan-teny Iombonana Eto Madagasikara.zip",
        #     "encoding" : "utf-8-sig",
        #     "validation_rules" : DIEM_RULES
        # },
        # {
        #     "lang" : "mg",
        #     "version" : "BKM",
        #     "src_type": "bicaso",
        #     "encoding" : "utf-8-sig",
        #     "file_name": "BKM - Baiboly Katolika Malagasy.zip",
        #     "validation_rules" : DIEM_RULES # change rules
        # },
        # {
        #     "lang" : "fr",
        #     "version" : "LSG_1910",
        #     "src_type": "bicaso",
        #     "file_name": "LSG_1910 - Bible Louis Second 1910.zip",
        #     "encoding" : "utf-8-sig",
        #     "validation_rules" : STANDARD_RULES
        # }, # ValueError: invalid literal for int() with base 10: '12b', common.py", line 288, in import_data
    ]

    for b in bibles:
        importer = importer_cls(**b)
        importer.run_import()  # validate=False

    logger.info("Init done !")


if __name__ == "__main__":
    main()
