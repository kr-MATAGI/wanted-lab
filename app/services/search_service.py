from sqlalchemy import select
from typing import List

from app.repositories import SearchRepository
from app.utils import get_db, setup_logger
from app.models import (
    CompanyName,
    Language,
)

# Logger 
logger = setup_logger("Search_Service")


class SearchService:
    async def search_company_name(
        self,
        company_name: str,
        language: str,
    ):
        """
        회사명 자동완성
            - 회사명의 일부만 들어가도 검색이 되어야 한다.
        
        Args:
            - query (str): 검색할 회사명
            - language (str): 출력 언어
        
        Returns:
            - List[str]: 검색된 회사명 리스트
        """
        search_repository = SearchRepository()
        results = await search_repository.search_company_name(
            company_name=company_name,
            language=language,
        )
        return results