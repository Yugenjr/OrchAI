# OrchAI Context

**Product Name:** OrchAI
**Tagline:** "The orchestration layer for AI coding agents."
**Core Principle:** "Agents execute. OrchAI orchestrates. Humans authorize."

OrchAI is a repository-aware, policy-aware, context-aware orchestration and governance layer for AI coding agents.

## Architectural Separation of Concerns
OrchAI explicitly separates capabilities into four distinct phases. It does NOT assume it can intercept arbitrary internal operations of coding agents like Antigravity. 

1. **PRE-EXECUTION GOVERNANCE:** Planning, context preparation, intent compilation, policy validation, and establishing the Expected Change Scope.
2. **EXECUTION / INTERCEPTION:** The actual running of the agent. Interception (e.g., stopping a tool mid-flight) is strictly INTEGRATION-DEPENDENT.
3. **POST-EXECUTION OBSERVATION:** Examining Git status, file system changes, and determining the Actual Change Scope.
4. **INDEPENDENT VERIFICATION:** Running tests, linters, and verifying against the policy independent of what the agent reported.

## Core Capabilities Classification
- **Pre-execution Policy Checks:** AVAILABLE
- **Git Diff Observation:** AVAILABLE
- **Post-execution Verification:** AVAILABLE
- **Agent Output Parsing:** AVAILABLE
- **Arbitrary Internal Tool Interception (Antigravity):** UNKNOWN / INTEGRATION-DEPENDENT
- **Real-time Event Streaming:** INTEGRATION-DEPENDENT
- **Multi-agent Hand-offs:** FUTURE

## Expected vs Actual Change Scope
- **Expected Change Scope:** Established BEFORE execution based on the task intent and policy (e.g., `src/auth/**`).
- **Actual Change Scope:** Determined AFTER execution through Git observation.
OrchAI detects deviations between these scopes and triggers human approval or rollbacks.
