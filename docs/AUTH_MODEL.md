# Auth Model

Phase 20 introduces a robust identity and authentication framework for OrchAI.

## Identity

Every request is bound to an `AuthContext`, which includes:
- `user_id`: The ID of the user performing the action.
- `tenant_id`: The tenant the user belongs to.
- `roles`: A list of assigned roles.
- `permissions`: The resolved list of granular permissions.
- `credential_id`: The identifier for the API credential used.

## Credentials
We use secure random API credentials stored as one-way SHA-256 hashes (`token_hash`) in `CredentialManager`. Secrets are never stored in plaintext and are only presented to the user once upon creation.

## Authentication
Authentication is verified via the `Authorization: Bearer <token>` header at the API Gateway level.
Tokens can expire or be explicitly revoked, instantly blocking future requests.
