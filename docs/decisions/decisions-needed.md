# Decisions Needed

This file lists the decision areas a great platform must have answered. Each entry maps to a decision in `docs/decisions/standards-overlap-decisions.md` (or a per-decision file once the decisions are split). The rubric's `decisions_complete` item grades whether every entry below has a real decision behind it.

A decision area belongs on this list if leaving it implicit would force the codebase to make the choice silently and inconsistently across artifacts.

## Cross-spec semantic overlap (existing)

These are the original 10 from `standards-overlap-decisions.md`. They must continue to be sharp.

| Area | Decision ID | Notes |
|---|---|---|
| Person, user, actor, profile, subject | `DEC-001-person-agent-subject` | |
| Class, course, context, group, section | `DEC-002-learning-context` | |
| Roles | `DEC-003-role-vocabulary` | |
| Enrollment vs membership | `DEC-004-enrollment-membership` | |
| Results, scores, outcomes, grade events | `DEC-005-results-scores` | |
| Standards alignment | `DEC-006-standards-alignment` | |
| Identifier schemes and crosswalks | `DEC-007-identifier-crosswalk` | |
| Time, school sessions, event timestamps | `DEC-008-time-session` | |
| Content, resources, packages, launch links | `DEC-009-content-resource` | |
| Tenant-owned vs shared reference data | `DEC-010-tenancy-reference-data` | |

## Platform-shape decisions (new — added when the rubric was restructured around decisions)

These were forced silently before the restructuring. They must be made explicit.

| Area | Decision ID | What it must answer |
|---|---|---|
| Privacy surfaces | `DEC-011-privacy-surfaces` | For each privacy class in the closed vocabulary decided by `DEC-019-closed-privacy-classes`, which surfaces (live PostgREST, Edge Functions, static Pages mirrors, generated docs) may expose it, and under what gate (none / RLS / audited Edge Function / never). This decision determines whether `site/api/people.json` may carry `email`. |
| Runtime coverage per spec | `DEC-012-runtime-coverage-per-spec` | For each Lead spec (OneRoster, CASE, QTI, Caliper, LTI, Security Framework, Data Privacy), whether the platform ships a runtime slice now, in a future slice with a target date, or doc-only as a deliberate choice. Names what doc-only specs sacrifice and why that is acceptable. |
| Audit response semantics | `DEC-013-audit-response-truth` | What an audited Edge Function's response body may say about audit activity. Choices: silent (no `audit` block), best-effort (advisory hint), or truthful (response reflects rows actually written, read back from `audit_log`). The current implementation hard-codes `logged: 5` which is none of these honestly. This decision forces a choice. |
| Static mirror policy | `DEC-014-static-mirror-policy` | Whether `site/api/*.json` is allowed to exist; if yes, what classes of data may live there, how staleness vs the live DB is handled (refresh on commit / banner showing freshness / removed entirely), and whether each mirror file must declare its source decision and last-refresh timestamp. Determines whether mirrors are part of the contract or a documentation aid. |
| Service-role policy | `DEC-015-service-role-policy` | When service-role access is allowed (only via `docs/admin-operations.md` allowlist), what guardrails wrap each entry, and whether tests counting on service-role fixtures pollute the user-JWT regression story. Determines whether the RLS verification chain has any service-role dependency. |
| Dictionary generation direction | `DEC-016-dictionary-generation-direction` | Whether the shared dictionary or per-spec dictionaries are upstream, whether hand-editing per-spec projections is allowed, and what CI must check when projections drift. |
| Cross-spec field reconciliation | `DEC-017-canonical-field-reconciliation` | Whether overlapping fields are reconciled through field-level canonical IDs, runtime conversion code, or prose-only documentation. Must decide how OneRoster, Caliper, LTI, QTI, CASE, and governance fields point at the same platform concept. |
| Allowed-value vocabulary unification | `DEC-018-global-enum-crosswalks` | Whether enum values stay per spec, become platform-only values, or map through one shared enum table with bidirectional spec-native crosswalks. |
| Privacy-class enumeration closure | `DEC-019-closed-privacy-classes` | Which exact privacy-class keys are allowed and how placeholder classes such as `depends_on_entity` and `depends_on_contents` are resolved. |
| Migration generation direction | `DEC-020-relational-graph-migrations` | Whether database relationships live in SQL first, dictionary first, or both, and whether Supabase migrations are generated from the dictionary relational graph. |

## Adding a new decision area

When a contributor finds an implicit choice that the codebase is making silently, they must either:

1. Open a decision in `docs/decisions/` with `id`, `question`, `options_considered`, `choice`, `consequences`, and `projects_to`, and add a row to this file, or
2. Add a row to `docs/decisions/decisions-pending.md` with an owner and target date.

Anything else fails `no_unforced_decisions`.
