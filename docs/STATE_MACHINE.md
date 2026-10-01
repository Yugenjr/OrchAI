# OrchAI Task State Machine

## 1. Formal States

- `PENDING`: Task created, execution not started.
- `ANALYZING`: OrchAI gathering context and defining Expected Scope.
- `PLANNED`: Prompt compiled and plan ready.
- `AWAITING_APPROVAL`: Pre-execution human approval if required by policy.
- `EXECUTING`: Agent is running (Black box or streamed).
- `VERIFYING`: Post-execution observation and independent verification.
- `FAILED`: Terminal or pre-retry error state.
- `RETRYING`: Agent retrying task based on verification failure.
- `AWAITING_REVIEW`: Human review needed (e.g., due to scope deviation).
- `APPROVED`: Human approved the verified changes.
- `REJECTED`: Human rejected the changes.
- `ROLLED_BACK`: Changes reverted via Git due to rejection or policy failure.
- `COMPLETED`: Terminal success state.

## 2. Behaviors and Transitions

- **Valid Transitions:** `PENDING -> ANALYZING -> PLANNED -> EXECUTING -> VERIFYING -> COMPLETED`.
- **Invalid Transitions:** `COMPLETED -> EXECUTING`.
- **Terminal States:** `COMPLETED`, `FAILED`, `REJECTED`, `ROLLED_BACK`.
- **Retry Behavior:** From `VERIFYING` failure, transitions to `RETRYING`, then back to `EXECUTING`. Limited by max retries.
- **Rollback Behavior:** Triggers `git restore` to the pre-execution SHA. If successful, transitions to `ROLLED_BACK`. If rollback fails, transitions to `FAILED`.
- **Human Approval:** Can occur pre-execution (`AWAITING_APPROVAL`) or post-execution (`AWAITING_REVIEW`).
- **Git State:** Execution can only transition to `EXECUTING` if the Git working tree is clean.
