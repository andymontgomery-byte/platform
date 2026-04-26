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


## 20260426T111736Z Harness Iteration 3

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 90
- Publish result: committed and pushed: Codex loop iteration 3: rubric pass=24/27
- Codex log: `.codex-loop/20260426T105012Z-iteration-003-codex.log`
- Verify log: `.codex-loop/20260426T105012Z-iteration-003-verify.log`
- Judge log: `.codex-loop/20260426T105012Z-iteration-003-judge.log`
- Judge JSON: `.codex-loop/20260426T105012Z-iteration-003-judge.json`


## 2026-04-26 07:32:35 EDT Non-CRUD Edge Function Coverage Iteration

- Chosen rubric item: `edge_functions_for_non_crud_endpoints`.
- Files changed: `supabase/functions/lti-launch-handler/index.ts`, `supabase/functions/lti-launch-handler/deno.json`, `supabase/functions/caliper-event-ingestion/index.ts`, `supabase/functions/caliper-event-ingestion/deno.json`, `supabase/functions/oauth-token-exchange/index.ts`, `supabase/functions/oauth-token-exchange/deno.json`, `supabase/README.md`, `docs/supabase-hosted-database.md`, `docs/spec-gap-backlog.md`, `docs/dictionary-coverage-matrix.md`, `docs/lead-spec-accounting.md`, rendered site docs for those Markdown files, `site/index.html`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `node --check site/app.js` passed; all three new `deno.json` files passed `python3 -m json.tool`; grep confirmed no `SUPABASE_SERVICE_ROLE_KEY` usage under `supabase/functions`; grep confirmed every Edge Function reads `req.headers.get("Authorization")` and forwards `Authorization: authorization`; deployed `lti-launch-handler`, `caliper-event-ingestion`, and `oauth-token-exchange` with `supabase functions deploy ... --use-api`; `supabase functions list --project-ref qzxlgrerjoiamxvnkklq` showed all five functions active; one-off live smoke with a temporary tenant-scoped Supabase Auth user passed for `lti-launch-handler`, `caliper-event-ingestion`, and `oauth-token-exchange` (an earlier helper-based OAuth form attempt returned the expected 400 because the helper JSON-encoded the form body); `python3 scripts/build_site_docs.py` passed; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `python3 scripts/check_spec_conformance.py --write-report site/api/spec-conformance.json` passed with advisory score 100.0; `python3 tests/supabase_tenant_rls_test.py` passed; `python3 tests/supabase_audit_log_test.py` passed; `node --check site/app.js && node --check demo/server.js` passed; `cd demo && npm run reset-db && npm test` passed; `python3 -m json.tool site/api/platform-evaluation.json` and `python3 -m json.tool site/api/spec-conformance.json` passed; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=26, partial=1, fail=0, blocked=0 and reports `edge_functions_for_non_crud_endpoints` as `pass`.
- Expected status change: `edge_functions_for_non_crud_endpoints` `partial` -> `pass`.
- What remains next: `lead_spec_full_accounting` remains `partial`; the evaluator still wants full OneRoster 1.2 accounting and explicit per-field `sourceStandard`/unsupported ledgers across Lead spec fields and values.


## 20260426T113857Z Harness Iteration 4

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 88
- Publish result: committed and pushed: Codex loop iteration 4: rubric pass=26/27
- Codex log: `.codex-loop/20260426T111736Z-iteration-004-codex.log`
- Verify log: `.codex-loop/20260426T111736Z-iteration-004-verify.log`
- Judge log: `.codex-loop/20260426T111736Z-iteration-004-judge.log`
- Judge JSON: `.codex-loop/20260426T111736Z-iteration-004-judge.json`

## 2026-04-26 08:02:48 EDT Lead Spec Full Accounting Iteration

- Chosen rubric item: `lead_spec_full_accounting`.
- Files changed: `dictionary/*.v1.json`; `scripts/generate_oneroster_core.py`, `scripts/generate_qti_core.py`, `scripts/generate_case_core.py`, `scripts/generate_caliper_core.py`, `scripts/generate_integration_governance_core.py`; `scripts/check_dictionary_artifacts.py`; `scripts/check_spec_conformance.py`; `scripts/evaluate_platform.py`; generated dictionary Markdown/OpenAPI/site HTML artifacts; `docs/lead-spec-accounting.md`; `docs/spec-gap-backlog.md`; `docs/dictionary-coverage-matrix.md`; `PLAN.md`; `site/api/spec-conformance.json`; `site/api/platform-evaluation.json`; `PROGRESS.md`.
- Checks run and result: all five dictionary generators passed; `python3 scripts/build_site_docs.py` passed; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values while enforcing `sourceStandard` and unsupported-ledger fields; `python3 -m py_compile` passed for the changed generator/check/evaluator scripts; dictionary and generated OpenAPI JSON validation passed; `python3 scripts/check_spec_conformance.py --write-report site/api/spec-conformance.json` passed with advisory score 100.0; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=27, partial=0, fail=0, blocked=0 and `done=true`.
- Expected status change: `lead_spec_full_accounting` `partial` -> `pass`; evaluator overall `done=false` -> `done=true`.
- What remains next: no non-pass rubric items remain. Future product backlog still includes status manifest cleanup, broader hosted runtime/API slices beyond the current OneRoster core and minimal Edge Function receipts, formal conformance fixtures, production deployment docs, generated dictionary URL cleanup, and Codex loop harness tests.


## 20260426T120824Z Harness Iteration 5

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 88
- Publish result: committed and pushed: Codex loop iteration 5: rubric pass=27/27
- Codex log: `.codex-loop/20260426T113857Z-iteration-005-codex.log`
- Verify log: `.codex-loop/20260426T113857Z-iteration-005-verify.log`
- Judge log: `.codex-loop/20260426T113857Z-iteration-005-judge.log`
- Judge JSON: `.codex-loop/20260426T113857Z-iteration-005-judge.json`

## 2026-04-26 11:29:25 EDT Decision Register Completion Iteration

- Chosen rubric item: `decisions_complete`.
- Files changed: `docs/decisions/standards-overlap-decisions.md`, `docs/decisions/decisions-pending.md`, rendered `site/docs/*` decision/doc pages, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 scripts/build_site_docs.py` passed; dictionary `projects_to` references in the decision register were checked against `dictionary/*.v1.json` and passed with 44 refs; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `python3 -m json.tool site/api/platform-evaluation.json` passed; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=5, partial=3, fail=3, blocked=0 and reports `decisions_complete` as `pass`.
- Expected status change: `decisions_complete` `fail` -> `pass`. The same decision-shape rewrite also moved `decisions_simplify` `fail` -> `pass`.
- What remains next: `projections_match_reality`, `portal_leads_with_decisions`, and `evaluator_runs_each_iteration` remain `fail`; `no_unforced_decisions`, `artifacts_cite_decisions`, and `runtime_coverage_per_spec_honest` remain `partial`. The next override priority is to fix the DEC-013 audit response truth divergence by removing the hard-coded audit count or reading back `audit_log` rows.


## 20260426T153401Z Harness Iteration 1

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 84
- Publish result: committed and pushed: Codex loop iteration 1: rubric pass=6/11
- Codex log: `.codex-loop/20260426T151901Z-iteration-001-codex.log`
- Verify log: `.codex-loop/20260426T151901Z-iteration-001-verify.log`
- Judge log: `.codex-loop/20260426T151901Z-iteration-001-judge.log`
- Judge JSON: `.codex-loop/20260426T151901Z-iteration-001-judge.json`

## 2026-04-26 11:40:23 EDT Audit Response Truth Projection Iteration

- Chosen rubric item: `projections_match_reality`.
- Files changed: `supabase/functions/audited-roster-read/index.ts`, `tests/supabase_audit_log_test.py`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 -m py_compile tests/supabase_audit_log_test.py` passed; `rg -n "logged:\s*5|fields:\s*\[|hard-code|auditRows" supabase/functions/audited-roster-read/index.ts tests/supabase_audit_log_test.py` confirmed the hard-coded audit response was removed and the response now uses `auditRows`; `supabase functions deploy audited-roster-read --project-ref qzxlgrerjoiamxvnkklq --use-api` passed; `python3 tests/supabase_audit_log_test.py` passed against the live Edge Function with 5 request-correlated audit rows and response audit assertions; `git diff --check` passed; `python3 -m json.tool supabase/functions/audited-roster-read/deno.json >/tmp/audited-roster-deno.json` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=7, partial=3, fail=1, blocked=0 and reports `projections_match_reality` as `pass`.
- Expected status change: `projections_match_reality` `fail` -> `pass`.
- What remains next: `evaluator_runs_each_iteration` remains `fail` because the evaluator report still lacks a `projections` summary section; `no_unforced_decisions`, `artifacts_cite_decisions`, and `portal_leads_with_decisions` remain `partial`.


## 20260426T154510Z Harness Iteration 2

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 86
- Publish result: committed and pushed: Codex loop iteration 2: rubric pass=7/11
- Codex log: `.codex-loop/20260426T153401Z-iteration-002-codex.log`
- Verify log: `.codex-loop/20260426T153401Z-iteration-002-verify.log`
- Judge log: `.codex-loop/20260426T153401Z-iteration-002-judge.log`
- Judge JSON: `.codex-loop/20260426T153401Z-iteration-002-judge.json`

## 2026-04-26 11:54:42 EDT Evaluator Projection Summary Iteration

- Chosen rubric item: `evaluator_runs_each_iteration`.
- Files changed: `scripts/evaluate_platform.py`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 -m py_compile scripts/evaluate_platform.py` passed; `python3 scripts/evaluate_platform.py --dry-run` passed with 11 rubric items and 55 evidence files; direct `build_projection_summary` smoke check reported 15 decisions, 99 projection refs, 99 present, 0 missing, and 0 unverified fragments; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=8, partial=2, fail=1, blocked=0 and reports `evaluator_runs_each_iteration` as `pass`; `python3 -m json.tool site/api/platform-evaluation.json >/tmp/platform-evaluation.json` passed; `git diff --check` passed.
- Expected status change: `evaluator_runs_each_iteration` `fail` -> `pass`.
- What remains next: `portal_leads_with_decisions` remains `fail`; `no_unforced_decisions` and `artifacts_cite_decisions` remain `partial`. The next cheapest item is likely exposing `docs/decisions/decisions-pending.md` to the evaluator evidence bundle or replacing the portal's hand-coded generic decision list with the canonical DEC-001 through DEC-015 register.


## 20260426T155915Z Harness Iteration 3

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 86
- Publish result: committed and pushed: Codex loop iteration 3: rubric pass=8/11
- Codex log: `.codex-loop/20260426T154510Z-iteration-003-codex.log`
- Verify log: `.codex-loop/20260426T154510Z-iteration-003-verify.log`
- Judge log: `.codex-loop/20260426T154510Z-iteration-003-judge.log`
- Judge JSON: `.codex-loop/20260426T154510Z-iteration-003-judge.json`

## 2026-04-26 12:06:12 EDT Portal Decision Register Iteration

- Chosen rubric item: `portal_leads_with_decisions`.
- Files changed: `site/app.js`, `site/index.html`, `site/styles.css`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `node --check site/app.js` passed; decision-register parser smoke check parsed 15 decisions and 99 projection refs from `docs/decisions/standards-overlap-decisions.md`; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=9, partial=2, fail=0, blocked=0 and reports `portal_leads_with_decisions` as `pass`; `python3 -m json.tool site/api/platform-evaluation.json >/tmp/platform-evaluation.json` passed.
- Expected status change: `portal_leads_with_decisions` `fail` -> `pass`.
- What remains next: `no_unforced_decisions` remains `partial` because the evaluator evidence still does not include `docs/decisions/decisions-pending.md`; `artifacts_cite_decisions` remains `partial` because SQL/RLS policies, Edge Functions, policy snapshot/static mirrors, and coverage entries still need explicit decision citations.


## 20260426T161024Z Harness Iteration 4

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 87
- Publish result: committed and pushed: Codex loop iteration 4: rubric pass=9/11
- Codex log: `.codex-loop/20260426T155915Z-iteration-004-codex.log`
- Verify log: `.codex-loop/20260426T155915Z-iteration-004-verify.log`
- Judge log: `.codex-loop/20260426T155915Z-iteration-004-judge.log`
- Judge JSON: `.codex-loop/20260426T155915Z-iteration-004-judge.json`

## 2026-04-26 12:14:38 EDT No Unforced Decisions Evidence Iteration

- Chosen rubric item: `no_unforced_decisions`.
- Files changed: `scripts/evaluate_platform.py`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 -m py_compile scripts/evaluate_platform.py` passed; `python3 scripts/evaluate_platform.py --dry-run` passed with 11 rubric items and 56 evidence files; direct `gather_evidence()` smoke check confirmed `docs/decisions/decisions-pending.md` and `docs/decisions/decisions-needed.md` are always-included evidence files at positions 10 and 11; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=10, partial=1, fail=0, blocked=0 and reports `no_unforced_decisions` as `pass`.
- Expected status change: `no_unforced_decisions` `partial` -> `pass`.
- What remains next: `artifacts_cite_decisions` remains `partial`; SQL/RLS policies, policy snapshots, Edge Functions, static API mirrors, and Lead-spec coverage/accounting need explicit decision citations or a documented mapping table.


## 20260426T161912Z Harness Iteration 5

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 82
- Publish result: committed and pushed: Codex loop iteration 5: rubric pass=9/11
- Codex log: `.codex-loop/20260426T161024Z-iteration-005-codex.log`
- Verify log: `.codex-loop/20260426T161024Z-iteration-005-verify.log`
- Judge log: `.codex-loop/20260426T161024Z-iteration-005-judge.log`
- Judge JSON: `.codex-loop/20260426T161024Z-iteration-005-judge.json`


## 2026-04-26 12:26:42 EDT Artifact Decision Citation Iteration

- Chosen rubric item: `artifacts_cite_decisions`.
- Files changed: `scripts/build_static_api.py`, generated static mirrors under `site/api/` and `site/api/views/`, `supabase/migrations/0001_oneroster_core_demo.sql`, `scripts/snapshot_pg_policies.py`, `supabase/policies/pg_policies.snapshot.json`, `supabase/functions/*/index.ts`, `docs/lead-spec-accounting.md`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 scripts/build_static_api.py` passed; `python3 -m py_compile scripts/build_static_api.py scripts/snapshot_pg_policies.py` passed; JSON validation for `site/api/*.json`, `site/api/views/*.json`, and `supabase/policies/pg_policies.snapshot.json` passed; targeted citation check passed with 13 static mirrors, 13 policy snapshot entries, 14 SQL policy/function comments, 5 Edge Functions, and 8 Lead accounting entries; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=11, partial=0, fail=0, blocked=0 and `done=true`.
- Expected status change: `artifacts_cite_decisions` `partial` -> `pass`.
- What remains next: No rubric items remain non-pass; the evaluator reports the platform loop as done.


## 20260426T163014Z Harness Iteration 6

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 90
- Publish result: committed and pushed: Codex loop iteration 6: rubric pass=11/11
- Codex log: `.codex-loop/20260426T161912Z-iteration-006-codex.log`
- Verify log: `.codex-loop/20260426T161912Z-iteration-006-verify.log`
- Judge log: `.codex-loop/20260426T161912Z-iteration-006-judge.log`
- Judge JSON: `.codex-loop/20260426T161912Z-iteration-006-judge.json`


## 2026-04-26 13:07:30 EDT Decision Completeness For Buildability Rubric

- Chosen rubric item: `decisions_complete`.
- Files changed: `docs/decisions/decisions-needed.md`, `docs/decisions/standards-overlap-decisions.md`, rendered `site/docs/*` decision/rubric/override pages from `scripts/build_site_docs.py`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 scripts/build_site_docs.py` passed; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; structural decision check passed with 20 unique needed decisions, no missing six-field decision sections, and the machine-readable section starting after all new decisions at byte 29970; projection summary smoke check passed with 20 decisions, 119 projection refs, 119 present, 0 missing, and 0 unverified fragments; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=6, partial=5, fail=9, blocked=0 and reports `decisions_complete` as `pass`; `python3 -m json.tool site/api/platform-evaluation.json >/tmp/platform-evaluation.json` passed; `git diff --check` passed.
- Expected status change: `decisions_complete` `fail` -> `pass`.
- What remains next: `decisions_have_real_alternatives` remains `partial` and is the next top-layer decision item; dictionary implementation items remain blocked by missing shared-dictionary projection data and generators, especially `dictionary_single_source_of_truth`, `dictionary_resolves_cross_spec_overlaps`, `dictionary_global_enums`, `dictionary_closed_privacy_classes`, and `dictionary_carries_relational_graph`.


## 20260426T171236Z Harness Iteration 1

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 85
- Publish result: committed and pushed: Codex loop iteration 1: rubric pass=6/20
- Codex log: `.codex-loop/20260426T165246Z-iteration-001-codex.log`
- Verify log: `.codex-loop/20260426T165246Z-iteration-001-verify.log`
- Judge log: `.codex-loop/20260426T165246Z-iteration-001-judge.log`
- Judge JSON: `.codex-loop/20260426T165246Z-iteration-001-judge.json`


## 2026-04-26T17:18:32Z Real Alternatives Decision Sweep

- Chosen rubric item: `decisions_have_real_alternatives`.
- Files changed: `docs/decisions/standards-overlap-decisions.md`, `site/docs/decisions-standards-overlap-decisions.html`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 scripts/build_site_docs.py` passed; targeted decision-options smoke check passed with 20 decisions and no remaining DEC-011/DEC-015 strawman wording; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=7, partial=3, fail=10, blocked=0 and reports `decisions_have_real_alternatives` as `pass`.
- Expected status change: `decisions_have_real_alternatives` `partial` -> `pass`.
- What remains next: all decision-layer items now pass. The next top-down fail is `dictionary_single_source_of_truth`: expand `data/data-dictionary.seed.json`, add `scripts/generate_spec_dictionaries.py`, and make CI/checks fail when committed per-spec projections diverge from the canonical seed.


## 20260426T172439Z Harness Iteration 2

- Harness status: pass
- Codex exit code: 0
- Verify exit code: 0
- Spec score before: 100.00
- Spec score after: 100.00
- LLM judge ok: True
- LLM judge recommendation: push
- LLM judge score: 80
- Publish result: committed and pushed: Codex loop iteration 2: rubric pass=7/20
- Codex log: `.codex-loop/20260426T171236Z-iteration-002-codex.log`
- Verify log: `.codex-loop/20260426T171236Z-iteration-002-verify.log`
- Judge log: `.codex-loop/20260426T171236Z-iteration-002-judge.log`
- Judge JSON: `.codex-loop/20260426T171236Z-iteration-002-judge.json`


## 2026-04-26T17:30:30Z Decision Alternatives Follow-up

- Chosen rubric item: `decisions_have_real_alternatives`.
- Files changed: `docs/decisions/standards-overlap-decisions.md`, `site/docs/decisions-standards-overlap-decisions.html`, `site/api/platform-evaluation.json`, and `PROGRESS.md`.
- Checks run and result: `python3 scripts/build_site_docs.py` passed; targeted decision-options smoke check passed with 20 decisions, at least three options each, and no remaining weak DEC-005/DEC-009 option wording; `python3 scripts/check_dictionary_artifacts.py` passed with 5 configs, 58 objects, 568 fields, and 912 values; `git diff --check` passed; `python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json` passed with counts pass=7, partial=4, fail=9, blocked=0 and reports `decisions_have_real_alternatives` as `pass`.
- Expected status change: `decisions_have_real_alternatives` `partial` -> `pass`.
- What remains next: all decision-layer items now pass. The next top-down fail remains `dictionary_single_source_of_truth`: expand `data/data-dictionary.seed.json`, add `scripts/generate_spec_dictionaries.py`, and make CI/checks fail when committed per-spec projections diverge from the canonical seed.
