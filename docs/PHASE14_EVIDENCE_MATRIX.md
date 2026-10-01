# Phase 14 Evidence Matrix

| Capability | Test | Evidence | Status |
|---|---|---|---|
| READ | test_runtime_allowed_read | Process creation and stdout capture | RUNTIME_VERIFIED |
| WRITE | test_runtime_approved_write | Filesystem mutation verified | RUNTIME_VERIFIED |
| COMMAND_EXECUTION | test_runtime_approved_command | Subprocess exit code verified | RUNTIME_VERIFIED |
| TOOL_INTERCEPTION | test_denied_write_never_executes | Marker file absence verified | RUNTIME_VERIFIED |
| APPROVAL | test_approval_pauses_execution | Temporal block verified | RUNTIME_VERIFIED |
| CANCELLATION | test_long_running_process_cancel | Process termination verified | RUNTIME_VERIFIED |
| MCP_CONTROLLED_TOOL | test_full_governance_chain | End-to-end trace verified | RUNTIME_VERIFIED |
