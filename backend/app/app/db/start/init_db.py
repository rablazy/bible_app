import logging

from app.db.start.init_langs import init_languages
from app.db.start.common import importer_cls
from app.db.start.rules import *
from app.db.start.reverse_version import ReverseData


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")    
    
    init_languages()
    
    bibles = [
        {
            "lang" : "mg", 
            "version" : "MG1886", 
            "src_type": "standard_json",
            "encoding" : "utf-8", 
            "validation_rules" : STANDARD_RULES # customize
        }, 
        { 
            "lang" : "en", 
            "version" : "KJV", 
            "src_type": "bicaso", 
            "file_name": "KJV - King James Version Bible.zip",
            "encoding" : "utf-8-sig", 
            "validation_rules" : KJV_RULES
        },
        {
            "lang" : "mg", 
            "version" : "BMG",          
            "src_type": "bicaso",
            "file_name": "BMG - Baiboly Malagasy 1865.zip",              
            "src_type": "bicaso",
            "encoding" : "utf-8-sig",
            "validation_rules" : STANDARD_RULES # customize
        },
        { 
            "lang" : "mg", 
            "version" : "DIEM", 
            "src_type": "bicaso",
            "file_name" : "DIEM - Dikan-teny Iombonana Eto Madagasikara.zip",
            "encoding" : "utf-8-sig", 
            "validation_rules" : DIEM_RULES
        },        
        { 
            "lang" : "fr", 
            "version" : "LSG_21", 
            "src_type": "bicaso",
            "file_name": "LSG_21 - Bible Louis Second 21eme siecle.zip",
            "encoding" : "utf-8-sig", 
            "validation_rules" : STANDARD_RULES
        },
        # { 
        #     "lang" : "fr", 
        #     "version" : "LSG_1910", 
        #     "src_type": "bicaso",
        #     "file_name": "LSG_1910 - Bible Louis Second 1910.zip",
        #     "encoding" : "utf-8-sig", 
        #     "validation_rules" : STANDARD_RULES
        # }, # ValueError: invalid literal for int() with base 10: '12b', common.py", line 288, in import_data 
        { 
            "lang" : "mg", 
            "version" : "BKM", 
            "src_type": "bicaso",
            "encoding" : "utf-8-sig", 
            "file_name": "BKM - Baiboly Katolika Malagasy.zip",
            "validation_rules" : DIEM_RULES # change rules
        }, 
    ]          
    
    for b in bibles:        
        importer = importer_cls(**b)
        importer.run_import() # validate=False
    
    # old import
    # importer = ImportMgBible(lang='mg', version="MG1886", file_encoding="utf-8")
    # importer.run_import()
    
    # # reverse existing data from db to uniformize format across all imports    
    # ReverseData().run("MG1886")    
    
    logger.info("Init done !")


if __name__ == "__main__":
    main()
