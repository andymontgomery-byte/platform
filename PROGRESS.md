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
