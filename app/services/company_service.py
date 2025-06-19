from fastapi import UploadFile
from typing import List

from app.utils import Parser
from app.models import CsvCompnay
from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    TagInfo,
)
from app.utils import get_db, setup_logger

# Logger
logger = setup_logger("CompanyService")

class CompanyService:
    async def add_company_from_csv(
        self,
        file_path: UploadFile,
    ):
        """
        업로드된 csv 파일 업로드 처리
        """
        parser: Parser = Parser()
        results: List[CsvCompnay] = parser.parse_csv_by_file_path(file_path)

        db = get_db()
        async for session in db:
            try:
                session.add()
            
            except Exception as e:
                logger.error(f"Error adding company from CSV: {e}")
            
        
        return len(results)

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
        # 회사가 이미 존재하는 지 확인

        # 기존에 있는 회사인 경우 회사명, 태그 업데이트 (새로운 언어 확인)

        # 회사 업데이트
        pass


    async def delete_tag(
        self,
        compnay_name: str,
        tag: str,
        language: str,
    ):
        pass


    