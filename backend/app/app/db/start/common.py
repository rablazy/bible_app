import os 
import pydantic_core
from pydash import omit

from app import crud
from app.models.bible import Bible, Book, BookTypeEnum, Chapter, Verse, Language
from app.db.session import SessionLocal
from app.schemas.bible import BibleItem

import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import enum
class RulesEnum(enum.Enum):
    """Validation methods

    Args:
        enum (_type_): _description_
    """
    BOOK_COUNT = "book_count"
    BOOK_COUNT_BY_CATEG = "boot_count_by_category"
    BOOK_CATEGORY = "book_category"
    BOOK_CHAPTER_COUNT = "book_chapter_count"
    VERSE_COUNT = "count_verse"

class ImportBible:
    
    def __init__(self, 
                 lang : str = None, 
                 version :str = None, 
                 file_path : str = None,
                 file_encoding : str = "UTF-8",
                 file_type : str ="json",
                 validation_rules: dict = {}
        ):
        self.db = SessionLocal()
        self.lang = lang
        self.language = None
        
        self.version = version
        self.file_type = file_type        
        self.file_encoding = file_encoding
        self.file_path = file_path or self.default_file_path()
        
        self.bible_id = None    
        self.validation_rules = validation_rules 
           
     
    def run_import(self):
        self.lang_exists_in_db()
        self.import_data()
        self.set_query_filter() 
        self.check_data()     
        
    def import_data(self):        
        if self.file_type == "json":
            self.import_json_data()
        else:
            raise NotImplementedError
    
    def check_data(self): # you can override this method if you don't like it
        logger.info("Checking bible data right now ...")          
        self.check_rules(self.validation_rules)
        logger.info("Checking done !")        
        
    @property
    def validation_rules(self) -> dict : 
        return self._validation_rules
    
    @validation_rules.setter    
    def validation_rules(self, values):
        self._validation_rules = values
              
    
    def default_file_path(self):
        return os.path.join(ROOT, 'data', 'bible', self.lang, f"{self.version}.{self.file_type}")
    
    def set_query_filter(self):        
        #b = self.db.query(Bible).filter(Bible.version.ilike(self.version)).first()               
        if not self.bible_id:
            raise ValueError("bible_id value not set, set it after import_data()")
        self.version_filter = [Book.bible_id == self.bible_id]       
    
    def q_book(self):        
        return self.db.query(Book).filter(*self.version_filter)
    
    def q_chapter(self):        
        return self.db.query(Chapter).join(Chapter.book).filter(*self.version_filter)
    
    def q_verse(self):        
        return self.db.query(Verse).join(Chapter).join(Chapter.book).filter(*self.version_filter)
    
    def lang_exists_in_db(self):
        lang = crud.language.get_by_code(self.db, self.lang)
        if not lang:
            raise ValueError(f"Source language {self.lang} not found in db")    
        self.language = lang        
    
    def exists_in_db(self):       
        q =  crud.bible.query_by_version_and_lang(self.db, self.version, self.lang)
        count = q.count()        
        if count:
            self.bible_id = q.first().id           
        return count
                    
    
    def import_json_data(self):
        """
        Import generic bible with <BibleItem> json format in input
        """           
        with open(self.file_path, 'r+', encoding=self.file_encoding) as f:            
            datas = f.read()                              
            bible_item = BibleItem.model_validate(pydantic_core.from_json(datas))                               
            
            if not self.exists_in_db():                 
                bible = Bible(**(omit(bible_item.__dict__, "books", "lang")))                    
                bible.lang_id = self.language.id
                crud.bible.create(self.db, bible)    
                
                self.bible_id = bible.id
                
                books = bible_item.books                                
                for b in books:                    
                    book = Book(**(omit(b.__dict__, "chapters", "chapter_count"))) # "bible_id"
                    book.category = BookTypeEnum(b.category)
                    book.bible_id = bible.id
                    crud.book.create(self.db, book)                                   

                    if b.chapters:
                        logger.info("Treating book %s with %s chapters ...",
                                book, len(b.chapters))   
                        for chap in b.chapters:                        
                            chapter = Chapter(**(omit(chap.__dict__, "book_rank", "verses"))) #"book_id", 
                            chapter.book_id = book.id                                                
                            crud.chapter.create(self.db, chapter)  
                            
                            if chap.verses:
                                for v in chap.verses:      
                                    verse = Verse(**(omit(v.__dict__, "chapter_rank", "book_rank"))) 
                                    verse.chapter_id = chapter.id
                                    chapter.verses.append(verse)

                self.db.commit()
                logger.info("%s book inserted.", len(books))                  
                
                
    def check_rules(self, user_rules):
        if user_rules:
            for rule, params in user_rules.items():                                          
                getattr(self, RulesEnum(rule).value)(*params)
      
        
    # Below are validation generic methods
    def book_count(self, expected):
        assert(self.q_book().count() == expected)  
        
    def boot_count_by_category(self, category, expected):        
        assert(self.q_book().filter(Book.category == category).count() == expected)
        
    def book_category(self, rank, expected):
        """assert books placed in right category     

        Args:
            rank (int): book rank
            expected (BookTypeEnum): expected category
        """
        assert(self.q_book().filter(Book.rank==rank).first().category == expected)
        
    def book_chapter_count(self, book_rank, expected_chapter_count):              
        assert(self.q_chapter().filter(Book.rank == book_rank).count() == expected_chapter_count)
        
    def count_verse(self, book_rank, chapter_rank, exoected):
        assert(self.q_verse().filter(Book.rank == book_rank, Chapter.rank==chapter_rank).count() == exoected)  