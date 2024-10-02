from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, column_property, Mapped
from sqlalchemy import select, func

from typing import List

from app.db.base_class import Base


class Language(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True) 
    code = Column(String(5))   
    
    def __str__(self):
        return self.name
    

import enum
class BookTypeEnum(enum.Enum):
    OLD = 'Old'
    NEW = 'New'
    APOCRYPHAL = 'Apocryphal'

class Bible(Base):
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(128))
    description = Column(String(1024))    
    year = Column(Integer)
    src = Column(String(1024))
    src_url = Column(String(1024))
    lang_id = Column(Integer, ForeignKey('language.id'))
    lang = relationship('Language')
    
    
class Chapter(Base):
    # __tablename__ = "chapter"
    
    id = Column(Integer, primary_key=True, index=True)
    rank = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='chapters')
    verses : Mapped[List["Verse"]] = relationship(back_populates="chapter")           
    
    def __str__(self):
        return f"{self.book.short_name.capitalize()}. {self.rank}"
        

class Book(Base):    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    short_name = Column(String(10))
    code = Column(String(10))
    rank = Column(Integer, nullable=False)
    classification = Column(String(256))
    category =  Column(Enum(BookTypeEnum, nullable=False))    
    bible_id = Column(Integer, ForeignKey('bible.id'))
    bible = relationship('Bible')
    chapters : Mapped[List["Chapter"]] = relationship(back_populates="book")     
    chapter_count = column_property(
        select(func.count(Chapter.book_id)).filter(Chapter.book_id == id).scalar_subquery(),
        deferred=True,
    )
    
    def __str__(self):
        return self.name


class Verse(Base):
    id = Column(Integer, primary_key=True, index=True)
    subtitle = Column(String(1024), nullable=True)
    content = Column(String(4096), nullable=False)
    rank = Column(Integer, nullable=False)
    chapter_id = Column(Integer, ForeignKey('chapter.id'))
    chapter = relationship('Chapter', back_populates='verses')
    
    @property
    def chapter_rank(self):
        return self.chapter.rank
    
    @property
    def book_rank(self):
        return self.chapter.book.rank    
    
    def __str__(self):
        return f"{self.chapter}.{self.rank}"