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

class ImportBible:
    
    def __init__(self, 
                 lang:str=None, 
                 version:str=None, 
                 file_path = None,
                 file_encoding = "UTF-8",
                 file_type="json"
        ):
        self.db = SessionLocal()
        self.lang = lang
        self.language = None
        
        self.version = version
        self.file_type = file_type        
        self.file_encoding = file_encoding
        self.file_path = file_path or self.default_file_path()
        
        self.run_import()       
        
    def import_data(self):        
        if self.file_type == "json":
            self.import_json_data()
        else:
            raise NotImplementedError
    
    def check_data(self):        
        raise NotImplementedError    
    
    def run_import(self):
        self.lang_exists_in_db()
        self.import_data()
        self.set_query_filter()
        self.check_data()
    
    def default_file_path(self):
        return os.path.join(ROOT, 'data', 'bible', self.lang, f"{self.version}.{self.file_type}")
    
    def set_query_filter(self):        
        b = self.db.query(Bible).filter(Bible.version.ilike(self.version)).first()        
        self.version_filter = [Book.bible_id == b.id]       
    
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
        return self.db.query(Bible).join(Language)\
                    .filter(Bible.version.ilike(self.version))\
                    .filter(Language.code.ilike(self.lang)).count()
                    
    
    def import_json_data(self):
        """
        Import generic bible with <BibleItem> json format in input
        """           
        with open(self.file_path, 'r+', encoding=self.file_encoding) as f:            
            datas = f.read()                              
            bible_item = BibleItem.model_validate(pydantic_core.from_json(datas))                                
            
            if not self.exists_in_db(): 
                bible = Bible(**(omit(bible_item.__dict__, "books", "lang")))    
                bible.language = self.language                  
                crud.bible.create(self.db, bible)
                
                books = bible_item.books                                
                for b in books:                    
                    book = Book(**(omit(b.__dict__, "chapters", "bible_id", "chapter_count")))
                    book.category = BookTypeEnum(b.category)
                    book.bible = bible                    
                    crud.book.create(self.db, book)                                   

                    if b.chapters:
                        logger.info("Treating book %s with %s chapters ...",
                                book, len(b.chapters))   
                        for chap in b.chapters:                        
                            chapter = Chapter(**(omit(chap.__dict__, "book_id", "book_rank", "verses")))
                            chapter.book = book                                                
                            crud.chapter.create(self.db, chapter)  
                            
                            if chap.verses:
                                for v in chap.verses:      
                                    verse = Verse(**(omit(v.__dict__, "chapter_rank", "book_rank"))) 
                                    verse.chapter = chapter                                                                                       
                                    chapter.verses.append(verse)

                self.db.commit()
                logger.info("%s book inserted.", len(books))      