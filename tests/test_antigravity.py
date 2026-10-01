import pytest
from unittest.mock import MagicMock, patch
from orchai.adapters.antigravity import AntigravitySDKAdapter, AntigravityCLIAdapter, AntigravityEventMapper, ANTIGRAVITY_SDK_AVAILABLE
from orchai.policy.bridge import PolicyBridge
from orchai.core.models import (
    AgentCapabilityType, PolicyDecisionType, TaskRequest, AgentEventType, AgentEvent,
    AgentExecutionReport, VerificationResult, ExecutionRecord, ReconciledExecutionResult
)
from orchai.core.reconciler import ExecutionReconciler

def test_policy_bridge_command_approval():
    bridge = PolicyBridge({AgentCapabilityType.COMMAND_EXECUTION: PolicyDecisionType.REQUIRE_APPROVAL})
    decision = bridge.evaluate_tool("run_command", {"command": "echo test"})
    assert decision == PolicyDecisionType.REQUIRE_APPROVAL

def test_policy_bridge_command_deny():
    bridge = PolicyBridge({AgentCapabilityType.COMMAND_EXECUTION: PolicyDecisionType.DENY})
    decision = bridge.evaluate_tool("run_command", {"command": "rm -rf /"})
    assert decision == PolicyDecisionType.DENY

def test_event_mapper():
    event = AntigravityEventMapper.map_tool_event("run_command", "requested", {"command": "echo test"})
    assert event.event_type == AgentEventType.COMMAND_REQUESTED
    assert event.details["tool"] == "run_command"
    assert event.details["command"] == "echo test"

def test_execution_reconciler_match():
    report = AgentExecutionReport(
        task_id="test_task", summary="Done", status="completed", final_message="Done",
        files_claimed_modified=["src/test.py"]
    )
    verification = VerificationResult(passed=True, summary="All good")
    record = ExecutionRecord(execution_id="exec_1", task_id="test_task", started_at="2023-01-01T00:00:00Z")
    
    reconciler = ExecutionReconciler()
    result = reconciler.reconcile(report, ["src/test.py"], verification, record)
    
    assert result.agent_claim_matches_repository is True
    assert not result.unexpected_changes

def test_execution_reconciler_unexpected_change():
    report = AgentExecutionReport(
        task_id="test_task", summary="Done", status="completed", final_message="Done",
        files_claimed_modified=["src/test.py"]
    )
    verification = VerificationResult(passed=True, summary="All good")
    record = ExecutionRecord(execution_id="exec_1", task_id="test_task", started_at="2023-01-01T00:00:00Z")
    
    reconciler = ExecutionReconciler()
    result = reconciler.reconcile(report, ["src/test.py", "README.md"], verification, record)
    
    assert result.agent_claim_matches_repository is False
    assert "README.md" in result.unexpected_changes

@pytest.mark.skipif(not ANTIGRAVITY_SDK_AVAILABLE, reason="SDK not available")
def test_sdk_adapter_capabilities():
    bridge = PolicyBridge({})
    adapter = AntigravitySDKAdapter(bridge, "system prompt")
    adapter.initialize()
    caps = adapter.capabilities()
    assert len(caps) > 0

def test_cli_adapter_capabilities():
    adapter = AntigravityCLIAdapter("system prompt")
    caps = adapter.capabilities()
    assert any(c.type == AgentCapabilityType.READ for c in caps)
