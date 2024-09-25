import logging
import pathlib
import os
import json

from app import crud
from app.models.bible import Bible, Language, Book, Chapter, Verse, OLD_TESTAMENT, NEW_TESTAMENT
from app.db.session import SessionLocal
from sqlalchemy import func, select, and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).resolve().parent.parent


class InitDb():

    def __init__(self):
        self.db = SessionLocal()
        self.run()

    def run(self):
        self.init_languages()
        self.init_mlg_bible()        

    def init_languages(self):
        langs = [Language(name=lg[1], code=lg[0])
                 for lg in [("en", "English"), ("fr", "Français"), ("mg", "Malagasy")]]
        if not crud.language.get_multi(self.db):
            crud.language.create_multi(self.db, langs)
            logger.info("%s languages inserted", len(langs))
        else:
            logger.info("Skipping languages insert")          
        

    def init_mlg_bible(self):
        """
        Import malagasy bible version
        """          
        baiboly_src = os.path.join(ROOT, 'data', 'bible', 'baiboly.json')

        with open(baiboly_src, 'r+', encoding='UTF-8') as f:
            datas = json.load(f)
                 
            src_lang = datas["lang"]
            lang = crud.language.get_by_code(self.db, src_lang)
            if not lang:
                raise ValueError(f"Source language {src_lang} not found in db")
            
            version = datas["version"]           
            
            if not self.db.query(Bible).filter(Bible.version==version, Bible.lang==lang).count():                                               
                bible = Bible(
                    src = datas["created"]["name"],
                    version = version,
                    lang = lang             
                )
                
                crud.bible.create(self.db, bible)
                
                data = datas['body']
                order = 0

                for d in data:
                    order += 1
                    book = Book(
                        name=d['title'],
                        short_name=d['id'],
                        rank=order,
                        category=OLD_TESTAMENT if order < 40 else NEW_TESTAMENT,
                        bible=bible
                    )
                    crud.book.create(self.db, book)               

                    book_chapters = d['books'] if isinstance(
                        d['books'], list) else [d['books']]
                    logger.info("Treating book %s with %s chapters ...",
                                book, len(book_chapters))

                    toko = 1
                    for chap in book_chapters:
                        verses_key = 'texts' if 'toko' in chap else 'seg'
                        chapter = Chapter(rank=toko, book=book)
                        crud.chapter.create(self.db, chapter)
                        toko += 1
                        try:
                            verses = chap[verses_key]
                        except Exception as e:
                            logger.error('%s - %s : %s', book, type(chap),
                                         chap.keys() if isinstance(chap, dict) else chap)
                            raise e

                        verse_order = 0
                        for v in verses:
                            verse_order += 1
                            verset = v.strip()
                            verse = Verse(
                                rank=verse_order,
                                chapter=chapter,
                                content=verset
                            )
                            if verset.startswith('['):
                                try:
                                    index = verset.index(']')
                                    if index:
                                        verse.subtitle = verset[1:index]
                                    verse.content = verset[index+1:len(verset)].strip()
                                except ValueError:
                                    pass
                            chapter.verses.append(verse)

                self.db.commit()
                logger.info("%s book inserted.", order)
            
            self.check_data()
            
    def check_data(self):
        # check chapters
        # check first book has 50 chapter
        assert(self.db.query(Chapter).join(Chapter.book).filter(Book.rank == 1).count() == 50)
        # check last book has 22 chapter
        assert(self.db.query(Chapter).join(Chapter.book).filter(Book.rank == 66).count() == 22)        


def main() -> None:
    logger.info("Creating initial data")
    InitDb()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
