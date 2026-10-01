from typing import Dict, Any, Optional
import hashlib
import json
from orchai.mcp.models import MCPToolRequest

class ApprovalStore:
    def __init__(self):
        self._approvals: Dict[str, str] = {} # request_id -> hash

    def _hash_request(self, request: MCPToolRequest) -> str:
        # Binding approval to exact request signature
        payload = {
            "task_id": request.task_id,
            "attempt_id": request.attempt_id,
            "tool": request.tool_name,
            "args": request.arguments
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def approve(self, request: MCPToolRequest):
        self._approvals[request.request_id] = self._hash_request(request)

    def is_approved(self, request: MCPToolRequest) -> bool:
        if request.request_id not in self._approvals:
            return False
        return self._approvals[request.request_id] == self._hash_request(request)

    def consume(self, request: MCPToolRequest):
        if request.request_id in self._approvals:
            del self._approvals[request.request_id]
