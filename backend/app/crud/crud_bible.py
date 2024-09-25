from app.crud.base import CRUD
from app.models.bible import Book, Chapter, Verse, Language


class CRUDLanguage(CRUD[Language]):    
    pass

class CRUDBook(CRUD[Book]):
    pass        

class CRUDChapter(CRUD[Chapter]):
    pass

class CRUDVerse(CRUD[Verse]):
    pass


language = CRUDLanguage(Language)
book = CRUDBook(Book)
chapter = CRUDChapter(Chapter)
verse = CRUDVerse(Verse)
