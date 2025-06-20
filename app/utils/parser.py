import os
import csv
from typing import List
from pydantic import BaseModel


class CsvCompnay(BaseModel):
    company_ko: str
    company_en: str
    company_ja: str
    
    tag_ko: List[str]
    tag_en: List[str]
    tag_ja: List[str]


class Parser:
    async def parse_csv_by_file_path(self, file_path: str):
        company_lists: List[CsvCompnay] = []
       
        # 파일 경로가 상대 경로인 경우 현재 작업 디렉토리 기준으로 절대 경로로 변환
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        
        with open(file_path, "r", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                # company_name
                company_info = CsvCompnay(
                    company_ko=row["company_ko"],
                    company_en=row["company_en"],
                    company_ja=row["company_ja"],
                    tag_ko=row["tag_ko"].split("|"),
                    tag_en=row["tag_en"].split("|"),
                    tag_ja=row["tag_ja"].split("|")
                )

                company_lists.append(company_info)

        return company_lists

async def main():
    parser = Parser()
    results = await parser.parse_csv_by_file_path("./company_tag_sample.csv")
    
    print(len(results))
    print(results[:5])

### MAIN
if "__main__" == __name__:
    import asyncio
    asyncio.run(main())