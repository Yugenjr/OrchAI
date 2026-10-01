import pytest
from orchai.adapters.offline import OfflineAgentAdapter
from orchai.adapters.base import AgentAdapter

def test_offline_adapter_initialization():
    adapter = OfflineAgentAdapter()
    assert adapter.initialize() is True
    assert adapter.health_check() == "OFFLINE"
    assert len(adapter.capabilities()) == 0

def test_offline_adapter_execution():
    adapter = OfflineAgentAdapter()
    res = adapter.execute("t1", "a1")
    assert res["status"] == "SUCCESS"
    assert adapter.supports_session_resume() is False

def test_adapter_contract_interface():
    assert issubclass(OfflineAgentAdapter, AgentAdapter)
    
def test_antigravity_adapter_is_isolated():
    # Even if missing runtime, adapter must instantiate safely
    from orchai.adapters.antigravity import AntigravitySDKAdapter
    adapter = AntigravitySDKAdapter(None, "")
    # It should not crash on init
    assert adapter is not None
