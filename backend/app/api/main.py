from fastapi import APIRouter

from app.api.routers import bible

api_router = APIRouter()
# api_router.include_router(bible.router, prefix="/bible", tags=["bible"])