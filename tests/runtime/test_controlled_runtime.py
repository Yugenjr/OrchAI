import pytest
import asyncio
import sys
from orchai.runtime.process import AgentRuntime
from orchai.runtime.models import AgentProcessStatus

@pytest.mark.asyncio
async def test_controlled_runtime_basic_lifecycle():
    # Run the reference agent
    runtime = AgentRuntime(
        command=[sys.executable, "tests/runtime/reference_agent.py"],
        task_id="t1",
        attempt_id="a1"
    )
    
    status = await runtime.start()
    assert status == AgentProcessStatus.RUNNING
    
    # Send request
    req = b'{"jsonrpc": "2.0", "id": "init", "method": "run", "params": {"scenario": "read"}}\n'
    await runtime.send(req)
    
    # Receive MCP tool call
    res = await runtime.receive()
    if res is None:
        stderr_output = await runtime.process.stderr.read()
        print(f"STDERR: {stderr_output}")
    assert res is not None
    assert b"tools/call" in res
    
    # Send back tool result
    tool_res = b'{"jsonrpc": "2.0", "id": "1", "result": {"content": "mocked"}}\n'
    await runtime.send(tool_res)
    
    # Receive final exit wrapper
    final = await runtime.receive()
    assert final is not None
    assert b"mocked" in final
    
    # close stdin
    runtime.process.stdin.close()
    await runtime.process.stdin.wait_closed()
    
    code = await runtime.wait(timeout=5.0)
    assert code == 0
    assert runtime.status == AgentProcessStatus.COMPLETED

@pytest.mark.asyncio
async def test_process_cancellation():
    # Test that cancel works
    runtime = AgentRuntime(
        command=[sys.executable, "-c", "import time; time.sleep(10)"],
        task_id="t2",
        attempt_id="a2"
    )
    await runtime.start()
    runtime.cancel()
    
    code = await runtime.wait()
    assert runtime.status == AgentProcessStatus.CANCELLED

@pytest.mark.asyncio
async def test_command_timeout():
    # Test timeout
    runtime = AgentRuntime(
        command=[sys.executable, "-c", "import time; time.sleep(10)"],
        task_id="t3",
        attempt_id="a3"
    )
    await runtime.start()
    
    code = await runtime.wait(timeout=0.1)
    assert runtime.status == AgentProcessStatus.TIMEOUT
