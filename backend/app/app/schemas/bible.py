from typing import Generic, List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class ListItems(BaseModel, Generic[DataT]):
    """Pydantic generic model for items in list"""

    results: Sequence[DataT]
    count: int = 0


class LanguageItem(BaseModel):
    """Pydantic model for Language"""

    name: str
    code: str
    model_config = ConfigDict(from_attributes=True)


class BibleItem(BaseModel):
    """Pydantic model for Bible"""

    model_config = ConfigDict(from_attributes=True)  # extra='allow|ignore',

    id: Optional[int] = None
    version: str
    year: Optional[int] = None
    src: str = None
    description: str = None
    src_url: Optional[str] = None
    lang: LanguageItem

    books: Optional[List["BookItem"]] = []

    # class Config:
    #     from_attributes = True


class BookItemShort(BaseModel):
    """Pydantic model for Book"""

    model_config = ConfigDict(from_attributes=True)
    # id : int
    name: str
    short_name: Optional[str] = None
    code: Optional[str] = None
    rank: int
    category: str = None
    classification: Optional[str] = None
    bible_id: Optional[int] = None
    chapter_count: int = 0


class ChapterItem(BaseModel):
    """Pydantic model for Chapter"""

    model_config = ConfigDict(from_attributes=True)
    # id : int
    rank: int
    book_id: Optional[int] = None
    book_rank: Optional[int] = None
    verses: List["VerseItem"] = []


class BookItem(BookItemShort):
    """Pydantic model for Book"""

    model_config = ConfigDict(from_attributes=True)
    chapters: List[ChapterItem] = []


class VerseItem(BaseModel):
    """Pydantic model for Verse"""

    model_config = ConfigDict(from_attributes=True)
    # id : int
    subtitle: Optional[Union[str, int, bytes]] = None
    content: str
    rank: int
    # chapter_id : int
    chapter_rank: Optional[int] = None
    book_rank: Optional[int] = None


class VerseItems(BaseModel):
    """Pydantic model for Verse list"""

    results: Sequence[VerseItem]
    next: Optional[VerseItem] = None
    previous: Optional[VerseItem] = None
    count: int = 0


BibleItem.model_rebuild()
ChapterItem.model_rebuild()
# BookItem.model_rebuild()
