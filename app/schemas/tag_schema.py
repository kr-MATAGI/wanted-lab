from pydantic import BaseModel
from typing import List, Dict

class TagInfo(BaseModel):
    tag_name: Dict[str, str]


class TagSearchResponse(BaseModel):
    company_name: str