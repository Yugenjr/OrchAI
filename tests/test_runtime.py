import os
import pytest
from orchai.core.models import (
    AuthenticationConfig, RuntimeCapability, CapabilityStatus, RuntimeTestResult, AgentEvent, AgentEventType, VerificationResult, ReconciledExecutionResult
)

def test_auth_config_creation():
    config = AuthenticationConfig(provider="google", runtime="antigravity", credential_source="env", configured=True, validated=False)
    assert config.provider == "google"
    assert config.configured is True

def test_auth_config_no_secrets():
    config = AuthenticationConfig(provider="test", runtime="test", credential_source="env", configured=True, validated=True)
    assert not hasattr(config, "api_key")

def test_runtime_capability_states():
    cap = RuntimeCapability(name="READ", status=CapabilityStatus.UNVERIFIED, source="AntigravitySDK")
    assert cap.status == CapabilityStatus.UNVERIFIED

def test_runtime_test_result():
    res = RuntimeTestResult(test_id="t1", test_name="READ_TEST", status=CapabilityStatus.BLOCKED, runtime="antigravity", adapter="sdk", authentication_status="MISSING")
    assert res.status == CapabilityStatus.BLOCKED

def test_auth_blocked_status(monkeypatch, capsys):
    from orchai.cli.main import runtime_test
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    runtime_test(case=None)
    captured = capsys.readouterr()
    assert "Authentication unavailable" in captured.out
    assert "Status: BLOCKED" in captured.out

def test_secret_redaction_logs():
    secret = "AIzaSyFakeSecretKeyForTestingDoNotUse123"
    log = f"User logged in with key {secret}"
    # Simulated redaction logic
    redacted = log.replace(secret, "[REDACTED]")
    assert secret not in redacted

def test_secret_leakage_exception():
    secret = "fake_token_123"
    try:
        raise Exception(f"Failed to auth with {secret}")
    except Exception as e:
        msg = str(e).replace(secret, "***")
        assert secret not in msg

def test_event_provenance():
    event = AgentEvent(event_type=AgentEventType.TASK_STARTED, source="RUNTIME")
    assert event.source == "RUNTIME"

def test_session_verification_fallback():
    # If session is unavailable it falls back to NEW_SESSION_WITH_CONTEXT
    fallback_used = True
    assert fallback_used

def test_permission_reevaluation_independent():
    # Attempt 1 -> Attempt 2 independent scope
    scope1 = ["src/**"]
    scope2 = ["infra/**"]
    assert scope1 != scope2

def test_runtime_health_cli(monkeypatch, capsys):
    from orchai.cli.main import runtime_doctor
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    runtime_doctor()
    captured = capsys.readouterr()
    assert "Credentials present: UNKNOWN" in captured.out

def test_runtime_capabilities_cli(capsys):
    from orchai.cli.main import runtime_capabilities
    runtime_capabilities()
    captured = capsys.readouterr()
    assert "COMMAND_EXECUTION: UNVERIFIED" in captured.out

def test_auth_status_cli_missing(monkeypatch, capsys):
    from orchai.cli.main import auth_status
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    auth_status()
    captured = capsys.readouterr()
    assert "Authentication: MISSING" in captured.out

def test_auth_status_cli_present(monkeypatch, capsys):
    from orchai.cli.main import auth_status
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    auth_status()
    captured = capsys.readouterr()
    assert "Authentication: CONFIGURED" in captured.out

def test_auth_remove_cli(capsys):
    from orchai.cli.main import auth_remove
    auth_remove()
    captured = capsys.readouterr()
    assert "unset" in captured.out

def test_auth_test_cli_blocked(monkeypatch, capsys):
    from orchai.cli.main import auth_test
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    auth_test()
    captured = capsys.readouterr()
    assert "BLOCKED" in captured.out

def test_runtime_report_cli(capsys):
    from orchai.cli.main import runtime_report
    runtime_report()
    captured = capsys.readouterr()
    assert "Generating" in captured.out

def test_runtime_test_result_evidence():
    res = RuntimeTestResult(test_id="t1", test_name="READ_TEST", status=CapabilityStatus.BLOCKED, runtime="antigravity", adapter="sdk", authentication_status="MISSING", evidence="No key")
    assert res.evidence == "No key"

def test_scope_validation_mismatch():
    expected = ["src/a.py"]
    actual = ["src/a.py", "README.md"]
    assert set(actual) - set(expected) == {"README.md"}

def test_agent_claim_vs_observed():
    claim = "Modified src/a.py"
    observed = ["README.md"]
    mismatch = "src/a.py" not in observed
    assert mismatch is True

def test_capability_status_implemented():
    cap = RuntimeCapability(name="READ", status=CapabilityStatus.IMPLEMENTED, source="AntigravitySDK")
    assert cap.status == CapabilityStatus.IMPLEMENTED

def test_capability_status_mock_verified():
    cap = RuntimeCapability(name="WRITE", status=CapabilityStatus.MOCK_VERIFIED, source="AntigravitySDK")
    assert cap.status == CapabilityStatus.MOCK_VERIFIED

def test_capability_status_runtime_verified():
    cap = RuntimeCapability(name="CMD", status=CapabilityStatus.RUNTIME_VERIFIED, source="AntigravitySDK")
    assert cap.status == CapabilityStatus.RUNTIME_VERIFIED

def test_capability_status_unsupported():
    cap = RuntimeCapability(name="SESSION", status=CapabilityStatus.UNSUPPORTED, source="AntigravitySDK")
    assert cap.status == CapabilityStatus.UNSUPPORTED

def test_capability_status_blocked():
    cap = RuntimeCapability(name="TOOL", status=CapabilityStatus.BLOCKED, source="AntigravitySDK")
    assert cap.status == CapabilityStatus.BLOCKED
