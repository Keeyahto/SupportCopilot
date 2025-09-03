from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Source(BaseModel):
    id: str
    score: float
    filename: str
    page: int = 1
    snippet: str
    highlights: List[List[int]] = Field(default_factory=list)


class ToolInfo(BaseModel):
    name: str
    sql: Optional[str] = None
    rows: Optional[List[dict]] = None
    summary: Optional[str] = None


class Metrics(BaseModel):
    confidence: Optional[float] = None
    tool_latency_ms: Optional[int] = None


class ChatRequest(BaseModel):
    text: str
    mode: str = Field(default="faq", pattern=r"^(faq|orders|policies|admin)$")
    strict: bool = False
    lang: str = Field(default="ru", pattern=r"^(ru|en)$")


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    metrics: Optional[Metrics] = None
    tool_info: Optional[ToolInfo] = None

