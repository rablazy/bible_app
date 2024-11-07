import enum
from typing import List, Optional

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text, func, select
from sqlalchemy.orm import Mapped, column_property, relationship

from app.db.base_class import Base


class Language(Base):
    """Language model
    e.g : (fr, Français), (en, English), ..
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    code = Column(String(5))

    def __str__(self):
        return self.name


class BookTypeEnum(enum.Enum):
    OLD = "Old"
    NEW = "New"
    APOCRYPHAL = "Apocryphal"


class Bible(Base):
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(128))
    description = Column(String(1024))
    comment = Column(Text)
    year = Column(Integer)
    src = Column(String(1024))
    src_url = Column(String(1024))
    lang_id = Column(Integer, ForeignKey("language.id"))
    lang = relationship("Language")
    # books = relationship("Book", back_populates="bible", cascade="all, delete")


class Verse(Base):
    id = Column(Integer, primary_key=True, index=True)
    subtitle = Column(String(1024), nullable=True)
    content = Column(String(4096), nullable=False)
    rank = Column(Integer, nullable=False)
    rank_all = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    refs = Column(String)
    chapter_id = Column(
        Integer, ForeignKey("chapter.id", ondelete="cascade"), nullable=False
    )
    chapter = relationship("Chapter", back_populates="verses")

    @property
    def chapter_rank(self):
        return self.chapter.rank

    @property
    def book_rank(self):
        return self.chapter.book.rank if (self.chapter and self.chapter.book) else None

    @property
    def book_name(self):
        return self.chapter.book.name if (self.chapter and self.chapter.book) else None

    @property
    def book_short_name(self):
        return (
            self.chapter.book.short_name
            if (self.chapter and self.chapter.book)
            else None
        )

    def __str__(self):
        return f"{self.chapter}.{self.rank}"


class Chapter(Base):
    # __tablename__ = "chapter"

    id = Column(Integer, primary_key=True, index=True)
    rank = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    book_id = Column(Integer, ForeignKey("book.id", ondelete="cascade"), nullable=False)
    book = relationship("Book", back_populates="chapters")
    verses: Mapped[List["Verse"]] = relationship(
        back_populates="chapter",
        cascade="all, delete",
        passive_deletes=True,
        order_by="Verse.rank_all",
    )

    verse_count = column_property(
        select(func.count(Verse.chapter_id))
        .filter(Verse.chapter_id == id)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self):
        return (
            f"{self.book.short_name.capitalize()}. {self.rank}"
            if self.book
            else self.code
        )

    @property
    def name(self):
        return f"{self.book.name} {self.rank}" if self.book else self.code

    @property
    def book_rank(self):
        return self.book.rank if self.book else None


class Book(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    short_name = Column(String(10))
    code = Column(String(10))
    rank = Column(Integer, nullable=False)
    classification = Column(String(256))
    category = Column(Enum(BookTypeEnum, nullable=False))
    bible_id = Column(
        Integer, ForeignKey("bible.id", ondelete="cascade"), nullable=False
    )
    bible = relationship("Bible")  # back_populates="books"
    chapters: Mapped[List["Chapter"]] = relationship(
        back_populates="book",
        cascade="all, delete",
        passive_deletes=True,
        order_by="Chapter.rank",
    )
    chapter_count = column_property(
        select(func.count(Chapter.book_id))
        .filter(Chapter.book_id == id)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self):
        return self.name


class Theme(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("theme.id", ondelete="cascade"))
    parent = relationship("Theme", remote_side=[id])
    references = Column(Text)

    @property
    def parent_name(self):
        return self.parent.name if self.parent else None
