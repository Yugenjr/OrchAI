import os
import json

# 1. Update models.py
models_path = 'src/orchai/core/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

new_models = '''
class MemoryCategory(str, Enum):
    ARCHITECTURE_DECISION = "ARCHITECTURE_DECISION"
    CODING_CONSTRAINT = "CODING_CONSTRAINT"
    PROJECT_CONSTRAINT = "PROJECT_CONSTRAINT"
    DEPENDENCY_DECISION = "DEPENDENCY_DECISION"
    SECURITY_RULE = "SECURITY_RULE"
    TASK_DECISION = "TASK_DECISION"
    BUG_FIX = "BUG_FIX"
    VERIFICATION_RESULT = "VERIFICATION_RESULT"
    AGENT_FEEDBACK = "AGENT_FEEDBACK"
    DEVELOPER_FEEDBACK = "DEVELOPER_FEEDBACK"

class MemoryProvenance(str, Enum):
    DEVELOPER = "DEVELOPER"
    DEVELOPER_FEEDBACK = "DEVELOPER_FEEDBACK"
    VERIFIED_EXECUTION = "VERIFIED_EXECUTION"
    AGENT_CLAIM = "AGENT_CLAIM"

class MemoryStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    CONFLICT = "CONFLICT"

class MemoryEntry(BaseModel):
    id: str
    type: MemoryCategory
    title: str
    content: str
    source_task_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    provenance: MemoryProvenance = MemoryProvenance.AGENT_CLAIM
    status: MemoryStatus = MemoryStatus.CANDIDATE

class TaskAttempt(BaseModel):
    attempt_number: int
    execution_id: str
    agent_result: Optional[AgentResult] = None
    verification_result: Optional[VerificationResult] = None
    review_result: Optional[str] = None
'''

if "MemoryCategory" not in models_content:
    with open(models_path, 'a', encoding='utf-8') as f:
        f.write(new_models)

# 2. Update state.py to handle CHANGES_REQUESTED
state_path = 'src/orchai/core/state.py'
with open(state_path, 'r', encoding='utf-8') as f:
    state_content = f.read()
if "CHANGES_REQUESTED" not in state_content:
    state_content = state_content.replace(
        'TaskState.AWAITING_REVIEW: {TaskState.APPROVED, TaskState.REJECTED}',
        'TaskState.AWAITING_REVIEW: {TaskState.APPROVED, TaskState.REJECTED, TaskState.CHANGES_REQUESTED}'
    )
    state_content = state_content.replace(
        'TaskState.COMPLETED: set()',
        'TaskState.CHANGES_REQUESTED: {TaskState.READY_FOR_EXECUTION, TaskState.EXECUTING, TaskState.REJECTED},\n            TaskState.COMPLETED: set()'
    )
    with open(state_path, 'w', encoding='utf-8') as f:
        f.write(state_content)

# Update models to include CHANGES_REQUESTED in TaskState enum
if "CHANGES_REQUESTED" not in models_content:
    with open(models_path, 'r', encoding='utf-8') as f:
        m = f.read()
    m = m.replace('COMPLETED = "COMPLETED"', 'COMPLETED = "COMPLETED"\n    CHANGES_REQUESTED = "CHANGES_REQUESTED"')
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(m)

# 3. Create Memory Module
os.makedirs('src/orchai/memory', exist_ok=True)
with open('src/orchai/memory/__init__.py', 'w', encoding='utf-8') as f:
    f.write('from .store import MemoryStore\nfrom .manager import MemoryManager\n')

with open('src/orchai/memory/store.py', 'w', encoding='utf-8') as f:
    f.write('''import json
from pathlib import Path
from typing import List, Optional
from orchai.core.models import MemoryEntry

class MemoryStore:
    def __init__(self, directory: str = ".orchai/memory"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.file_path = self.directory / "entries.json"
        self._load()

    def _load(self):
        if not self.file_path.exists():
            self.entries = []
            return
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.entries = [MemoryEntry(**e) for e in data]

    def _save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([e.model_dump() for e in self.entries], f, default=str, indent=2)

    def add(self, entry: MemoryEntry) -> None:
        self.entries.append(entry)
        self._save()

    def get(self, id: str) -> Optional[MemoryEntry]:
        for e in self.entries:
            if e.id == id:
                return e
        return None

    def list_all(self) -> List[MemoryEntry]:
        return self.entries

    def update(self, entry: MemoryEntry) -> None:
        for i, e in enumerate(self.entries):
            if e.id == entry.id:
                self.entries[i] = entry
                self._save()
                return

    def delete(self, id: str) -> None:
        self.entries = [e for e in self.entries if e.id != id]
        self._save()
''')

with open('src/orchai/memory/manager.py', 'w', encoding='utf-8') as f:
    f.write('''import uuid
from typing import List
from .store import MemoryStore
from orchai.core.models import MemoryEntry, MemoryCategory, MemoryProvenance, MemoryStatus

class MemoryManager:
    def __init__(self, store: MemoryStore):
        self.store = store

    def search(self, query: str) -> List[MemoryEntry]:
        # Simple deterministic search
        q = query.lower()
        results = []
        for e in self.store.list_all():
            if q in e.title.lower() or q in e.content.lower() or any(q in t.lower() for t in e.tags):
                results.append(e)
        return results

    def add_decision(self, title: str, content: str, category: MemoryCategory, tags: List[str]) -> MemoryEntry:
        # Check for conflicts deterministically
        existing = self.search(title)
        status = MemoryStatus.ACTIVE
        for e in existing:
            if e.type == category and e.status == MemoryStatus.ACTIVE:
                e.status = MemoryStatus.CONFLICT
                status = MemoryStatus.CONFLICT
                self.store.update(e)

        entry = MemoryEntry(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            type=category,
            title=title,
            content=content,
            tags=tags,
            provenance=MemoryProvenance.DEVELOPER,
            status=status
        )
        self.store.add(entry)
        return entry
        
    def add_candidate(self, title: str, content: str, category: MemoryCategory, source_task_id: str) -> MemoryEntry:
        entry = MemoryEntry(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            type=category,
            title=title,
            content=content,
            source_task_id=source_task_id,
            provenance=MemoryProvenance.AGENT_CLAIM,
            status=MemoryStatus.CANDIDATE
        )
        self.store.add(entry)
        return entry
''')

print("Phase 6 modules scaffolded.")
