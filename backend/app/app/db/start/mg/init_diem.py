import logging
import pathlib
import os
import json

from app import crud
from app.models.bible import Bible, Language, Book, Chapter, Verse, BookTypeEnum
from app.db.session import SessionLocal
from app.db.start.common import ImportBible

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# {
#         "lang": "mg", 
#         "version": "DIEM", 
#         "description": "Baiboly Dikan-teny Iombonana Malagasy", 
#         "src": "internet", 
#         "src_url": "https://www.bicaso.fr/Bible.html", 
#         "books": [
#             {"rank": 1, 
#             "name": "Genes\u1ef3",             
#             "short_name": "GEN", 
#             "classification": "Fiandohana", 
#             "chaps": [
#                 {
#                     "book_rank": 1, 
#                     "rank": 1, 
#                     "verses": [
#                         {
#                             "rank": 1, 
#                             "text": "Tamin'ny fiandohana, fony Andriamanitra nahary ny lanitra sy ny tany."
#                         }, 
#                         {
#                             "rank": 2, 
#                             "text": "dia tsy nisy endriny sady foana ny tany fa ny haizina 
#                                 no nandrakotra ny lalina, ary ny Fanahin'Andriamanitra no nanomba tambonin'ny rano."
#                         }
#                 }
#             ]
#         ]
#     }

class ImportDiemBible(ImportBible):
    
    """Import Diem bible
    """
    
    def import_data(self):
        """
        Import malagasy diem bible version
        """           
        with open(self.file_path, 'r+', encoding=self.file_encoding) as f:
            datas = json.load(f)                
            version = datas["version"]                       
            
            if not self.exists_in_db():                                               
                bible = Bible(
                    src = datas["src"],
                    src_url = datas["src_url"],
                    version = version,
                    description = datas["description"],
                    lang = self.language             
                )
                
                crud.bible.create(self.db, bible)
                
                data = datas['books']
                order = 0

                for d in data:
                    order += 1
                    book = Book(
                        name = d['name'],
                        short_name = d['short_name'],
                        rank= d['rank'],
                        category = BookTypeEnum(d['category']),
                        classification = d['classification'],
                        bible=bible
                    )
                    crud.book.create(self.db, book)               

                    book_chapters = d['chaps']
                    logger.info("Treating book %s with %s chapters ...",
                                book, len(book_chapters))
                    
                    for chap in book_chapters:                        
                        chapter = Chapter(rank=chap['rank'], book=book)
                        crud.chapter.create(self.db, chapter)                                                
                        
                        for v in chap['verses']:                           
                            verse = Verse(
                                rank=v['rank'],
                                chapter=chapter,
                                content=v['text']
                            )                            
                            chapter.verses.append(verse)

                self.db.commit()
                logger.info("%s book inserted.", order)            
            
            
    
    def check_data(self):
        logger.info("Checking DIEM bible data right now ...")              
        
        # assert number of books inserted
        assert(self.q_book().count() == 73)        
        assert(self.q_book().filter(Book.category == BookTypeEnum.OLD).count() == 39)
        assert(self.q_book().filter(Book.category == BookTypeEnum.NEW).count() == 27)
        assert(self.q_book().filter(Book.category == BookTypeEnum.APOCRYPHAL).count() == 7)
        
        # assert books placed in right category        
        assert(self.q_book().filter(Book.rank==38).first().category == BookTypeEnum.OLD ) # zakaria
        assert(self.q_book().filter(Book.rank==41).first().category == BookTypeEnum.NEW ) # marka
        assert(self.q_book().filter(Book.rank==73).first().category == BookTypeEnum.APOCRYPHAL ) # baroka
        
        # check book chapter count
        assert(self.q_chapter().filter(Book.rank == 14).count() == 36)        
        assert(self.q_chapter().join(Chapter.book).filter(Book.rank == 66).count() == 22) 
        assert(self.q_chapter().join(Chapter.book).filter(Book.rank == 72).count() == 19) 
        
        # assert Luke 8 has 25 verses
        assert(self.q_verse().filter(Book.rank == 42, Chapter.rank==8).count() == 56)                    
                
        logger.info("Checking done !")
        
             
             
def main() -> None:
    logger.info("Creating initial DIEM data")
    ImportDiemBible()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
