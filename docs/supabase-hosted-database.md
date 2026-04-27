# Supabase Hosted Database

Project URL: `https://qzxlgrerjoiamxvnkklq.supabase.co`

The repository now has a live Supabase setup for the OneRoster core demo. The schema and seed data were loaded through the shared pooler and verified on 2026-04-26 after tenant-scoped RLS was added.

## What Is Ready

- PostgreSQL schema for the current OneRoster core demo tables and review views.
- Deterministic seed data matching the local SQLite demo, plus a second-tenant fixture row used only to prove isolation.
- Read-only row-level security policies scoped by `tenant_id` from the caller's JWT claim, with anonymous public reads limited to the synthetic North Valley demo tenant.
- Smoke queries for table counts, class roster, and gradebook result views.
- Tenant-scoped `audit_log` table plus an audited sensitive-read RPC and Edge Function for restricted `people` fields.
- Public client environment variables in `.env.example`.
- Optional REST smoke test script: `scripts/check_supabase_rest.py`.
- Live cross-tenant RLS test: `python3 tests/supabase_tenant_rls_test.py`.
- Live sensitive-read audit test: `python3 tests/supabase_audit_log_test.py`.
- Supabase Edge Function source for authenticated gradebook bulk submit, audited roster reads, LTI launch handling, Caliper event ingestion, and OAuth token exchange under `supabase/functions/`.

## Verified Live Status

- `supabase/migrations/0001_oneroster_core_demo.sql` loaded successfully.
- `supabase/seed.sql` loaded successfully.
- `supabase/smoke.sql` returned the expected table counts and review view rows.
- `python3 scripts/check_supabase_rest.py` returned `ok: true` through the public Supabase REST API.
- `python3 tests/supabase_tenant_rls_test.py` created two temporary Supabase Auth users with different `app_metadata.tenant_id` claims and confirmed each JWT could read only its tenant's `people` rows. The public publishable-key curl remains limited to the synthetic North Valley tenant and cannot read the second-tenant fixture.
- `python3 tests/supabase_audit_log_test.py` created a temporary Supabase Auth user with tenant, client, scope, and purpose claims; called the live `audited-roster-read` Edge Function for `person_ada`; and confirmed `audit_log` rows were written for `people.display_name`, `people.given_name`, `people.family_name`, and `people.email`.
- `supabase functions list --project-ref qzxlgrerjoiamxvnkklq` shows `gradebook-bulk-submit`, `audited-roster-read`, `lti-launch-handler`, `caliper-event-ingestion`, and `oauth-token-exchange` active.
- A live Edge Function smoke on 2026-04-26 created a temporary tenant-scoped Supabase Auth user and successfully called `lti-launch-handler`, `caliper-event-ingestion`, and `oauth-token-exchange` with that user's JWT.

This closes the hosted relational database target for the current OneRoster core demo slice. It does not close the hosted API/server work by itself. Supabase now exposes simple read-only REST endpoints, an audited sensitive-read wrapper, and minimal non-CRUD Edge Function entry points for gradebook bulk submit, LTI launch receipts, Caliper event receipts, and OAuth token-exchange receipts. Safe SQL query execution, full OAuth/scope enforcement, and full LTI Advantage callbacks still need additional backend slices.

## Where To Find The Service Role Key

The buildability guide uses the service-role key once to create a temporary Supabase Auth user with an `app_metadata.tenant_id` claim. Use this key only from a trusted shell or backend environment; never put it in browser code.

1. Open the Supabase project dashboard for `qzxlgrerjoiamxvnkklq`.
2. In the left sidebar, open **Project Settings**.
3. Open **API**.
4. In **Project API keys**, copy the key labeled **service_role** or **service_role secret**.
5. Put that value in `.env.local` as `SUPABASE_SERVICE_ROLE_KEY=...`, or paste it into the `export SUPABASE_SERVICE_ROLE_KEY='...'` line in `docs/build-an-edtech-app.md` while running the guide locally.

The publishable key in `.env.example` is safe for client requests. The service-role key bypasses row-level security when used directly, so the guide uses it only for the Auth Admin user-creation call and then switches to the tenant-scoped user JWT for all platform table writes.

## New Developer Onboarding Without Platform Admin Access

You do not need access to the platform team's hosted project to run the buildability guide. Use a self-hosted Supabase sandbox:

1. Create a new Supabase project in your own Supabase account.
2. In that project's dashboard, open **Project Settings -> Database** and copy the connection string or pooler URL into `SUPABASE_DB_URL`.
3. From the repository root, load the generated platform schema:

```sh
export SUPABASE_DB_URL='postgresql://postgres.<your-project-ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres'

psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 \
  -f supabase/migrations/0001_oneroster_core_demo.sql
```

4. In **Project Settings -> API**, copy the Project URL, publishable key, and service-role key from your own project.
5. Use those three values in `docs/build-an-edtech-app.md` Step 0. The guide creates a tenant-scoped test user in your project, then uses that user's JWT for the roster, gradebook, CASE alignment, and Caliper feed curls.

This self-hosted path exercises the same migration-generated tables, RLS policies, and PostgREST requests as the hosted sandbox. It exists so a new developer can complete the guide from the docs without being a platform administrator on `qzxlgrerjoiamxvnkklq`.

## Reviewer Path

1. Inspect `supabase/migrations/0001_oneroster_core_demo.sql`.
2. Inspect `supabase/seed.sql`.
3. Inspect `supabase/smoke.sql`.
4. Run `supabase/smoke.sql` to confirm the expected counts.
5. Run `python3 scripts/check_supabase_rest.py` to verify the REST endpoint is reachable.
6. Run `python3 tests/supabase_tenant_rls_test.py` with `.env.local` secrets to verify tenant A cannot read tenant B rows and tenant B cannot read tenant A rows.
7. Run `python3 tests/supabase_audit_log_test.py` with `.env.local` secrets to verify a restricted `people` read writes audit rows with `client_id`, `scope`, `purpose`, `field_accessed`, `tenant_id`, and `timestamp`.

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

## Edge Function: Gradebook Bulk Submit

Live function URL: `https://qzxlgrerjoiamxvnkklq.functions.supabase.co/gradebook-bulk-submit`

This non-CRUD endpoint accepts a batch of OneRoster-style result submissions. It requires a Supabase Auth access token with a `tenant_id` claim, constructs its database client from the request `Authorization` header, and upserts only rows allowed by PostgreSQL RLS.

```sh
curl 'https://qzxlgrerjoiamxvnkklq.functions.supabase.co/gradebook-bulk-submit' \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  --data '{
    "submissions": [
      {
        "id": "res_ada_homework_1",
        "sourcedId": "RESULT-9003",
        "lineItemId": "li_math_homework_1",
        "personId": "person_ada",
        "scoreStatus": "fullyGraded",
        "score": 9,
        "scoreDate": "2026-09-06T10:00:00Z",
        "comment": "Complete."
      }
    ]
  }'
```

## Edge Function: Audited Roster Read

Live function URL: `https://qzxlgrerjoiamxvnkklq.functions.supabase.co/audited-roster-read`

Direct REST access to `people` exposes only non-restricted review columns. Reads of restricted `people` fields such as `given_name`, `family_name`, and `email` go through `read_people_sensitive_audited`, which writes one `audit_log` row per field before returning data. Each row includes `client_id`, `scope`, `purpose`, `field_accessed`, `tenant_id`, and `timestamp`. The Edge Function forwards the caller's Supabase Auth JWT to PostgREST and never uses the service-role key.

```sh
curl 'https://qzxlgrerjoiamxvnkklq.functions.supabase.co/audited-roster-read?personId=person_ada' \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'x-platform-client-id: demo-lms-client' \
  -H 'x-platform-scope: platform.roster.users.directory:read' \
  -H 'x-platform-purpose: directory-review'
```

## Edge Function: LTI Launch Handler

Live function URL: `https://qzxlgrerjoiamxvnkklq.functions.supabase.co/lti-launch-handler`

This non-CRUD endpoint accepts an authenticated LTI launch payload, resolves the posted context ID through tenant-scoped `source_identifiers`, and writes an `audit_log` receipt. It forwards the caller's Supabase Auth JWT to PostgREST and never uses the service-role key.

```sh
curl 'https://qzxlgrerjoiamxvnkklq.functions.supabase.co/lti-launch-handler' \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  --data '{"messageType":"LtiResourceLinkRequest","contextId":"LTI-CONTEXT-MATH-6A","resourceLinkId":"resource-math-home","userId":"person_ms_rivera"}'
```

## Edge Function: Caliper Event Ingestion

Live function URL: `https://qzxlgrerjoiamxvnkklq.functions.supabase.co/caliper-event-ingestion`

This non-CRUD endpoint accepts a Caliper envelope or single Caliper event, forwards the caller's JWT into the Supabase client, and writes tenant-scoped receipt rows through RLS. It is the authenticated entry point for event ingestion; immutable raw-event storage and profile-specific projections remain a future backend slice.

```sh
curl 'https://qzxlgrerjoiamxvnkklq.functions.supabase.co/caliper-event-ingestion' \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  --data '{"sensor":"https://platform.example/sensors/demo","data":[{"id":"urn:uuid:11111111-2222-3333-4444-555555555555","type":"GradeEvent","action":"Graded"}]}'
```

## Edge Function: OAuth Token Exchange

Live function URL: `https://qzxlgrerjoiamxvnkklq.functions.supabase.co/oauth-token-exchange`

This non-CRUD endpoint accepts an authenticated OAuth token-exchange request, forwards the caller's JWT into the Supabase client, writes a tenant-scoped database receipt, and returns the scoped sandbox bearer context. It is not a production authorization server; persistent token issuance, key rotation, and consent workflows remain future backend work.

```sh
curl 'https://qzxlgrerjoiamxvnkklq.functions.supabase.co/oauth-token-exchange' \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange&client_id=demo-lms-client&scope=platform.roster.users.directory:read'
```

## Optional Vercel Role

Vercel is not required to load the database. It is useful for future runtime layers such as hosting a custom JSON API, a safe SQL query endpoint, production OAuth/scope checks, and full LTI Advantage callbacks. Without that server layer, GitHub Pages remains static and Supabase provides database, basic REST behavior, and the current Edge Function entry points.

The Supabase dashboard's `@supabase/supabase-js`, `@supabase/ssr`, `page.tsx`, and middleware instructions are for a Next.js app. They should be applied inside a Vercel/Next runtime package when that app exists, not to the current static portal root.

Keep `SUPABASE_SECRET_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and database passwords in `.env.local` or the deployment platform's secret store. Do not commit them.
