import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AuditEventType(str, Enum):
    TASK_CREATED = "TASK_CREATED"
    TASK_STARTED = "TASK_STARTED"
    TASK_ATTEMPT_STARTED = "TASK_ATTEMPT_STARTED"
    TOOL_REQUESTED = "TOOL_REQUESTED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    TOOL_APPROVED = "TOOL_APPROVED"
    TOOL_DENIED = "TOOL_DENIED"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    VERIFICATION_STARTED = "VERIFICATION_STARTED"
    VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    TASK_RESUMED = "TASK_RESUMED"
    TASK_CANCELLED = "TASK_CANCELLED"
    TASK_RECOVERED = "TASK_RECOVERED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"

class StructuredEvent(BaseModel):
    event_id: str
    event_type: AuditEventType
    task_id: str
    attempt_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    execution_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = "SYSTEM"
    actor_type: str = "SYSTEM"
    actor_id: Optional[str] = None
    tenant_id: Optional[str] = None
    status: str = "SUCCESS"
    payload: Dict[str, Any] = Field(default_factory=dict)
    previous_event_hash: Optional[str] = None
    event_hash: Optional[str] = None

    def compute_hash(self) -> str:
        # Create a canonical representation without the event_hash itself
        data = self.model_dump(exclude={"event_hash"})
        # Convert datetime to string for stable hashing
        data["timestamp"] = data["timestamp"].isoformat()
        
        # Sort keys for deterministic JSON serialization
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
