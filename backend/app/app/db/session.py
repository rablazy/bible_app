import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

env = os.environ.get("ENVIRONMENT", "normal")

engine = create_engine(
    settings.DATABASE_TEST_URL
    if env == "test"
    else settings.DATABASE_URL
    # required for sqlite
    # connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
