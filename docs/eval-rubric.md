# Platform Evaluation Rubric

This rubric is the source of truth for what "done" means on this platform. It is graded by an LLM evaluator (`scripts/evaluate_platform.py`), not by file-presence checks. The deterministic score gate (`scripts/check_spec_conformance.py`) is now **advisory only** — it provides signal to the LLM, but does not gate publish.

The Codex loop iterates until every requirement below is `pass` (or every remaining requirement is `blocked` for a documented external reason).

## How to read this file

Each requirement has:

- **id** — stable identifier the evaluator reports against
- **requirement** — what must be true
- **how_to_verify** — what the evaluator should check, in plain language
- **substance_check** — what counts as a real pass vs. a stub that names the right files
- **blocked_if** — external conditions that flip the item to `blocked` instead of `fail` (e.g., requires hosted infra not yet provisioned)

Status values the evaluator emits per requirement: `pass`, `partial`, `fail`, `blocked`.

## Categories

1. Portal and developer experience
2. Shared dictionary as source of truth
3. Vertical slice runnable end-to-end
4. Cross-spec decisions and reconciliation
5. Privacy, tenancy, and security
6. Coverage and accounting
7. Hosted runtime
8. Loop and harness hygiene

---

## 1. Portal and developer experience

### portal_renders_as_html

- **requirement:** Site renders documentation as HTML, not raw Markdown or YAML.
- **how_to_verify:** Fetch the live portal, confirm doc and OpenAPI pages are HTML with navigation and styling.
- **substance_check:** No `href` to `.md`, `.yaml`, or `.yml` from any page under `site/`. OpenAPI rendered with Redoc, Swagger UI, or equivalent — not as a text dump.
- **blocked_if:** never.

### developer_guide_present

- **requirement:** Portal explains what the platform provides and what the app developer owns.
- **how_to_verify:** Open the portal and locate a Developer Guide section that reads as guidance, not as a feature list.
- **substance_check:** Two distinct sections labelled (or clearly equivalent to) "Platform Provides" and "App Developer Owns," each with concrete bullets that name OneRoster, CASE, QTI, Caliper, LTI, Open Badges or CLR, and at least one item the app owns (e.g., pedagogy, UI quality, scope minimization).
- **blocked_if:** never.

---

## 2. Shared dictionary as source of truth

### dictionary_single_source

- **requirement:** A single governed dictionary source generates SQL comments, OpenAPI descriptions, and Markdown docs.
- **how_to_verify:** Inspect `dictionary/*.v1.json` plus `scripts/generate_*.py`. Confirm a generator exists per spec and that running it produces the SQL/OpenAPI/Markdown artifacts. Spot-check that an edit to a dictionary entry would propagate to all three surfaces.
- **substance_check:** Generators must read the dictionary file and emit all three surface artifacts in one run. Hand-authored SQL comments or OpenAPI descriptions in the generated files fail this check.
- **blocked_if:** never.

### dictionary_covers_lead_specs

- **requirement:** Each spec marked `Lead` on the standards registry has a structured dictionary source plus generated SQL/OpenAPI/Markdown.
- **how_to_verify:** Read `docs/lead-spec-accounting.md` and confirm OneRoster, QTI, CASE, Caliper, LTI, Security Framework, and Data Privacy each have an entry. For each, locate the corresponding `dictionary/*.v1.json`.
- **substance_check:** Every Lead spec has a real dictionary file with multiple objects and fields, not a placeholder with one object.
- **blocked_if:** never.

### lead_spec_full_accounting

- **requirement:** For every spec marked `Lead`, every object, field, and controlled vocabulary value in that spec is either mapped to a canonical dictionary entry via an explicit `sourceStandard` reference, or appears on an "intentionally not supported" list with a reason.
- **how_to_verify:** For each Lead spec, compare the dictionary contents against the published spec object/field/value list. Confirm anything missing is on the unsupported ledger with a written reason.
- **substance_check:** "Not yet documented" is not a reason. Reasons must reference business value, scope, or downstream impact (e.g., "QTI custom interactions not supported in v1; revisit when adaptive testing slice opens").
- **blocked_if:** never. Coverage may grow over multiple iterations; partial coverage with backlog tracking is `partial`, not `pass`.

### dictionary_covers_canonical_model

- **requirement:** Every object, field, and enum value in the canonical model has a layperson dictionary entry.
- **how_to_verify:** Run `scripts/check_dictionary_artifacts.py`, then sample 5 random fields from generated SQL or OpenAPI and confirm each has a plain-language description in the dictionary that a non-engineer could understand.
- **substance_check:** Descriptions must be in plain language — "the unique identifier for the user record" passes; "uuid pk" fails.
- **blocked_if:** never.

---

## 3. Vertical slice runnable end-to-end

### vertical_slice_runnable_locally

- **requirement:** At least one 1EdTech area (currently OneRoster core) runs end-to-end locally with seeded data, an API, and a SQL surface.
- **how_to_verify:** From a clean checkout, run `cd demo && npm run reset-db && npm test`. Confirm tests pass and the API returns spec-shaped JSON.
- **substance_check:** API responses match OneRoster 1.2 REST shapes (e.g., `/users/{sourcedId}` returns `sourcedId` as `id`).
- **blocked_if:** never.

### vertical_slice_callable_externally

- **requirement:** The vertical slice is callable from the open internet at a stable URL with a real database behind it.
- **how_to_verify:** From outside the repo, issue an HTTP request against the hosted Supabase REST URL using the publishable key. Confirm 200 response with spec-shaped JSON for `/people`, `/class_roster`, and `/gradebook_results`.
- **substance_check:** Must hit a live database, not a static JSON file mirrored from `site/api/`. The Supabase publishable key may be public, but the response must come from PostgREST, not GitHub Pages.
- **blocked_if:** Supabase project is not reachable. Should not be `blocked` unless the hosted DB has been intentionally torn down.

### try_it_surface_present

- **requirement:** The portal lets a visitor run a real query and a real API call without leaving the site.
- **how_to_verify:** Open the portal and confirm there is a browser-based SQL console connected to seed data (read-only is fine) AND a try-it API surface (Swagger UI / Redoc with a working "Try it out" against the live endpoint, or curl-style examples that actually work against the hosted URL).
- **substance_check:** The console and try-it surface must execute against real data — not a screenshot, not a code block.
- **blocked_if:** never.

---

## 4. Cross-spec decisions and reconciliation

### overlap_decisions_substance

- **requirement:** Every cross-spec overlap or conflict is resolved in the decisions file with named specs, the conflict, the choice, the projection back to each source spec, and the tradeoff.
- **how_to_verify:** Read `docs/decisions/standards-overlap-decisions.md`. For each required area below, confirm the entry contains all five elements in real prose.
- **substance_check:** Each required area must have an entry with: (1) specs involved, (2) what the conflict is, (3) the choice, (4) projection back to each spec, (5) the tradeoff. Section headers without prose fail. Required areas at minimum: Person identity, Class/course/section/context, Role vocabularies, Enrollment vs. membership, Results/scores/outcomes, Standards alignment, Identifier schemes, Time and session model, Content/resource, Tenancy. Additional overlap areas the model finds also count.
- **blocked_if:** never.

### decision_traces_to_dictionary

- **requirement:** Each architectural decision links to the dictionary fields it produced; each generated dictionary field cites the decision that shaped it.
- **how_to_verify:** Pick 3 decisions and confirm each names the dictionary fields it determined. Pick 5 dictionary fields and confirm each cites the decision that shaped its shape (or notes "no decision applies").
- **substance_check:** Link must be machine-readable (a `decision_id` field in the dictionary, or a `produces_fields` list in the decision file). Prose-only "see decision X" mentions are `partial`.
- **blocked_if:** never.

---

## 5. Privacy, tenancy, and security

### tenant_isolation_enforced

- **requirement:** Every fact table carries a `tenant_id` column and PostgreSQL row-level security policies are enabled and tested against the live database. Policies must reference `tenant_id` (or an equivalent JWT claim) in their `USING` predicate — not `true`.
- **how_to_verify:** Inspect `supabase/migrations/*.sql` for `tenant_id` columns and `CREATE POLICY ... USING (tenant_id = ...)` statements with `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`. Confirm `supabase/policies/pg_policies.snapshot.json` shows the same predicate per fact-table policy. Run an integration test (committed under `tests/` and runnable from `npm test` or a documented script) that uses two distinct JWTs scoped to different tenants and confirms tenant A cannot read tenant B's rows via the live Supabase URL.
- **substance_check:** A policy whose `using` clause is `true` (unconditional) FAILS this item, even if RLS is enabled. The predicate must scope rows to a tenant claim from the JWT (e.g., `tenant_id = (auth.jwt() ->> 'tenant_id')::uuid` or equivalent). The integration test must hit the live Supabase URL, not a local mock, and must be runnable by a fresh evaluator with documented JWTs.
- **blocked_if:** never. Path is clear: add `tenant_id` columns + tenant-scoped RLS policies in a Supabase migration, regenerate the policy snapshot, add the cross-tenant test.

### oauth_scopes_mapped_to_fields

- **requirement:** OAuth scopes are mapped to specific dictionary fields and privacy classes, not just to resource names.
- **how_to_verify:** Inspect the dictionary for `privacy_class` and `oauth_scope` (or equivalent) attributes on each field. Confirm the OpenAPI security schemes reference scopes and the scopes are documented in the portal.
- **substance_check:** A scope like `roster:read` is `partial`. A scope like `roster.users.directory:read` mapped to fields with `privacy_class: directory` is `pass`.
- **blocked_if:** never.

### privacy_class_on_every_field

- **requirement:** Every field in the dictionary carries a privacy classification.
- **how_to_verify:** Read each `dictionary/*.v1.json`, confirm every field has a non-empty `privacy_class` (or equivalent) value drawn from a documented vocabulary.
- **substance_check:** Vocabulary must be enumerated somewhere (e.g., `public`, `directory`, `educational_record`, `behavioral`, `sensitive_pii`, `system`). `unknown` or empty fails.
- **blocked_if:** never.

### service_role_calls_allowlisted

- **requirement:** Every `SUPABASE_SERVICE_ROLE_KEY` (or equivalent service-role) usage in `supabase/functions/**`, `scripts/**`, and `demo/**` is justified by an entry in `docs/admin-operations.md` that names the operation, the caller, and why the user JWT path is insufficient.
- **how_to_verify:** Run a grep for `SUPABASE_SERVICE_ROLE_KEY` (and `service_role`, `service-role`) across the repo. For each match, confirm an inline comment names the admin operation AND a matching row exists in `docs/admin-operations.md` with columns `caller`, `operation`, `why_user_jwt_insufficient`, `last_reviewed`. Confirm `last_reviewed` is within 30 days.
- **substance_check:** A service-role call without an allowlist row fails the item. An allowlist row whose `why_user_jwt_insufficient` is empty, vague (`admin work`), or stale (>30 days) fails. The allowlist must list every caller — the file existing alone is not enough.
- **blocked_if:** never.

### audit_log_for_sensitive_reads

- **requirement:** Reads of fields classified `directory_pii` or stricter are audited with the OAuth client, scope, purpose claim, and field accessed.
- **how_to_verify:** Inspect Supabase migrations for an `audit_log` table and either (a) a Postgres trigger on restricted views, or (b) a Supabase Edge Function wrapper that logs before returning data. Run a test call against the live URL that reads a restricted field and confirm a row appears in `audit_log`.
- **substance_check:** Audit rows must include `client_id`, `scope`, `purpose`, `field_accessed`, `tenant_id`, and `timestamp`. `console.log` on access does not count. Postgres triggers or Edge Functions are both acceptable; static `site/api/*.json` mirrors are not (they cannot audit).
- **blocked_if:** never. Path is clear: add an `audit_log` table and either Postgres triggers (for read auditing on views) or a thin Supabase Edge Function that wraps restricted reads. No external infra needed.

---

## 6. Coverage and accounting

### gap_backlog_current

- **requirement:** Every known unmet requirement from this rubric is tracked in `docs/spec-gap-backlog.md` with status, target slice, and owner notes.
- **how_to_verify:** Cross-reference each `fail` and `blocked` item from this rubric against the backlog. Every one must appear.
- **substance_check:** Backlog entries must reference the rubric `id`. Generic "improve QTI" entries do not count.
- **blocked_if:** never.

### coverage_matrix_distinguishes_layers

- **requirement:** `docs/dictionary-coverage-matrix.md` distinguishes structured source, generated artifacts, runnable slice, and unsupported ledger per spec.
- **how_to_verify:** Open the matrix and confirm columns for each layer exist and are populated honestly per spec.
- **substance_check:** A spec with generated docs but no runnable slice must show "no" in the runnable column, not "see backlog."
- **blocked_if:** never.

---

## 7. Hosted runtime

### edge_functions_for_non_crud_endpoints

- **requirement:** Endpoints that PostgREST cannot model (gradebook bulk submit, LTI 1.3 launch handler, Caliper event ingestion, OAuth token exchange) are implemented as Supabase Edge Functions, not faked with static JSON.
- **how_to_verify:** Inspect `supabase/functions/*` for the relevant function directories. Confirm each has a `deno.json` and an `index.ts` that calls the database with the user's JWT (so RLS applies). Confirm the portal documents the live Edge Function URLs and at least one is callable from a curl example in the portal.
- **substance_check:** Edge Functions must verify the JWT and pass it through to PostgREST or the Postgres client so RLS applies — they must NOT use the service role key to bypass RLS unless the operation is documented as service-only (e.g., bulk import). PostgREST handles standard CRUD; Edge Functions only need to exist for non-CRUD endpoints.
- **blocked_if:** Supabase CLI not installed locally OR `SUPABASE_SERVICE_ROLE_KEY` not set in `.env.local`. The evaluator must report the missing prerequisite explicitly so the dev can unblock.

### edge_functions_propagate_user_jwt

- **requirement:** Every Edge Function in `supabase/functions/*` initializes the Supabase client from the request `Authorization` header so RLS is enforced as the calling user. Service-role usage is allowed only for explicitly documented admin paths.
- **how_to_verify:** Grep `supabase/functions/**/index.ts` for `SUPABASE_SERVICE_ROLE_KEY`. For each match, confirm an inline comment names the admin operation AND a matching entry exists in `docs/admin-operations.md`. Confirm the default client construction in each function reads `req.headers.get('Authorization')` and passes it as the bearer token.
- **substance_check:** A function that calls Postgres or PostgREST without forwarding the user JWT silently bypasses RLS and must fail this item. The allowlist file must exist and enumerate every service-role caller.
- **blocked_if:** No Edge Functions exist yet (covered by `edge_functions_for_non_crud_endpoints`).

### rls_enabled_on_referenced_tables

- **requirement:** Every table referenced by OneRoster, Caliper, LTI, or QTI endpoints has row-level security enabled with at least one NON-TRIVIAL policy. A non-trivial policy has a `using` predicate that references row data (a column, a JWT claim, or a function) — not the literal `true`.
- **how_to_verify:** Read the committed `supabase/policies/pg_policies.snapshot.json` (produced by `scripts/snapshot_pg_policies.py` against the live project). For each table named in the dictionary's runtime-backed objects, confirm `rowsecurity = true`, `forceRowSecurity = true` (so table owners are not exempt), and at least one policy whose `using` clause is NOT `true` and NOT empty. Confirm the snapshot's `generatedAt` is within 24 hours of the latest schema-touching commit.
- **substance_check:** Policies of the form `using (true)` open the table to whoever has connect access — they fail this item even though RLS is technically enabled. `forceRowSecurity = false` lets the table owner bypass policies and also fails. The snapshot must be regenerated whenever the schema changes; a stale snapshot fails the item.
- **blocked_if:** Supabase project credentials missing locally — evaluator must report the missing prerequisite explicitly.

### hosted_database_live

- **requirement:** A real hosted relational database is live for the OneRoster demo slice with seed data and read access for evaluators.
- **how_to_verify:** Run `python3 scripts/check_supabase_rest.py` from a clean checkout with the publishable key. Confirm it returns 200s for `/people`, `/class_roster`, `/gradebook_results`.
- **substance_check:** Connection must reach PostgREST against a Postgres backend, not a static JSON mirror.
- **blocked_if:** Supabase project intentionally torn down or evaluator credentials not provided.

### hosted_api_callable_no_setup

- **requirement:** An external evaluator (human or AI) can issue a working API call against the hosted runtime with only the public docs as input.
- **how_to_verify:** Confirm the portal includes a copy-pasteable curl command (with publishable key) that returns 200 against the live URL. Run it.
- **substance_check:** Curl must work without local setup, env vars not documented in the portal, or non-public keys.
- **blocked_if:** Same as `hosted_database_live`.

---

## 8. Loop and harness hygiene

### evaluator_runs_each_iteration

- **requirement:** `scripts/evaluate_platform.py` runs at the end of each loop iteration and writes `site/api/platform-evaluation.json`.
- **how_to_verify:** Read `VERIFY.md` and confirm the evaluator is invoked. Read the most recent iteration's logs and confirm the evaluator wrote a fresh report.
- **substance_check:** Report must contain a per-rubric-item status array and an overall summary (pass count / fail count / blocked count).
- **blocked_if:** never.

### advisory_score_gate_kept

- **requirement:** The deterministic `check_spec_conformance.py` still runs and writes `site/api/spec-conformance.json` for advisory signal, but does not gate publish.
- **how_to_verify:** Inspect `scripts/codex_loop.py` and confirm publish gating uses the LLM evaluator, not the deterministic score.
- **substance_check:** Loop driver should pass the deterministic report into the LLM evaluator's context as one signal among many.
- **blocked_if:** never.

### loop_overrides_respected

- **requirement:** The Codex loop reads `docs/loop-overrides.md` at the start of every iteration and passes its contents to the Codex prompt as authoritative guidance. The loop also halts when the Pause section contains the literal token `PAUSE` on its own line.
- **how_to_verify:** Inspect `scripts/codex_loop.py`. Confirm a helper reads `docs/loop-overrides.md`, a check halts the loop on the `PAUSE` token, and the prompt builder injects the overrides into the iteration prompt under a section labeled "Human overrides". Confirm `docs/loop-overrides.md` exists with at minimum a `## Pause`, `## Decisions`, and `## Unblocks` section.
- **substance_check:** A loop that reads the file but never injects it into the prompt fails this item. A prompt that mentions the file but does not include its contents fails. The PAUSE check must short-circuit before the next iteration runs, not after.
- **blocked_if:** never.

### loop_terminates_on_pass

- **requirement:** The Codex loop stops iterating when every rubric item is `pass`, or when every remaining unmet item is `blocked` with a backlog entry.
- **how_to_verify:** Read the loop driver. Confirm termination condition references the LLM evaluator output, not a numeric score threshold.
- **substance_check:** Hard caps (max iterations, stall detection, cost ceiling) still apply as safety rails.
- **blocked_if:** never.

---

## Summary

| Category | Count |
|---|---|
| Portal and developer experience | 2 |
| Shared dictionary as source of truth | 4 |
| Vertical slice runnable end-to-end | 3 |
| Cross-spec decisions and reconciliation | 2 |
| Privacy, tenancy, and security | 5 |
| Coverage and accounting | 2 |
| Hosted runtime | 5 |
| Loop and harness hygiene | 4 |
| **Total** | **27** |

The loop is "done" when all 27 are `pass`, or when every remaining item is `blocked` with a documented external prerequisite and a backlog entry.
