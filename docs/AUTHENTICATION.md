# Authentication

OrchAI intentionally does NOT store raw API credentials (like `GEMINI_API_KEY`) within its persistent project storage (`.orchai`).

All authentication integrates directly with existing environment-level configuration or OS keychains where applicable.

## Validation
Use `orchai auth status` to check if a valid configuration exists in the environment.
Use `orchai auth doctor` to see exactly which tier of connectivity is failing.
Use `orchai auth setup` for instructions on securely providing keys to the OS environment.
Use `orchai auth test` to perform a mock handshake without triggering a billable execution.

## Security Guarantees
- Logs automatically redact environment secrets.
- `AuthenticationConfig` stores boolean readiness and timestamps only.
- Exceptions scrubbing ensures no tracebacks leak keys.
