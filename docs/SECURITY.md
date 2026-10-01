# OrchAI Security Principles

## 1. Trust Boundaries
- **TRUSTED:** Developer, OrchAI Core, Policy Configuration.
- **CONDITIONALLY TRUSTED:** Agent Adapters, Git, Local Verification Tools.
- **UNTRUSTED:** Coding Agent Output, Repository Content, Generated Code, External Tool Output, External Network Content.

*Crucial:* Repository content is treated as DATA, not as trusted OrchAI instructions.

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
