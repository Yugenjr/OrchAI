import pytest
from orchai.core.state import TaskStateMachine, InvalidStateTransitionError
from orchai.core.models import TaskState, TaskAttempt

def test_review_state_transitions():
    sm = TaskStateMachine()
    
    # EXECUTING -> VERIFYING -> AWAITING_REVIEW
    sm.validate_transition(TaskState.EXECUTING, TaskState.VERIFYING)
    sm.validate_transition(TaskState.VERIFYING, TaskState.AWAITING_REVIEW)
    
    # AWAITING_REVIEW -> CHANGES_REQUESTED
    sm.validate_transition(TaskState.AWAITING_REVIEW, TaskState.CHANGES_REQUESTED)
    
    # CHANGES_REQUESTED -> EXECUTING (Attempt 2)
    sm.validate_transition(TaskState.CHANGES_REQUESTED, TaskState.EXECUTING)
    
    # EXECUTING -> VERIFYING -> AWAITING_REVIEW -> APPROVED -> COMPLETED
    sm.validate_transition(TaskState.AWAITING_REVIEW, TaskState.APPROVED)
    
def test_review_state_invalid_transition():
    sm = TaskStateMachine()
    with pytest.raises(InvalidStateTransitionError):
        sm.validate_transition(TaskState.AWAITING_REVIEW, TaskState.COMPLETED)

def test_developer_feedback_transition():
    sm = TaskStateMachine()
    # Changes requested allows returning to READY_FOR_EXECUTION
    sm.validate_transition(TaskState.CHANGES_REQUESTED, TaskState.READY_FOR_EXECUTION)

def test_attempt_history_structure():
    attempt1 = TaskAttempt(attempt_id="att_1", task_id="t1", session_id="s1", objective="O", attempt_number=1, execution_id="exec_1", review_result="CHANGES_REQUESTED")
    attempt2 = TaskAttempt(attempt_id="att_2", task_id="t1", session_id="s1", objective="O", attempt_number=2, execution_id="exec_2", review_result="APPROVED")
    
    history = [attempt1, attempt2]
    assert len(history) == 2
    assert history[0].attempt_number == 1
    assert history[1].review_result == "APPROVED"

def test_execution_history_retained():
    # Verify execution records are distinct
    assert TaskAttempt(attempt_id="a1", task_id="t1", session_id="s1", objective="O", attempt_number=1, execution_id="e1").execution_id != TaskAttempt(attempt_id="a2", task_id="t1", session_id="s1", objective="O", attempt_number=2, execution_id="e2").execution_id

def test_reconciliation_history_integration():
    from orchai.core.reconciler import ExecutionReconciler
    from orchai.core.models import AgentExecutionReport, VerificationResult, ExecutionRecord, ReconciledExecutionResult
    
    report = AgentExecutionReport(task_id="t1", summary="s", status="c", final_message="fm")
    verification = VerificationResult(passed=True, summary="ok")
    record = ExecutionRecord(execution_id="exec_1", task_id="t1", started_at="2024-01-01T00:00:00Z")
    
    result = ExecutionReconciler().reconcile(report, [], verification, record)
    assert result.agent_claim_matches_repository is True
    
    attempt = TaskAttempt(attempt_id="att_1", task_id="t1", session_id="s1", objective="O", attempt_number=1, execution_id="exec_1", verification_result=verification)
    assert attempt.verification_result.passed is True
