from typing import Dict, Any, Callable
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
