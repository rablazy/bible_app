from app.models.bible import Bible, Book, Chapter, Verse
from app.db.session import SessionLocal

class ImportBible:
    
    def __init__(self):
        self.db = SessionLocal()
        self.import_json_data() 
        self.set_default_filter()
        self.check_data()
        
    def version(self):
        raise NotImplementedError
    
    def set_default_filter(self):        
        b = self.db.query(Bible).filter(Bible.version.ilike(self.version())).first()        
        self.version_filter = [Book.bible_id == b.id]   

    def import_json_data(self):
        raise NotImplementedError
    
    def check_data(self):        
        raise NotImplementedError
    
    def q_book(self):        
        return self.db.query(Book).filter(*self.version_filter)
    
    def q_chapter(self):        
        return self.db.query(Chapter).join(Chapter.book).filter(*self.version_filter)
    
    def q_verse(self):        
        return self.db.query(Verse).join(Chapter).join(Chapter.book).filter(*self.version_filter)