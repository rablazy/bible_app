import logging

import pytest

from app.models.bible import BookTypeEnum
from tests import delete_url, get_raw_url, get_url

logger = logging.getLogger(__name__)

pytest.BASE_URL = "bible"

MG_VERSION = "BMG_1886"


def test_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Saimon !"}


def test_search_mg_bible(client):
    data = get_url(client, "search/")
    default_bible = [b for b in data.results if b.version == MG_VERSION]
    assert len(default_bible) > 0
    assert default_bible[0].lang.code == "mg"
    assert data.count >= 1


def test_search_bible_fake_lang(client):
    data = get_url(client, "search/?lang=xx&version=grigri", check_empty=False)
    assert data.results == []


def test_search_all_books(client):
    data = get_url(client, f"{MG_VERSION}/books")
    assert len(data.results) == 66
    assert data.count == 66


def test_search_books_new_testament(client):
    data = get_url(
        client, f"{MG_VERSION}/books?max_results=5&book_type={BookTypeEnum.NEW.value}"
    )
    assert len(data.results) == 5
    book = data.results[-1]
    assert book.short_name.upper() == "ASA"
    assert book.chapter_count == 28


def test_search_books_old_testament(client):
    data = get_url(
        client,
        f"{MG_VERSION}/books?offset=10&max_results=20&book_type={BookTypeEnum.OLD.value}",
    )
    assert len(data.results) == 20
    assert data.results[0].short_name.upper() == "1 MPA"
    assert data.results[-1].short_name.upper() == "AMO"


def test_search_books_limi_set(client):
    data = get_url(client, f"{MG_VERSION}/books?max_results=35")
    assert len(data.results) == 35
    assert data.count == 35
    assert data.offset == 0
    assert data.total == 66

    data = get_url(client, "xxx/books", check_empty=False)
    assert len(data.results) == 0


def test_search_books_by_name_code(client):
    data = get_url(client, f"{MG_VERSION}/books?name=Salamo")
    assert len(data.results) == 1
    assert data.results[0].rank == 19

    data = get_url(client, f"{MG_VERSION}/books?code=psa_")
    assert len(data.results) == 1
    assert data.results[0].rank == 19

    data = get_url(client, f"{MG_VERSION}/books?code=xla_", check_empty=False)
    assert len(data.results) == 0


def test_get_verse_errors(client):
    response = get_raw_url(
        client, f"{MG_VERSION}/verses/rev_/2/1?to_book_code=mat_&to_verse=4"
    )
    assert response.status_code == 400

    response = get_raw_url(
        client, f"{MG_VERSION}/verses/rev_/2/1?to_chapter=1&to_verse=4"
    )
    assert response.status_code == 400


def test_get_verse_translate(client):
    get_url(client, "search?version=kjv")
    data = get_url(
        client, f"{MG_VERSION}/verses/mat_/5/1?to_verse=3&translate_versions=kjv"
    )
    assert len(data.results) == 3
    assert len(data.trans) == 1
    assert data.trans[0].version == "kjv"
    assert len(data.trans[0].verses) == 3
    assert data.trans[0].verses[0].code == "mat_.05.01"


def test_get_verse_same_chapter_set(client):
    data = get_url(client, f"{MG_VERSION}/verses/rev_/15/1?to_chapter=17&to_verse=3")
    first_verse = data.results[0]
    assert first_verse.chapter_rank == 15
    assert first_verse.subtitle is not None
    assert first_verse.rank == 1
    last_verse = data.results[-1]
    assert last_verse.chapter_rank == 17
    assert last_verse.rank == 3
    assert any(verse.chapter_rank == 16 for verse in data.results)


def test_get_verse_same_chapter_notset(client):
    data = get_url(client, f"{MG_VERSION}/verses/psa_/93/2?to_verse=4")
    assert len(data.results) == 3
    first_verse = data.results[0]
    assert first_verse.chapter_rank == 93
    assert first_verse.book_rank == 19
    assert first_verse.subtitle is None
    assert first_verse.rank == 2
    last_verse = data.results[-1]
    assert last_verse.rank == 4
    assert last_verse.chapter_rank == 93
    assert last_verse.book_rank == 19


def test_get_all_verses_in_chapter(client):
    data = get_url(client, f"{MG_VERSION}/verses/psa_/91/1")
    assert len(data.results) == 16


def test_get_verse_across_chapters(client):
    data = get_url(client, f"{MG_VERSION}/verses/psa_/91/1?to_chapter=93")
    assert len(data.results) == 36
    assert data.count == 36

    data = get_url(client, f"{MG_VERSION}/verses/psa_/91/2?to_chapter=94&to_verse=3")
    assert len(data.results) == 38


def test_get_verse_across_books(client):
    data = get_url(
        client,
        f"{MG_VERSION}/verses/mat_/28/1?to_book_code=mar_&to_chapter=2&to_verse=5",
    )
    assert len(data.results) == 70
    assert data.count == 70
    assert data.previous.rank == 66
    assert data.previous.chapter_rank == 27
    assert data.previous.book_rank == 40
    assert data.next.rank == 6
    assert data.next.chapter_rank == 2

    data = get_url(
        client,
        f"{MG_VERSION}/verses/mat_/1/1?to_book=mar_&to_chapter=2&to_verse=5",
    )
    assert data.previous.rank == 24
    assert data.previous.chapter_rank == 3
    assert data.previous.book_rank == 39
    assert data.next.rank == 6
    assert data.next.chapter_rank == 2


def test_count_verses(client):
    """count all verses of new testament and overall"""
    data = get_url(client, f"{MG_VERSION}/verses/mat_/1/1?to_book_code=rev_")
    assert len(data.results) == 100
    assert data.total == 7958

    # data = get_url(client, f"{MG_VERSION}/verses/gen_/1?from_verse=1&to_book_code=rev_")
    # assert len(data.results) == 100
    # assert data.total == 31102


def test_get_all_verses_limit_set(client):
    data = get_url(
        client,
        f"{MG_VERSION}/verses/mat_/1/1?to_book_code=rev_&offset=100&max_results=25",
    )
    assert len(data.results) == 25
    assert data.total == 7958
    assert data.count == 25
    assert data.offset == 100


def test_get_verse_empty(client):
    data = get_url(
        client, f"{MG_VERSION}/verses/col_/2/25?to_verse=26", check_empty=False
    )
    assert len(data.results) == 0


def test_search_text(client):
    data = get_url(client, f"{MG_VERSION}/search?text=ampionony")
    assert data.count == 1
    assert data.total == 1
    assert data.results[0].code == "isa_.40.01"


def test_search_text_in_book(client):
    data = get_url(
        client, f"{MG_VERSION}/search?text=sambatra&book_code=mat_&book_chapter=5"
    )  # béatitudes
    assert data.total == 9


def test_search_text_translate(client):
    get_url(client, "search?version=kjv")
    data = get_url(
        client,
        f"{MG_VERSION}/search?text=sambatra&book_code=mat_&book_chapter=5&translate_versions=kjv",
    )
    assert len(data.results) == 9
    assert len(data.trans) == 1
    assert data.trans[0].version == "kjv"
    assert len(data.trans[0].verses) == 9
    assert data.trans[0].verses[-1].code == "mat_.05.11"


def test_chapter_list(client):
    data = get_url(client, f"{MG_VERSION}/mat_/chapters")
    assert data.total == 28
    chapter_23 = data.results[22]
    assert chapter_23.name == "Matio 23"
    assert chapter_23.code == "mat_.23"
    assert chapter_23.verse_count == 39


def test_delete_bible_error(client):
    data = delete_url(client, "delete/version/ssss", assert_ok=False, to_dict=False)
    assert data.status_code == 404

    data = delete_url(client, "delete/id/-1", assert_ok=False, to_dict=False)
    assert data.status_code == 404


def test_delete_bible_by_version(client):
    data = get_url(client, "search/")
    assert data.count == 2

    delete_version = data.results[0].version
    data = delete_url(client, f"delete/version/{delete_version}")
    assert data.msg == "Successfully deleted."

    data = delete_url(
        client, f"delete/version/{delete_version}", assert_ok=False, to_dict=False
    )
    assert data.status_code == 404

    data = get_url(client, "search/")
    assert data.count == 1


def test_delete_bible_by_id(client):

    data = get_url(client, "search/")
    assert data.count > 0

    delete_id = data.results[0].id

    data = delete_url(client, f"delete/id/{delete_id}")
    assert data.msg == "Successfully deleted."

    data = delete_url(client, f"delete/id/{delete_id}", assert_ok=False, to_dict=False)
    assert data.status_code == 404
