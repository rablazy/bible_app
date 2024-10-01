import logging

from app.db.start.init_langs import init_languages
from app.db.start.common import ImportBible
from app.db.start.rules import DIEM_RULES, STANDARD_RULES


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")    
    
    init_languages()
    
    bibles = [
        { "lang" : "mg", "version" : "DIEM", "file_encoding" : "utf-8-sig", "validation_rules" : DIEM_RULES},
        { "lang" : "en", "version" : "KJV", "file_encoding" : "utf-8-sig", "validation_rules" : STANDARD_RULES},
    ]    
    # ImportMgBible(lang='mg', version="MG1886", )
    
    for b in bibles:
        importer = ImportBible(**b)
        importer.run_import()
    
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
