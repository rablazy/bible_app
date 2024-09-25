from app.crud.base import CRUD
from app.models.bible import Bible, Book, Chapter, Verse, Language
from sqlalchemy.orm import Session


class CRUDLanguage(CRUD[Language]):    
    
    def get_by_code(self, db: Session, code: str):
        return db.query(self.model).filter(self.model.code==code).first()

class CRUDBook(CRUD[Book]):
    pass        

class CRUDChapter(CRUD[Chapter]):
    pass

class CRUDVerse(CRUD[Verse]):
    pass


language = CRUDLanguage(Language)
book = CRUDBook(Book)
bible = CRUDBook(Bible)
chapter = CRUDChapter(Chapter)
verse = CRUDVerse(Verse)
