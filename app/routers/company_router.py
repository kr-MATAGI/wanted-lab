import os
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from typing import Dict, List, Any

from app.services import CompanyService
from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    CompanyAddResponse,
    TagAddRequest,
    TagInfo,
)
from app.utils import setup_logger


# Router
router = APIRouter()

# Logger 
logger = setup_logger("CompanyRouter")

# Global Variable
ALLOWED_EXTENSIONS = {"csv"}

def validate_file(file: UploadFile):
    """
    업로드된 파일이 허용되는지 검사
    """
    return file.filename.split(".")[-1] in ALLOWED_EXTENSIONS

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
    company_info: Dict[str, Any] = await company_service.get_company_info(
        company_name,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    # 검색 결과가 없음 -> 404 Return
    if not company_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{company_name} information not found",
        )

    return CompanyInfoResponse(**company_info)


### POST
@router.post("/upload")
async def upload_company_from_csv(
    file: UploadFile = File(...),
):
    """
    CSV 파일 업로드를 통해 초기 회사 정보 추가 (임의 추가 함수)
    
    Args:
        pass
    
    Returns:
        results (Dict[str, str]): 추가된 회사 개수
    """        
    
    # 유효성 검사
    if not validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        os.makedirs("./tmps", exist_ok=True)
        
        file_path = f"./tmps/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Uploaded file: {file_path}")

        company_service: CompanyService = CompanyService()
        results: Dict[str, str] = await company_service.add_company_from_csv(
            file_path,
    )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 업로드된 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted uploaded file: {file_path}")
    
    return results

@router.post("/")
async def add_new_company(
    new_company_info: CompanyAddRequest,
    request: Request,
):
    """
    - 새로운 회사 추가
        - 새로운 언어도 같이 추가 될 수 있다.
        - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력
        
    - Args:
        - new_company_info (CompanyAddRequest): 새로운 회사 정보
    
    - Returns:
        - results (CompanyAddResponse): 추가된 회사 정보
    """

    company_service: CompanyService = CompanyService()
    add_results: Dict[str, Any] = await company_service.add_new_company(
        new_company_info.model_dump(),
        language=request.headers.get("x-wanted-language", "tw"),
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
    5. 회사 태그 정보 추가
        - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력

    Args:
        company_name (str): 회사 이름
        tags (List[TagInfo]): 추가할 태그 정보

    Returns:
        Dict[str, str]: 추가된 태그 정보
    """
    company_service: CompanyService = CompanyService()
    results: Dict[str, Any] = await company_service.add_new_tag(
        company_name,
        tags,
        language=request.headers.get("x-wanted-language", "ko"),
    )

    return CompanyAddResponse(**results)


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
