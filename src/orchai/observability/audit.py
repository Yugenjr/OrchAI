import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from orchai.observability.models import StructuredEvent

class AuditLedgerError(Exception):
    pass

class AuditLedger:
    def __init__(self, root_dir: str = ".orchai/audit"):
        self.audit_dir = Path(root_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        # We maintain one ledger file per task_id for atomic appends
        
    def _get_ledger_path(self, task_id: str) -> Path:
        return self.audit_dir / f"{task_id}.jsonl"

    def append(self, event: StructuredEvent) -> StructuredEvent:
        ledger_path = self._get_ledger_path(event.task_id)
        
        latest_hash = self.latest_hash(event.task_id)
        event.previous_event_hash = latest_hash
        event.event_hash = event.compute_hash()
        
        # Simple file locking for atomicity on Windows is tricky with fcntl, 
        # but since we're providing a basic atomic append, we just open in append mode.
        with open(ledger_path, "a", encoding="utf-8") as f:
            data = event.model_dump()
            data["timestamp"] = data["timestamp"].isoformat()
            f.write(json.dumps(data, sort_keys=True) + "\n")
            
        return event

    def read(self, task_id: str) -> List[StructuredEvent]:
        ledger_path = self._get_ledger_path(task_id)
        if not ledger_path.exists():
            return []
            
        events = []
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(StructuredEvent(**json.loads(line)))
        return events

    def read_attempt(self, task_id: str, attempt_id: str) -> List[StructuredEvent]:
        all_events = self.read(task_id)
        return [e for e in all_events if e.attempt_id == attempt_id]

    def verify_chain(self, task_id: str) -> bool:
        events = self.read(task_id)
        if not events:
            return True
            
        expected_prev = None
        for i, event in enumerate(events):
            if event.previous_event_hash != expected_prev:
                raise AuditLedgerError(f"Chain broken at event {i}: invalid previous_event_hash")
                
            computed = event.compute_hash()
            if event.event_hash != computed:
                raise AuditLedgerError(f"Chain broken at event {i}: invalid event_hash (Payload modified)")
                
            expected_prev = event.event_hash
            
        return True

    def latest_hash(self, task_id: str) -> Optional[str]:
        events = self.read(task_id)
        if not events:
            return None
        return events[-1].event_hash
