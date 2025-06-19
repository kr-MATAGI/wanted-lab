from fastapi import APIRouter, Request
from typing import List, Dict

from app.services import SearchService
from app.schemas import SearchResponse

# Router
router = APIRouter()


### GET
@router.get("/query")
async def search_company_name(query: str, request: Request):
    """
    1. 회사명 자동 완성
        - 회사명의 일부만 들어가도 검색 가능
        - header의 x-wanted-language 언어 값에 따라 해당 언어로 출력되어야 함
          (query의 언어와 출력 언어는 다를 수 있음)
    
    Args:
        query (str): 검색할 회사명
    
    Returns:
        results (List[SearchResponse]): 검색 결과
        
    """
    wanted_lang: str = request.headers.get("x-wanted-language", "ko")

    # 검색
    search_service: SearchService = SearchService()
    search_results: List[Dict[str, str]] = await search_service.search_company_name(
        query,
        wanted_lang,
    )
    
    return [SearchResponse(**result) for result in search_results]