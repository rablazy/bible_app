import logging
import pathlib
import os
import json

from app import crud
from app.models.bible import Bible, Language, Book, Chapter, Verse, BookTypeEnum
from app.db.session import SessionLocal
from sqlalchemy import func, select, and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).resolve().parent.parent


class InitMgBible():

    def __init__(self):
        self.db = SessionLocal()
        self.import_json_data()         

    def import_json_data(self):
        """
        Import malagasy bible version
        """          
        baiboly_src = os.path.join(ROOT, 'data', 'bible', 'mg', 'MG1886.json')

        with open(baiboly_src, 'r+', encoding='UTF-8') as f:
            datas = json.load(f)
                 
            src_lang = datas["lang"]
            lang = crud.language.get_by_code(self.db, src_lang)
            if not lang:
                raise ValueError(f"Source language {src_lang} not found in db")
            
            version = datas["version"]           
            
            if not self.db.query(Bible).filter(Bible.version==version, Bible.lang==lang).count():                                               
                bible = Bible(
                    src = datas["created"]["name"],
                    version = version,
                    lang = lang             
                )
                
                crud.bible.create(self.db, bible)
                
                data = datas['body']
                order = 0

                for d in data:
                    order += 1
                    book = Book(
                        name=d['title'],
                        short_name=d['id'],
                        rank=order,
                        category=BookTypeEnum.OLD if order < 40 else BookTypeEnum.NEW,
                        bible=bible
                    )
                    crud.book.create(self.db, book)               

                    book_chapters = d['books'] if isinstance(
                        d['books'], list) else [d['books']]
                    logger.info("Treating book %s with %s chapters ...",
                                book, len(book_chapters))

                    toko = 1
                    for chap in book_chapters:
                        verses_key = 'texts' if 'toko' in chap else 'seg'
                        chapter = Chapter(rank=toko, book=book)
                        crud.chapter.create(self.db, chapter)
                        toko += 1
                        try:
                            verses = chap[verses_key]
                        except Exception as e:
                            logger.error('%s - %s : %s', book, type(chap),
                                         chap.keys() if isinstance(chap, dict) else chap)
                            raise e

                        verse_order = 0
                        for v in verses:
                            verse_order += 1
                            verset = v.strip()
                            verse = Verse(
                                rank=verse_order,
                                chapter=chapter,
                                content=verset
                            )
                            if verset.startswith('['):
                                try:
                                    index = verset.index(']')
                                    if index:
                                        verse.subtitle = verset[1:index]
                                    verse.content = verset[index+1:len(verset)].strip()
                                except ValueError:
                                    pass
                            chapter.verses.append(verse)

                self.db.commit()
                logger.info("%s book inserted.", order)
            
            self.check_data()
            
    
    def check_data(self):
        logger.info("Checking mg bible data right now ...")
        
        # assert number of books inserted
        assert(self.db.query(Book).count() == 66)        
        assert(self.db.query(Book).filter(Book.category == BookTypeEnum.OLD).count() == 39)
        assert(self.db.query(Book).filter(Book.category == BookTypeEnum.NEW).count() == 27)
        
        # assert books placed in right category        
        assert(self.db.query(Book).filter(Book.rank==38).first().category == BookTypeEnum.OLD ) # zakaria
        assert(self.db.query(Book).filter(Book.rank==41).first().category == BookTypeEnum.NEW ) # marka
        
        # check first book has 50 chapter
        assert(self.db.query(Chapter).join(Chapter.book).filter(Book.rank == 1).count() == 50)
        # check last book has 22 chapter
        assert(self.db.query(Chapter).join(Chapter.book).filter(Book.rank == 66).count() == 22) 
        # assert Luke 8 has 25 verses
        assert(self.db.query(Verse)
               .join(Chapter)
               .join(Chapter.book)
               .filter(Book.rank == 42, Chapter.rank==8).count() == 56
        )  
        # asset some verses have substitle       
        verse = self.db.query(Verse).join(Chapter).join(Chapter.book).filter(
            Book.rank == 2, Chapter.rank == 6, Verse.rank == 2).first()
        assert(verse.subtitle is not None)           
             
        verse = self.db.query(Verse).join(Chapter).join(Chapter.book).filter(
            Book.rank == 44, Chapter.rank == 25, Verse.rank == 1).first()
        assert(verse.subtitle is not None)       
        
        logger.info("Checking done !")
        
             
             
def main() -> None:
    logger.info("Creating initial MG1886 data")
    InitMgBible()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
