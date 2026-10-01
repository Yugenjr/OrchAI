with open('docs/ARCHITECTURE.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
out = []
for i, line in enumerate(lines):
    if line.startswith('## 5.'):
        break
    out.append(line)
out.append("## 5. Antigravity Integration Architecture (Phase 4)\n\nOrchAI integrates with Antigravity using the official Python SDK (`google-antigravity`) as the primary mechanism, and the headless CLI as a fallback.\n\n**Integration Flow:**\nOrchAI -> Adapter -> Antigravity Runtime -> Tools -> Events -> OrchAI Verification\n\n**Key Distinctions:**\n- **Agent claim:** What the agent reports in its `AgentExecutionReport`.\n- **Observed change:** What Git evidence shows.\n- **Verified result:** The output of `ExecutionReconciler`, which flags deviations.\n\n**Security Boundaries:**\n- OrchAI handles: expected scope, repository snapshot, policy interpretation, independent Git observation, verification, reconciliation, and task state.\n- Antigravity handles: agent reasoning, tool execution, code generation, and execution according to configured policies (via SDK capabilities and hooks).\n\n## 6. Implementation Constraints\n- **AgentResult is untrusted**: The result returned by an agent is merely its claim and must be verified independently.\n- **Verification is independent**: The verification layer is fully decoupled from the agent execution layer.\n- **Git rollback is repository-level recovery**: It does not provide complete execution-level containment (e.g., database mutations or network requests cannot be rolled back via Git).\n- **ExecutionSandbox is an abstraction only**: It does not currently provide security isolation or Docker containerization.\n")
with open('docs/ARCHITECTURE.md', 'w', encoding='utf-8') as f:
    f.writelines(out)
