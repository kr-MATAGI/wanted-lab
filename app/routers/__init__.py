from app.routers.company_router import router as company_router
from app.routers.search_router import router as  search_router
from app.routers.tag_router import router as tags_router

__all__ = ["company_router", "search_router", "tags_router"]