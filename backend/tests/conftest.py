import logging
import os
from typing import Generator

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)
loaded = load_dotenv("./.env.test", override=True)

from app.core.config import settings
from app.main import app

# print(f"loaded : {loaded}, from conftest db_url >>>  {settings.db_url}")
# exit(1)


def pytest_configure():
    pytest.BASE_URL = ""  # global variable to override in each test file
    pytest.MAIN_URL = settings.API_VERSION


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as client:
        yield client
        app.dependency_overrides = {}
