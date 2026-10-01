from .models import MCPToolRequest, MCPPolicyDecision, MCPToolResponse
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
