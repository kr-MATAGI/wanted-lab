from typing import List, Dict, Any

from sqlalchemy import select

from app.utils import get_db, setup_logger
from app.models import (
    CompanyName,
    Language,
    Tag,
)

# Logger
logger = setup_logger("Tag_Repository")

class TagRepository:
    async def get_company_id_by_tag_name(
        self,
        tag_name: str,
    ):
        """
        태그 이름을 통해 회사 id 조회

        Returns:
            - List[int]: 회사 id 리스트
        """
        results: List[int] = []

        try:
            async for session in get_db():
                stmt = select(
                    Tag,
                ).where(
                    Tag.tag_name == tag_name
                ).order_by(
                    Tag.company_id.asc(),
                )

                db_results = await session.execute(stmt)
                rows = db_results.all()

                for row in rows:
                    tag_obj: Tag = row[0]
                    results.append(tag_obj.company_id)
            
        except Exception as e:
            logger.error(f"[ERROR] get_company_id_by_tag_name: {e}")
            raise e

        results = list(set(results))
        return results

    async def get_company_name_by_company_id(
        self,
        company_ids: List[int],
    ):
        """
        회사 id를 통해 회사 이름 조회

        Returns:
            - Dict[str, Any]: 회사 정보
            {
                "회사 id": {
                    "ko": "",
                    "en": "",
                    "ja": "",
                    ...
                }
            }
        """
        results: Dict[int, Any] = {}

        try:
            async for session in get_db():
                stmt = select(
                    CompanyName,
                    Language,
                ).join(
                    Language,
                    Language.id == CompanyName.language_id,
                ).where(
                    CompanyName.company_id.in_(company_ids),
                    CompanyName.name != '',
                ).order_by(
                    CompanyName.company_id.asc(),
                )

                db_results = await session.execute(stmt)
                rows = db_results.all()

                for row in rows:
                    company_name_obj: CompanyName = row[0]
                    language_obj: Language = row[1]

                    if company_name_obj.company_id not in results.keys():
                        results[company_name_obj.company_id] = {
                            language_obj.language_type: company_name_obj.name
                        }
                    else:
                        results[company_name_obj.company_id][language_obj.language_type] = company_name_obj.name
                
        except Exception as e:
            logger.error(f"[ERROR] get_company_info_by_company_id: {e}")

        return results