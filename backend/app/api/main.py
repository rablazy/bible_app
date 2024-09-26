from fastapi import APIRouter

from app.api.routers import bible_routes

api_router = APIRouter()
api_router.include_router(bible_routes.router, prefix="/bible", tags=["bible"])