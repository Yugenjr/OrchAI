# Phase 12 Runtime Discovery

## Environment
- Python version: 3.13.9
- Operating system: Windows
- Executable PATH: Python path active, but no `agy` executable found in path.

## Installed Packages
The full `pip list` confirmed that official packages for:
- `google-antigravity`
- `mcp` (or similar)
are **MISSING**.

## Executables
- `agy` CLI is **MISSING**.

## Environment Configuration
There are no configuration directories (`.antigravity`, etc.) clearly associated with the runtime locally.

## Authentication Surface
`GEMINI_API_KEY` was assumed in earlier phases but its validity as the primary authentication mechanism for the Antigravity SDK is **UNKNOWN**. 
The SDK might use OAuth, a local configuration file, or another token mechanism. We cannot prove this until the package exists.

## MCP Surface
Official MCP servers and configuration structures are **UNKNOWN** in the context of the external runtime. OrchAI's internal MCP gateway is functional, but whether Antigravity can connect to it is unproven.

## Agent Runtime Surface
The core Agent APIs (Agent, Session, Capability) are completely **MISSING**.

## Unknowns
- How Antigravity SDK handles tool interception.
- The actual Python class structure for `google.antigravity.Agent`.
- Session resumption mechanisms and identifiers.
- Official tool namespace naming conventions.

## Evidence
`pip list` returned zero results for `google-antigravity`.

## Security Notes
Subprocess usage in the CLI adapter (e.g. `subprocess.run(["agy", ...])`) correctly avoided `shell=True`, preventing basic command injections. Future connections must continue to structure arguments directly.

## Adapter API Assumptions (src/orchai/adapters/antigravity.py)
| API | Source | Installed? | Verified? | Evidence |
|---|---|---|---|---|
| `Agent` | `google.antigravity` | NO | NO | Assumed context manager behavior (`async with Agent(...)`). |
| `LocalAgentConfig` | `google.antigravity` | NO | NO | Speculative configuration struct. |
| `CapabilitiesConfig` | `google.antigravity` | NO | NO | Speculative capabilities struct. |
| `Agent.chat()` | `google.antigravity` | NO | NO | Speculative method for passing objectives. |
| `response.tool_calls` | `google.antigravity` | NO | NO | Speculative streaming interface for interception. |
| `agy` | CLI | NO | NO | Headless command line execution structure assumed. |

## Recommended Next Integration Step
We must **WAIT** for the official `google-antigravity` SDK and CLI to be published or provisioned before moving to Phase 13. OrchAI is now structurally hardened to accept it.
