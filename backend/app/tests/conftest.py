from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def pytest_configure():
    pytest.BASE_URL = ""  # global variable to override in each test file
    pytest.MAIN_URL = settings.API_V1_STR


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as client:
        yield client
        app.dependency_overrides = {}
