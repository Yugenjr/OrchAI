# API Security

The OrchAI API Gateway incorporates multiple layers of security to form a zero-trust model:

## Threat Mitigation
1. **Authentication:** Only authenticated requests resolve to an `AuthContext`.
2. **Authorization:** Endpoints verify that the `AuthContext` has appropriate permissions.
3. **Tenant Isolation:** Enforced implicitly within service calls.
4. **Rate Limiting:** An in-process rate limiter (using a token bucket logic per tenant/user and action) protects endpoints from abuse and DoS.

## Admin Override
Cross-tenant actions are explicitly guarded by `TENANT_CROSS_READ` and `TENANT_CROSS_OPERATE` and are recorded in the audit logs with the actor marked as the Admin.
