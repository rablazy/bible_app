import logging

import pytest

from app.models.bible import BookTypeEnum
from tests import get_url

logger = logging.getLogger(__name__)

pytest.BASE_URL = "bible"

MG_VERSION = "BMG_1886"


# def test_main(client):
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello Saimon !"}


# def test_search_mg_bible(client):
#     data = get_url(client, "search/")
#     default_bible = [b for b in data.results if b.version == MG_VERSION]
#     assert len(default_bible) > 0
#     assert default_bible[0].lang.code == "mg"
#     assert data.count >= 1


# def test_search_bible_fake_lang(client):
#     data = get_url(client, "search/?lang=xx&version=grigri", check_empty=False)
#     assert data.results == []


# def test_search_all_books(client):
#     data = get_url(client, f"{MG_VERSION}/books")
#     assert len(data.results) == 66
#     assert data.count == 66


# def test_search_books_new_testament(client):
#     data = get_url(
#         client, f"{MG_VERSION}/books?max_results=5&book_type={BookTypeEnum.NEW.value}"
#     )
#     assert len(data.results) == 5
#     book = data.results[-1]
#     assert book.short_name.upper() == "ASA"
#     assert book.chapter_count == 28


# def test_search_books_old_testament(client):
#     data = get_url(
#         client,
#         f"{MG_VERSION}/books?offset=10&max_results=20&book_type={BookTypeEnum.OLD.value}",
#     )
#     assert len(data.results) == 20
#     assert data.results[0].short_name.upper() == "1 MPA"
#     assert data.results[-1].short_name.upper() == "AMO"


# def test_search_books_limi_set(client):
#     data = get_url(client, f"{MG_VERSION}/books?max_results=35")
#     assert len(data.results) == 35
#     assert data.count == 35
#     assert data.offset == 0
#     assert data.total == 66

#     data = get_url(client, "xxx/books", check_empty=False)
#     assert len(data.results) == 0


# def test_get_verse_same_chapter_set(client):
#     data = get_url(
#         client, f"{MG_VERSION}/verses/66/15?from_verse=1&to_chapter=17&to_verse=3"
#     )
#     first_verse = data.results[0]
#     assert first_verse.chapter_rank == 15
#     assert first_verse.subtitle is not None
#     assert first_verse.rank == 1
#     last_verse = data.results[-1]
#     assert last_verse.chapter_rank == 17
#     assert last_verse.rank == 3
#     assert any(verse.chapter_rank == 16 for verse in data.results)


# def test_get_verse_same_chapter_notset(client):
#     data = get_url(client, f"{MG_VERSION}/verses/19/93?from_verse=2&to_verse=4")
#     assert len(data.results) == 3
#     first_verse = data.results[0]
#     assert first_verse.chapter_rank == 93
#     assert first_verse.book_rank == 19
#     assert first_verse.subtitle is None
#     assert first_verse.rank == 2
#     last_verse = data.results[-1]
#     assert last_verse.rank == 4
#     assert last_verse.chapter_rank == 93
#     assert last_verse.book_rank == 19


# def test_get_all_verses_in_chapter(client):
#     data = get_url(client, f"{MG_VERSION}/verses/19/91?from_verse=1")
#     assert len(data.results) == 16


# def test_get_verse_across_chapters(client):
#     data = get_url(client, f"{MG_VERSION}/verses/19/91?from_verse=1&to_chapter=93")
#     assert len(data.results) == 36
#     assert data.count == 36

#     data = get_url(
#         client, f"{MG_VERSION}/verses/19/91?from_verse=2&to_chapter=94&to_verse=3"
#     )
#     assert len(data.results) == 38


# def test_get_verse_across_books(client):
#     data = get_url(
#         client,
#         f"{MG_VERSION}/verses/40/28?from_verse=1&to_book=41&to_chapter=2&to_verse=5",
#     )
#     assert len(data.results) == 70
#     assert data.count == 70
#     assert data.previous.rank == 66
#     assert data.previous.chapter_rank == 27
#     assert data.previous.book_rank == 40
#     assert data.next.rank == 6
#     assert data.next.chapter_rank == 2

#     data = get_url(
#         client,
#         f"{MG_VERSION}/verses/40/1?from_verse=1&to_book=41&to_chapter=2&to_verse=5",
#     )
#     assert data.previous.rank == 24
#     assert data.previous.chapter_rank == 3
#     assert data.previous.book_rank == 39
#     assert data.next.rank == 6
#     assert data.next.chapter_rank == 2


# def test_get_all_verses(client):
#     # new testament from Mat to Apo
#     data = get_url(client, f"{MG_VERSION}/verses/40/1?from_verse=1&to_book=66")
#     assert len(data.results) == 100
#     assert data.total == 7958


# def test_get_all_verses_limit_set(client):
#     data = get_url(
#         client,
#         f"{MG_VERSION}/verses/40/1?from_verse=1&to_book=66&offset=100&max_results=25",
#     )
#     assert len(data.results) == 25
#     assert data.total == 7958
#     assert data.count == 25
#     assert data.offset == 100


def test_search_text(client):
    data = get_url(client, f"{MG_VERSION}/search/ampionony")
    assert data.count == 1
    assert data.total == 1
    assert data.results[0].code == "isa_.40.01"
