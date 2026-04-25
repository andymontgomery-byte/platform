# Admin Operations

This file is the allowlist for Supabase Edge Functions or server code that use `SUPABASE_SERVICE_ROLE_KEY`.

Default rule: request-scoped operations must pass the caller's `Authorization` bearer token through to Supabase so PostgreSQL row-level security applies as the user. Service-role access is allowed only for operations listed here, and the calling code must include an inline comment naming the matching operation ID.

## Current Allowlist

No service-role callers are approved yet.

## Entry Format

| Operation ID | Caller | Why service role is required | Guardrails |
| --- | --- | --- | --- |
| `example_admin_operation` | `supabase/functions/example/index.ts` | Explain why user-scoped RLS cannot perform this operation. | Explain input validation, audit logging, tenant constraints, and monitoring. |
