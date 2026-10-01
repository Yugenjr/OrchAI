# Phase 16: CI/CD & Artifact Generation

## Overview
Phase 16 establishes the continuous integration, continuous delivery, and release verification infrastructure for OrchAI. OrchAI is packaged as a distributable Python tool.

## 1. CI Configuration
The `.github/workflows/ci.yml` file is configured to run the test suite on every push and pull request to `main`. It tests against both Ubuntu and Windows utilizing Python 3.13.

## 2. Packaging Configuration
The `pyproject.toml` defines the build backend using `setuptools.build_meta`. It leverages modern `pyproject.toml` standards to define entry points, dependencies, and project metadata. Running `python -m build` reliably creates both `.whl` and source distributions.

## 3. Artifact Manifest
`orchai.core.artifact.ArtifactMetadata` generates deterministic metadata summarizing the build constraints, git commit, test metrics, and capability statuses. Notably, it strips out all credentials safely before JSON serialization.

## 4. Clean-Install Verification
The `release_validation.py` script automatically:
1. Installs dependencies
2. Runs the deterministic test suite
3. Builds the wheels
4. Creates an isolated temporary virtual environment
5. Installs the compiled `.whl`
6. Runs `orchai doctor` and `orchai artifact inspect` CLI smoke tests

## 5. CLI Additions
New top-level commands were implemented:
- `orchai doctor`: Global diagnostic check (including native antigravity SDK check).
- `orchai build info`: Outputs local build metadata.
- `orchai artifact inspect`: Outputs the deterministic artifact manifest.

## Security Guarantees
Artifacts explicitly omit sensitive tokens. Testing asserts the non-presence of `token` or `secret` substrings in serialized outputs. No test runs skip blocked tests natively; native Antigravity remains strictly unsupported in the artifact metadata until runtime verification is legitimately possible.
