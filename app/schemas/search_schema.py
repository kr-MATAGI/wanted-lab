from pydantic import BaseModel


class SearchResponse(BaseModel):
    company_name: str
    