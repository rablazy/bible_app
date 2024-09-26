from app.crud.base import CRUD
from app.models.bible import Bible, Book, Chapter, Verse, Language
from sqlalchemy.orm import Session


class CRUDLanguage(CRUD[Language]):    
    
    def get_by_code(self, db: Session, code: str):
        return db.query(self.model).filter(self.model.code==code).first()


class CRUDBible(CRUD[Bible]): ...
    # def get_by_version_and_lang(self, db: Session, version: str, lang:str):
    #     return db.query(Book).filter(
    #         Book.version.ilike(version),
    #         Book.lang.ilike(lang)
    #         ).first()   

class CRUDBook(CRUD[Book]):...  

class CRUDChapter(CRUD[Chapter]): ...

class CRUDVerse(CRUD[Verse]): ...
    

language = CRUDLanguage(Language)
book = CRUDBook(Book)
bible = CRUDBible(Bible)
chapter = CRUDChapter(Chapter)
verse = CRUDVerse(Verse)
