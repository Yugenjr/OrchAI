# OrchAI Agent Protocol

## 1. Conceptual Agent Adapter Contract

The `AgentAdapter` handles communication between OrchAI and external agents. It does NOT assume interception is possible natively.

```python
class AgentAdapter:
    def initialize(self)
    def capabilities(self) -> List[AgentCapability]
    def prepare_task(self, request: TaskRequest, context: TaskContext)
    def execute(self) -> AgentResult
    def stream_events(self) -> Iterator[AgentEvent]
    def collect_result(self) -> AgentResult
    def cancel(self)
    def health_check(self)
```

## 2. Conceptual Pydantic Models
- `TaskRequest`
- `TaskContext`
- `AgentCapability`
- `AgentAction`
- `AgentEvent`
- `AgentResult`
- `VerificationResult`
- `PolicyDecision`

## 3. Event Model

Events represent agent activity. OrchAI classifies them based on observability and security:
- `TASK_STARTED`, `TASK_COMPLETED`, `TASK_FAILED`: Observable.
- `FILE_READ`, `FILE_CREATED`, `FILE_MODIFIED`, `FILE_DELETED`: Observable (Post-execution via Git).
- `COMMAND_REQUESTED`, `COMMAND_STARTED`, `COMMAND_COMPLETED`: Interceptable (INTEGRATION-DEPENDENT).
- `DEPENDENCY_CHANGED`, `TEST_STARTED`, `TEST_COMPLETED`: Interceptable (INTEGRATION-DEPENDENT).
- `AGENT_MESSAGE`, `AGENT_ERROR`: Observable.

*Note on Interception:* OrchAI never claims interception (e.g., blocking a `COMMAND_STARTED` event mid-flight) unless the underlying integration explicitly guarantees it.


## Phase 5 Runtime Validation Note
As of Phase 5, real-time tool execution interception (e.g. blocking a command before it runs) remains UNPROVEN against the live Antigravity runtime due to missing authentication credentials during test execution. Therefore, OrchAI strictly enforces a Zero-Trust black-box boundary: the agent is NOT trusted during execution, and all validation occurs via POST-EXECUTION Git observation and reconciliation.


## Phase 6: Engineering Memory & Review Loop
OrchAI implements persistent Engineering Memory backed by a MemoryStore inside .orchai/memory/. 
Memory entries capture architecture decisions, constraints, and developer feedback with distinct MemoryProvenance. 
Agent-originated memories remain untrusted CANDIDATE memory until verified by human review. 
Memory conflicts (e.g. conflicting db decisions) enter a CONFLICT state for developer resolution.

The Review Loop introduces the AWAITING_REVIEW and CHANGES_REQUESTED states, decoupled from pre-execution approval. 
Tasks now track execution iterations via an Attempt History, preserving previous AgentResult, VerificationResult, and developer feedback.
