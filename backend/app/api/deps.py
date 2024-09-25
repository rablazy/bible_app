from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm.session import Session


from app.core.config import settings
from app.db.session import SessionLocal

from app import crud


def get_db() -> Generator:
    db = SessionLocal()
    db.current_user_id = None
    try:
        yield db
    finally:
        db.close()



