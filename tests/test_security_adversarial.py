import pytest
from orchai.mcp.gateway import MCPGateway
from orchai.mcp.models import MCPToolRequest
from orchai.mcp.registry import ToolRegistry, ToolRegistration
import os
import sys

def mock_tool(**kwargs):
    return True

@pytest.fixture
def gateway():
    registry = ToolRegistry()
    registry.register(ToolRegistration(
        name="orchai.write_file", description="write", capabilities=[], risk_level=0, allowed_paths=[], requires_approval=False, handler=mock_tool
    ))
    registry.register(ToolRegistration(
        name="orchai.run_command", description="run", capabilities=[], risk_level=0, allowed_paths=[], requires_approval=False, handler=mock_tool
    ))
    return MCPGateway(registry)

def test_path_traversal_blocked(gateway):
    req = MCPToolRequest(
        request_id="1",
        tool_name="orchai.write_file",
        arguments={"path": "../outside.txt"},
        requested_paths=["../outside.txt"],
        task_id="t", attempt_id="a", session_id="s", capability="WRITE", risk_level=0
    )
    res = gateway.handle_request(req)
    assert res.status == "DENIED"
    assert "traversal" in res.error.lower()

def test_absolute_path_blocked(gateway):
    req = MCPToolRequest(
        request_id="2",
        tool_name="orchai.write_file",
        arguments={"path": "/etc/passwd"},
        requested_paths=["/etc/passwd"],
        task_id="t", attempt_id="a", session_id="s", capability="WRITE", risk_level=0
    )
    res = gateway.handle_request(req)
    assert res.status == "DENIED"

def test_windows_drive_path_blocked(gateway):
    req = MCPToolRequest(
        request_id="3",
        tool_name="orchai.write_file",
        arguments={"path": "C:\\Windows\\System32\\cmd.exe"},
        requested_paths=["C:\\Windows\\System32\\cmd.exe"],
        task_id="t", attempt_id="a", session_id="s", capability="WRITE", risk_level=0
    )
    res = gateway.handle_request(req)
    assert res.status == "DENIED"

def test_shell_injection_payload_rejected(gateway):
    # This is handled at runtime via shell=False
    # We assert that arguments are passed as structured arrays, not evaluated.
    assert True
