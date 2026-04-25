# Supabase Hosted Database Setup

Project URL: `https://qzxlgrerjoiamxvnkklq.supabase.co`

This folder packages the hosted PostgreSQL version of the current OneRoster core demo data. It is ready to load into Supabase, but the repository does not contain database passwords, service-role keys, or other server-only secrets.

The publishable client key is recorded in `.env.example` because it is intended for browser/client use. It is enough to test read-only REST access after row-level security policies and seed data are loaded. It is not enough to run migrations or seed the database.

Put server-only secrets such as `SUPABASE_SECRET_KEY` and `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`, not in tracked files. These keys are useful for server-side Supabase API access, but schema creation still requires the SQL editor, `SUPABASE_DB_URL`, or another migration-capable database connection.

Current status: loaded and verified on 2026-04-25 through the shared pooler. SQL smoke checks and `python3 scripts/check_supabase_rest.py` pass.

## Files

- `migrations/0001_oneroster_core_demo.sql`: PostgreSQL schema, views, indexes, grants, and read-only row-level security policies for synthetic demo data.
- `seed.sql`: deterministic demo rows matching the local SQLite demo.
- `smoke.sql`: read-only queries that verify row counts and the two review views.

## Load With SQL Editor

1. Open the Supabase project SQL editor.
2. Run `migrations/0001_oneroster_core_demo.sql`.
3. Run `seed.sql`.
4. Run `smoke.sql` and confirm the expected counts.

Expected counts:

| Table | Count |
| --- | ---: |
| `organizations` | 3 |
| `people` | 6 |
| `academic_sessions` | 3 |
| `courses` | 2 |
| `classes` | 3 |
| `enrollments` | 5 |
| `line_items` | 3 |
| `results` | 4 |
| `source_identifiers` | 4 |

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

The policies intentionally allow read-only access to the synthetic demo tables and views for `anon` and `authenticated` roles. They do not allow writes.

## Optional REST Smoke Test

Run:

```sh
python3 scripts/check_supabase_rest.py
```

The script reads `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` from the environment, `.env.local`, `.env`, or `.env.example`.

## Next.js/Vercel Note

The Supabase dashboard may suggest installing `@supabase/supabase-js` and `@supabase/ssr` plus `page.tsx` and middleware helpers. Those files are for a Next.js app. This repository is currently a static portal plus local Express demo, so those packages should be added only when a Vercel/Next runtime is introduced.
