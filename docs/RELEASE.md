# Release Process

This document outlines the deterministic release verification process for OrchAI.

## 1. Release Validation Script
Before every release, you must execute the integration release script:

```bash
python scripts/release_validation.py
```

### Steps Executed
1. **Test Execution**: Validates all tests in an isolated manner.
2. **Build**: Packages source distributions and wheels via `build`.
3. **Smoke Test**: In a `temp_release_venv`, installs the compiled wheel to simulate a fresh environment.
4. **CLI Validation**: Executes `orchai doctor` and `orchai artifact inspect`.
5. **Metadata Verification**: Specifically asserts that the resulting artifact manifest accurately claims `Native Antigravity: UNSUPPORTED/UNVERIFIED` and prevents capability upgrading without physical runtime evidence.

## 2. Runtime Capability Classification
The controlled runtime tests confirm deterministically that we can trap read, write, and command executions safely. The native Antigravity IDE agent runs on undocumented APIs and remains beyond governance until a certified adapter exists. It will remain classified as UNSUPPORTED.
