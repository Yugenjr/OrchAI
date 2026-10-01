# Container Security Model

The OrchAI Container enforces zero-trust boundaries at the OS level:

1. **Non-Root Execution**: Runs entirely under the unprivileged `orchai` user.
2. **Deterministic Filesystem**: The `/app` directory is locked. `workspace` and `.orchai` state are explicitly mounted or managed.
3. **Network Isolation**: By default, the container runs without host network privileges.
4. **Environment Constraints**: Standard secrets (e.g. `GEMINI_API_KEY`) are intentionally prevented from polluting the global container scope unless explicitly passed via CLI overrides, preventing accidental logging.
5. **Resource Limits**: The `docker-compose.yml` sets explicit CPU and Memory ceilings.

## Tests
The security properties are verified by `tests/test_container_security.py` which guarantees non-root execution, filesystem boundaries, and proper isolation metrics.
