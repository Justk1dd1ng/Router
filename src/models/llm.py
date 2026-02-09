from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Standardized LLM response"""
    content: str
    model: str
