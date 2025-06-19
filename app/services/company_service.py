from typing import List

from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    TagInfo,
)
from app.utils.database import get_db

class CompanyService:
    async def get_company_info(
        self,
        company_name: str,
        language: str,
    ):
        results: CompanyInfoResponse = ''


    async def add_new_company(
        self,
        new_company_info: CompanyAddRequest,
        language: str,
    ):
        async with get_db() as session:
            pass

        
        return
    
    async def add_new_tag(
        self,
        compnay_name: str,
        tags: List[TagInfo],
        language: str,
    ):
        pass


    async def delete_tag(
        self,
        compnay_name: str,
        tag: str,
        language: str,
    ):
        pass