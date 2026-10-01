import os
from pathlib import Path

base = Path('src/orchai/mcp')
base.mkdir(parents=True, exist_ok=True)
(base / '__init__.py').touch()
(base / 'tools').mkdir(exist_ok=True)
(base / 'tools' / '__init__.py').touch()

# 1. Models
with open(base / 'models.py', 'w', encoding='utf-8') as f:
    f.write("""from pydantic import BaseModel, Field
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
""")

# 2. Registry
with open(base / 'registry.py', 'w', encoding='utf-8') as f:
    f.write("""from typing import Dict, Any, Callable
from pydantic import BaseModel

class ToolRegistration(BaseModel):
    name: str
    description: str
    capabilities: list[str]
    risk_level: int
    allowed_paths: list[str]
    requires_approval: bool
    handler: Any

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolRegistration] = {}

    def register(self, tool: ToolRegistration):
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolRegistration:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolRegistration]:
        return list(self._tools.values())
""")

# 3. Policy & Gateway (Simplified scaffolding for testing logic)
with open(base / 'gateway.py', 'w', encoding='utf-8') as f:
    f.write("""from .models import MCPToolRequest, MCPPolicyDecision, MCPToolResponse
from .registry import ToolRegistry
import os
import uuid
from datetime import datetime

class MCPGateway:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def handle_request(self, request: MCPToolRequest) -> MCPToolResponse:
        tool_reg = self.registry.get(request.tool_name)
        if not tool_reg:
            return MCPToolResponse(
                request_id=request.request_id,
                status="DENIED",
                error="Tool not found",
                execution_duration=0.0
            )

        # Basic path traversal check
        for path in request.requested_paths:
            if ".." in path or path.startswith("/") or path.startswith("C:"):
                return MCPToolResponse(
                    request_id=request.request_id,
                    status="DENIED",
                    error="Path traversal forbidden",
                    execution_duration=0.0
                )

        if tool_reg.requires_approval:
            return MCPToolResponse(
                request_id=request.request_id,
                status="REQUIRE_APPROVAL",
                execution_duration=0.0
            )

        try:
            res = tool_reg.handler(**request.arguments)
            return MCPToolResponse(
                request_id=request.request_id,
                status="SUCCESS",
                result=res,
                execution_duration=0.1
            )
        except Exception as e:
            return MCPToolResponse(
                request_id=request.request_id,
                status="ERROR",
                error=str(e),
                execution_duration=0.1
            )
""")

print("MCP scaffold created.")
