# Decisions Pending

Implicit choices the codebase is making that have not yet been decided explicitly. Each entry must have an owner, a target date, and a one-line description of why it matters and what blocks the decision.

The rubric's `no_unforced_decisions` item fails if anything important is silently TBD. It also fails if a pending entry's target date is past.

## Format

| ID | Description | Why it matters | Blocked on | Owner | Target date |
|---|---|---|---|---|---|

## Current pending decisions

| ID | Description | Why it matters | Blocked on | Owner | Target date |
|---|---|---|---|---|---|
| `PEND-001-privacy-surfaces` | Decide which surfaces may expose which privacy classes (`DEC-011`). Currently `site/api/people.json` exposes `email` (privacy_class `directory`) on a public unauthenticated GitHub Pages mirror, while a sibling `audited-roster-read` Edge Function gates the same field through `audit_log`. Two surfaces, two gates, no decision. | Either the static mirrors are violating an unwritten privacy decision, or the audit log on the Edge Function is theatre. The decision must say which. | Maintainer review | Andy | 2026-04-28 |
| `PEND-002-runtime-coverage-per-spec` | Decide each Lead spec's runtime status (`DEC-012`). CASE, QTI, Caliper, LTI have full per-field accounting in the dictionary but zero runtime tables. The coverage matrix shows runtime for OneRoster only. The `lead_spec_full_accounting` rubric pass hides this. | A platform that documents 5 specs and ships 1 is mis-claiming its readiness, or it has deliberately deferred the others — which is fine if said out loud. | Product priority on next slice | Andy | 2026-04-30 |
| `PEND-003-audit-response-truth` | Decide what `audited-roster-read` (and future audited Edge Functions) may put in the response `audit` block (`DEC-013`). The current implementation hard-codes `logged: 5` and a hard-coded `fields` list. The Postgres function probably writes the rows, but the response is not derived from the table. | If the trigger ever silently no-ops the response will lie. Trust in the audit story collapses the moment a caller checks. | Engineering review | Andy | 2026-04-28 |
| `PEND-004-static-mirror-policy` | Decide whether `site/api/*.json` is part of the contract or a documentation aid, and how it stays in sync with the live DB (`DEC-014`). Files claim `dateLastModified: 2026-04-24` but the live DB has changed since. | Two sources of truth quietly drifting is the most common cause of "the docs say X but the API does Y" support pain. | Maintainer review | Andy | 2026-04-30 |
| `PEND-005-deno-check-in-ci` | Decide whether `deno check` runs in CI for Edge Functions (`DEC-015` adjacent). Five live functions deployed without a static type-check pass because Deno is not installed locally. | Type errors only surface at deploy, when fewer rollbacks are possible. | CI capacity | Andy | 2026-05-03 |

## Resolving a pending decision

Move the row to `decisions-needed.md` once the decision is written in `docs/decisions/` with all six fields populated. Delete from this file.

A pending entry whose target date is past fails `no_unforced_decisions` until the target is updated with a justification or the decision is made.
