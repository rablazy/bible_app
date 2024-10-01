from typing import Annotated, Any, Optional

from fastapi import Path
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
def search_bibles(
    *,
    db: Session = Depends(deps.get_db),
    lang: Optional[str] = None,
    version: Optional[str] = None,
    offset: Optional[int] = 0,
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
    q = crud.bible.get_multi(db, filters=filters, query_only=True)
    
    return {
        "results": list(q.order_by(Bible.lang_id).offset(offset).limit(max_results).all()),
        "count" : q.count()
    }


@router.get("/{version}/books/", status_code=200, response_model=ListItems[BookItemShort])
def search_books(
    *,
    version: str,
    book_type: Optional[str] = Query(
        "All", enum=[BookTypeEnum.OLD.value, BookTypeEnum.NEW.value, BookTypeEnum.APOCRYPHAL.value]),
    short_name: Optional[str] = None,
    offset : Optional[int] = 0,
    max_results: Optional[int] = 100,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for book(s) in specific bible
    """
    filters = [Bible.version.ilike(version)]
    if book_type != "All":
        filters.append(Book.category == book_type.upper())
    if short_name:
        filters.append(Book.short_name.ilike(short_name))
    q = db.query(Book).join(Bible).filter(*filters)    
    return {
        "results": list(q.offset(offset).limit(max_results).all()), 
        "count": q.count()
    }


@router.get("/{version}/verses/{from_book}/{from_chapter}", status_code=200, response_model=VerseItems)
def search_verses(
    *,
    version: str,
    from_book: Annotated[int, Path(ge=1)],
    from_chapter: Annotated[int, Path(ge=1)],
    from_verse: Optional[int] = 1,
    to_book: Optional[int] = -1,
    to_chapter: Optional[int] = -1,
    to_verse: Optional[int] = -1,
    offset : Optional[int] = 0,
    max_results: Optional[int] = 100,
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
    
    qf = crud.verse.query_by_version(db, version)
        
    start_verse = qf.filter(and_(Book.rank == from_book, 
                                      Chapter.rank == from_chapter, Verse.rank == from_verse)).first()
    if to_verse > 0:       
        end_verse = qf.filter(and_(Book.rank == to_book, 
                                   Chapter.rank == to_chapter, Verse.rank == to_verse)).first()      
    else:          
        qf = qf.filter(Book.rank == to_book)
        if to_chapter > -1 :
            qf = qf.filter(Chapter.rank == to_chapter)
        end_verse = qf.order_by(Verse.id.desc()).first()            
   
    if start_verse and end_verse:
        base_q = crud.verse.query_by_version(db, version)
        q = base_q.filter(Verse.id >= start_verse.id, Verse.id <= end_verse.id)       
        return {
            "results": list(q.offset(offset).limit(max_results).all()), 
            "count": q.count(),
            "previous": base_q.filter(Verse.id == start_verse.id-1).first(),
            "next": base_q.filter(Verse.id == end_verse.id+1).first()
        }
    else:
        return {"results": []}
      
    
