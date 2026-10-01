# OrchAI Context

**Product Name:** OrchAI
**Tagline:** "The orchestration layer for AI coding agents."
**Core Principle:** "Agents execute. OrchAI orchestrates. Humans authorize."

OrchAI is a repository-aware, policy-aware, context-aware orchestration and governance layer for AI coding agents. It is NOT another coding agent, but a control plane that coordinates agents to perform software-engineering tasks.

## Core Problem
The current workflow involving AI systems involves manual copy-pasting, context loss, high token consumption, lack of execution governance, independent verification, and persistent memory.

## Core Vision
OrchAI provides a continuous pipeline:
Human Intent → Project Understanding → Task Planning → Context Selection → Prompt Compilation → Policy Validation → Agent Execution → Action Monitoring → Code Verification → Human Approval → Git / CI → Engineering Memory

## Key Features
1. **Persistent Project Context Engine:** Retrieves task-specific context instead of sending the entire repository.
2. **Bidirectional Agent Communication:** Consumes structured execution reports from agents to update project state.
3. **Prompt Compiler:** Transforms natural language requests into structured implementation tasks with constraints and validation requirements.
4. **Context and Token Optimization:** Minimizes context via compression, selection, and caching.
5. **Codebase Governance:** Policy engine to control agent permissions (allowed/forbidden paths, required approvals).
6. **Intent vs Actual Change Analysis:** Detects deviations between expected and actual change surfaces.
7. **Agent Action Monitoring:** Observes and logs agent execution traces.
8. **Independent Verification Engine:** Independently verifies results via git diff, linting, testing, etc.
9. **Risk-Based Human-in-the-Loop:** Requires human approval for high-risk operations based on policy.
10. **Agent Cost and Resource Controller:** Configurable limits for tokens, tool calls, retries, time, etc.
11. **Checkpoints, Recovery and Rollback:** Uses Git for pre-execution checkpoints and recovery.
12. **Task State Machine:** Explicit lifecycle states for tasks.
13. **Multi-Agent Orchestration (Future):** Supports specialized agents (Planner, Coder, Reviewer, etc.).
14. **Agent-Agnostic Adapter Layer:** Core engine abstracts agent-specific details.
15. **Engineering Memory:** Remembers project-level decisions and constraints.
16. **Explainability:** Provides reasoning for agent actions and file modifications.
17. **Agent Execution Analytics:** Exposes metrics on agent performance and behavior.
18. **Execution Learning:** Uses past results to improve future tasks.

## MVP Scope
- Local CLI
- Project context
- Task management
- Prompt compilation
- Antigravity integration/adapter
- Git diff inspection
- Basic policy engine
- Human approval gate
- Verification
- Execution report
- Task state tracking
- Basic rollback

## Architectural Principles
- Agent-agnostic core
- Local-first development
- Security by default
- Human control for high-risk operations
- Least-privilege agent execution
- Observable execution and independent verification
- Minimal context transfer and dependencies
