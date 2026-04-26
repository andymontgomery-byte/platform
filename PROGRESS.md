# PROGRESS

This file is append-only loop memory for `scripts/codex_loop.py`.

## 2026-04-24 Initial State

- OneRoster core is the strongest generated and runnable slice.
- QTI repository projection now has a structured dictionary and generated SQL/OpenAPI/docs, but no runtime import/projection slice yet.
- CASE is the next open backlog item. A partial `dictionary/case-core.v1.json` may exist if work was interrupted; continue from it instead of deleting it.
- Caliper, LTI/LTI Advantage, Security Framework, and Data Privacy are still Markdown-only.
- GitHub Pages can host static docs, static JSON, and browser SQL, but cannot satisfy real hosted database/API runtime requirements.

## 2026-04-24 Harness Policy Update

- The loop must compare work to the actual spec, not only run syntax and generated-artifact checks.
- `scripts/check_spec_conformance.py` is the deterministic score gate.
- `site/api/spec-conformance.json` is the machine-readable public report for AI agents.
- The harness should commit and push only when Codex exits successfully, VERIFY passes, and the spec score improves over the start of the iteration.
- Newly discovered gaps must become backlog TODOs, not only comments in logs.

## 2026-04-24 CASE + Opus Judge Iteration

- Chosen checklist item: item 7, convert CASE to a structured source dictionary and generated artifacts.
- Files changed: added `dictionary/case-core.v1.json`, `scripts/generate_case_core.py`, generated CASE SQL/OpenAPI/Markdown/HTML artifacts, and updated VERIFY/backlog/coverage/Lead accounting.
- Harness changed: `scripts/codex_loop.py` now loads Anthropic API credentials from `~/.zprofile`, resolves `opus-4.7` to `claude-opus-4-7`, runs the LLM judge with adaptive `xhigh` thinking, gates publish on the judge, and stops hung worker/VERIFY processes with timeouts.
- Checks run: full VERIFY block passed, including generators, spec conformance, JSON validation, Python compile, Node syntax checks, demo DB reset/test, and `git diff --check`.
- Spec score impact: deterministic score improved from 81.05 to 87.37.
- LLM judge: Opus 4.7/xhigh judged the final diff as improved, not regressed, and recommended `push`.
- New gaps found by the judge: tracked backlog items 25 and 26 for duplicate/orphaned generated dictionary pages and `scripts/codex_loop.py` runbook/smoke tests.
- What remains next: wire CASE into `scripts/check_dictionary_artifacts.py`, then convert Caliper to a structured/generated dictionary.

## 2026-04-24 17:21:06 EDT Caliper Generated Dictionary Iteration

- Chosen checklist item: `shared_dictionary_caliper`, convert Caliper to a structured source dictionary and generated artifacts.
- Files changed: added `dictionary/caliper-core.v1.json`, `scripts/generate_caliper_core.py`, generated Caliper SQL/OpenAPI/Markdown/HTML artifacts, and updated VERIFY, artifact checking, backlog, coverage matrix, Lead spec accounting, README, portal link text, rendered docs, and `site/api/spec-conformance.json`.
- Checks run and result: Caliper dictionary JSON validation passed; Caliper generator py_compile passed; OneRoster/QTI/CASE/Caliper generators passed; `build_static_api.py` and `build_site_docs.py` passed; `check_dictionary_artifacts.py` passed with 4 configs, 45 objects, 430 fields, and 753 values; `check_spec_conformance.py --write-report site/api/spec-conformance.json --min-score 75` passed with score 93.68; full generator/build/check py_compile passed; generated OpenAPI/report/index JSON validation passed; `node --check site/app.js` and `node --check demo/server.js` passed; `cd demo && npm run reset-db && npm test` passed; `git diff --check` passed.
- Spec score impact expected: +6 deterministic points, from 87.37 to 93.68, because `shared_dictionary_caliper` now passes.
- New gaps found: none.
- What remains next: item 9, convert LTI/LTI Advantage, Security Framework, and Data Privacy to structured/generated or explicitly deferred artifacts; the public report now leaves only `shared_dictionary_lti_security_privacy` open.


## 20260424T212302Z Harness Iteration 1

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 87.37
- Spec score after: 93.68
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 90
- Publish result: committed and pushed: Codex loop iteration 1: improve spec score to 93.68
- Codex log: `.codex-loop/20260424T211108Z-iteration-001-codex.log`
- Verify log: `.codex-loop/20260424T211108Z-iteration-001-verify.log`
- Judge log: `.codex-loop/20260424T211108Z-iteration-001-judge.log`
- Judge JSON: `.codex-loop/20260424T211108Z-iteration-001-judge.json`

## 2026-04-24 17:47:31 EDT Integration/Governance Generated Dictionary Iteration

- Chosen checklist item: `shared_dictionary_lti_security_privacy`, convert LTI/LTI Advantage, Security Framework, and Data Privacy to structured/generated or explicitly deferred artifacts.
- Files changed: added `dictionary/integration-governance-core.v1.json`, `scripts/generate_integration_governance_core.py`, generated integration/governance SQL/OpenAPI/Markdown/HTML artifacts, and updated VERIFY, artifact checking, backlog, coverage matrix, Lead spec accounting, README, portal link text, rendered docs, PLAN, and `site/api/spec-conformance.json`.
- Checks run and result: integration/governance dictionary JSON validation passed; generator and artifact checker py_compile passed; all OneRoster/QTI/CASE/Caliper/integration generators passed; `build_static_api.py` and `build_site_docs.py` passed; `check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `check_spec_conformance.py --write-report site/api/spec-conformance.json --min-score 75` passed with score 100.0; full generator/build/check py_compile passed; generated OpenAPI/report/index JSON validation passed; `node --check site/app.js` and `node --check demo/server.js` passed; `cd demo && npm run reset-db && npm test` passed; `git diff --check` passed.
- Spec score impact expected: +6 deterministic points, from 93.68 to 100.0, because `shared_dictionary_lti_security_privacy` now passes and `openGaps` is empty.
- New gaps found: none.
- What remains next: deterministic score-gate coverage is fully passing for the current docs/dictionary/demo criteria; this is not platform completion. Remaining public backlog items start with full OneRoster 1.2 accounting and later runnable/backend work.


## 20260424T214917Z Harness Iteration 2

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 93.68
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 92
- Publish result: committed and pushed: Codex loop iteration 2: improve spec score to 100.00
- Codex log: `.codex-loop/20260424T213303Z-iteration-002-codex.log`
- Verify log: `.codex-loop/20260424T213303Z-iteration-002-verify.log`
- Judge log: `.codex-loop/20260424T213303Z-iteration-002-judge.log`
- Judge JSON: `.codex-loop/20260424T213303Z-iteration-002-judge.json`

## 2026-04-25 16:26:17 EDT Decision Trace Iteration

- Chosen rubric item: `decision_traces_to_dictionary`.
- Files changed: added `decision_id` metadata to every field in `dictionary/*.v1.json`; added machine-readable `produces_fields` JSON to `docs/decisions/standards-overlap-decisions.md`; updated all dictionary generators to emit OpenAPI `x-decisionId` and generated Markdown/HTML decision columns; updated `scripts/check_dictionary_artifacts.py` to enforce bidirectional trace consistency; regenerated generated dictionary/OpenAPI/site artifacts; marked the trace work done in `PLAN.md` and `docs/spec-gap-backlog.md`; removed the stale decision-trace advisory gap from `scripts/check_spec_conformance.py` and regenerated reports.
- Checks run and result: all five dictionary generators passed; `python3 scripts/build_static_api.py` passed; `python3 scripts/build_site_docs.py` passed; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; generator/build/check py_compile passed; generated OpenAPI JSON validation passed; `python3 scripts/check_spec_conformance.py --write-report site/api/spec-conformance.json` passed with advisory score 100.0; `node --check site/app.js` passed; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed and now reports `decision_traces_to_dictionary` as `pass`.
- Expected status change: `decision_traces_to_dictionary` `fail` -> `pass`.
- What remains next: address the remaining rubric non-pass items in the latest evaluator report: `tenant_isolation_enforced`, `audit_log_for_sensitive_reads`, and `edge_functions_for_non_crud_endpoints` are fail; `developer_guide_present`, `lead_spec_full_accounting`, `vertical_slice_runnable_locally`, `try_it_surface_present`, `oauth_scopes_mapped_to_fields`, and `rls_enabled_on_referenced_tables` are partial; `edge_functions_propagate_user_jwt` remains blocked until Edge Functions exist.


## 20260425T203148Z Harness Iteration 1

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 87
- Publish result: committed and pushed: Codex loop iteration 1: rubric pass=16/25
- Codex log: `.codex-loop/20260425T200915Z-iteration-001-codex.log`
- Verify log: `.codex-loop/20260425T200915Z-iteration-001-verify.log`
- Judge log: `.codex-loop/20260425T200915Z-iteration-001-judge.log`
- Judge JSON: `.codex-loop/20260425T200915Z-iteration-001-judge.json`

## 2026-04-25 16:40:58 EDT OneRoster Local Users Route Iteration

- Chosen rubric item: `vertical_slice_runnable_locally`.
- Files changed: `demo/server.js`, `demo/test.js`, `demo/README.md`, `README.md`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `node --check demo/server.js` passed; `cd demo && npm run reset-db && npm test` passed with `demo-api-ok`; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=17, partial=4, fail=3, blocked=1 and reports `vertical_slice_runnable_locally` as `pass`.
- Expected status change: `vertical_slice_runnable_locally` `partial` -> `pass`.
- What remains next: latest evaluator non-pass items are `developer_guide_present`, `lead_spec_full_accounting`, `oauth_scopes_mapped_to_fields`, and `rls_enabled_on_referenced_tables` as partial; `tenant_isolation_enforced`, `audit_log_for_sensitive_reads`, and `edge_functions_for_non_crud_endpoints` as fail; `edge_functions_propagate_user_jwt` as blocked until Edge Functions exist.


## 20260425T204547Z Harness Iteration 2

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 72
- Publish result: skipped: rubric did not progress this iteration
- Codex log: `.codex-loop/20260425T203148Z-iteration-002-codex.log`
- Verify log: `.codex-loop/20260425T203148Z-iteration-002-verify.log`
- Judge log: `.codex-loop/20260425T203148Z-iteration-002-judge.log`
- Judge JSON: `.codex-loop/20260425T203148Z-iteration-002-judge.json`

## 2026-04-25 16:54:41 EDT Developer Guide Evidence Iteration

- Chosen rubric item: `developer_guide_present`.
- Files changed: `site/index.html`, `site/app.js`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `node --check site/app.js` passed; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=18, partial=3, fail=3, blocked=1 and reports `developer_guide_present` as `pass`.
- Expected status change: `developer_guide_present` `partial` -> `pass`.
- What remains next: latest evaluator non-pass items are `lead_spec_full_accounting`, `oauth_scopes_mapped_to_fields`, and `rls_enabled_on_referenced_tables` as partial; `tenant_isolation_enforced`, `audit_log_for_sensitive_reads`, and `edge_functions_for_non_crud_endpoints` as fail; `edge_functions_propagate_user_jwt` as blocked until Edge Functions exist.


## 20260425T205857Z Harness Iteration 3

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: do_not_push
- LLM judge score: 55
- Publish result: skipped: LLM judge recommended do_not_push
- Codex log: `.codex-loop/20260425T204547Z-iteration-003-codex.log`
- Verify log: `.codex-loop/20260425T204547Z-iteration-003-verify.log`
- Judge log: `.codex-loop/20260425T204547Z-iteration-003-judge.log`
- Judge JSON: `.codex-loop/20260425T204547Z-iteration-003-judge.json`

## 2026-04-25 17:10:03 EDT OAuth Scope Field Mapping Iteration

- Chosen rubric item: `oauth_scopes_mapped_to_fields`.
- Files changed: `dictionary/integration-governance-core.v1.json`, `scripts/generate_integration_governance_core.py`, `openapi/generated/integration-governance-core.v0.json`, `docs/generated/integration-governance-core-dictionary.md`, `docs/spec-gap-backlog.md`, `site/docs/integration-governance-core-dictionary.html`, `site/docs/generated-integration-governance-core-dictionary.html`, `site/docs/spec-gap-backlog.html`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 -m json.tool dictionary/integration-governance-core.v1.json` passed; `python3 -m py_compile scripts/generate_integration_governance_core.py scripts/build_site_docs.py scripts/check_dictionary_artifacts.py` passed; `python3 scripts/generate_integration_governance_core.py` passed; `python3 scripts/build_site_docs.py` passed; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `python3 -m json.tool openapi/generated/integration-governance-core.v0.json` passed; `python3 scripts/check_spec_conformance.py --write-report site/api/spec-conformance.json` passed with advisory score 100.0; `node --check site/app.js` passed; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=19, partial=2, fail=3, blocked=1 and reports `oauth_scopes_mapped_to_fields` as `pass`.
- Expected status change: `oauth_scopes_mapped_to_fields` `partial` -> `pass`; evaluator also moved `gap_backlog_current` `partial` -> `pass` because the backlog now distinguishes done scope mapping from remaining runtime enforcement.
- What remains next: `lead_spec_full_accounting` and `rls_enabled_on_referenced_tables` are partial; `tenant_isolation_enforced`, `audit_log_for_sensitive_reads`, and `edge_functions_for_non_crud_endpoints` are fail; `edge_functions_propagate_user_jwt` remains blocked until Edge Functions exist.


## 20260425T211537Z Harness Iteration 4

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 82
- Publish result: skipped: rubric did not progress this iteration
- Codex log: `.codex-loop/20260425T205857Z-iteration-004-codex.log`
- Verify log: `.codex-loop/20260425T205857Z-iteration-004-verify.log`
- Judge log: `.codex-loop/20260425T205857Z-iteration-004-judge.log`
- Judge JSON: `.codex-loop/20260425T205857Z-iteration-004-judge.json`

## 2026-04-26 06:23:16 EDT Tenant Isolation RLS Iteration

- Chosen rubric item: `tenant_isolation_enforced`.
- Files changed: `supabase/migrations/0001_oneroster_core_demo.sql`, `supabase/seed.sql`, `supabase/policies/pg_policies.snapshot.json`, `tests/supabase_tenant_rls_test.py`, `VERIFY.md`, `scripts/evaluate_platform.py`, `docs/admin-operations.md`, `docs/spec-gap-backlog.md`, `docs/supabase-hosted-database.md`, `supabase/README.md`, generated site docs for the changed docs, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: live Supabase migration, seed, and smoke SQL passed; `python3 scripts/snapshot_pg_policies.py` passed; `python3 scripts/check_supabase_rest.py` passed and returned seeded `/people`, `/class_roster`, and `/gradebook_results` rows; `python3 tests/supabase_tenant_rls_test.py` passed with tenant A seeing 6 rows, tenant B seeing 1 row, and neither tenant reading the other's `people` row; all generator/build/check commands from `VERIFY.md` passed through local demo API tests; `python3 -m json.tool supabase/policies/pg_policies.snapshot.json` passed; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=23, partial=1, fail=3, blocked=0.
- Expected status change: `tenant_isolation_enforced` `fail` -> `pass`; the same schema/policy work also moved `rls_enabled_on_referenced_tables` `fail` -> `pass` while preserving `vertical_slice_callable_externally` as `pass`.
- What remains next: `lead_spec_full_accounting` remains `partial`; `audit_log_for_sensitive_reads`, `edge_functions_for_non_crud_endpoints`, and `edge_functions_propagate_user_jwt` are reported as `fail` in the latest evaluator report. The next override priority is audit logging after Edge Functions unless the loop first follows the listed order and ships a real Edge Function.


## 20260426T103047Z Harness Iteration 1

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 88
- Publish result: committed and pushed: Codex loop iteration 1: rubric pass=21/27
- Codex log: `.codex-loop/20260426T100322Z-iteration-001-codex.log`
- Verify log: `.codex-loop/20260426T100322Z-iteration-001-verify.log`
- Judge log: `.codex-loop/20260426T100322Z-iteration-001-judge.log`
- Judge JSON: `.codex-loop/20260426T100322Z-iteration-001-judge.json`

## 2026-04-26 06:43:57 EDT Gradebook Edge Function Iteration

- Chosen rubric item: `edge_functions_for_non_crud_endpoints`.
- Files changed: `supabase/functions/gradebook-bulk-submit/index.ts`, `supabase/functions/gradebook-bulk-submit/deno.json`, `supabase/migrations/0001_oneroster_core_demo.sql`, `supabase/policies/pg_policies.snapshot.json`, `supabase/README.md`, `docs/supabase-hosted-database.md`, `docs/spec-gap-backlog.md`, rendered site docs for the changed docs, `site/index.html`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: live Supabase migration, seed, smoke SQL, and policy snapshot generation passed; `supabase functions deploy gradebook-bulk-submit --project-ref qzxlgrerjoiamxvnkklq --use-api` passed; live function call with a temporary tenant-scoped Supabase Auth JWT returned HTTP 200 with `accepted: 1`; live seed was restored afterward; `supabase functions list` showed `gradebook-bulk-submit` active with `verify_jwt: true`; `python3 scripts/check_supabase_rest.py` passed; `python3 tests/supabase_tenant_rls_test.py` passed; all dictionary generators, `build_static_api.py`, `build_site_docs.py`, `check_dictionary_artifacts.py`, `check_spec_conformance.py --write-report site/api/spec-conformance.json`, Python compile, OpenAPI/report JSON validation, `node --check site/app.js`, `node --check demo/server.js`, `cd demo && npm run reset-db && npm test`, and `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=24, partial=2, fail=1, blocked=0.
- Expected status change: `edge_functions_for_non_crud_endpoints` `fail` -> `partial` because the first real non-CRUD function is now shipped and live; `edge_functions_propagate_user_jwt` `blocked` -> `pass` because the function forwards `req.headers.get("Authorization")` into the Supabase client and uses no service-role key.
- What remains next: `audit_log_for_sensitive_reads` remains `fail`; `lead_spec_full_accounting` and `edge_functions_for_non_crud_endpoints` remain `partial`. The evaluator wants the remaining non-CRUD functions for LTI launch, Caliper ingestion, OAuth token exchange, and/or QTI import before giving the Edge Function item a full pass.


## 20260426T105012Z Harness Iteration 2

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 90
- Publish result: committed and pushed: Codex loop iteration 2: rubric pass=24/27
- Codex log: `.codex-loop/20260426T103047Z-iteration-002-codex.log`
- Verify log: `.codex-loop/20260426T103047Z-iteration-002-verify.log`
- Judge log: `.codex-loop/20260426T103047Z-iteration-002-judge.log`
- Judge JSON: `.codex-loop/20260426T103047Z-iteration-002-judge.json`

## 2026-04-26 07:04:45 EDT Sensitive-Read Audit Log Iteration

- Chosen rubric item: `audit_log_for_sensitive_reads`.
- Files changed: `supabase/migrations/0001_oneroster_core_demo.sql`, `supabase/seed.sql`, `supabase/policies/pg_policies.snapshot.json`, `supabase/functions/audited-roster-read/index.ts`, `supabase/functions/audited-roster-read/deno.json`, `tests/supabase_audit_log_test.py`, `VERIFY.md`, `docs/admin-operations.md`, `docs/supabase-hosted-database.md`, `docs/spec-gap-backlog.md`, rendered site docs for the changed docs, `site/index.html`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: live Supabase migration and seed load passed; `supabase functions deploy audited-roster-read --project-ref qzxlgrerjoiamxvnkklq --use-api` passed; `python3 tests/supabase_audit_log_test.py` passed with direct restricted REST blocked and 5 audit rows for `person_ada`; `python3 tests/supabase_tenant_rls_test.py` passed; `python3 scripts/check_supabase_rest.py` passed; `python3 scripts/snapshot_pg_policies.py` passed with 10 tables; all dictionary generators plus `python3 scripts/build_static_api.py` and `python3 scripts/build_site_docs.py` passed; `python3 scripts/check_dictionary_artifacts.py` passed; `python3 scripts/check_spec_conformance.py --write-report site/api/spec-conformance.json` passed with advisory score 100.0; JSON validation for the policy snapshot, advisory report, OpenAPI files, API index, and evaluator report passed; Python compile for scripts and Supabase tests passed; `node --check site/app.js` and `node --check demo/server.js` passed; `cd demo && npm run reset-db && npm test` passed with `demo-api-ok`; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=25, partial=2, fail=0, blocked=0 and reports `audit_log_for_sensitive_reads` as `pass`. Local `deno check` could not run because Deno is not installed, but Supabase deployment accepted the function.
- Expected status change: `audit_log_for_sensitive_reads` `fail` -> `pass`.
- What remains next: latest evaluator non-pass items are `lead_spec_full_accounting` and `edge_functions_for_non_crud_endpoints` as `partial`. The next highest-leverage item is likely another real non-CRUD Edge Function for LTI launch, Caliper ingestion, or OAuth token exchange, unless the loop chooses to finish Lead spec accounting first.
