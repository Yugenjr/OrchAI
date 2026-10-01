import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ExecutionLedgerRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    attempt_id: str
    request_id: str
    tool: str
    policy_decision: str
    execution_status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutionLedger:
    def __init__(self, storage_dir: str = ".orchai/ledger"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_path(self, record_id: str) -> str:
        return os.path.join(self.storage_dir, f"{record_id}.json")

    def _write_atomic(self, path: str, data: str):
        tmp_path = path + ".tmp"
        with open(tmp_path, "w") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)

    def save(self, record: ExecutionLedgerRecord):
        # Sanitize metadata
        sanitized = self._sanitize(record.metadata)
        record.metadata = sanitized
        data = record.model_dump_json()
        self._write_atomic(self._get_path(record.record_id), data)

    def _sanitize(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        sensitive_keys = {"key", "token", "password", "secret", "auth", "credential"}
        for k, v in metadata.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize(v)
            else:
                sanitized[k] = v
        return sanitized

    def get(self, record_id: str) -> Optional[ExecutionLedgerRecord]:
        path = self._get_path(record_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                return ExecutionLedgerRecord.model_validate_json(f.read())
        except Exception:
            return None

    def list_all(self) -> List[ExecutionLedgerRecord]:
        records = []
        for file in os.listdir(self.storage_dir):
            if file.endswith(".json") and not file.endswith(".tmp"):
                record_id = file[:-5]
                r = self.get(record_id)
                if r:
                    records.append(r)
        return records
