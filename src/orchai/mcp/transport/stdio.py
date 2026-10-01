import sys
import json
import asyncio
from orchai.mcp.transport.protocol import JSONRPCRequest, JSONRPCResponse

class StdioTransport:
    def __init__(self, in_stream=None, out_stream=None):
        self.in_stream = in_stream or sys.stdin
        self.out_stream = out_stream or sys.stdout

    async def listen(self, handler_coroutine):
        loop = asyncio.get_event_loop()
        while True:
            # Run blocking readline in executor to avoid blocking event loop
            line = await loop.run_in_executor(None, self.in_stream.readline)
            if not line:
                break
                
            if len(line) > 1024 * 1024:
                err = JSONRPCResponse(id="null", error={"code": -32700, "message": "Payload too large"})
                self.send(err)
                continue
                
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                if not isinstance(data, dict):
                    raise ValueError("Request must be an object")
                if "jsonrpc" not in data or data["jsonrpc"] != "2.0":
                    raise ValueError("Invalid JSON-RPC version")
                if "method" not in data:
                    raise ValueError("Method is required")
                if "id" not in data:
                    raise ValueError("ID is required")
                    
                req = JSONRPCRequest(**data)
                # Dispatch to handler
                res = await handler_coroutine(req)
                self.send(res)
            except json.JSONDecodeError:
                err = JSONRPCResponse(id="null", error={"code": -32700, "message": "Parse error"})
                self.send(err)
            except Exception as e:
                err = JSONRPCResponse(id=data.get("id", "null"), error={"code": -32603, "message": str(e)})
                self.send(err)

    def send(self, response: JSONRPCResponse):
        out = response.model_dump_json(exclude_none=True)
        self.out_stream.write(out + "\n")
        self.out_stream.flush()
