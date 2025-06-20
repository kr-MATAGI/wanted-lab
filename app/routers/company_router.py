from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from typing import Dict, List, Any

from app.services import CompanyService
from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    CompanyAddResponse,
    TagInfo,
)
from app.utils import setup_logger


# Router
router = APIRouter()

# Logger 
logger = setup_logger("Company_Router")


### GET
@router.get("/{company_name}")
async def get_company_info(
    company_name: str,
    request: Request,
):
    """
    🏢 회사 상세 정보 조회 API

    - **회사 이름**을 기준으로 상세 정보를 조회합니다.
    - 헤더의 **x-wanted-language** 값에 따라 **다국어**로 정보를 출력합니다.
      (입력한 회사명과 출력 언어는 다를 수 있습니다)

    ---
    **Parameters**
      - **company_name** (**str**): 검색할 회사 이름 (ex: "원티드랩")
      - **request** (**Request**): FastAPI 요청 객체 (헤더 정보 활용)

    **Returns**
      - **CompanyInfoResponse**:  
        검색된 회사의 상세 정보 (지정한 언어로 반환)

    **Error**
      - **404 Not Found**:  
        입력한 이름에 해당하는 회사가 존재하지 않을 경우

    ---
    **Example Request**
    ```http
    GET /Wantedlab
    x-wanted-language: ko
    ```

    **Example Response**
    ```json
    [
        "compnay_name": "Wantedlab",
        "tags": [
            "태그_4",
            "태그_20",
            "태그_16"
        ]
    ]
    ```
    """
    company_service: CompanyService = CompanyService()
    company_info: Dict[str, Any] = await company_service.get_company_info(
        company_name=company_name,
        language=request.headers.get("x-wanted-language"),
    )

    # 검색 결과가 없음 -> 404 Return
    if not company_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{company_name} information not found",
        )
    
    return CompanyInfoResponse(**company_info)


### POST
@router.post("/")
async def add_new_company(
    new_company_info: CompanyAddRequest,
    request: Request,
):
    """
    🏢 새로운 회사 등록 API

    - **신규 회사** 정보를 등록합니다.
    - 요청 데이터에 **새로운 언어**도 함께 추가할 수 있습니다.
    - 저장이 완료되면 헤더의 **x-wanted-language**에 따라  
      **지정한 언어로 추가된 회사 정보를 반환**합니다.

    ---
    **Parameters**
      - **new_company_info** (**CompanyAddRequest**):  
        등록할 회사의 상세 정보 (다국어 정보 포함 가능)
      - **request** (**Request**):  
        FastAPI 요청 객체 (헤더 정보 활용)

    **Returns**
      - **CompanyAddResponse**:  
        저장된 회사 정보 (지정한 언어로 반환)

    ---
    **Example Request**
    ```http
    POST /
    x-wanted-language: ko
    Content-Type: application/json

    {
      "company_name": {
        "ko": "라인 프레쉬",
        "tw": "LINE FRESH",
        "en": LINE FRESH"
      },
      "tags": [
        {
          "tag_name": {
            "ko": "태그_1",
            "tw": "tag_1",
            "en": "tag_1",
          }
        },
      ]
    }
    ```

    **Example Response**
    ```json
    {
      "company_name": "LINE FRESH",
      "tags": ["tag_1", "tag_8", "tag_15"],
    }
    ```
    """

    company_service: CompanyService = CompanyService()
    add_results: Dict[str, Any] = await company_service.add_new_company(
        new_company_info.model_dump(),
        language=request.headers.get("x-wanted-language"),
    )

    return CompanyAddResponse(**add_results)



### PUT
@router.put("/{company_name}/tags")
async def add_new_tag(
    company_name: str,
    tags: List[TagInfo],
    request: Request,
):
    """
    🏢 회사 태그 추가 API

    - 특정 회사에 **새로운 태그** 정보를 추가합니다.
    - 저장이 완료되면, 헤더의 **x-wanted-language**에 따라  
      **지정한 언어로 태그 정보를 반환**합니다.

    ---
    **Parameters**
      - **company_name** (**str**):  
        태그를 추가할 회사 이름 (예: "원티드랩")
      - **tags** (**List[TagInfo]**):  
        추가할 태그 정보 목록 (다국어 태그명 등 포함)
      - **request** (**Request**):  
        FastAPI 요청 객체 (헤더 정보 활용)

    **Returns**
      - **CompanyAddResponse**:
        추가된 태그 정보 (지정한 언어별)

    ---
    **Example Request**
    ```http
    PUT /원티드랩/tags
    x-wanted-language: en
    Content-Type: application/json

   [
     {
        "tag_name": {
            "ko": "태그_50",
            "jp": "タグ_50",
            "en": "tag_50"
        }
     },
     {
        "tag_name": {
            "ko": "태그_4",
            "tw": "tag_4",
            "en": "tag_4"
        }
     }
    ]
    ```

    **Example Response**
    ```json
    {
        "company_name": "Wantedlab",
        "tags": [
            "tag_4",
            "tag_16",
            "tag_20",
            "tag_50",
        ]
    }
    ```
    """
    company_service: CompanyService = CompanyService()
    results: Dict[str, Any] = await company_service.add_new_tag(
        company_name,
        tags,
        language=request.headers.get("x-wanted-language"),
    )

    return CompanyAddResponse(**results)


### DELETE
@router.delete("/{company_name}/tags/{tag}")
async def delete_tag(
    company_name: str,
    tag: str,
    request: Request,
):
    """
    🏢 회사 태그 삭제 API

    - 특정 회사에서 **지정한 태그** 정보를 삭제합니다.
    - 삭제가 완료된 후, 헤더의 **x-wanted-language**에 따라
      **지정한 언어로 남은 태그 정보를 반환**합니다.

    ---
    **Parameters**
      - **company_name** (**str**):
        태그를 삭제할 회사 이름 (예: "원티드랩")
      - **tag** (**str**):
        삭제할 태그명 (예: "태그_16")
      - **request** (**Request**):
        FastAPI 요청 객체 (헤더 정보 활용)

    **Returns**
      - **CompanyAddResponse**:
        태그 삭제 후 남아있는 태그 정보 (지정한 언어별)

    ---
    **Example Request**
    ```http
    DELETE /companies/원티드랩/tags/태그_16
    x-wanted-language: en
    ```

    **Example Response**
    ```json
    {
        "company_name": "Wantedlab",
        "tags": [
            "tag_4",
            "tag_20",
            "tag_50",
        ],
    }
    ```

    **Error**
      - **404 Not Found**:  
        해당 회사 또는 태그가 존재하지 않는 경우
    """
    
    company_service: CompanyService = CompanyService()
    results = await company_service.delete_tag(
        company_name,
        tag,
        language=request.headers.get("x-wanted-language"),
    )

    if not results:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="information not found",
      )

    return CompanyAddResponse(**results)
