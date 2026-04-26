# Platform Evaluation Rubric

This rubric is the source of truth for what "done" means on this platform. It is graded by an LLM evaluator (`scripts/evaluate_platform.py`), not by file-presence checks. The deterministic score gate (`scripts/check_spec_conformance.py`) is now **advisory only** — it provides signal to the LLM, but does not gate publish.

The Codex loop iterates until every requirement below is `pass` (or every remaining requirement is `blocked` for a documented external reason).

## The shape of this rubric

A great platform's source of truth is **decisions**, not checklist items. Every other artifact (dictionary, schema, RLS policy, Edge Function, static mirror, audit log, docs) is a *projection* of decisions. If decisions are sharp and correctly forced, simplicity falls out for free — because the same decision shapes the SQL column, the OpenAPI field, the privacy class, the RLS predicate, and what's allowed on each surface.

This rubric reflects that. Decisions are the spine. The other items grade whether the spine is real and whether reality matches it.

A decision artifact has:

- **id** — stable identifier (`DEC-NNN-slug`)
- **question** — the real-world ambiguity or trade-off
- **options_considered** — the alternatives that were on the table
- **choice** — the chosen option, in plain language
- **consequences** — what becomes simpler because of this choice; what new constraint it creates
- **projects_to** — the literal list of fields, tables, policies, surfaces, scopes, and Edge Functions this decision determines

A great decision *deletes work*. If the consequences section cannot name something this decision makes unnecessary, the decision is suspect.

## How to read this file

Each requirement has:

- **id** — stable identifier the evaluator reports against
- **requirement** — what must be true
- **how_to_verify** — what the evaluator should check, in plain language
- **substance_check** — what counts as a real pass vs. a stub
- **blocked_if** — external conditions that flip the item to `blocked` instead of `fail`

Status values: `pass`, `partial`, `fail`, `blocked`.

## Categories

1. Decisions as the spine
2. Projections match reality
3. Vertical slice
4. Loop and harness hygiene

---

## 1. Decisions as the spine

### decisions_complete

- **requirement:** Every required decision area has a documented decision with id, question, options considered, choice, consequences, and a `projects_to` list. Required areas are listed in `docs/decisions/decisions-needed.md` and grow as the platform grows.
- **how_to_verify:** Read `docs/decisions/decisions-needed.md` and `docs/decisions/`. For each entry in `decisions-needed.md`, confirm a decision exists (in `docs/decisions/standards-overlap-decisions.md` or a per-decision file) with all six fields populated. Confirm the consequences section names at least one piece of work the decision eliminates or simplifies.
- **substance_check:** A decision whose `consequences` is "TBD" or only lists what the decision *creates* (not what it removes) fails. A decision without a `projects_to` list fails. Required areas at minimum: person/agent, learning context, roles, enrollment vs membership, results/scores, standards alignment, identifiers, time/session, content/resource, tenancy AND privacy surfaces, runtime coverage per spec, audit response semantics, static mirror policy, service-role policy. The last five are the new ones added when the rubric was restructured around decisions.
- **blocked_if:** never.

### no_unforced_decisions

- **requirement:** Every cross-spec overlap, runtime trade-off, or privacy/security choice is either decided in `docs/decisions/` or listed in `docs/decisions/decisions-pending.md` with an owner and a target date. Nothing important is silently TBD.
- **how_to_verify:** Read `docs/decisions/decisions-pending.md`. Confirm every pending entry has `owner`, `target_date`, and a one-line description of why it matters. Cross-reference against the rubric and the codebase: any artifact that exists without a decision behind it is a forced decision masquerading as a fact.
- **substance_check:** "TBD" without an owner fails. A pending entry whose target date is past fails. The pending file existing alone is not enough — pending items must reference what blocks the decision (e.g., "needs council input on multi-tenant key rotation").
- **blocked_if:** never.

### decisions_simplify

- **requirement:** Each decision's `consequences` section names what the decision makes unnecessary or simpler — not just what it requires. A great decision deletes work.
- **how_to_verify:** For each decision, read the consequences section. Confirm at least one bullet starts with words like "removes the need for," "makes X redundant," "lets Y be derived," "eliminates," or equivalent.
- **substance_check:** A consequences section that only adds requirements (e.g., "every fact table must carry tenant_id") without naming what it removes (e.g., "removes the need for per-table access checks in application code; RLS is the single gate") is `partial`. Decisions that genuinely cannot simplify anything are rare and must be marked `simplifies: none` with a reason.
- **blocked_if:** never.

---

## 2. Projections match reality

### artifacts_cite_decisions

- **requirement:** Every dictionary field, RLS policy, Edge Function, OAuth scope mapping, static API mirror, and Lead-spec coverage entry cites the decision that produced it via a `decision_id` (or equivalent) reference. Anything without a citation is an orphan.
- **how_to_verify:** Run a structural check across `dictionary/*.v1.json`, `supabase/migrations/*.sql`, `supabase/policies/pg_policies.snapshot.json`, `supabase/functions/*/index.ts`, `site/api/*.json`, and `docs/lead-spec-accounting.md`. For each field/policy/function/mirror, confirm a `decision_id` (in JSON), an inline comment naming a decision (in SQL/TS), or a documented mapping table (in MD). Orphans fail the item.
- **substance_check:** A `decision_id` that does not match any decision in `docs/decisions/` fails (broken link). A field with `decision_id: "none"` is acceptable only if the decisions-pending file or a per-field exemption explains why no decision applies. Static mirror files (`site/api/*.json`) must be covered by the static-mirror-policy decision or fail.
- **blocked_if:** never.

### projections_match_reality

- **requirement:** For every decision, the artifacts in its `projects_to` list actually exist, are correctly shaped, and don't contradict the decision. The decision is the assertion; the projection is the implementation; they must agree.
- **how_to_verify:** For each decision, walk its `projects_to` list. For each projected artifact: confirm it exists, confirm its shape matches the decision (e.g., if the decision says "tenant_id JWT-claim predicate, no `using(true)`," confirm the policy snapshot proves it), confirm no sibling artifact exists that would contradict the decision (e.g., if the privacy-surfaces decision says "no surface may expose `directory` PII without audit," confirm `site/api/people.json` does NOT carry such fields).
- **substance_check:** A divergence between decision and projection fails this item and must be reported with the decision id, the artifact, and the specific contradiction. Examples: an Edge Function response that hard-codes a logged count without reading from the audit table contradicts an audit-truthfulness decision; a static `site/api/people.json` carrying `email` (privacy_class `directory`) contradicts a privacy-surfaces decision that says only `public` and `operational` may be statically mirrored. Both fail this item, not via separate items.
- **blocked_if:** never.

### runtime_coverage_per_spec_honest

- **requirement:** Each Lead spec's coverage row honestly reports whether it has runtime backing, partial runtime backing, or doc-only. The coverage matrix and the runtime-coverage decision must agree.
- **how_to_verify:** Read `docs/dictionary-coverage-matrix.md` and the runtime-coverage decision. For each Lead spec, the matrix's "runnable slice" column must match what is actually deployed (Supabase tables + Edge Functions + tests). A spec with 100+ documented fields and zero runtime tables must show "doc-only" with a target date in `decisions-pending.md`, not "see backlog."
- **substance_check:** Generated docs do not count as runtime. A spec marked "runtime: yes" must have at least one fact table with non-trivial RLS, at least one test that hits the live URL, and at least one Edge Function or PostgREST endpoint exercised by that test. Otherwise `partial` or `fail`.
- **blocked_if:** never.

---

## 3. Vertical slice

### vertical_slice_runs_end_to_end

- **requirement:** The platform has at least one Lead spec slice that runs end-to-end against the hosted runtime with one curl, with provable tenant isolation and audited sensitive reads. The slice is callable from the open internet using only documented public credentials.
- **how_to_verify:** From a clean checkout: run `cd demo && npm run reset-db && npm test` (passes locally). From outside the repo: `curl` against the hosted PostgREST URL with the publishable key returns spec-shaped JSON for the slice's core endpoints. Run `python3 tests/supabase_tenant_rls_test.py` and `python3 tests/supabase_audit_log_test.py` against the live URL — both pass. The portal includes a copy-pasteable curl that works.
- **substance_check:** Static mirrors do not count as the slice. The slice must hit PostgREST or Edge Functions backed by Postgres with real RLS. Tests must use distinct tenant JWTs and confirm cross-tenant reads are blocked. Audit tests must read the `audit_log` table after the call (not just the function's response body) to confirm rows were written with `client_id`, `scope`, `purpose`, `field_accessed`, `tenant_id`, and `timestamp`.
- **blocked_if:** Supabase project intentionally torn down or evaluator credentials not provided.

### portal_leads_with_decisions

- **requirement:** The developer-facing portal leads with the decision register — why before what. A new developer should see the platform's choices first, then the dictionary, then the API.
- **how_to_verify:** Open the portal landing page. Confirm a "Decisions" section appears above or alongside "Dictionary" and "API" in primary navigation, that it links to `docs/decisions/`, and that each decision has a one-line summary readable on the site (not just a link to a Markdown file).
- **substance_check:** A nav link to a 845-line single Markdown dump fails the spirit of the item. Each decision must be addressable with its own anchor (`#dec-001-person-agent-subject`) and have its `consequences` and `projects_to` sections rendered. Linking to raw `.md` from the site fails per `portal_renders_as_html` (now folded in here).
- **blocked_if:** never.

---

## 4. Loop and harness hygiene

### evaluator_runs_each_iteration

- **requirement:** `scripts/evaluate_platform.py` runs at the end of each loop iteration and writes `site/api/platform-evaluation.json` with `done` flag, per-item status, and a per-decision projection-match summary.
- **how_to_verify:** Read the most recent iteration's logs and confirm the evaluator wrote a fresh report. Report contains items + a `projections` section summarizing decision-to-reality matches.
- **substance_check:** Report missing the projections summary fails (it's the new spine signal).
- **blocked_if:** never.

### loop_overrides_respected

- **requirement:** The Codex loop reads `docs/loop-overrides.md` at the start of every iteration and passes its contents to the Codex prompt as authoritative guidance. Loop halts when a `## Pause` section contains the literal token `PAUSE` on its own line.
- **how_to_verify:** Inspect `scripts/codex_loop.py`. Confirm the helper reads the file, the PAUSE check halts the loop before the next iteration runs, and the prompt builder injects overrides under a "Human overrides" section.
- **substance_check:** A loop that reads the file but never injects it fails. PAUSE check that runs after the next iteration fails.
- **blocked_if:** never.

### loop_terminates_on_done

- **requirement:** The loop stops iterating when every rubric item is `pass`, or when every remaining item is `blocked` with a documented prerequisite. Hard caps (max iterations, stall detection, cost ceiling) still apply as safety rails.
- **how_to_verify:** Read the loop driver. Confirm termination condition references the LLM evaluator's `done` flag, not a numeric score threshold.
- **substance_check:** Numeric-threshold gating fails this item.
- **blocked_if:** never.

---

## Summary

| Category | Count |
|---|---|
| Decisions as the spine | 3 |
| Projections match reality | 3 |
| Vertical slice | 2 |
| Loop and harness hygiene | 3 |
| **Total** | **11** |

The loop is "done" when all 11 are `pass`, or when every remaining item is `blocked` with a documented external prerequisite.

## What this rubric replaces

The previous rubric had 27 items. Many of them — `tenant_isolation_enforced`, `rls_enabled_on_referenced_tables`, `service_role_calls_allowlisted`, `edge_functions_propagate_user_jwt`, `audit_log_for_sensitive_reads`, `oauth_scopes_mapped_to_fields`, `privacy_class_on_every_field`, `decision_traces_to_dictionary`, `lead_spec_full_accounting`, `coverage_matrix_distinguishes_layers`, `gap_backlog_current` — were checking individual projections of decisions that already existed (or should have existed). This rubric folds them into `projections_match_reality` and `artifacts_cite_decisions`. If a privacy decision says "no surface may expose `directory` PII without audit," then a static `site/api/people.json` carrying email fails the projection check automatically — no separate "static_mirrors_enforce_privacy_class" item needed.

This is fewer items but harder to fake. Each item now requires the decision to actually exist, the projection to actually match, and the simplification to actually be claimed.
