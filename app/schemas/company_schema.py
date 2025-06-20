from pydantic import BaseModel
from typing import List, Dict

class TagName(BaseModel):
    tag_name: Dict[str, str]

class CompanyInfoResponse(BaseModel):
    company_name: str
    tags: List[str]

class CompanyRequest(BaseModel):
    company_name: Dict[str, str]
    tags: List[TagName]

class CompanyResponse(BaseModel):
    company_name: str
    tags: List[str]