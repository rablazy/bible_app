from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import deps
from app.core.config import settings

def pytest_configure():
    pytest.BASE_URL = "" # global variable to override in each test file
    pytest.MAIN_URL = settings.API_V1_STR

@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as client:        
        yield client
        app.dependency_overrides = {}
