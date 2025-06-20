import pytest
from app.repositories.company_repository import CompanyRepository

@pytest.mark.asyncio
async def test_add_get_tag_info():
    """
    태그 정보 조회 테스트
    pytest -s tests/test_company_repo.py::test_add_get_tag_info
    """
    company_repository = CompanyRepository()

    # 태그 정보 조회
    tag_infos = await company_repository.get_company_info_by_company_id(company_id=1)
    print("태그 정보:", tag_infos)


    # 검증
    assert isinstance(tag_infos, list)
    assert len(tag_infos) > 0