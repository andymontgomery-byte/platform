# PLAN

This file is the persistent task memory for `scripts/codex_loop.py`.

Goal: incrementally move this repository toward satisfying the platform spec in `/Users/andymontgomery/Downloads/WF - Platform - 260424-144348.md`.

Current public backlog: `docs/spec-gap-backlog.md`.

## Loop Rules

- Do one focused improvement per Codex iteration.
- Prefer the easiest open backlog item first.
- Touch only files needed for that improvement.
- Do not revert user work or unrelated dirty files.
- Do not push manually. The harness commits and pushes only after verification passes and the spec score improves.
- Keep generated artifacts in sync with structured dictionary sources.
- Update `PROGRESS.md` after every iteration.
- If you discover a missing spec requirement that is not tracked, add it to `docs/spec-gap-backlog.md`, update `docs/dictionary-coverage-matrix.md` if coverage changes, and mention it in `PROGRESS.md`.
- Treat `scripts/check_spec_conformance.py` and `site/api/spec-conformance.json` as the deterministic spec scoreboard.

## Current Priority Order

- [x] Finish item 7 from `docs/spec-gap-backlog.md`: convert CASE to a structured source dictionary and generated artifacts.
- [x] Wire CASE into `scripts/check_dictionary_artifacts.py`.
- [x] Update the coverage matrix and Lead spec accounting for generated CASE coverage.
- [x] Convert Caliper to a structured source dictionary and generated artifacts.
- [x] Convert LTI/LTI Advantage, Security Framework, and Data Privacy to structured source dictionaries.
- [x] Add generated cross-spec decision traces.
- [x] Expand OneRoster full 1.2 accounting beyond the current core generated slice.
- [ ] Add a machine-readable platform status manifest.
- [ ] Improve the browser "try it" workflow with more sample queries.
- [ ] Add real hosted database/API infrastructure after GitHub-only work is exhausted.

## Completion Target

The current project is not complete until every Lead spec is either:

- Represented in a structured dictionary source and generated into SQL comments, OpenAPI descriptions, and rendered portal docs.
- Implemented as a runnable SQL/API slice where required by the spec.
- Explicitly listed as unsupported or deferred with a reason.
