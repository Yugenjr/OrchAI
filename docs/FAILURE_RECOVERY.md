# OrchAI Failure Recovery Guide

## Philosophy
When the system encounters a hard crash or process termination, OrchAI favors explicit manual recovery over silent arbitrary retries. The goal is to prevent duplicate side effects, corrupted state, and runaway background processes.

## The Execution Ledger
The `ExecutionLedger` (`.orchai/ledger/`) persists atomic, crash-safe records of all tool execution events. 
- If OrchAI terminates mid-execution, the ledger contains the last known state.
- Sensitive information is strictly redacted before writing to disk.

## Stale Executions & the Recovery State
Upon startup or initialization, the `RecoveryManager` scans the `TaskRepository` for tasks in the `EXECUTING` state. 
Since OrchAI lost its tracking context during the crash, these tasks are marked as **`RECOVERY_REQUIRED`**.

### Handling RECOVERY_REQUIRED
A task in `RECOVERY_REQUIRED` cannot be automatically resumed. The developer must inspect the physical side effects (via Git) and explicitly reset the task state (e.g. back to `READY_FOR_EXECUTION` or `FAILED`).

## Process Termination
When an execution times out or is cancelled, the `AgentRuntime` guarantees the underlying subprocess is terminated via `SIGKILL` (or OS equivalent), avoiding orphan processes from escaping the governance boundary.
