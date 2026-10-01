# Tamper-Evident Audit Ledger

## Overview
As part of Phase 19, OrchAI has upgraded the Phase 15 `ExecutionLedger` into a cryptographically tamper-evident `AuditLedger`. This ensures that an AI agent or a malicious actor cannot retroactively modify the execution history or claim authorization that was never granted.

## Hash Chain
Every `StructuredEvent` maintains a strict sequence:
1. `previous_event_hash` points to the `event_hash` of the immediately preceding event.
2. `event_hash` is calculated via `SHA256` using the canonical JSON string of the event itself appended with the previous hash.

## Integrity Verification
If an event payload is modified, or if an event is deleted/reordered, the subsequent `previous_event_hash` references will break, and `orchai audit verify <task_id>` will report an `AuditLedgerError`.

## Secrets Management
Audit ledgers only contain correlation IDs and semantic actions. Credentials and payloads explicitly exclude raw token values, ensuring the ledger is safe for SIEM ingestion.
