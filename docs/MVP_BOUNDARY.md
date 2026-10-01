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
