from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import deps

@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as client:        
        yield client
        app.dependency_overrides = {}
