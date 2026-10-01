# OrchAI MVP Boundary

This document defines exactly what V0.1 (MVP) will and will not implement.

## Included in MVP (V0.1)
- Local CLI
- Project initialization
- Project context extraction
- Task creation
- State machine (Implementation of states defined in `STATE_MACHINE.md`)
- Prompt compilation
- Agent adapter abstraction
- First Antigravity integration
- Basic policy engine (Allow/Deny on paths)
- Git observation (Determining Actual Change Scope)
- Verification (Running tests)
- Human approval (CLI prompts)
- Rollback (via Git)
- Structured execution reports

## Deferred (NOT in MVP)
- Arbitrary tool/command interception mid-flight (MVP relies on post-execution verification and rollback).
- Real-time event streaming.
- Multi-agent orchestration.
- Advanced context/token optimization algorithms.
- Persistent engineering memory database.
- Web dashboard or UI.
- ChatGPT/Web integration.
- Cloud/SaaS deployment.
- Enterprise RBAC.
- CI/CD integration.
- Issue tracker integrations (Jira, Linear, GitHub).


## Phase 5 Runtime Validation Note
As of Phase 5, real-time tool execution interception (e.g. blocking a command before it runs) remains UNPROVEN against the live Antigravity runtime due to missing authentication credentials during test execution. Therefore, OrchAI strictly enforces a Zero-Trust black-box boundary: the agent is NOT trusted during execution, and all validation occurs via POST-EXECUTION Git observation and reconciliation.


## Phase 6: Engineering Memory & Review Loop
OrchAI implements persistent Engineering Memory backed by a MemoryStore inside .orchai/memory/. 
Memory entries capture architecture decisions, constraints, and developer feedback with distinct MemoryProvenance. 
Agent-originated memories remain untrusted CANDIDATE memory until verified by human review. 
Memory conflicts (e.g. conflicting db decisions) enter a CONFLICT state for developer resolution.

The Review Loop introduces the AWAITING_REVIEW and CHANGES_REQUESTED states, decoupled from pre-execution approval. 
Tasks now track execution iterations via an Attempt History, preserving previous AgentResult, VerificationResult, and developer feedback.
