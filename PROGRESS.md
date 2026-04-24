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
