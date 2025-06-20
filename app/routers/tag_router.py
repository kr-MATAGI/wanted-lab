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
    🔎 태그명 기반 회사 검색 API

    - 입력한 태그명(다국어 포함)으로 **관련된 회사** 목록을 검색합니다.
    - 일본어 등 어떤 언어로 태그를 검색해도,
      응답은 헤더의 **x-wanted-language** 값에 따라 **지정한 언어**로 회사명을 출력합니다.
    - 회사명 한글(ko) 정보가 없으면 **노출 가능한 다른 언어**로 자동 대체됩니다.
    - **동일 회사는 한 번만** 결과에 노출됩니다.

    ---
    **Parameters**
      - **query** (**str**):  
        검색할 태그명 (예: "タグ_22")
      - **request** (**Request**):
        FastAPI 요청 객체 (헤더에서 언어 정보 추출)

    **Returns**
      - **List[TagSearchResponse]**:
        검색된 회사명 목록 (중복 없이, 지정 언어로)

    ---
    **Example Request**
    ```http
    GET /tags?query=タグ_22
    x-wanted-language: ko
    ```

    **Example Response**
    ```json
    [
      {"company_name": "Wantedlab"},
      {"company_name": "Springk"}
    ]
    ```

    **Notes**
      - 일본어 태그로 검색해도, 응답은 영어(혹은 원하는 언어)로 반환
      - 회사명(ko)이 없는 경우, 노출 가능한 다른 언어명으로 응답
    """
    tag_service: TagService = TagService()
    results: List[str] = await tag_service.search_by_tag_name(
        tag_name=query,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return [TagSearchResponse(company_name=x) for x in results]