import pytest
from orchai.runtime.container import ContainerRuntimeAdapter, ContainerRuntimeConfig

def test_container_runtime_config():
    config = ContainerRuntimeConfig(memory_limit="256m")
    assert config.memory_limit == "256m"
    assert config.cpu_limit == "0.5"
    assert config.network_mode == "none"

def test_container_runtime_unavailable_mocked(monkeypatch):
    adapter = ContainerRuntimeAdapter(ContainerRuntimeConfig())
    monkeypatch.setattr(adapter, "is_available", lambda: False)
    
    with pytest.raises(RuntimeError, match="Docker is unavailable"):
        adapter.execute(["echo", "test"])
