import sys
import json
import asyncio

async def main():
    # Read commands from stdin
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        req = json.loads(line)
        method = req.get("method")
        
        # Determine behavior based on params to test various conditions
        if method == "run":
            scenario = req.get("params", {}).get("scenario")
            
            # For this test reference agent, it just sends MCP calls to stdout
            # and waits for response. We simulate the protocol manually here for simplicity.
            
            rpc_req = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "tools/call",
                "params": {
                    "name": "orchai.read_file" if "read" in scenario else "orchai.write_file",
                    "arguments": {"path": "test.txt"},
                    "task_id": "test_task",
                    "attempt_id": "test_attempt"
                }
            }
            if "command" in scenario:
                rpc_req["params"]["name"] = "orchai.run_command"
                
            print(json.dumps(rpc_req), flush=True)
            
            res_line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            res = json.loads(res_line)
            
            # Print back to OrchAI runner via stderr so it's not confused with MCP? 
            # Actually, the reference agent is supposed to run in a subprocess and communicate via JSON-RPC.
            # Our runner will send {"method": "run", ...} and we do the MCP flow.
            # Then we can exit.
            
            final_res = {"jsonrpc": "2.0", "id": req.get("id"), "result": res}
            print(json.dumps(final_res), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
