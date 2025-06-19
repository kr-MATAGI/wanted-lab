from pydantic import BaseModel
from typing import List, Dict

class CompanyInfoResponse(BaseModel):
    company_name: str
    tags: List[str]


class CompanyAddRequest(BaseModel):
    company_name: Dict[str, str]
    tags: List[Dict[str, str]]