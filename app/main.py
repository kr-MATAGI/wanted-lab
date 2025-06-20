from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from app.utils import setup_logger
from app.routers import (
    search_router,
    company_router,
    tags_router,
)

# Set Logger
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[MAIN] Application startup")

    yield

    logger.info("[MAIN] Application shutdown")


# App
app = FastAPI(
    title="Wantedlab API",
    version="0.1.0",
    lifespan=lifespan
)

# Add test_client method to app
def test_client():
    return TestClient(app)

app.test_client = test_client

# Middleware
PREFIX_TO_CHECK = ("/companies", "/tags", "/search")

@app.middleware("http")
async def check_x_wanted_language_header(request: Request, call_next):
    path = request.url.path
    
    # Header에 x_wanted_language가 없으면 400 반환
    if path.startswith(PREFIX_TO_CHECK):
        x_wanted_language = request.headers.get("x-wanted-language")
        if not x_wanted_language:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "x-wanted-language is required"},
            )
    
    response = await call_next(request)
    return response


# Router 등록
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(company_router, prefix="/companies", tags=["companies"])
app.include_router(tags_router, prefix="/tags", tags=["tags"])

# docs에서 x-wanted-language 추가
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Wantedlab API",
        version="0.1.0",
        routes=app.routes,
    )
    for path in openapi_schema["paths"].values():
        for op in path.values():
            op.setdefault("parameters", []).append({
                "in": "header",
                "name": "x-wanted-language",
                "required": False,
                "schema": {"type": "string"},
                "description": "ko"
            })
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Root
@app.get("/")
async def root():
    return {"message": "Wantedlab API"}