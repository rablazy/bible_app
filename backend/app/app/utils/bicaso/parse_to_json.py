import csv
import json
from typing import List

import os
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent


class Ouput :   
    
    def __init__(self, books, *args, **kwargs) -> None:                
        self.books = books
        if kwargs:
            self.__dict__.update(kwargs)
   
   
def importer(    
    infos: dict,
    encoding: str ="'utf-8-sig'", 
    delimiter: str ='\t'    
):   
    version = infos.get("version", None)
    base_path = os.path.join(ROOT, version.lower()) 
    chap_file = os.path.join(base_path, 'Livre_chap.txt')    
    verse_file_old = os.path.join(base_path, f'{version}-O.txt')    
    verse_file_new = os.path.join(base_path, f'{version}-N.txt')   
    
    entries = list(csv.reader(open(chap_file, 'r', encoding=encoding), delimiter=delimiter))  
    
    books = dict()      
    for i, entry in enumerate(entries):           
        b = Book().from_dict({
            "rank": i + 1,
            "name" :((entry[0].split('-'))[1]).strip(), 
            "category" : None,
            "short_name" : entry[3],
            "code" : entry[1], 
            "chapter_count" : entry[2],            
            "classification" : entry[4].strip()
        })       
        if b.rank < 40 :
            b.category = "Old"
        else:
            if b.rank <= 66:
                b.category = "New"
            else:        
                b.category = "Apocryphal"
            
        books[b.code] = b                           
   
        
    for verse_file in [verse_file_old, verse_file_new]:
        verses = list(csv.reader(open(verse_file, 'r', encoding=encoding), delimiter=delimiter))      
        for i, verse in enumerate(verses):
            if len(verse):                
                book_code, chapter_rank, verse_rank, content = verse[0], int(verse[1]), int(verse[2]), verse[4].strip()                 
                subtitle = None
                if content and content.startswith("["):
                    x = content.rfind(']')
                    if x :
                        subtitle = content[0:x+1]
                        content = content[x+1:].strip()              
                book = books.get(book_code) 
                book.add_verse(chapter_rank, Verse(verse_rank, content, subtitle))
        
    
    book_values = list(books.values())
    output_books = []
    for b in book_values :
        b.chapters = list(b.chapters.values())        
        delattr(b, "code")
        delattr(b, "chapter_count")
        output_books.append(b)
    
    output = Ouput(output_books, **infos)
    with open(os.path.join(base_path, f'{version}.json'), 'w') as fp:
        json_string = json.dumps(output, default=lambda x: x.__dict__)
        fp.write(json_string)  


def main():   
    importer(infos={
        "lang" : { "code" : "mg", "name" : "Malagasy" },
        "version": "DIEM",
        "description": "Baiboly Dikan-teny Iombonana Malagasy",
        "src" : "internet",
        "src_url" : "https://www.bicaso.fr/Bible.html"
    }) 
    
    importer(infos={
        "lang" : { "code" : "en", "name" : "English" },
        "version": "KJV",
        "description": "King James Version Bible",
        "src" : "internet",
        "src_url" : "https://www.bicaso.fr/Bible.html"
    })  
    
    importer(infos={
        "lang" : { "code" : "fr", "name" : "Français" },
        "version": "LSG_21",
        "description": "Bible Louis Second 21ème siecle",
        "src" : "internet",
        "src_url" : "https://www.bicaso.fr/Bible.html"
    }) 
    
    importer(infos={
        "lang" : { "code" : "mg", "name" : "Malagasy" },
        "version": "BKM",
        "description": "Baiboly Katolika Malagasy",
        "src" : "internet",
        "src_url" : "https://www.bicaso.fr/Bible.html"
    })   
    
    
    
class Book:  
       
    rank : int
    name : str    
    short_name : str
    category : str
    code : str
    chapter_count : int
    classification : str    
    
    def from_dict(self, d):
        self.__dict__.update(d)
        self.chapters = dict()
        self.chaps = []
        return self
    
    def chapter_at(self, rank:int):
        if not self.chapters.get(rank):            
            self.chapters[rank] = Chapter(self.rank, rank)
        return self.chapters.get(rank)
    
    def add_verse(self, chapter_rank, verse):
        chapter = self.chapter_at(chapter_rank)
        chapter.add_verse(verse)
    
    def __str__(self) -> str:
        return f"{self.rank} - {self.name}"
    
    
class Verse :    
    rank : int
    content : str    
    
    def __init__(self, rank, content, subtitle=None) -> None:
        self.rank = rank
        self.content = content
        self.subtitle = subtitle        
    
class Chapter:
    book_rank: int
    rank : int        
    
    def __init__(self, book_rank, rank) -> None:
        self.book_rank = book_rank
        self.rank = rank
        self.verses = []
    
    def add_verse(self, verse:Verse):
        self.verses.append(verse)
        
    def verse_at(self, rank):
        return self.verses[rank-1]    
    
     

if __name__ == "__main__":
    main()