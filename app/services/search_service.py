from app.utils.database import get_db
from app.utils.logger import setup_logger


# Logger 
logger = setup_logger("Search_Service")


class SearchService:
    async def search_company_name(
        self,
        query: str,
        language: str,
        auto_complete: bool=True,
    ):
        async with get_db() as session:
            pass

        

        
