# Decisions Pending

Implicit choices the codebase is making that have not yet been decided explicitly. Each entry must have an owner, a target date, and a one-line description of why it matters and what blocks the decision.

The rubric's `no_unforced_decisions` item fails if anything important is silently TBD. It also fails if a pending entry's target date is past.

## Format

| ID | Description | Why it matters | Blocked on | Owner | Target date |
|---|---|---|---|---|---|

## Current pending decisions

| ID | Description | Why it matters | Blocked on | Owner | Target date |
|---|---|---|---|---|---|
| `PEND-001-runtime-slice-schedule` | Schedule the next runtime slices declared deferred by `DEC-012-runtime-coverage-per-spec`: CASE search, QTI package import/projection, full Caliper raw-event projection, LTI Advantage services, production OAuth issuance, and broader privacy workflows. | DEC-012 decides the current posture, but the platform still needs dated delivery choices before any deferred Lead spec can be claimed as runtime-backed. | Product priority on next runtime slice | Andy | 2026-05-15 |
| `PEND-005-deno-check-in-ci` | Decide whether `deno check` runs in CI for Edge Functions (`DEC-015` adjacent). Five live functions deployed without a static type-check pass because Deno is not installed locally. | Type errors only surface at deploy, when fewer rollbacks are possible. | CI capacity | Andy | 2026-05-03 |

## Resolving a pending decision

Move the row to `decisions-needed.md` once the decision is written in `docs/decisions/` with all six fields populated. Delete from this file.

A pending entry whose target date is past fails `no_unforced_decisions` until the target is updated with a justification or the decision is made.
