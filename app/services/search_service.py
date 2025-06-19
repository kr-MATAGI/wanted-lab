from sqlalchemy import select
from typing import List

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
        db = get_db()
        results: List[str] = []
        try:
            async for session in db:
                stmt = select(
                    CompanyName,
                    Language,
                ).where(
                    Language.language_type == language,
                    CompanyName.name.like(f"%{company_name}%"),
                )

                db_results = await session.execute(stmt)
                rows = db_results.all()

                for row in rows:
                    company_name_obj = row[0] # CompanyName 객체
                    results.append(company_name_obj.name)

        except Exception as e:
            logger.error(f"[ERROR] search_company_name: {e}")
            raise e
        
        finally:
            await db.aclose()

        return results