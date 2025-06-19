from fastapi import FastAPI
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

# Router 등록
app.include_router(search_router, prefix="search")
app.include_router(company_router, prefix="companies")
app.include_router(tags_router, prefix="tags")


# Root
@app.get("/")
async def root():
    return {"message": "Wantedlab API"}