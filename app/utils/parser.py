import os
import csv
from typing import List
from pydantic import BaseModel

from app.models.csv_base import CsvCompnay
from app.utils.logger import setup_logger

# Logger
logger = setup_logger("Parser")

class Parser:
    async def parse_csv_by_file_path(self, file_path: str):
        
        company_lists: List[CsvCompnay] = []

        # Parse CSV
        logger.debug(f"Parsing CSV file: {file_path}")
        
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
        
        logger.debug(f"Parsed {len(company_lists)} companies")

        return company_lists


### MAIN
if "__main__" == __name__:
    parser = Parser()
    results = parser.parse_csv_by_file_path("./company_tag_sample.csv")

    print(len(results))
    print(results[:5])
