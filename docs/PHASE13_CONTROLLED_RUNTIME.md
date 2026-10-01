# Phase 13: Controlled Headless Agent Runtime

## Architectural Shift
The native Antigravity IDE agent cannot be governed from inside the OrchAI Python runtime. The Antigravity IDE executes tools like `write_to_file` and `run_command` natively, bypassing any Python-based MCP hooks OrchAI attempts to install. 
Therefore, OrchAI's architecture transitions from attempting to "wrap" the IDE host agent to explicitly orchestrating a **Controlled Headless Runtime** through a mechanically enforced MCP gateway.

## Reference Runtime
Because the official headless `google-antigravity` SDK remains unprovisioned, Phase 13 introduces a deterministic `Reference Agent`. This is not an LLM. It is a strictly conformant JSON-RPC protocol agent used to prove the end-to-end governance of OrchAI's transport and policy layers.

## MCP Control Boundary
The boundary is now mechanically enforced:
1. OrchAI spawns the agent process using `asyncio.create_subprocess_exec`, forcing `shell=False`.
2. Stdin/Stdout pipes are captured and routed exclusively through the `StdioTransport`.
3. The agent has no native capabilities. It MUST send a JSON-RPC `tools/call` message.
4. The `MCPServer` routes the request to the `MCPGateway`.
5. The `PolicyBridge` evaluates the tool against the task constraints (e.g. `REQUIRE_APPROVAL`).

## Command Confinement
Any `orchai.run_command` request must contain a structured `argv` list. `shell=True` is prohibited in the runtime manager. Execution timeouts and working directory confinements are enforced at the process level.

## Git Post-Execution Verification
Even if a headless agent escapes confinement, OrchAI maintains the Git observation loop. A Git snapshot is taken before the runtime starts, and observed after completion to reconcile the expected vs. actual scope changes.

## Verification Statuses
- **REFERENCE_RUNTIME_CONTROL**: Verified mechanically via integration tests against the reference agent.
- **ANTIGRAVITY_NATIVE_TOOLS**: Remain strictly UNCONTROLLED and UNVERIFIED.
