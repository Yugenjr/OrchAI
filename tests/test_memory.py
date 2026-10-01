import pytest
import shutil
from pathlib import Path
from orchai.memory.store import MemoryStore
from orchai.memory.manager import MemoryManager
from orchai.core.models import MemoryEntry, MemoryCategory, MemoryStatus, MemoryProvenance

@pytest.fixture
def memory_store(tmp_path):
    store = MemoryStore(directory=str(tmp_path / ".orchai/memory"))
    yield store

@pytest.fixture
def memory_manager(memory_store):
    return MemoryManager(memory_store)

def test_memory_store_create(memory_store):
    assert len(memory_store.list_all()) == 0

def test_memory_add(memory_manager):
    entry = memory_manager.add_decision("Auth", "Use JWT", MemoryCategory.ARCHITECTURE_DECISION, ["auth", "security"])
    assert entry.id.startswith("mem_")
    assert entry.status == MemoryStatus.ACTIVE

def test_memory_crud_get(memory_manager, memory_store):
    entry = memory_manager.add_decision("DB", "Postgres", MemoryCategory.ARCHITECTURE_DECISION, ["db"])
    retrieved = memory_store.get(entry.id)
    assert retrieved is not None
    assert retrieved.title == "DB"

def test_memory_crud_update(memory_manager, memory_store):
    entry = memory_manager.add_decision("DB", "Postgres", MemoryCategory.ARCHITECTURE_DECISION, ["db"])
    entry.content = "Postgres 15"
    memory_store.update(entry)
    retrieved = memory_store.get(entry.id)
    assert retrieved.content == "Postgres 15"

def test_memory_crud_delete(memory_manager, memory_store):
    entry = memory_manager.add_decision("DB", "Postgres", MemoryCategory.ARCHITECTURE_DECISION, ["db"])
    memory_store.delete(entry.id)
    assert memory_store.get(entry.id) is None

def test_memory_search_title(memory_manager):
    memory_manager.add_decision("Frontend", "React", MemoryCategory.ARCHITECTURE_DECISION, ["ui"])
    results = memory_manager.search("Frontend")
    assert len(results) == 1

def test_memory_search_content(memory_manager):
    memory_manager.add_decision("Backend", "FastAPI", MemoryCategory.ARCHITECTURE_DECISION, ["api"])
    results = memory_manager.search("fastapi")
    assert len(results) == 1

def test_memory_search_tags(memory_manager):
    memory_manager.add_decision("Cache", "Redis", MemoryCategory.ARCHITECTURE_DECISION, ["redis", "performance"])
    results = memory_manager.search("performance")
    assert len(results) == 1

def test_memory_search_no_match(memory_manager):
    memory_manager.add_decision("Cache", "Redis", MemoryCategory.ARCHITECTURE_DECISION, ["redis"])
    assert len(memory_manager.search("unknown")) == 0

def test_memory_provenance_developer(memory_manager):
    entry = memory_manager.add_decision("Test", "Data", MemoryCategory.ARCHITECTURE_DECISION, [])
    assert entry.provenance == MemoryProvenance.DEVELOPER

def test_memory_conflict_detection(memory_manager):
    memory_manager.add_decision("Auth", "Use JWT", MemoryCategory.ARCHITECTURE_DECISION, [])
    entry2 = memory_manager.add_decision("Auth", "Use OAuth", MemoryCategory.ARCHITECTURE_DECISION, [])
    assert entry2.status == MemoryStatus.CONFLICT

def test_memory_extraction_candidate(memory_manager):
    entry = memory_manager.add_candidate("Auth", "Agent proposes JWT", MemoryCategory.ARCHITECTURE_DECISION, "task_123")
    assert entry.status == MemoryStatus.CANDIDATE
    assert entry.provenance == MemoryProvenance.AGENT_CLAIM

def test_security_restriction(memory_manager):
    # Agent claims permanent architectural decision
    entry = memory_manager.add_candidate("Disable Auth", "Just turn it off", MemoryCategory.SECURITY_RULE, "task_999")
    # Must not be active automatically
    assert entry.status == MemoryStatus.CANDIDATE
    assert entry.provenance == MemoryProvenance.AGENT_CLAIM

def test_memory_relevance_selection():
    # Simple selection simulation for context compiler
    from orchai.core.context import OrchAIContextCompiler
    from orchai.core.models import Task
    
    compiler = OrchAIContextCompiler()
    task = Task(id="t1", title="Add OAuth login", description="Implement OAuth")
    
    memories = [
        MemoryEntry(id="m1", type=MemoryCategory.ARCHITECTURE_DECISION, title="Auth", content="JWT"),
        MemoryEntry(id="m2", type=MemoryCategory.ARCHITECTURE_DECISION, title="UI", content="React")
    ]
    
    # Filter memories manually as manager.search would
    relevant = [m for m in memories if "Auth" in m.title]
    prompt = compiler.compile_prompt(task, None, [], relevant)
    
    assert "ENGINEERING DECISIONS" in prompt
    assert "JWT" in prompt
    assert "React" not in prompt

def test_memory_manager_conflict_resolution(memory_manager):
    e1 = memory_manager.add_decision("DB", "MySQL", MemoryCategory.ARCHITECTURE_DECISION, [])
    e2 = memory_manager.add_decision("DB", "Postgres", MemoryCategory.ARCHITECTURE_DECISION, [])
    assert e2.status == MemoryStatus.CONFLICT
    e2.status = MemoryStatus.ACTIVE
    memory_manager.store.update(e2)
    assert memory_manager.store.get(e2.id).status == MemoryStatus.ACTIVE
