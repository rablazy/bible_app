import logging
import pathlib
import os

from app import crud
from app.models.bible import *
from app.schemas.bible import *

from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# good doc : https://www.reddit.com/r/FastAPI/comments/rf2n1i/how_do_i_convert_a_manytomany_sqlalchemy_model_to/


ROOT = pathlib.Path(__file__).resolve().parent.parent

class ReverseData:

    def run(self, version):
        logger.info("Reverse MG1886 from db")
        
        db = SessionLocal()

        bible = crud.bible.query_by_version(db, version).first()        
        b_item = BibleItem.model_validate(bible)        
        
        books = db.query(Book).join(Chapter).filter(Book.bible_id==bible.id).all()                      
        b_item.books = [BookItem.model_validate(book) for book in books]        
        
        file_name = os.path.join(ROOT, 'data', 'bible', bible.lang.code, f'{version}.json')
        with open(file_name, 'w', encoding="utf-8") as fp:
            fp.write(b_item.model_dump_json())            
                
        logger.info("Reverse done !")


# if __name__ == "__main__":
#     main()
