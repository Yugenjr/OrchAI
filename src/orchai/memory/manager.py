import uuid
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
