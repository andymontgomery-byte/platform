# Loop overrides

This file is the **human-to-loop channel**. The Codex loop reads it at the start of every iteration and treats its contents as authoritative — they supersede rubric defaults and any prior decision recorded elsewhere.

Edit this file (commit + push to `main`) to communicate with the running loop. The loop picks up changes on the next iteration.

## Pause

<!--
Leave the section below empty to keep running.
Write the literal token PAUSE on its own line to halt the loop after the current iteration finishes.
-->



## Decisions

<!--
One bullet per override. Format:
- For `<rubric-item-id>`: <what to accept / reject / treat differently and why>.
Codex must follow these even if they conflict with the rubric's substance_check.
Move stale entries to the bottom of this section under "## Decisions (archived)" once they are no longer in effect.
-->

- **Rubric was restructured around decisions** (2026-04-26 14:30 UTC). The old 27-item rubric is replaced by 11 items organized around decisions as the spine. Read `docs/eval-rubric.md` from scratch — do not assume continuity with prior items.
- **Priority order for the next iterations:** the spine work, in order:
  1. `decisions_complete` — add the five new platform-shape decisions (`DEC-011-privacy-surfaces`, `DEC-012-runtime-coverage-per-spec`, `DEC-013-audit-response-truth`, `DEC-014-static-mirror-policy`, `DEC-015-service-role-policy`) to `docs/decisions/standards-overlap-decisions.md`. Each must have id, question, options_considered, choice, consequences, and `projects_to`. Required projection lists are non-empty.
  2. `decisions_simplify` — for every existing decision (`DEC-001` through `DEC-010`), add or sharpen the `consequences` section to name what the decision makes unnecessary or simpler. Decisions that genuinely cannot simplify anything must be marked `simplifies: none` with a reason.
  3. `projections_match_reality` — once `DEC-011-privacy-surfaces` is decided, fix the divergence: either remove `email` and other `directory`-class fields from `site/api/people.json` and the other static mirrors, OR document that those mirrors are part of the surface and update `DEC-011` to permit it (and explain why the audit gate on the live URL is then redundant). The decision rules; the artifacts follow.
  4. `projections_match_reality` — fix `audited-roster-read` so the response `audit` block reflects rows actually written (read back from `audit_log`), or change `DEC-013` to declare a silent / advisory response and remove the misleading hard-coded fields. Do not leave a hard-coded `logged: 5` in the response with a decision that says responses must be truthful.
  5. `runtime_coverage_per_spec_honest` — update `docs/dictionary-coverage-matrix.md` so each Lead spec's runtime column is honest. CASE, QTI, Caliper, LTI: doc-only with target date in `decisions-pending.md`, not "see backlog."
  6. `artifacts_cite_decisions` — ensure every static `site/api/*.json` mirror, every RLS policy, every Edge Function, and every dictionary field has a `decision_id` (or inline comment) tying it to a decision in `docs/decisions/`.
- **Stop adding rubric items.** If you find a problem the current rubric doesn't catch, the answer is a missing decision, not a new check. Add the decision instead.



## Unblocks

<!--
One bullet per unblock signal. Format:
- <timestamp ET>: <prereq that is now satisfied>. Retry items previously blocked on this.
Codex should re-attempt the listed blocked items on the next iteration.
-->



## Notes to Codex

<!--
Free-form guidance: hints about which file to look at, what NOT to try, what we already ruled out.
Keep entries short. Stale entries belong in git history, not here — delete when no longer relevant.
-->


