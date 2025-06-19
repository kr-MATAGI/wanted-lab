from fastapi import UploadFile
from typing import List
from sqlalchemy import select

from app.utils import Parser
from app.models import (
    CsvCompnay,
    CompanyID,
    Language,
    CompanyName,
    Tag,
)
from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    TagInfo,
)
from app.utils import get_db, setup_logger

# Logger
logger = setup_logger("Company_Service")

class CompanyService:
    async def add_company_from_csv(
        self,
        file_path: str,
    ):
        """
        업로드된 csv 파일 업로드 처리
        """
        parser: Parser = Parser()
        csv_results: List[CsvCompnay] = await parser.parse_csv_by_file_path(file_path)

        db = get_db()
        try:
            async for session in db:
                for csv_item in csv_results:
                    new_company: CompanyAddRequest = CompanyAddRequest(
                        company_name={
                            "ko": csv_item.company_ko,
                            "en": csv_item.company_en,
                            "ja": csv_item.company_ja,
                        },
                        tags=[
                            csv_item.tag_ko,
                            csv_item.tag_en,
                            csv_item.tag_ja,
                        ],
                    )

                    await self.add_new_company(new_company, "ko")
        
        except Exception as e:
            raise e
        
        finally:
            await db.aclose()
        
        return


    async def get_company_info(
        self,
        company_name: str,
        language: str,
    ):
        """
        회사명을 검색해서 해당 정보 모두 가져옴
        """
        results = {
            "company_name": "",
            "tags": [],
        }
        
        db = get_db()
        try:
            async for session in db:
                stmt = select(
                    CompanyName,
                    Tag,
                    Language,
                ).where(
                    CompanyName.name == company_name,
                    Language.language_type == language,
                    CompanyName.language_id == Language.id,
                    Tag.language_id == Language.id,
                )
                
                db_results = await session.execute(stmt)
                rows = db_results.all()
                for row in rows:
                    company_name_obj = row[0]  # CompanyName 객체
                    tag_obj = row[1]  # Tag 객체

                    if not results["company_name"]:
                        results["company_name"] = company_name_obj.name
                    
                    results["tags"].append(tag_obj.tag_name)                    

        except Exception as e:
            logger.error(f"[ERROR] get_company_info: {e}")
            raise e

        finally:
            await db.aclose()
            
        return results
    


    async def add_new_company(
        self,
        new_company_info: CompanyAddRequest,
        language: str,
    ):
        db = get_db()
        try:
            async for session in db:
                
                pass
                

        except Exception as e:
            raise e
        
        finally:
            await db.aclose()
        
        return None
    
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