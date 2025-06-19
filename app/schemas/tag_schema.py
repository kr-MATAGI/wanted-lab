from pydantic import BaseModel
from typing import List, Dict

class TagInfo(BaseModel):
    tag_name: Dict[str, str]


class TagAddRequest(BaseModel):
    compnay_name: str
    tags: List[TagInfo]


class TagSearchResponse(BaseModel):
    company_name: str