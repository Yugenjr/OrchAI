import json
from pathlib import Path
from typing import List, Optional
from orchai.core.models import Task

class TaskRepository:
    def __init__(self, root_dir: str = ".orchai"):
        self.tasks_dir = Path(root_dir) / "tasks"
        
    def create(self, task: Task) -> None:
        if self._exists(task.id):
            raise ValueError(f"Task {task.id} already exists.")
        self._write(task)
        
    def get(self, task_id: str) -> Optional[Task]:
        file_path = self.tasks_dir / f"{task_id}.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Task(**data)
        except Exception:
            return None
            
    def update(self, task: Task) -> None:
        if not self._exists(task.id):
            raise ValueError(f"Task {task.id} does not exist.")
        self._write(task)
        
    def list(self) -> List[Task]:
        tasks = []
        if not self.tasks_dir.exists():
            return tasks
        for file_path in self.tasks_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    tasks.append(Task(**data))
            except Exception:
                pass
        return tasks
        
    def delete(self, task_id: str) -> None:
        file_path = self.tasks_dir / f"{task_id}.json"
        if file_path.exists():
            file_path.unlink()

    def _exists(self, task_id: str) -> bool:
        return (self.tasks_dir / f"{task_id}.json").exists()

    def _write(self, task: Task) -> None:
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.tasks_dir / f"{task.id}.json"
        # Atomic write would be ideal, but for MVP standard write is acceptable
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(task.model_dump_json(indent=2))
