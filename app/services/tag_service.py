from typing import List, Dict
from sqlalchemy import select

from app.utils import get_db, setup_logger
from app.models import (
    CompanyName,
    Language,
    Tag,
)

# Logger
logger = setup_logger("Tag_Service")

class TagService:
    async def search_by_tag_name(
        self,
        tag_name: str,
        language: str,
    ):
        """
        4. 태그명으로 회사이름 검색
            - 태그로 검색 관련된 회사가 검색되어야 한다.
            - 다국어로 검색 가능
            - 일본어 태그 검색 해도 x-wanted-language 언어값에 따라 해당 언어로 출력
            - ko가 없는 경우 노출가능한 언어로 출력
            - 동일한 회사는 한 번만 노출

        Args:
            - tag_name (str): 검색할 태그명
            - language (str): 출력 언어

        Returns:
            - List[str]: 검색된 회사이름 리스트
        """

        db = get_db()
        results: List[str] = []

        try:
            async for session in db:
                # 태그 검색
                stmt = select(
                    Tag,
                    CompanyName,
                    Language,
                ).join(
                    CompanyName,
                    CompanyName.company_id == Tag.company_id
                ).join(
                    Language,
                    Language.id == Tag.language_id
                ).where(
                    Tag.tag_name == tag_name
                )

                db_results = await session.execute(stmt)
                rows = db_results.all()

                # 언어에 따라 회사명 정리
                company_infos: Dict[str, List[str]] = {}

                for row in rows:
                    # tag_obj: Tag = row[0] # Not Used
                    company_name_obj: CompanyName = row[1]
                    language_obj: Language = row[2]

                    if language_obj.language_type not in company_infos.keys():
                        company_infos[language_obj.language_type] = [company_name_obj.name]
                    else:    
                        company_infos[language_obj.language_type].append(company_name_obj.name)

                # 출력 언어에 따라 결과 만들기 (없다면 가능한 언어로)
                if company_infos.get(language):
                    results = company_infos[language]
                else:
                    for key, val in company_infos.items():
                        if val:
                            results = company_infos[key]
                            break

                # 결과 중복제거
                results = list(set(results))

        except Exception as e:
            logger.error(f"[ERROR] search_by_tag_name: {e}")
            raise e

        finally:
            await db.aclose()


        return results