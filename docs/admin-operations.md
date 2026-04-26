# Admin Operations

This file is the allowlist for Supabase Edge Functions or server code that use `SUPABASE_SERVICE_ROLE_KEY`.

Default rule: request-scoped operations must pass the caller's `Authorization` bearer token through to Supabase so PostgreSQL row-level security applies as the user. Service-role access is allowed only for operations listed here, and the calling code must include an inline comment naming the matching operation ID.

## Current Allowlist

| operation | caller | why_user_jwt_insufficient | last_reviewed |
| --- | --- | --- | --- |
| `tenant_rls_test_auth_fixture_setup` | `tests/supabase_tenant_rls_test.py` | The test must create temporary Supabase Auth users with different `app_metadata.tenant_id` claims before it can verify user-JWT RLS isolation through the live REST URL. The service role is used only for Auth user setup and cleanup, not for table reads. | 2026-04-26 |

## Entry Format

| Operation ID | Caller | Why service role is required | Guardrails |
| --- | --- | --- | --- |
| `example_admin_operation` | `supabase/functions/example/index.ts` | Explain why user-scoped RLS cannot perform this operation. | Explain input validation, audit logging, tenant constraints, and monitoring. |
