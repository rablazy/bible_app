from app.models.bible import Language
from pydantic import BaseModel, computed_field, ConfigDict, model_validator
from datetime import date

from typing import Generic, Optional, Sequence, List, TypeVar, Union

DataT = TypeVar('DataT')    
class ListItems(BaseModel, Generic[DataT]):
    results: Sequence[DataT]   
    count: int = 0
    

class LanguageItem(BaseModel):
    name: str
    code: str
    model_config = ConfigDict(from_attributes=True)


class BibleItem(BaseModel):    
    
    model_config = ConfigDict(from_attributes=True) #extra='allow|ignore', 
    
    id: int
    version: str
    year: Optional[date] = None
    src: str
    src_url: Optional[str] = None
    lang: LanguageItem           
   
    # class Config:
    #     from_attributes = True         
       

class BookItemShort(BaseModel):   
    model_config = ConfigDict(from_attributes=True)
    id : int
    name : str
    short_name : str
    rank : int
    category : str
    bible_id : int
    chapter_count: int = 0                           


class ChapterItem(BaseModel):
    id : int
    rank : int
    book_id : int    
    #verses : List[VerseItem]

class BookItem(BookItemShort):   
    model_config = ConfigDict(from_attributes=True) 
    chapters : List[ChapterItem]
    
    
class VerseItem(BaseModel):         
    # id : int
    subtitle : Optional[Union[str, int, bytes]] = None
    content : str
    rank : int
    #chapter_id : int
    chapter_rank: int
    book_rank: int    
    

class VerseItems(BaseModel):
    results: Sequence[VerseItem] 
    next : Optional[VerseItem] = None
    previous: Optional[VerseItem] = None
    count: int = 0
    

    
# BookItem.model_rebuild() 
# ChapterItem.model_rebuild() 
        
    
    