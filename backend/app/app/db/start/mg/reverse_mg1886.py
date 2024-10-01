import logging

from app import crud
from app.models.bible import *
from app.schemas.bible import *

from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# good doc : https://www.reddit.com/r/FastAPI/comments/rf2n1i/how_do_i_convert_a_manytomany_sqlalchemy_model_to/


class ReverseData:

    def run(self):
        logger.info("Reverse MG1886 from db")
        version = "MG1886"

        db = SessionLocal()

        bible = crud.bible.query_by_version_and_lang(db, "MG1886", "mg").first()        
        b_item = BibleItem.model_validate(bible)
        b_item.description = "Baiboly Malagasy 1886"
        
        books = db.query(Book).join(Chapter).filter(Book.bible_id==bible.id).all()                      
        b_item.books = [BookItem.model_validate(book) for book in books]        
        
        with open(f'{version}.json', 'w', encoding="utf-8") as fp:
            fp.write(b_item.model_dump_json())            
                
        logger.info("Reverse done baby !!!")


# if __name__ == "__main__":
#     main()
