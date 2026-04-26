# Supabase Hosted Database Setup

Project URL: `https://qzxlgrerjoiamxvnkklq.supabase.co`

This folder packages the hosted PostgreSQL version of the current OneRoster core demo data. It is ready to load into Supabase, but the repository does not contain database passwords, service-role keys, or other server-only secrets.

The publishable client key is recorded in `.env.example` because it is intended for browser/client use. It is enough to test read-only REST access after row-level security policies and seed data are loaded. It is not enough to run migrations or seed the database.

Put server-only secrets such as `SUPABASE_SECRET_KEY` and `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`, not in tracked files. These keys are useful for server-side Supabase API access, but schema creation still requires the SQL editor, `SUPABASE_DB_URL`, or another migration-capable database connection.

Current status: loaded and verified on 2026-04-26 through the shared pooler. SQL smoke checks, `python3 scripts/check_supabase_rest.py`, and `python3 tests/supabase_tenant_rls_test.py` pass.

## Files

- `migrations/0001_oneroster_core_demo.sql`: PostgreSQL schema, views, indexes, grants, and tenant-scoped read-only row-level security policies for synthetic demo data.
- `seed.sql`: deterministic demo rows matching the local SQLite demo plus a second-tenant fixture used by the live RLS test.
- `smoke.sql`: read-only queries that verify row counts and the two review views.
- `functions/gradebook-bulk-submit`: Supabase Edge Function for authenticated bulk result submission using the caller's bearer token so RLS applies.

## Load With SQL Editor

1. Open the Supabase project SQL editor.
2. Run `migrations/0001_oneroster_core_demo.sql`.
3. Run `seed.sql`.
4. Run `smoke.sql` and confirm the expected counts.

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

## Load With `psql`

Set `SUPABASE_DB_URL` locally. Do not commit it.

```sh
psql "$SUPABASE_DB_URL" -f supabase/migrations/0001_oneroster_core_demo.sql
psql "$SUPABASE_DB_URL" -f supabase/seed.sql
psql "$SUPABASE_DB_URL" -f supabase/smoke.sql
```

## Read-Only REST Review

After the schema and seed are loaded, a reviewer with the public publishable key can query Supabase REST:

```sh
curl 'https://qzxlgrerjoiamxvnkklq.supabase.co/rest/v1/people?select=*' \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_PUBLISHABLE_KEY"
```

The policies allow read-only access when the caller's JWT carries a matching tenant claim. Anonymous public reads are restricted to the synthetic North Valley demo tenant so the no-setup review curl still returns seeded demo rows without exposing the second-tenant isolation fixture. Supabase Auth users created with `app_metadata.tenant_id` can read rows for their tenant and cannot read rows for another tenant. The policies do not allow writes.

The gradebook bulk-submit Edge Function is the first authenticated write path. It forwards the request `Authorization` bearer token into the Supabase client and the `results` write policies allow only authenticated tenant-matched inserts or updates.

## Deploy Edge Functions

```sh
supabase functions deploy gradebook-bulk-submit --project-ref qzxlgrerjoiamxvnkklq --use-api
```

## Optional REST Smoke Test

Run:

```sh
python3 scripts/check_supabase_rest.py
```

The script reads `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` from the environment, `.env.local`, `.env`, or `.env.example`.

## Cross-Tenant RLS Test

Run:

```sh
python3 tests/supabase_tenant_rls_test.py
```

The test reads `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` or `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` from `.env.local`. It creates two temporary Supabase Auth users with different `app_metadata.tenant_id` claims, calls the live REST `/people` endpoint with each user JWT, confirms tenant A cannot read tenant B's seeded person row and tenant B cannot read tenant A's seeded person row, then deletes the temporary Auth users.

## Next.js/Vercel Note

The Supabase dashboard may suggest installing `@supabase/supabase-js` and `@supabase/ssr` plus `page.tsx` and middleware helpers. Those files are for a Next.js app. This repository is currently a static portal plus local Express demo, so those packages should be added only when a Vercel/Next runtime is introduced.
