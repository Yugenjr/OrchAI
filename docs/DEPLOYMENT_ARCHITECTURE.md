# Deployment Architecture

## Trust Boundaries
The deployment architecture introduces two new trust boundaries:
1. **API Gateway (Webhook)**: Authenticates external triggers (e.g. CI/CD) using `ORCHAI_DEPLOYMENT_TOKEN` (distinct from execution secrets like `GEMINI_API_KEY`).
2. **Container Boundary**: Isolates the OrchAI runtime from the host using OS-level abstractions.

## Components
- `ContainerRuntimeAdapter`: Connects OrchAI to a local Docker daemon (or remote orchestrator) ensuring deterministic resource limits (`cpu: 0.5`, `mem: 512m`) and explicit workspace mounts.
- `DeploymentManager`: Abstracts the execution target so we can seamlessly shift from `local_docker` to `ecs` or `k8s` in future phases.
- `WebhookHandler`: A minimal `http.server` exposing `POST /tasks` for programmatic headless trigger.

## Security
- No host root access.
- Secrets are NEVER logged.
- The webhook rejects arbitrary execution commands; it only creates deterministic `Task` definitions inside the repository which are then governed by standard policies.
