import json
import sys
from orchai.mcp.transport.stdio import StdioTransport
from orchai.mcp.transport.protocol import JSONRPCRequest, JSONRPCResponse
from orchai.mcp.gateway import MCPGateway
from orchai.core.models import PolicyDecisionType

class MCPServer:
    def __init__(self, gateway: MCPGateway):
        self.gateway = gateway
        self.transport = StdioTransport()

    async def handle_request(self, req: JSONRPCRequest) -> JSONRPCResponse:
        if req.method == "initialize":
            return JSONRPCResponse(id=req.id, result={"protocolVersion": "2.0", "capabilities": {}})
        
        elif req.method == "tools/list":
            tools = [
                {"name": "orchai.read_file", "description": "Read file"},
                {"name": "orchai.write_file", "description": "Write file"},
                {"name": "orchai.run_command", "description": "Run structured command"}
            ]
            return JSONRPCResponse(id=req.id, result={"tools": tools})
            
        elif req.method == "tools/call":
            params = req.params
            tool_name = params.get("name")
            args = params.get("arguments", {})
            task_id = params.get("task_id", "default_task")
            attempt_id = params.get("attempt_id", "default_attempt")
            
            # Policy check
            decision, reason = self.gateway.evaluate_request(task_id, attempt_id, tool_name, args)
            
            if decision == PolicyDecisionType.DENY:
                return JSONRPCResponse(id=req.id, error={"code": 403, "message": f"Denied: {reason}"})
                
            elif decision == PolicyDecisionType.REQUIRE_APPROVAL:
                # Approval flow simulation (wait for human, block here)
                return JSONRPCResponse(id=req.id, error={"code": 401, "message": "Approval required"})
                
            # Simulate execution for now (in real system, invoke actual tool)
            return JSONRPCResponse(id=req.id, result={"content": f"Executed {tool_name}"})
            
        return JSONRPCResponse(id=req.id, error={"code": -32601, "message": "Method not found"})

    async def serve(self):
        await self.transport.listen(self.handle_request)
