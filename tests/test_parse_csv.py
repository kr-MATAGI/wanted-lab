import pytest
import json
from typing import List, Dict, Any

from app.services import CompanyService
from app.utils.parser import Parser, CsvCompnay

@pytest.mark.asyncio
async def test_add_new_company():
    """
    CSV 파일 기반의 새로운 회사 추가 테스트
    """
    # Service
    company_service = CompanyService()

    # Parse CSV
    parser = Parser()
    results: List[CsvCompnay] = await parser.parse_csv_by_file_path("./company_tag_sample.csv")

    for item in results:
        new_tags: List[Dict[str, Any]] = []
        tag_len: int = len(item.tag_ko)
        for idx in range(tag_len):
            new_tags.append({
                "tag_name": {
                    "ko": item.tag_ko[idx],
                    "en": item.tag_en[idx],
                    "ja": item.tag_ja[idx],
                }
            })

        new_company = {
            "company_name": {
                "ko": item.company_ko,
                "en": item.company_en,
                "ja": item.company_ja,
            },
            "tags": new_tags,
        }


        # When
        result = await company_service.add_new_company(new_company, language="ko")

        # Then
        assert result != None