import http
import logging
import os
import pathlib
from typing import Annotated, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_, or_

from app import crud
from app.api import deps
from app.api.routers.utils import parse_bible_ref, set_query_parameter
from app.core.config import settings
from app.models.bible import Bible, Book, BookTypeEnum, Chapter, Verse
from app.schemas.bible import (
    BibleItem,
    BookItemShort,
    ChapterItem,
    ChapterItemNoVerses,
    ListItems,
    VerseItem,
    VerseItems,
    VerseReferences,
)

logger = logging.getLogger(__name__)
header_scheme = APIKeyHeader(name="api-key")

router = APIRouter()

BASE_PATH = pathlib.Path(__file__).resolve().parent.parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


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
def view_book_chapters(
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
    "/{version}/chapters/{chapter_code}",
    status_code=200,
    response_model=ChapterItem,
)
def get_chapter(
    *,
    version: str,
    chapter_code: str,
    db: Session = Depends(deps.get_db),
):
    """Get one chapter with all its verses"""

    q = crud.chapter.get_items(db, version, filters=[Chapter.code == chapter_code])
    chapter = q.first()
    if chapter:
        return chapter
    raise HTTPException(status_code=404, detail="Chapter not found")


@router.get(
    "/{version}/verses/{from_book}",  # /{from_chapter}/{from_verse}
    status_code=200,
    response_model=VerseItems,
)
def search_verses(
    *,
    version: str,
    from_book: str,
    from_chapter: Annotated[int, Query(ge=1)] = None,
    from_verse: Annotated[int, Query(ge=1)] = 1,
    to_book: Optional[str] = None,
    to_chapter: Optional[int] = None,
    to_verse: Optional[int] = None,
    translate_versions: List[str] = Query(None),
    mix_trans: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    max_results: Annotated[int, Query(ge=1, le=100)] = 100,
    to_html: bool = False,
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Load on verse or multiple verses across chapters"""

    start_book = crud.book.query_by_name_or_code(db, from_book) if from_book else None
    f_book = start_book.rank if start_book else -1

    t_book = -1
    if to_book is None:
        to_book = from_book
        t_book = f_book

    dest_book = crud.book.query_by_name_or_code(db, to_book)

    if not to_book == from_book:
        t_book = dest_book.rank if dest_book else -1

    if t_book < f_book:
        raise HTTPException(
            status_code=400,
            detail="<to_book> param should be greater than <from_book>",
        )

    if to_chapter is None:
        if from_chapter is None:
            from_chapter = 1
            to_chapter = max([c.rank for c in dest_book.chapters])
        else:
            if f_book == t_book:
                to_chapter = from_chapter
            else:
                to_chapter = max([c.rank for c in dest_book.chapters])

    if f_book == t_book and to_chapter < from_chapter:
        raise HTTPException(
            status_code=400,
            detail="<to_chapter> param should be greater than <from_chapter>",
        )

    if not translate_versions:
        translate_versions = []
    try:
        translate_versions.remove(version)
    except (ValueError, AttributeError):
        pass
    translate_versions.insert(0, version)

    results = []
    trans = []
    total = 0
    for vers in translate_versions:
        qf = crud.verse.query_by_version(db, vers)

        start_verse = qf.filter(
            and_(
                Book.rank == f_book,
                Chapter.rank == from_chapter,
                Verse.rank == from_verse,
            )
        ).first()
        if to_verse is not None and to_verse > 0:
            end_verse = qf.filter(
                and_(
                    Book.rank == t_book,
                    Chapter.rank == to_chapter,
                    Verse.rank == to_verse,
                )
            ).first()
        else:
            qf = qf.filter(Book.rank == t_book)
            if to_chapter is not None and to_chapter > 0:
                qf = qf.filter(Chapter.rank == to_chapter)
            end_verse = qf.order_by(Verse.rank_all.desc()).first()

        if start_verse and end_verse:
            logger.info("start_verse : %s , end_verse: %s", start_verse, end_verse)
            base_q = crud.verse.query_by_version(db, vers)
            q = base_q.filter(
                Verse.rank_all >= start_verse.rank_all,
                Verse.rank_all <= end_verse.rank_all,
            )
            res = q.order_by(Verse.rank_all).offset(offset).limit(max_results).all()
            if mix_trans or vers == version:
                results.extend(res)
                total = max(
                    total, q.count()
                )  # number of verses may differ per translation
            else:
                trans.append({"version": vers, "verses": res})

    if mix_trans:
        results.sort(key=lambda x: (x.book_rank, x.chapter_rank, x.rank))

    data = {
        "results": results,
        "count": len(results),
        "offset": offset,
        "total": total,
        "trans": trans,
        "more_url": set_query_parameter(
            str(request.url),
            new_param_values={"offset": offset + max_results},
        )
        if results
        else None,
        "less_url": set_query_parameter(
            str(request.url),
            new_param_values={"offset": offset - max_results},
        )
        if offset > 0
        else None,
    }

    if results:
        data.update(
            {
                "previous": base_q.filter(
                    Verse.rank_all == start_verse.rank_all - 1
                ).first(),
                "next": base_q.filter(Verse.rank_all == end_verse.rank_all + 1).first(),
            }
        )

    if to_html:
        data.update({"request": request})
        return TEMPLATES.TemplateResponse("verse.html", data)
    else:
        return data


@router.get(
    "/{version}/verses_ref",
    status_code=200,
    response_model=VerseReferences,
)
def search_references(
    *,
    version: str,
    references: str,
    # to_html: bool = False,
    # request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Search one or multiple references using common format:<br/>
    (Book identifier can be name or short_name or code)
    <p>e.g :
    <ul>
    <li>Rev.5:1,4-5,17,21; Acts 5:15-20,25; John 3.16;Psa 23;1 John 3.16-19,22
    <li>psa_ 24;apocalypse 5:10-12; 2 the 3:1,4,6-8<br/>
    </ul>

    """
    refs = parse_bible_ref(references)
    results = []
    for ref in refs:
        qf = crud.verse.query_by_version(db, version)
        logger.info(ref)
        book_name = ref["book"]
        chapter_rank = ref["chapter"]
        q = qf.filter(
            or_(
                Book.name.ilike(book_name),
                Book.short_name.ilike(book_name),
                Book.code.ilike(book_name),
            )
        ).filter(Chapter.rank == chapter_rank)

        verse_range = ref["verses"]
        if verse_range:
            for verse in verse_range:
                interval = verse.split("-")
                if len(interval) == 1:
                    qv = q.filter(Verse.rank == interval[0].strip())
                else:
                    qv = q.filter(
                        Verse.rank >= interval[0].strip(),
                        Verse.rank <= interval[1].strip(),
                    )
                results.append(
                    {
                        "reference": f"{book_name} {chapter_rank}:{verse}",
                        "verses": qv.all(),
                    }
                )
        else:
            results.append(
                {
                    "reference": f"{book_name} {chapter_rank}",
                    "verses": q.all(),
                }
            )

    return {"results": results}


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
def delete_bible_by_id(
    bid: int, db: Session = Depends(deps.get_db), key: str = Depends(header_scheme)
):
    """Delete bible by id"""
    try:
        if key == settings.SECRET_API_KEY:
            crud.bible.delete_by_id(db, bid)
            return {"msg": "Successfully deleted."}
        else:
            raise HTTPException(status_code=403, detail="Bad key supplied")
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Bible with id {bid} not found")


@router.delete("/delete/version/{version}")
def delete_bible_by_version(
    version: str, db: Session = Depends(deps.get_db), key: str = Depends(header_scheme)
):
    """Delete bible by version name"""
    if key == settings.SECRET_API_KEY:
        bible = crud.bible.query_by_version(db, version).first()
        if bible:
            crud.bible.delete_by_id(db, bible.id)
            return {"msg": "Successfully deleted."}
        else:
            raise HTTPException(
                status_code=404, detail=f"Bible version {version} not found"
            )
    else:
        raise HTTPException(status_code=403, detail="Bad key supplied")
