import logging
import pathlib
import os
import sys

from app import crud
from app.models.bible import *
from app.schemas.bible import *

from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).resolve().parent.parent

class ReverseData:

    def run(self, version):
        logger.info("Reverse %s from db...", version)
        
        db = SessionLocal()

        bible = crud.bible.query_by_version(db, version).first()        
        b_item = BibleItem.model_validate(bible)        
        
        books = db.query(Book).join(Chapter).filter(Book.bible_id==bible.id).all()                      
        b_item.books = [BookItem.model_validate(book) for book in books]        
        
        path = os.path.join(ROOT, 'data', 'bible', 'reverse', bible.lang.code)
        file_name = os.path.join(path, (f'{version}.json').upper())
        abort = False
        try:
            os.mkdir( path, 0o755 );
            logger.info("Path created successfully")                  
        except FileExistsError as err: ...
        except OSError as err:
            abort = True
            logger.error("Error: %s", err)          
            
        if not abort:            
            with open(file_name, 'w', encoding="utf-8") as fp:
                fp.write(b_item.model_dump_json())  
            logger.info("Reverse done, file saved at %s", file_name)      
        
        

if __name__ == "__main__":    
    if sys.argv and len(sys.argv) > 1:                
        version = sys.argv[1]        
        if version:            
            ReverseData().run(version)
    else:
        logger.error("Give <version> string as param to the script")
