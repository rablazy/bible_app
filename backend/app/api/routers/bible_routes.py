from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps

from app.models.bible import Bible, Book, Chapter, Verse, BookTypeEnum
from app.schemas.bible import ListItems, BibleItem, BookItem

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
    if lang :
        filters.append(Bible.lang.has(code=lang))
    if version:
        filters.append(Bible.version.ilike(version))
    results = crud.bible.get_multi(
        db, limit=max_results, filters=filters) 
    return {"results": list(results)}


@router.get("/{bible_id}/books/", status_code=200, response_model=ListItems[BookItem])
def search_books(
    *,    
    bible_id: int,
    book_type: Optional[str]=Query("All", enum=[BookTypeEnum.OLD.value, BookTypeEnum.NEW.value]),
    short_name: Optional[str]= None,
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





