# OrchAI Threat Model

## 1. Threat Analysis & Mitigations

- **Prompt Injection:** Mitigated by treating repository content as untrusted data. User intent and system policies are isolated from file content.
- **Malicious Repository Instructions:** Repo content is never executed as OrchAI instructions.
- **Command Injection:** If interception is available, commands are sanitized. If not, OrchAI relies on post-execution verification and rollback.
- **Secret Exposure:** Policy explicitly `DENY`s `READ`/`WRITE` access to `.env` and `secrets/`.
- **Malicious Dependencies:** `DEPENDENCY_CHANGE` capability defaults to `REQUIRE_APPROVAL`.
- **Unrestricted Shell Access:** Handled by integration constraints or post-execution rollback.
- **Agent Privilege Escalation:** Agents run with minimal OS privileges.
- **Malicious External Tool Output:** Tool output is parsed safely, not evaluated or executed.
- **MCP Tool Abuse:** MCP tools respect OrchAI policies.
- **Accidental Destructive Commands:** Post-execution Git rollback restores state if interception fails.

## 2. Failure Modes

- **Agent crashes / times out:** Adapter reports failure, state moves to `FAILED` or `RETRYING`.
- **Malformed agent response:** Adapter falls back to Git observation to determine state.
- **Unexpected file modification:** Detected by Actual Scope deviation; state moves to `AWAITING_REVIEW` or `ROLLED_BACK`.
- **Test failure:** State moves to `RETRYING` or `FAILED`.
- **Policy denial:** State moves to `REJECTED` or `ROLLED_BACK`.
- **Human rejection:** State moves to `REJECTED` or `ROLLED_BACK`.
- **Verification failure:** State moves to `FAILED` or `RETRYING`.
- **Dirty Git state before execution:** OrchAI refuses to execute.
- **Rollback failure:** Terminal state `FAILED`, requires manual human intervention.
- **Adapter unavailable:** State moves to `FAILED`.
