from app.models.bible import Language
from pydantic import BaseModel, computed_field, ConfigDict, model_validator
from datetime import date

from typing import Generic, Sequence, ClassVar, TypeVar

DataT = TypeVar('DataT')    
class ListItems(BaseModel, Generic[DataT]):
    results: Sequence[DataT]   
    

class LanguageItem(BaseModel):
    name: str
    code: str
    model_config = ConfigDict(from_attributes=True)


class BibleItem(BaseModel):    
    
    model_config = ConfigDict(from_attributes=True) #extra='allow|ignore', 
    
    id: int
    version: str
    year: date | None = None
    src: str
    lang: LanguageItem           
   
    # class Config:
    #     from_attributes = True         
                          

class BookItem(BaseModel):
    id : int
    name : str
    short_name : str
    rank : int
    category : str
    bible_id : int
    chapter_count: int = 0      
        
    
    