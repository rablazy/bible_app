import pytest

from tests import get_url
from app.models.bible import BookTypeEnum

pytest.BASE_URL = "bible"


def test_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == { "message" : "Hello Saimon !"}
    

def test_search_bible(client):
    # check default mg bible is in db    
    data = get_url(client, "search/")    
    default_bible = [b for b in data.results if b.version == "MG1886"]
    assert len(default_bible) > 0
    assert default_bible[0].lang.code == "mg"
    
    # check no result for fake lang and version
    data = get_url(client, "search/?lang=xx&version=grigri", check_empty=False)
    assert data.results == []
    
def test_search_books(client):
    data = get_url(client, "search/?lang=mg&version=MG1886")    
    bible_id = data.results[0].id
    
    data = get_url(client, f"{bible_id}/books?max_results=5&book_type={BookTypeEnum.NEW.value}")
    assert len(data.results) == 5
    book = data.results[-1]
    assert book.short_name == "ASA"
    assert book.chapter_count == 28
    
    # data = standard_check(client.get(get_url(f"{bible_id}/books")))
    
    
    

