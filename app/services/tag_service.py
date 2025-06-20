from typing import List, Dict, Any
from sqlalchemy import select

from app.repositories import TagRepository
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

        tag_repository = TagRepository()

        # Tag명에 연관된 회사 id 조회
        company_ids: List[int] = await tag_repository.get_company_id_by_tag_name(
            tag_name=tag_name,
        )

        # 회사 id를 통해 회사 정보 조회
        company_names: Dict[int, Any] = await tag_repository.get_company_name_by_company_id(
            company_ids=company_ids,
        )
        
        # 결과 반환
        results: List[str] = []
        for cmpany_id, company_names in company_names.items():
            if language in company_names.keys():
                results.append(company_names[language])
            else:
                for key, val in company_names.items():
                    if val:
                        results.append(val)
                        break

        return results