from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps

from app.models.bible import Book, Chapter, Verse

router = APIRouter()



