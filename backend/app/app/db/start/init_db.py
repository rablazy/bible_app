import logging

from app.db.start.init_langs import init_languages
from app.db.start.common import JsonBible
from app.db.start.rules import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")    
    
    init_languages()
    
    bibles = [
        {
            "lang" : "mg", "version" : "MG1886", 
            "encoding" : "utf-8", "validation_rules" : STANDARD_RULES # customize
        }, 
        # { 
        #     "lang" : "mg", "version" : "DIEM", 
        #     "encoding" : "utf-8-sig", "validation_rules" : DIEM_RULES
        # },
        # { 
        #     "lang" : "en", "version" : "KJV", 
        #     "encoding" : "utf-8-sig", "validation_rules" : KJV_RULES},
        # { 
        #     "lang" : "fr", "version" : "LSG_21", 
        #     "encoding" : "utf-8-sig", "validation_rules" : STANDARD_RULES
        # },
        # { 
        #     "lang" : "mg", "version" : "BKM", 
        #     "encoding" : "utf-8-sig", "validation_rules" : DIEM_RULES # change rules
        # }, 
    ]          
    
    for b in bibles:
        importer = JsonBible(**b)
        importer.run_import()
    
    # old import
    # importer = ImportMgBible(lang='mg', version="MG1886", file_encoding="utf-8")
    # importer.run_import()
    
    # reverse old import to uniformize format across all imports
    # from app.db.start.mg.reverse_mg1886 import ReverseData
    # ReverseData().run()    
    
    logger.info("Init done !")


if __name__ == "__main__":
    main()
