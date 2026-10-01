# OrchAI Agent Protocol

This document defines the expected interface and communication protocol between OrchAI and external coding agents.

## 1. Concept

OrchAI acts as the orchestrator, and coding agents act as executors. To avoid manual parsing of arbitrary text, agents are expected to communicate back to OrchAI using structured reports.

## 2. The Input: Compiled Prompt

OrchAI sends a compiled, structured JSON prompt to the agent (either directly via API or via system prompt configuration).

```json
{
  "task_id": "tsk_12345",
  "objective": "Implement JWT authentication",
  "allowed_paths": ["src/auth/**", "tests/auth/**"],
  "forbidden_paths": ["src/frontend/**", ".env"],
  "context": {
    "files": ["src/models/user.py"],
    "memory": ["Do not use Redis."]
  },
  "validation_requirements": ["pytest tests/auth"]
}
```

## 3. The Output: Structured Execution Report

When the agent finishes its execution, it MUST output a structured report in a parseable format (e.g., JSON inside a specific markdown block).

```json
{
  "task_id": "tsk_12345",
  "status": "COMPLETED",
  "metrics": {
    "files_read": 3,
    "files_modified": 2,
    "files_created": 1,
    "files_deleted": 0,
    "commands_executed": 2
  },
  "actions": [
    {
      "type": "modify",
      "path": "src/auth/jwt.py"
    },
    {
      "type": "run_command",
      "command": "pytest tests/auth",
      "result": "success"
    }
  ],
  "deviations": [],
  "next_suggested_action": null
}
```

## 4. Adapter Responsibility

The `AgentAdapter` in OrchAI is responsible for translating OrchAI's internal state into the agent's expected input format, and parsing the agent's output back into OrchAI's structured state. If an agent fails to provide a structured report, the adapter must fallback to Git diff analysis to reconstruct the execution report.
