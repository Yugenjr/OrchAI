import json
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
