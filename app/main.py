import time
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

BASE_PATH = Path(__file__).resolve().parent
# TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

root_router = APIRouter()
app = FastAPI(
    title=f"{settings.API_TITLE}", openapi_url=f"{settings.API_VERSION}/openapi.json"
)

# app = FastAPI(
#     title=settings.title,
#     version=settings.version,
#     description=settings.description,
#     openapi_prefix=settings.openapi_prefix,
#     docs_url=settings.docs_url,
#     openapi_url=settings.openapi_url
# )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@root_router.get("/", status_code=200)
def root(request: Request) -> dict:
    """
    Root GET
    """
    return {"message": "Hello Saimon !"}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(api_router, prefix=settings.API_VERSION)
app.include_router(root_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
