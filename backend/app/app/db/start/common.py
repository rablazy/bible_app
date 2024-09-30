import os 
import pathlib
from app.models.bible import Bible, Book, Chapter, Verse, Language
from app.db.session import SessionLocal
from app import crud

ROOT = pathlib.Path(__file__).resolve().parent.parent

class ImportBible:
    
    def __init__(self):
        self.db = SessionLocal()
        self.language = None
        self.run_import() 
        
    def version(self):
        raise NotImplementedError
    
    def lang(self):
        raise NotImplementedError    
    
    def import_data(self):
        raise NotImplementedError
    
    def check_data(self):        
        raise NotImplementedError    
    
    def run_import(self):
        self.lang_exists_in_db()
        self.import_data()
        self.set_query_filter()
        self.check_data()
    
    def src(self, extension):
        return os.path.join(ROOT, 'data', 'bible', self.lang(), f'{self.version()}.{extension}')
    
    def set_query_filter(self):        
        b = self.db.query(Bible).filter(Bible.version.ilike(self.version())).first()        
        self.version_filter = [Book.bible_id == b.id]       
    
    def q_book(self):        
        return self.db.query(Book).filter(*self.version_filter)
    
    def q_chapter(self):        
        return self.db.query(Chapter).join(Chapter.book).filter(*self.version_filter)
    
    def q_verse(self):        
        return self.db.query(Verse).join(Chapter).join(Chapter.book).filter(*self.version_filter)
    
    def lang_exists_in_db(self):
        lang = crud.language.get_by_code(self.db, self.lang())
        if not lang:
            raise ValueError(f"Source language {self.lang()} not found in db")    
        self.language = lang        
    
    def exists_in_db(self):
        return self.db.query(Bible).join(Language)\
                    .filter(Bible.version.ilike(self.version()))\
                    .filter(Language.code.ilike(self.lang())).count()