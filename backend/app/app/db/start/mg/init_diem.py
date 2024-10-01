import logging

from app.models.bible import Book, Chapter, BookTypeEnum
from app.db.start.common import ImportBible

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImportDiemBible(ImportBible):    
    
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
  
