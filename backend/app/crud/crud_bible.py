from sqlalchemy import delete, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUD
from app.models.bible import Bible, Book, Chapter, Language, Verse


class CRUDLanguage(CRUD[Language]):
    """Language model queries"""

    def get_by_code(self, db: Session, code: str):
        return db.query(self.model).filter(self.model.code == code).first()


class CRUDBible(CRUD[Bible]):
    """Bible model queries"""

    def query_by_version_and_lang(self, db: Session, version: str, lang: str):
        return (
            db.query(Bible)
            .join(Language)
            .filter(Bible.version.ilike(version), Language.code.ilike(lang))
        )

    def query_by_version(self, db: Session, version: str):
        """Search bible with version"""
        return db.query(Bible).filter(Bible.version.ilike(version))

    def delete_by_id(self, db: Session, bible_id: int):
        """Delete bible with all its content"""
        obj = db.query(Bible).get(bible_id)
        if obj:
            stmt = delete(Book).where(Book.bible_id == obj.id)
            db.execute(stmt)
            db.delete(obj)
            db.commit()
        else:
            raise ValueError(f"Bible with id {bible_id} not found")


class CRUDBook(CRUD[Book]):
    ...


class CRUDChapter(CRUD[Chapter]):
    ...


class CRUDVerse(CRUD[Verse]):
    def query_by_version(self, db: Session, version):
        return (
            db.query(Verse)
            .join(Chapter)
            .join(Book)
            .join(Bible)
            .filter(Bible.version.ilike(version))
        )

    def query_by_versions(self, db: Session, *versions):
        q = db.query(Verse).join(Chapter).join(Book).join(Bible)
        version_filter = [Bible.version.ilike(version) for version in versions]
        q = q.filter(or_(*version_filter))
        return q


language = CRUDLanguage(Language)
book = CRUDBook(Book)
bible = CRUDBible(Bible)
chapter = CRUDChapter(Chapter)
verse = CRUDVerse(Verse)
