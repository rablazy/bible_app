from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_utils import ChoiceType

from typing import List

from app.db.base_class import Base


class Language(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)    
    
    def __str__(self):
        return self.name
    

OLD_TESTAMENT = 1
NEW_TESTAMENT = 2
BOOK_CATEGORIES = (
        (OLD_TESTAMENT, 'Old Testament'),
        (NEW_TESTAMENT, 'New Testament')
)

class Book(Base):    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True)
    short_name = Column(String(10))
    rank = Column(Integer, nullable=False)
    category =  ChoiceType(BOOK_CATEGORIES, impl=Integer)
    lang_id = Column(Integer, ForeignKey('language.id'))
    lang = relationship('Language')
    # chapters = Mapped[List["Chapter"]] = relationship(back_populates="book")
    chapters = relationship(
        "Chapter",
        cascade="all,delete-orphan",
        back_populates="book",
        uselist=True,
    )
    
    def __str__(self):
        return self.name


class Chapter(Base):
    id = Column(Integer, primary_key=True, index=True)
    rank = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='chapters')
    verses = relationship(
        "Verse",
        cascade="all,delete-orphan",
        back_populates="chapter",
        uselist=True,
    )     
    
    def __str__(self):
        return f"{self.book.short_name.capitalize()}. {self.rank}"


class Verse(Base):
    id = Column(Integer, primary_key=True, index=True)
    subtitle = Column(String(1024), nullable=True)
    content = Column(String(4096), nullable=False)
    rank = Column(Integer, nullable=False)
    chapter_id = Column(Integer, ForeignKey('chapter.id'))
    chapter = relationship('Chapter', back_populates='verses')
    
    def __str__(self):
        return f"{self.chapter}.{self.rank}"