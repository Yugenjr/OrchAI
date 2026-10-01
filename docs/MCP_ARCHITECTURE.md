# MCP Architecture

OrchAI utilizes the Model Context Protocol (MCP) as an explicit tool gateway. 

## Flow
1. **Agent** connects via MCP Client.
2. **OrchAI MCP Gateway** intercepts request.
3. Maps tool to `ToolRegistration`.
4. Validates path boundaries and expected scopes.
5. Emits `MCP_POLICY_DECISION`.
6. Executes tool if ALLOW or APPROVE flow passes.
7. Emits `MCP_TOOL_EXECUTION` and returns `MCPToolResponse`.

## Caveats
MCP is a tool boundary. It does NOT automatically govern tools executed by the agent outside of the MCP connection (e.g., if the agent maintains its own internal `bash` session).
