from app.models.bible import BookTypeEnum
from app.db.start.common import RulesEnum

DIEM_RULES = {
    RulesEnum.BOOK_COUNT: [73],
    RulesEnum.BOOK_COUNT_BY_CATEG: [BookTypeEnum.OLD, 39],
    RulesEnum.BOOK_COUNT_BY_CATEG: [BookTypeEnum.NEW, 27],
    RulesEnum.BOOK_COUNT_BY_CATEG: [BookTypeEnum.APOCRYPHAL, 7],
    RulesEnum.BOOK_CATEGORY: [38, BookTypeEnum.OLD],  # zakaria
    RulesEnum.BOOK_CATEGORY: [41, BookTypeEnum.NEW],  # marka
    RulesEnum.BOOK_CATEGORY: [73, BookTypeEnum.APOCRYPHAL],  # baroka
    RulesEnum.BOOK_CHAPTER_COUNT: [14, 36],  # 2 Tantara
    RulesEnum.BOOK_CHAPTER_COUNT: [66, 22],  # Apokalypsy
    RulesEnum.BOOK_CHAPTER_COUNT: [72, 19],  # Baroka
    RulesEnum.VERSE_COUNT: [42, 8, 56]  # Lioka 8.5
}
