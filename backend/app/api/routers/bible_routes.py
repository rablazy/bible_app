from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_, and_

from app import crud
from app.api import deps

from app.models.bible import Bible, Book, Chapter, Verse, BookTypeEnum
from app.schemas.bible import BookItemShort, ChapterItem, ListItems, BibleItem, BookItem, VerseItem, VerseItems

import logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search/", status_code=200, response_model=ListItems[BibleItem])
def search_bible(
    *,
    db: Session = Depends(deps.get_db),
    lang: Optional[str] = None,
    version: Optional[str] = None,
    max_results: Optional[int] = 10
) -> dict:
    """
    Search for bible(s)
    """
    filters = []
    if lang:
        filters.append(Bible.lang.has(code=lang))
    if version:
        filters.append(Bible.version.ilike(version))
    results = crud.bible.get_multi(
        db, limit=max_results, filters=filters)
    return {"results": list(results)}


@router.get("/{bible_id}/books/", status_code=200, response_model=ListItems[BookItemShort])
def search_books(
    *,
    bible_id: int,
    book_type: Optional[str] = Query(
        "All", enum=[BookTypeEnum.OLD.value, BookTypeEnum.NEW.value]),
    short_name: Optional[str] = None,
    max_results: Optional[int] = 70,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for book(s) in specific bible
    """
    filters = [Book.bible.has(id=bible_id)]
    if book_type != "All":
        filters.append(Book.category == book_type.upper())
    if short_name:
        filters.append(Book.short_name.ilike(short_name))
    results = crud.book.get_multi(db, limit=max_results, filters=filters)
    return {"results": list(results)}


@router.get("/verses/{from_book}/{from_chapter}", status_code=200, response_model=VerseItems)
def search_chapter(
    *,
    from_book: int,
    from_chapter: int,
    from_verse: Optional[int] = 1,
    to_book: Optional[int] = -1,
    to_chapter: Optional[int] = -1,
    to_verse: Optional[int] = -1,
    db: Session = Depends(deps.get_db),
) -> dict:
    if to_book == -1:
        to_book = from_book
    
    if to_book < from_book:
        raise ValueError(f"<to_book> param should be greater than <from_book>")
    
    if to_chapter == -1 and from_book == to_book:
        to_chapter = from_chapter    
        
    if from_book == to_book and to_chapter < from_chapter:
        raise ValueError(f"<to_chapter> param should be greater than <from_chapter>")       
        
    start_verse = db.query(Verse).join(Chapter).join(Book).\
        filter(and_(Book.rank == from_book, Chapter.rank == from_chapter, Verse.rank == from_verse)).first()
    if to_verse > 0:       
        end_verse = db.query(Verse).join(Chapter).join(Book).\
            filter(and_(Book.rank == to_book, Chapter.rank == to_chapter, Verse.rank == to_verse)).first()      
    else:          
        q = db.query(Verse).join(Chapter).join(Book).\
            filter(Book.rank == to_book)
        if to_chapter > -1 :
            q = q.filter(Chapter.rank == to_chapter)
        end_verse = q.order_by(Verse.id.desc()).first()            
   
    if start_verse and end_verse:
        q = db.query(Verse).join(Chapter).join(Book).filter(Verse.id >= start_verse.id, Verse.id <= end_verse.id)     
        results = q.all()
        return {"results": list(results)}
    else:
        return {"results": []}
      
    
