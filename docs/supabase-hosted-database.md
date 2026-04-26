# Supabase Hosted Database

Project URL: `https://qzxlgrerjoiamxvnkklq.supabase.co`

The repository now has a live Supabase setup for the OneRoster core demo. The schema and seed data were loaded through the shared pooler and verified on 2026-04-26 after tenant-scoped RLS was added.

## What Is Ready

- PostgreSQL schema for the current OneRoster core demo tables and review views.
- Deterministic seed data matching the local SQLite demo, plus a second-tenant fixture row used only to prove isolation.
- Read-only row-level security policies scoped by `tenant_id` from the caller's JWT claim, with anonymous public reads limited to the synthetic North Valley demo tenant.
- Smoke queries for table counts, class roster, and gradebook result views.
- Public client environment variables in `.env.example`.
- Optional REST smoke test script: `scripts/check_supabase_rest.py`.
- Live cross-tenant RLS test: `python3 tests/supabase_tenant_rls_test.py`.

## Verified Live Status

- `supabase/migrations/0001_oneroster_core_demo.sql` loaded successfully.
- `supabase/seed.sql` loaded successfully.
- `supabase/smoke.sql` returned the expected table counts and review view rows.
- `python3 scripts/check_supabase_rest.py` returned `ok: true` through the public Supabase REST API.
- `python3 tests/supabase_tenant_rls_test.py` created two temporary Supabase Auth users with different `app_metadata.tenant_id` claims and confirmed each JWT could read only its tenant's `people` rows. The public publishable-key curl remains limited to the synthetic North Valley tenant and cannot read the second-tenant fixture.

This closes the hosted relational database target for the current OneRoster core demo slice. It does not close the hosted API/server work by itself. Supabase now exposes simple read-only REST endpoints; custom API behavior, safe SQL query execution, OAuth/scope enforcement, and LTI callbacks still need a server layer such as Vercel or Supabase Edge Functions.

## Reviewer Path

1. Inspect `supabase/migrations/0001_oneroster_core_demo.sql`.
2. Inspect `supabase/seed.sql`.
3. Inspect `supabase/smoke.sql`.
4. Run `supabase/smoke.sql` to confirm the expected counts.
5. Run `python3 scripts/check_supabase_rest.py` to verify the REST endpoint is reachable.
6. Run `python3 tests/supabase_tenant_rls_test.py` with `.env.local` secrets to verify tenant A cannot read tenant B rows and tenant B cannot read tenant A rows.

Copy-paste public REST check:

```sh
curl 'https://qzxlgrerjoiamxvnkklq.supabase.co/rest/v1/people?select=id,display_name&order=id.asc&limit=1' \
  -H 'apikey: sb_publishable_DaJsnILCWdUIjl4cCaL3Jw_qLy8BPXK' \
  -H 'authorization: Bearer sb_publishable_DaJsnILCWdUIjl4cCaL3Jw_qLy8BPXK'
```

Expected counts:

| Table | Count |
| --- | ---: |
| `organizations` | 4 |
| `people` | 7 |
| `academic_sessions` | 3 |
| `courses` | 2 |
| `classes` | 3 |
| `enrollments` | 5 |
| `line_items` | 3 |
| `results` | 4 |
| `source_identifiers` | 5 |

## Optional Vercel Role

Vercel is not required to load the database. It is useful for the next runtime layer: hosting a custom JSON API, a safe SQL query endpoint, OAuth/scope checks, and LTI launch callbacks. Without that server layer, GitHub Pages remains static and Supabase provides only database plus basic REST behavior.

The Supabase dashboard's `@supabase/supabase-js`, `@supabase/ssr`, `page.tsx`, and middleware instructions are for a Next.js app. They should be applied inside a Vercel/Next runtime package when that app exists, not to the current static portal root.

Keep `SUPABASE_SECRET_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and database passwords in `.env.local` or the deployment platform's secret store. Do not commit them.
