# Supabase Hosted Database

Project URL: `https://qzxlgrerjoiamxvnkklq.supabase.co`

The repository now has a live Supabase setup for the OneRoster core demo. The schema and seed data were loaded through the shared pooler and verified on 2026-04-25.

## What Is Ready

- PostgreSQL schema for the current OneRoster core demo tables and review views.
- Deterministic seed data matching the local SQLite demo.
- Read-only row-level security policies for the synthetic demo data.
- Smoke queries for table counts, class roster, and gradebook result views.
- Public client environment variables in `.env.example`.
- Optional REST smoke test script: `scripts/check_supabase_rest.py`.

## Verified Live Status

- `supabase/migrations/0001_oneroster_core_demo.sql` loaded successfully.
- `supabase/seed.sql` loaded successfully.
- `supabase/smoke.sql` returned the expected table counts and review view rows.
- `python3 scripts/check_supabase_rest.py` returned `ok: true` through the public Supabase REST API.

This closes the hosted relational database target for the current OneRoster core demo slice. It does not close the hosted API/server work by itself. Supabase now exposes simple read-only REST endpoints; custom API behavior, safe SQL query execution, OAuth/scope enforcement, and LTI callbacks still need a server layer such as Vercel or Supabase Edge Functions.

## Reviewer Path

1. Inspect `supabase/migrations/0001_oneroster_core_demo.sql`.
2. Inspect `supabase/seed.sql`.
3. Inspect `supabase/smoke.sql`.
4. Run `supabase/smoke.sql` to confirm the expected counts.
5. Run `python3 scripts/check_supabase_rest.py` to verify public REST access.

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

## Optional Vercel Role

Vercel is not required to load the database. It is useful for the next runtime layer: hosting a custom JSON API, a safe SQL query endpoint, OAuth/scope checks, and LTI launch callbacks. Without that server layer, GitHub Pages remains static and Supabase provides only database plus basic REST behavior.

The Supabase dashboard's `@supabase/supabase-js`, `@supabase/ssr`, `page.tsx`, and middleware instructions are for a Next.js app. They should be applied inside a Vercel/Next runtime package when that app exists, not to the current static portal root.

Keep `SUPABASE_SECRET_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and database passwords in `.env.local` or the deployment platform's secret store. Do not commit them.
