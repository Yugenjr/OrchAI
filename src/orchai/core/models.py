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
