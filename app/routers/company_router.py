from fastapi import APIRouter, Request
from typing import Dict, List

from app.services import CompanyService
from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    TagAddRequest,
    TagInfo,
)


# Router
router = APIRouter()

### GET
@router.get("/{company_name}")
async def get_company_info(
    company_name: str,
    request: Request,
):
    """
    2. 회사 이름으로 회사 검색
        - header의 x-wanted-language 언어 값에 따라 해당 언어로 출력
          (compnay_name과 출력 언어는 다를 수 있음)
        
    Args:
        company_name (str): 회사 이름

    Returns:
        CompanyInfoResponse: 검색된 회사 정보
    
    Exception:
        404 - 검색된 회사 없는 경우
    """

    company_service: CompanyService = CompanyService()
    company_info: CompanyInfoResponse = await company_service.get_company_info(
        company_name,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return


### POST
@router.post("/")
async def add_new_company(
    new_company_info: CompanyAddRequest,
    request: Request,
):
    """
    3. 새로운 회사 추가
        - 새로운 언어도 같이 추가 될 수 있다.
        - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력
        
    Args:
        new_company_info (CompanyAddRequest): 새로운 회사 정보
    
    Returns:
        @TODO:
        ???: 저장된 회사 정보
    """

    company_service: CompanyService = CompanyService()
    add_results: Dict[str, str] = await company_service.add_new_company(
        new_company_info,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return add_results



### PUT
@router.put("/{company_name}/tags")
async def add_new_tag(
    company_name: str,
    tags: List[TagInfo],
    request: Request,
):
    """
    5. 회사 태그 정보 추가
        - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력

    Args:
        company_name (str): 회사 이름
        tags (List[TagInfo]): 추가할 태그 정보

    Returns:
        Dict[str, str]: 추가된 태그 정보
    """
    company_service: CompanyService = CompanyService()
    results: Dict[str, str] = await company_service.add_new_tag(
        company_name,
        tags,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return results


### DELETE
@router.delete("/{company_name}/tags/{tag}")
async def delete_tag(
    compnay_name: str,
    tag: str,
    request: Request,
):
    """
    6. 회사 태그 정보 삭제
        - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력

    Args:
        compnay_name (str): 회사 이름
        tag_name (str): 삭제할 태그
    
    Returns:
        Dict[str, str]: 삭제 후 태그 정보
    """
    company_service: CompanyService = CompanyService()
    results = await company_service.delete_tag(
        compnay_name,
        tag,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return results
