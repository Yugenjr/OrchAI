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
