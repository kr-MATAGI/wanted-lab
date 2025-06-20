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
    🔍 회사명 자동완성 API

    - 입력한 문자열이 **포함**된 회사명을 자동 완성 방식으로 검색합니다.
    - 헤더의 **x-wanted-language** 값에 따라 **결과 언어**를 다르게 출력합니다.
      (예: 입력은 한글, 출력은 영어 등)
    - 입력 쿼리와 출력 언어는 서로 다를 수 있습니다.

    ---
    **Parameters**
      - **query** (**str**): 검색할 회사명 일부 또는 전체 문자열  
      - **request** (**Request**): FastAPI 요청 객체 (헤더 정보 활용)

    **Returns**
      - **results** (**List[SearchResponse]**):  
        자동완성된 회사명 리스트 (지정한 언어로)

    ---
    **Example Request**
    ```http
    GET /query?query=원티드
    x-wanted-language: ko
    ```

    **Example Response**
    ```json
    [
      {"company_name": "Wantedlab"},
      {"company_name": "Wanted Korea"}
    ]
    ```
    """
    
    search_service: SearchService = SearchService()
    search_results: List[Dict[str, str]] = await search_service.search_company_name(
        query,
        request.headers.get("x-wanted-language"),
    )
    
    return [SearchResponse(company_name=item) for item in search_results]