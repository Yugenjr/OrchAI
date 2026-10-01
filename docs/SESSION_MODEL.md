# OrchAI Session Model

This document outlines the multi-turn session persistence and attempt history structures.

## Core Entities
- **Task**: The persistent, high-level goal (`Task` model).
- **Execution Attempt**: A distinct effort to execute the Task (`TaskAttempt` model). An attempt holds its own verification, agent claims, and developer feedback.
- **Agent Session**: The external connection to the execution runtime (`AgentSession` model). It tracks `external_session_id`.

## Resumption & Feedback
If a Task goes to `AWAITING_REVIEW` and a developer requests changes, it enters `CHANGES_REQUESTED`.
During resumption (`orchai task resume`), a new attempt is spun up.
The `OrchAIContextCompiler` binds previous attempt feedback, failed verifications, and memory configurations into the system prompt.

## Capability Checks
Adapters implement `supports_session_resume()`. If the native adapter (e.g., Antigravity SDK) cannot resume a given conversation ID, OrchAI will launch a **new session** while injecting the historic attempt contexts manually. 
