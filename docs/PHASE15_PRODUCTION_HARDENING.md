# Phase 15: Production Hardening

## Overview
Phase 15 hardens the Controlled Reference Runtime against failures, adversarial inputs, and process crashes.

## 1. Execution Ledger
OrchAI now persists all execution events to a crash-safe `.orchai/ledger` directory using atomic file writes. Sensitive metadata is automatically redacted before persistence.

## 2. Failure Recovery
Tasks that are interrupted during execution (e.g. OrchAI crash) transition to `RECOVERY_REQUIRED` upon startup. OrchAI does not blindly restart commands; it safely requires developer intervention.

## 3. Process Hardening
The headless runtime enforces:
- `shell=False` execution.
- Configured working directory.
- Hard output size limits (1MB).
- Strict environment variables (`SystemRoot` and `SystemDrive` safely passed on Windows for networking/asyncio support).
- Process cancellation via `SIGKILL` equivalent to avoid orphan processes.
- Process timeout enforcement.

## 4. MCP Protocol Hardening
The stdio transport handles malformed JSON, payload size limits, and invalid RPC frames gracefully, keeping the main loop alive.

## 5. Approval Replay Prevention
Approvals are mathematically bound to the SHA-256 hash of the specific tool call payload.

## Limitations
This hardening applies strictly to the explicitly governed Reference Runtime. Native Antigravity IDE capabilities bypass this runtime and remain unsupported.
