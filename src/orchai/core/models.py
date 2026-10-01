from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AgentCapabilityType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    COMMAND_EXECUTION = "COMMAND_EXECUTION"
    DEPENDENCY_CHANGE = "DEPENDENCY_CHANGE"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    DATABASE_CHANGE = "DATABASE_CHANGE"
    SECRET_ACCESS = "SECRET_ACCESS"
    DEPLOYMENT = "DEPLOYMENT"
    DESTRUCTIVE_OPERATION = "DESTRUCTIVE_OPERATION"

class AgentCapability(BaseModel):
    type: AgentCapabilityType
    description: str
    risk_level: int

class TaskState(str, Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    PLANNED = "PLANNED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    READY_FOR_EXECUTION = "READY_FOR_EXECUTION"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"
    COMPLETED = "COMPLETED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    CANCELLED = "CANCELLED"

class RepositorySnapshot(BaseModel):
    head_sha: str
    branch: str
    tracked_files: List[str]
    staged_files: List[str] = Field(default_factory=list)
    unstaged_files: List[str] = Field(default_factory=list)
    untracked_files: List[str] = Field(default_factory=list)
    working_tree_clean: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: TaskState = TaskState.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Ownership (Phase 20)
    tenant_id: Optional[str] = None
    created_by: Optional[str] = None

    expected_scope: List[str] = Field(default_factory=list)
    risk_level: int = 0
    approval_required: bool = False
    pre_execution_snapshot: Optional[RepositorySnapshot] = None

class TaskRequest(BaseModel):
    task_id: str
    objective: str
    constraints: List[str] = Field(default_factory=list)
    expected_scope: List[str] = Field(default_factory=list)

class AgentActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    RUN_COMMAND = "RUN_COMMAND"

class AgentAction(BaseModel):
    action_type: AgentActionType
    target: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentEventType(str, Enum):
    TASK_STARTED = "TASK_STARTED"
    FILE_READ = "FILE_READ"
    FILE_CREATED = "FILE_CREATED"
    FILE_MODIFIED = "FILE_MODIFIED"
    FILE_DELETED = "FILE_DELETED"
    COMMAND_REQUESTED = "COMMAND_REQUESTED"
    COMMAND_STARTED = "COMMAND_STARTED"
    COMMAND_COMPLETED = "COMMAND_COMPLETED"
    DEPENDENCY_CHANGED = "DEPENDENCY_CHANGED"
    TEST_STARTED = "TEST_STARTED"
    TEST_COMPLETED = "TEST_COMPLETED"
    AGENT_MESSAGE = "AGENT_MESSAGE"
    AGENT_ERROR = "AGENT_ERROR"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    COMMAND_DENIED = "COMMAND_DENIED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    FILE_OPERATION = "FILE_OPERATION"
    TOOL_ERROR = "TOOL_ERROR"

class AgentEvent(BaseModel):
    event_type: AgentEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    target: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class AgentResult(BaseModel):
    success: bool
    summary: str
    events: List[AgentEvent] = Field(default_factory=list)
    error: Optional[str] = None
    files_changed: List[str] = Field(default_factory=list)

class PolicyDecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ALLOW_WITH_CONSTRAINTS = "ALLOW_WITH_CONSTRAINTS"

class PolicyDecision(BaseModel):
    decision: PolicyDecisionType
    reason: str
    policy_identifier: Optional[str] = None

class VerificationResult(BaseModel):
    passed: bool
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    unexpected_changes: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    summary: str

class ExecutionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ScopeComparisonResult(BaseModel):
    expected_files: List[str]
    actual_files: List[str]
    unexpected_changes: List[str]
    missing_expected_changes: List[str]
    compliant: bool

class ExecutionRecord(BaseModel):
    execution_id: str
    task_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    pre_execution_snapshot: Optional[RepositorySnapshot] = None
    post_execution_snapshot: Optional[RepositorySnapshot] = None
    changed_files: List[str] = Field(default_factory=list)
    scope_result: Optional[ScopeComparisonResult] = None
    status: ExecutionStatus = ExecutionStatus.NOT_STARTED
    runtime: Optional[str] = None
    adapter: Optional[str] = None
    external_session_id: Optional[str] = None
    events_observed: int = 0
    policy_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    approval_events: List[Dict[str, Any]] = Field(default_factory=list)
    verification_result: Optional[VerificationResult] = None

class SecurityAuditEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    task_id: str
    execution_id: str
    event: str
    capability: Optional[str] = None
    decision: Optional[str] = None

class AgentExecutionReport(BaseModel):
    task_id: str
    summary: str
    status: str
    actions_attempted: int = 0
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    files_claimed_modified: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    final_message: str

class ReconciledExecutionResult(BaseModel):
    agent_claim_matches_repository: bool
    unexpected_changes: List[str] = Field(default_factory=list)
    execution_record: ExecutionRecord
    report: AgentExecutionReport

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
    attempt_id: str
    task_id: str
    attempt_number: int
    session_id: str
    execution_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    objective: str
    developer_feedback: Optional[str] = None
    agent_result: Optional[AgentExecutionReport] = None
    verification_result: Optional[VerificationResult] = None
    reconciliation_result: Optional[ReconciledExecutionResult] = None
    review_result: Optional[str] = None


class AgentSessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

class AgentSession(BaseModel):
    id: str
    task_id: str
    adapter: str
    runtime: str
    external_session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: AgentSessionStatus = AgentSessionStatus.ACTIVE
    attempt_ids: List[str] = Field(default_factory=list)

class DeveloperFeedback(BaseModel):
    id: str
    task_id: str
    attempt_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CapabilityStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    MOCK_VERIFIED = "MOCK_VERIFIED"
    RUNTIME_VERIFIED = "RUNTIME_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    UNSUPPORTED = "UNSUPPORTED"
    BLOCKED = "BLOCKED"

class RuntimeCapability(BaseModel):
    name: str
    status: CapabilityStatus
    source: str
    verified_at: Optional[datetime] = None
    evidence: Optional[str] = None
    limitations: Optional[str] = None

class AuthenticationConfig(BaseModel):
    provider: str
    runtime: str
    credential_source: str
    configured: bool
    validated: bool
    last_validated_at: Optional[datetime] = None
    
    # Never persist secrets. Only metadata.
    
class RuntimeTestResult(BaseModel):
    test_id: str
    test_name: str
    status: CapabilityStatus
    runtime: str
    adapter: str
    authentication_status: str
    before_sha: Optional[str] = None
    after_sha: Optional[str] = None
    expected_scope: List[str] = Field(default_factory=list)
    actual_scope: List[str] = Field(default_factory=list)
    agent_claim: Optional[str] = None
    events: List[AgentEvent] = Field(default_factory=list)
    verification: Optional[VerificationResult] = None
    reconciliation: Optional[ReconciledExecutionResult] = None
    evidence: Optional[str] = None
    limitations: Optional[str] = None
