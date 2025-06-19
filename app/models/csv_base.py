from pydantic import BaseModel
from typing import List

class CsvCompnay(BaseModel):
    company_ko: str
    company_en: str
    company_ja: str
    
    tag_ko: List[str]
    tag_en: List[str]
    tag_ja: List[str]