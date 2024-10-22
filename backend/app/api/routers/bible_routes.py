import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_, or_

from app import crud
from app.api import deps
from app.models.bible import Bible, Book, BookTypeEnum, Chapter, Verse
from app.schemas.bible import (
    BibleItem,
    BookItemShort,
    ChapterItem,
    ChapterItemNoVerses,
    ListItems,
    VerseItems,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search/", status_code=200, response_model=ListItems[BibleItem])
def search_bibles(
    *,
    db: Session = Depends(deps.get_db),
    lang: Optional[str] = None,
    version: Optional[str] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    max_results: Annotated[int, Query(ge=1, le=100)] = 100,
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
    results = list(q.order_by(Bible.lang_id).offset(offset).limit(max_results).all())

    return {
        "results": results,
        "total": q.count(),
        "count": len(results),
        "offset": offset,
    }


@router.get(
    "/{version}/books/", status_code=200, response_model=ListItems[BookItemShort]
)
def search_books(
    *,
    version: str,
    book_type: Optional[str] = Query(
        "All",
        enum=[
            BookTypeEnum.OLD.value,
            BookTypeEnum.NEW.value,
            BookTypeEnum.APOCRYPHAL.value,
        ],
    ),
    name: Optional[str] = None,
    code: Optional[str] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    max_results: Annotated[int, Query(ge=1, le=100)] = 100,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for book(s) in specific bible
    """
    filters = []
    if book_type != "All":
        filters.append(Book.category == book_type.upper())
    if name:
        filters.append(Book.name.icontains(name))
    if code:
        filters.append(Book.code.icontains(code))

    q = crud.book.get_items(
        db,
        version,
        filters=filters,
        ordering=Book.rank,
    )
    results = list(q.offset(offset).limit(max_results).all())
    return {
        "results": results,
        "total": q.count(),
        "count": len(results),
        "offset": offset,
    }


@router.get(
    "/{version}/{book_code}/chapters",
    status_code=200,
    response_model=ListItems[ChapterItemNoVerses],
)
def view_chapters(
    *,
    version: str,
    book_code: str,
    db: Session = Depends(deps.get_db),
):
    q = crud.chapter.get_items(
        db, version, filters=[Book.code == book_code], ordering=Chapter.rank
    )
    count = q.count()
    return {"results": q.all(), "offset": 0, "count": count, "total": count}


@router.get(
    "/{version}/verses/{from_book_code}/{from_chapter}/{from_verse}",
    status_code=200,
    response_model=VerseItems,
)
def search_verses(
    *,
    version: str,
    from_book_code: str,
    from_chapter: Annotated[int, Path(ge=1)],
    from_verse: Annotated[int, Path(ge=1)],
    to_book_code: Optional[str] = None,
    to_chapter: Optional[int] = None,
    to_verse: Optional[int] = None,
    translate_versions: List[str] = Query(None),
    offset: Annotated[int, Query(ge=0)] = 0,
    max_results: Annotated[int, Query(ge=1, le=100)] = 100,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Load on verse or multiple verses across chapters"""

    start_book = (
        db.query(Book).filter(Book.code.ilike(from_book_code)).first()
        if from_book_code
        else None
    )
    from_book = start_book.rank if start_book else -1

    to_book = -1
    if to_book_code is None:
        to_book_code = from_book_code
        to_book = from_book

    if not to_book_code == from_book_code:
        dest_book = db.query(Book).filter(Book.code.ilike(to_book_code)).first()
        to_book = dest_book.rank if dest_book else -1

    if to_book < from_book:
        raise HTTPException(
            status_code=400,
            detail="<to_book> param should be greater than <from_book>",
        )

    if to_chapter is None:
        if from_book == to_book:
            to_chapter = from_chapter
        else:
            to_chapter = max([c.rank for c in dest_book.chapters])

    if from_book == to_book and to_chapter < from_chapter:
        raise HTTPException(
            status_code=400,
            detail="<to_chapter> param should be greater than <from_chapter>",
        )

    qf = crud.verse.query_by_version(db, version)

    start_verse = qf.filter(
        and_(
            Book.rank == from_book,
            Chapter.rank == from_chapter,
            Verse.rank == from_verse,
        )
    ).first()
    if to_verse is not None and to_verse > 0:
        end_verse = qf.filter(
            and_(
                Book.rank == to_book, Chapter.rank == to_chapter, Verse.rank == to_verse
            )
        ).first()
    else:
        qf = qf.filter(Book.rank == to_book)
        if to_chapter is not None and to_chapter > 0:
            qf = qf.filter(Chapter.rank == to_chapter)
        end_verse = qf.order_by(Verse.rank_all.desc()).first()

    if start_verse and end_verse:
        print(f"start_verse : {start_verse} , end_verse: {end_verse}")
        base_q = crud.verse.query_by_version(db, version)
        q = base_q.filter(
            Verse.rank_all >= start_verse.rank_all, Verse.rank_all <= end_verse.rank_all
        )
        results = list(
            q.order_by(Verse.rank_all).offset(offset).limit(max_results).all()
        )

        try:
            translate_versions.remove(version)
        except (ValueError, AttributeError):
            pass

        trans = []
        if results and translate_versions:
            verse_codes = [verse.code for verse in results]
            for tv in translate_versions:
                qv = (
                    crud.verse.query_by_version(db, tv)
                    .filter(Verse.code.in_(verse_codes))
                    .order_by(Verse.rank_all)
                    .all()
                )
                trans.append({"version": tv, "verses": qv})

        return {
            "results": results,
            "count": len(results),
            "offset": offset,
            "total": q.count(),
            "trans": trans,
            "previous": base_q.filter(
                Verse.rank_all == start_verse.rank_all - 1
            ).first(),
            "next": base_q.filter(Verse.rank_all == end_verse.rank_all + 1).first(),
        }

    else:
        return {"results": []}


@router.get(
    "/{version}/search",
    status_code=200,
    response_model=VerseItems,
)
def search_text(
    *,
    version: str,
    text: List[str] = Query(...),
    book_code: Optional[str] = None,
    book_chapter: Optional[int] = None,
    translate_versions: List[str] = Query(None),
    offset: Annotated[int, Query(ge=0)] = 0,
    max_results: Annotated[int, Query(ge=1, le=100)] = 100,
    db: Session = Depends(deps.get_db),
):
    """Search for text in verses"""
    base_q = crud.verse.query_by_version(db, version)
    filters = []
    for t in text:
        filters.append(or_(Verse.content.icontains(t), Verse.subtitle.icontains(t)))
    q = base_q.filter(or_(*filters))
    if book_code:
        q = q.filter(Book.code == book_code)
    if book_chapter:
        q = q.filter(Chapter.rank == book_chapter)

    results = list(q.order_by(Verse.rank_all).offset(offset).limit(max_results).all())

    try:
        translate_versions.remove(version)
    except (ValueError, AttributeError):
        pass

    trans = []
    if results and translate_versions:
        verse_codes = [verse.code for verse in results]
        for tv in translate_versions:
            qv = (
                crud.verse.query_by_version(db, tv)
                .filter(Verse.code.in_(verse_codes))
                .order_by(Verse.rank_all)
                .all()
            )
            trans.append({"version": tv, "verses": qv})

    return {
        "results": results,
        "offset": offset,
        "count": len(results),
        "total": q.count(),
        "trans": trans,
    }


@router.delete("/delete/id/{bid}")
def delete_bible_by_id(bid: int, db: Session = Depends(deps.get_db)):
    """Delete bible by id"""
    try:
        crud.bible.delete_by_id(db, bid)
        return {"msg": "Successfully deleted."}
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Bible with id {bid} not found")


@router.delete("/delete/version/{version}")
def delete_bible_by_version(version: str, db: Session = Depends(deps.get_db)):
    """Delete bible by version name"""
    bible = crud.bible.query_by_version(db, version).first()
    if not bible:
        raise HTTPException(
            status_code=404, detail=f"Bible version {version} not found"
        )
    crud.bible.delete_by_id(db, bible.id)
    return {"msg": "Successfully deleted."}
