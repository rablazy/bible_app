from app.core.config import settings
import json

from tests import DictObj

def get_url(uri):
    return f"{settings.API_V1_STR}/bible/{uri}"

def test_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == { "message" : "Hello Saimon !"}
    

def test_search_bible(client):
    response = client.get(get_url("search/"))
    assert response.status_code == 200
    data = DictObj(response.json())    
    assert len(data.results) > 0
    default_bible = [b for b in data.results if b.version == "MG1886"]
    assert len(default_bible) > 0
    assert default_bible[0].lang.code == "mg"
    
