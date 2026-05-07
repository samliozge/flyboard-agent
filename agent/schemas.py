from pydantic import BaseModel
from typing import Optional, List, Any

class AgentRequest(BaseModel):
    task: str
    customer_id: Optional[str] = None
    language: Optional[str] = None

class ToolCall(BaseModel):
    name: str
    arguments: dict
    result: Any

class Metrics(BaseModel):
    latency_ms: float
    model: str
    openai_calls: int

class AgentResponse(BaseModel):
    trace_id: str
    final_answer: str
    tool_calls: List[ToolCall]
    metrics: Metrics