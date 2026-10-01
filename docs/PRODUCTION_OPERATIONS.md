# Production Operations

## API Endpoints for Operations
The API Gateway exposes operations endpoints on standard HTTP paths for easy ingestion:

- `GET /health`: Returns 200 OK. Confirms process vitality.
- `GET /ready`: Returns 200 OK if underlying TaskRepository and AuditLedger boundaries are responsive and initialized. 503 if blocked.
- `GET /metrics`: Emits standard Prometheus format metrics detailing tasks, counters, tool attempts, and latency.

## CLI for SREs
The `orchai` CLI features operational diagnostics:
- `orchai metrics`: Standard-out rendering of telemetry.
- `orchai health`: Fast vitality check.
- `orchai readiness`: Dependency availability.
- `orchai audit task <id>`: JSON-based extraction of task telemetry.
- `orchai audit verify <id>`: Immediate cryptology validation of an execution chain.

## Limitations
Native Antigravity IDE execution is NOT governed by OrchAI unless the host explicitly routes execution through OrchAI.
Controlled Reference Runtime remains RUNTIME_VERIFIED.
Controlled Container Runtime remains RUNTIME_VERIFIED only where actual container execution has been proven.
