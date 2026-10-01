# OrchAI Security Principles

Security is a primary concern for OrchAI. The system operates on the principle of least privilege and zero trust regarding agent execution.

## 1. Core Principles

- **Zero Trust Execution:** Never trust agent-generated success reports without independent verification.
- **Least Privilege:** Agents execute with minimal necessary context and permissions.
- **Human-in-the-Loop:** High-risk operations (e.g., production deployments, modifying secrets, dependency changes) require explicit human approval.
- **Distinct Trust Domains:** User intent, project content, agent instructions, system policies, and tool output are separate and must not override one another.

## 2. Threat Mitigation

### 2.1 Unauthorized File Modification
- **Mitigation:** The Policy Engine enforces `allowed_paths` and `forbidden_paths`. Any changes outside the expected surface are flagged, blocked, or require human approval.

### 2.2 Prompt Injection
- **Mitigation:** Strict separation of user prompt, file content, and system instructions. User prompts are treated as data, not executable system instructions.

### 2.3 Malicious MCP Tools / Shell Execution
- **Mitigation:** Shell commands proposed by agents are intercepted and evaluated by the Policy Engine. Destructive commands are blocked or require human consent.

### 2.4 Secret Exposure
- **Mitigation:** Hardcoded rules to prevent agents from reading or modifying common secret paths (e.g., `.env`, `secrets/`) unless explicitly authorized.

## 3. Execution Verification
All agent modifications are first staged. A Git diff is generated and analyzed against the task's expected change scope before changes are finalized.
