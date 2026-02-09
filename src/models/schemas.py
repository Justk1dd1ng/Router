from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    route: str
    response: str
    data: dict = Field(default_factory=dict)
