import pytest
import os
import asyncio
from orchai.observability.models import StructuredEvent, AuditEventType
from orchai.observability.audit import AuditLedger, AuditLedgerError
from orchai.observability.metrics import MetricsStore
from orchai.service.task_service import TaskService
from orchai.core.models import TaskState

def test_structured_event_hashing():
    event = StructuredEvent(
        event_id="test-1",
        event_type=AuditEventType.TASK_CREATED,
        task_id="tsk_test",
        payload={"key": "value"}
    )
    h1 = event.compute_hash()
    
    # modify payload
    event.payload["key"] = "modified"
    h2 = event.compute_hash()
    assert h1 != h2

def test_audit_ledger_chaining(tmp_path):
    ledger = AuditLedger(str(tmp_path))
    task_id = "tsk_chain_test"
    
    e1 = StructuredEvent(event_id="e1", event_type=AuditEventType.TASK_CREATED, task_id=task_id)
    ledger.append(e1)
    
    e2 = StructuredEvent(event_id="e2", event_type=AuditEventType.TASK_STARTED, task_id=task_id)
    ledger.append(e2)
    
    events = ledger.read(task_id)
    assert len(events) == 2
    assert events[1].previous_event_hash == events[0].event_hash
    assert ledger.verify_chain(task_id) is True

def test_audit_ledger_tampering(tmp_path):
    ledger = AuditLedger(str(tmp_path))
    task_id = "tsk_tamper_test"
    
    e1 = StructuredEvent(event_id="e1", event_type=AuditEventType.TASK_CREATED, task_id=task_id)
    ledger.append(e1)
    
    # Tamper with file
    path = ledger._get_ledger_path(task_id)
    with open(path, "r") as f:
        content = f.read()
    
    # Modify the content to break the hash
    modified_content = content.replace('"event_id": "e1"', '"event_id": "e_hacked"')
    with open(path, "w") as f:
        f.write(modified_content)
        
    with pytest.raises(AuditLedgerError):
        ledger.verify_chain(task_id)

def test_metrics_store():
    metrics = MetricsStore()
    metrics.increment("test_counter", 1)
    metrics.observe("test_hist", 0.5)
    
    data = metrics.get_metrics()
    assert data["counters"]["test_counter"] >= 1
    assert data["histograms"]["test_hist"]["count"] >= 1
    
    prom = metrics.format_prometheus()
    assert "# TYPE test_counter counter" in prom

@pytest.mark.asyncio
async def test_task_service_observability_integration():
    service = TaskService()
    task = service.create_task("Test Observability")
    
    # Audit should have TASK_CREATED
    events = service.get_events(task.id)
    assert len(events) == 1
    assert events[0]["event_type"] == AuditEventType.TASK_CREATED
    
    # Metrics should be updated
    assert service.metrics.counters["tasks_created_total"] >= 1
    
    # Start task to trigger more events
    service.start_task(task.id)
    await asyncio.sleep(0.3)
    
    events = service.get_events(task.id)
    event_types = [e["event_type"] for e in events]
    assert AuditEventType.TASK_STARTED in event_types
    assert AuditEventType.TOOL_REQUESTED in event_types
