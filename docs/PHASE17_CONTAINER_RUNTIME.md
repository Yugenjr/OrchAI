# Phase 17: Containerized Controlled Runtime

## Overview
Phase 17 successfully encapsulates the verified Headless Reference Runtime into a strict Docker boundary. The container is a security boundary enforcing non-root execution, explicit filesystem paths, network isolation, and strict process limits.

## Architecture
```
Host
  ↓
Docker Container (Non-Root)
  ↓
OrchAI (python -m orchai)
  ↓
MCP Gateway
  ↓
Controlled Runtime -> Subprocess
```

## Security Boundaries
1. **Network**: Container uses `network_mode: "none"` where appropriate.
2. **Filesystem**: Reads and writes are isolated to `/app/workspace` and `/app/.orchai`. No host escapes are possible.
3. **Execution**: Processes execute under a dedicated `orchai` non-root user. Shell injection and path traversal tests from Phase 14 carry over and pass inside the container.

## Known Limitations
Docker is required for deployment and executing container tests. The runtime cannot natively govern the Antigravity IDE agent. Container limits augment, but do not replace, the strict timeout and process management implemented in OrchAI's state machine.
