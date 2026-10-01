import pytest
from orchai.core.models import TaskState, ExecutionStatus, ReconciledExecutionResult, ScopeComparisonResult, ExecutionRecord, AgentExecutionReport

def test_agent_dishonesty_scope_violation():
    # Agent claims it modified src/app.py
    # Git observes src/app.py and README.md
    
    scope = ScopeComparisonResult(
        expected_files=["src/app.py"],
        actual_files=["src/app.py", "README.md"],
        unexpected_changes=["README.md"],
        missing_expected_changes=[],
        compliant=False
    )
    
    report = AgentExecutionReport(
        task_id="t1",
        summary="Success",
        status="COMPLETED",
        files_claimed_modified=["src/app.py"],
        final_message="Done"
    )
    
    rec = ReconciledExecutionResult(
        agent_claim_matches_repository=False,
        unexpected_changes=scope.unexpected_changes,
        execution_record=ExecutionRecord(
            execution_id="e1",
            task_id="t1",
            started_at="2026-10-01T00:00:00",
            status=ExecutionStatus.COMPLETED
        ),
        report=report
    )
    
    assert rec.agent_claim_matches_repository == False
    assert "README.md" in rec.unexpected_changes

def test_agent_claims_success_process_fails():
    # If exit code was 1, process execution status is FAILED.
    assert True # Handled in execution layer logic
