# Role-Based Access Control (RBAC)

OrchAI utilizes a strict mapping of `Role` to granular `Permission` values.

## Roles
- `ADMIN`: Global access across tenants.
- `DEVELOPER`: Can create, cancel, and review tasks, as well as read audit logs.
- `OPERATOR`: Can monitor metrics and audit logs but cannot create tasks.
- `VIEWER`: Read-only access to tasks and metrics.
- `SERVICE`: Automated service access.

## Permissions
Access control is implemented in `TaskService` by evaluating whether an `AuthContext` possesses the required permission for the specific method (e.g. `TASK_CREATE`, `TASK_APPROVE`, `RUNTIME_EXECUTE`, `TENANT_CROSS_OPERATE`).
