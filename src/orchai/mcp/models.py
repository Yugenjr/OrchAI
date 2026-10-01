from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime

class MCPToolRequest(BaseModel):
    request_id: str
    tool_name: str
    arguments: Dict[str, Any]
    task_id: str
    attempt_id: str
    session_id: str
    capability: str
    requested_paths: List[str] = Field(default_factory=list)
    risk_level: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MCPPolicyDecision(BaseModel):
    request_id: str
    decision: str  # ALLOW, DENY, REQUIRE_APPROVAL
    reason: str
    policy_rule: str
    requires_approval: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MCPToolResponse(BaseModel):
    request_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    execution_duration: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
