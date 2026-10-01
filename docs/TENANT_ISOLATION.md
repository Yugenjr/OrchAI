# Tenant Isolation

Tenant isolation is heavily enforced below the API layer, inside the `TaskRepository` and `TaskService`.

## Data Boundary
Every Task is assigned a `tenant_id`. The repository layer refuses to yield data for a task if the requested `tenant_id` does not match the actual task.

## Audit and Memory
Events in the `AuditLedger` contain a `tenant_id`. Reading events or task records explicitly verifies that the requester shares the same tenant context as the target resource, unless they hold `TENANT_CROSS_READ` or `TENANT_CROSS_OPERATE` permissions.
