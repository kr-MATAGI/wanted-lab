from fastapi import APIRouter, Request
from typing import List

from app.services import TagService
from app.schemas import TagSearchResponse

# Router
router = APIRouter()



### GET
@router.get("/")
async def search_by_tag_name(
    query: str,
    request: Request,
):
    """
    4. 태그명으로 회사 검색
        - 태그로 검색 관련된 회사가 검색되어야 한다.
        - 다국어로 검색 가능
        - 일본어 태그 검색 해도 x-wanted-language 언어값에 따라 해당 언어로 출력
        - ko가 없는 경우 노출가능한 언어로 출력
        - 동일한 회사는 한 번만 노출
    
    Args:
        query (str): 검색할 태그명
    
    Returns:
        Dict[str, Any]: 검색된 결과
    """
    tag_service: TagService = TagService()
    results: List[str] = await tag_service.search_by_tag_name(
        tag_name=query,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return [TagSearchResponse(company_name=x) for x in results]