# OrchAI Security Principles

## 1. Trust Boundaries
- **TRUSTED:** Developer, OrchAI Core, Policy Configuration.
- **CONDITIONALLY TRUSTED:** Agent Adapters, Git, Local Verification Tools.
- **UNTRUSTED:** Coding Agent Output, Repository Content, Generated Code, External Tool Output, External Network Content.

*Crucial:* Repository content is treated as DATA, not as trusted OrchAI instructions.

### Security Boundary

UNTRUSTED AGENT
       |
       v
MCP TRANSPORT
       |
       v
ORCHAI POLICY
       |
       +--> DENY
       |
       +--> REQUIRE_APPROVAL
       |
       +--> ALLOW
              |
              v
        CONTROLLED TOOL

Git Observation
       |
       v
Independent Verification

Antigravity IDE native tools: NOT CONTROLLED BY ORCHAI
Reference Runtime: CONTROLLED BY ORCHAI

## 2. Agent Capabilities
Agent actions are classified into capabilities:
- `READ`, `WRITE`
- `COMMAND_EXECUTION`
- `DEPENDENCY_CHANGE`
- `CONFIGURATION_CHANGE`
- `DATABASE_CHANGE`
- `SECRET_ACCESS`
- `DEPLOYMENT`
- `DESTRUCTIVE_OPERATION`

## 3. Policy Decisions
Policies map capabilities to decisions:
- **ALLOW:** Action proceeds automatically (e.g., `WRITE src/auth/login.py`).
- **DENY:** Action is blocked or rolled back (e.g., `WRITE .env`).
- **REQUIRE_APPROVAL:** Human intervention required before proceeding (e.g., `RUN pip install package`).
- **ALLOW_WITH_CONSTRAINTS:** e.g., allow `READ` up to 10 files.

## 4. Enforcement via Change Scope Observation
Security is enforced by comparing the Expected Scope (determined pre-execution) with the Actual Scope (observed post-execution via Git). Deviations are treated as security events that trigger warnings, approval requests, or automatic rollbacks.


## Phase 5 Runtime Validation Note
As of Phase 5, real-time tool execution interception (e.g. blocking a command before it runs) remains UNPROVEN against the live Antigravity runtime due to missing authentication credentials during test execution. Therefore, OrchAI strictly enforces a Zero-Trust black-box boundary: the agent is NOT trusted during execution, and all validation occurs via POST-EXECUTION Git observation and reconciliation.


## Phase 6: Engineering Memory & Review Loop
OrchAI implements persistent Engineering Memory backed by a MemoryStore inside .orchai/memory/. 
Memory entries capture architecture decisions, constraints, and developer feedback with distinct MemoryProvenance. 
Agent-originated memories remain untrusted CANDIDATE memory until verified by human review. 
Memory conflicts (e.g. conflicting db decisions) enter a CONFLICT state for developer resolution.

The Review Loop introduces the AWAITING_REVIEW and CHANGES_REQUESTED states, decoupled from pre-execution approval. 
Tasks now track execution iterations via an Attempt History, preserving previous AgentResult, VerificationResult, and developer feedback.
