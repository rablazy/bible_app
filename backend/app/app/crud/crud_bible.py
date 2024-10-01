from app.crud.base import CRUD
from app.models.bible import Bible, Book, Chapter, Verse, Language
from sqlalchemy.orm import Session


class CRUDLanguage(CRUD[Language]):    
    
    def get_by_code(self, db: Session, code: str):
        return db.query(self.model).filter(self.model.code==code).first()


class CRUDBible(CRUD[Bible]): 
    def query_by_version_and_lang(self, db: Session, version: str, lang:str):
        return db.query(Bible).join(Language).filter(
            Bible.version.ilike(version),
            Language.code.ilike(lang)
        )  

class CRUDBook(CRUD[Book]):...  

class CRUDChapter(CRUD[Chapter]): ...

class CRUDVerse(CRUD[Verse]):
    def query_by_version(self, db: Session, version:str):
        return db.query(Verse).join(Chapter).join(Book).join(Bible).filter(Bible.version.ilike(version))
    
    

language = CRUDLanguage(Language)
book = CRUDBook(Book)
bible = CRUDBible(Bible)
chapter = CRUDChapter(Chapter)
verse = CRUDVerse(Verse)
