from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_, and_

from app import crud
from app.api import deps

from app.models.bible import Bible, Book, Chapter, Verse, BookTypeEnum
from app.schemas.bible import BookItemShort, ChapterItem, ListItems, BibleItem, BookItem, VerseItem

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


@router.get("/{bible_id}/books/", status_code=200, response_model=ListItems[BookItemShort])
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

@router.get("/verse/{book_start}/{chapter_start}/{verse_start}", status_code=200, response_model=ListItems[VerseItem])
def search_chapter(
    *,    
    book_start: int,
    chapter_start: int,
    verse_start: int,     
    # book_end: Optional[int] = -1,
    chapter_end: Optional[int] = -1,
    verse_end: Optional[int] = -1,    
    db: Session = Depends(deps.get_db),
) -> dict:
    # if book_end == -1:
    #     book_end = book_start
    if chapter_end == -1:
        chapter_end = chapter_start
    
    # results = crud.book.get_multi(db, limit=max_results, filters=filters) 
    q = db.query(Verse).join(Chapter).join(Book)    
    if book_start:
        q = q.filter(Book.rank == book_start)
    # if book_end and book_end > book_start:
    #     q = q.filter(Book.rank <= book_end)
    if chapter_start:        
        if chapter_end :
            if chapter_start == chapter_end:
                q = q.filter(Chapter.rank == chapter_start).filter(Verse.rank >= verse_start)
                if verse_end > -1:
                    q = q.filter(Verse.rank <= verse_end)
            else:     
                filters = []           
                for i in range(chapter_start, chapter_end+1):
                    if i == chapter_start:
                        filters.append(and_(Chapter.rank == chapter_start, Verse.rank >= verse_start))
                    else:
                        if i == chapter_end:
                            filters.append(and_(Chapter.rank == chapter_end, Verse.rank <= verse_end))
                        else:
                            filters.append(Chapter.rank == i)
                q = q.filter(or_(*filters))
    # print(q)  
    # print(f"book_rank : {book_start} , chapter_start: {chapter_start}, chapter_end : {chapter_end}")  
    # print(f"verse_start : {verse_start}, verse_end : {verse_end}")  
    results = q.all()
    return {"results": list(results)}
    
        
           


