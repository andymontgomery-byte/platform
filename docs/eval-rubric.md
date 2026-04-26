# Platform Evaluation Rubric

This rubric is the source of truth for what "done" means on this platform. It is graded by an LLM evaluator (`scripts/evaluate_platform.py`), not by file-presence checks. The deterministic score gate (`scripts/check_spec_conformance.py`) is now **advisory only**.

The Codex loop iterates until every requirement below is `pass` (or every remaining requirement is `blocked` for a documented external reason).

## The shape of this rubric

A great platform is buildable. A layperson developer reads the documentation and knows exactly how to build a real edtech teaching app on top of it — without guessing field names, joining tables the docs don't describe, converting between spec formats the platform should have unified, or asking what an enum value means.

If buildability fails, the failure cascades up:

- **Documentation is unclear** → because the dictionary is ambiguous.
- **Dictionary is ambiguous** → because the decisions were incomplete or wrong.
- **The fix is at the cause, not the symptom.** Patching docs over an ambiguous dictionary is worthless. Patching the dictionary over a missing decision is worse.

This rubric grades three layers, top-down, with backward traceability:

1. **Decisions are great.** Every cross-spec or platform-shape conflict has a sharp decision that deletes work. No strawman alternatives, no unforced choices.
2. **Dictionary is great** *(because decisions are great)*. The shared dictionary is the upstream source of truth and generates per-spec projections. Cross-spec overlaps are resolved at the field level — no API ever has to convert between specs.
3. **Documentation is great** *(because the dictionary is great)*. Every doc claim projects from a dictionary entry or a decision. A layperson can build a working teaching app from `docs/` alone.

The apex item is `buildable_by_layperson` — a single end-to-end test that traces every failure backward to the layer that caused it.

## How to read this file

Each requirement has:

- **id** — stable identifier the evaluator reports against
- **requirement** — what must be true
- **how_to_verify** — what the evaluator should check, in plain language
- **substance_check** — what counts as a real pass vs. a stub
- **traces_to** — for layers 2 and 3, which lower-layer item a failure must be reported against if the cause is below this layer
- **blocked_if** — external conditions that flip the item to `blocked` instead of `fail`

Status values: `pass`, `partial`, `fail`, `blocked`.

Backward traceability is required. When an item fails, the evaluator must name (a) the symptom at this layer, (b) the lower-layer cause if any, and (c) the specific decision, dictionary entry, or doc that needs to change. A fail with no traced cause is itself a fail of `evaluator_traces_failures_backward`.

## Categories

1. Decisions are great
2. Dictionary is great
3. Documentation is great
4. Buildability (the apex test)
5. Loop and harness hygiene

---

## 1. Decisions are great

### decisions_complete

- **requirement:** Every cross-spec overlap, runtime trade-off, privacy/security boundary, or platform-shape ambiguity has a documented decision with id, question, options_considered, choice, consequences, and projects_to. Required areas are listed in `docs/decisions/decisions-needed.md`.
- **how_to_verify:** For each entry in `decisions-needed.md`, confirm a decision exists with all six fields populated. Cross-reference against the codebase: any artifact whose existence implies a choice (e.g. dual ID columns, a separate `agent` table, a static mirror, a per-spec dictionary) must trace to a decision.
- **substance_check:** A decision whose `consequences` is "TBD" or only lists what the decision creates (not what it removes) fails. A decision without a `projects_to` list fails. Decisions are also required for: dictionary generation direction, cross-spec field reconciliation, allowed-value vocabulary unification, privacy-class enumeration closure.
- **blocked_if:** never.

### no_unforced_decisions

- **requirement:** Nothing important is silently TBD. Every cross-spec overlap, runtime trade-off, or privacy/security choice is either decided in `docs/decisions/` or listed in `docs/decisions/decisions-pending.md` with owner, target_date, and what blocks the decision.
- **how_to_verify:** Read `decisions-pending.md`. Confirm every pending entry has owner, target_date, blocker, and one-line rationale. Cross-reference against the codebase: any artifact that exists without a decision behind it is a forced decision masquerading as a fact.
- **substance_check:** "TBD" without an owner fails. A pending entry whose target date is past fails. Pending items must reference what blocks the decision. The pending file existing alone is not enough.
- **blocked_if:** never.

### decisions_simplify

- **requirement:** Each decision's consequences section names what the decision makes unnecessary or simpler — not just what it requires. A great decision deletes work.
- **how_to_verify:** For each decision, read the consequences section. Confirm at least one bullet starts with words like "removes the need for," "makes X redundant," "lets Y be derived," "eliminates," or equivalent, AND names a concrete artifact, code path, or category that this decision deletes or collapses.
- **substance_check:** Generic "removes complexity" without naming what's removed fails. A consequences section that only adds requirements (e.g., "every fact table must carry tenant_id") without naming what it removes (e.g., "removes the need for per-table access checks in application code") is `partial`. Decisions that preserve multiple coexisting surfaces or add inheritance/conditional layers must justify the preservation against a simpler alternative that collapses them; absence of that justification is `partial`.
- **blocked_if:** never.

### decisions_have_real_alternatives

- **requirement:** Each decision's `options_considered` brackets the real design space. Strawman options that only exist to make the chosen option look obvious are not acceptable.
- **how_to_verify:** For each decision, read options_considered. Confirm at least three options including (a) a more aggressive simplification than the chosen option, (b) a more permissive option than the chosen option, (c) the chosen option. Confirm the more-aggressive option is one a competent architect would actually consider, not a paper tiger ("allow everything because it's a demo" is a strawman).
- **substance_check:** Two extreme bookends plus a chosen middle, where the bookends are obviously wrong, fails. Real alternatives include credible architectural choices that other production platforms make.
- **blocked_if:** never.

---

## 2. Dictionary is great

### dictionary_single_source_of_truth

- **requirement:** `data/data-dictionary.seed.json` (the shared dictionary) is the upstream canonical model. Every per-spec dictionary (`dictionary/oneroster-core.v1.json`, etc.) is generated from it. Hand-editing a per-spec dictionary is a build error.
- **how_to_verify:** Confirm a generator script exists (e.g. `scripts/generate_spec_dictionaries.py`) that reads the shared dictionary and writes the per-spec files. Confirm running it on a clean checkout produces zero diff against the committed per-spec files. Confirm CI fails when the per-spec files diverge from the generator output.
- **substance_check:** A shared dictionary stub (e.g. 21 fields against 568 in the per-spec files) fails. The shared dictionary must contain enough canonical objects and fields to project every per-spec field, either as a direct mapping or as an explicitly `spec_only` exception with a documented reason.
- **traces_to:** If failure is because the platform has not decided to invert the direction, fail `decisions_complete` with "missing decision: dictionary generation direction."
- **blocked_if:** never.

### dictionary_resolves_cross_spec_overlaps

- **requirement:** Every spec field whose meaning overlaps with another spec's field carries an explicit `canonical_field_id` reference (or equivalent typed mapping) pointing to the shared dictionary's canonical field. No runtime, no API, no projection ever has to convert between specs.
- **how_to_verify:** For each per-spec field, confirm one of: (a) `canonical_field_id` referencing a real field in the shared dictionary, or (b) `spec_only: true` with a documented reason. Examples that must resolve to one canonical field: OneRoster `User.email`, Caliper `Person.email`, LTI `lis_person_contact_email_primary`, QTI `Candidate.email` — all four must point to the same canonical email field.
- **substance_check:** Cross-spec overlap resolved only in DEC-prose (not in field-level data) fails. The platform must not have any code that converts between spec field names; if such code exists, the overlap is unresolved.
- **traces_to:** If a specific overlap has no canonical field, fail `decisions_complete` with the missing decision named.
- **blocked_if:** never.

### dictionary_unifies_identity

- **requirement:** Person, User, Actor, Subject, Candidate, and any other identity-shaped object across specs map to a single canonical identity entity in the shared dictionary via `canonical_object_id`. The unification is data, not prose.
- **how_to_verify:** Find every spec object that represents an identity (e.g. OneRoster `Person`, Caliper `Person`/`Actor`, LTI `lis_person_*`, QTI `Candidate`). Confirm each carries `canonical_object_id` pointing to the same canonical identity entity in the shared dictionary.
- **substance_check:** A canonical identity entity that exists only in DEC-001 prose fails. The canonical entity must have its own object record in the shared dictionary, with fields, allowed values, and projections.
- **traces_to:** If unification is impossible without a decision (e.g. how to handle confidence on imprecise identity claims), fail `decisions_complete` with the missing decision named.
- **blocked_if:** never.

### dictionary_global_enums

- **requirement:** Allowed-value vocabularies are global. Every spec-native enum (OneRoster role names, LTI URI roles, Caliper actor types, QTI item types, etc.) maps to a single shared enum in the canonical dictionary, with a documented crosswalk in both directions.
- **how_to_verify:** For each enum field across the per-spec dictionaries, confirm it references a shared enum (e.g. `shared_enum_id: "role_family"`) and that the shared enum lists every spec-native value with its mapping to the canonical value.
- **substance_check:** Per-spec enums declared independently (even if they share names) fail. The mapping from spec-native to canonical must be complete and bidirectional — given any spec-native value, the canonical value is unambiguous, and given any canonical value, every spec-native value mapping to it is enumerated.
- **traces_to:** If the canonical vocabulary itself is undecided (e.g. what role families exist), fail `decisions_complete` for the missing role-vocabulary decision.
- **blocked_if:** never.

### dictionary_closed_privacy_classes

- **requirement:** Privacy classes are a closed enumeration applied identically across all specs. No escape-hatch values like `depends_on_contents` or `depends_on_entity` — every privacy class is concrete and defined once.
- **how_to_verify:** Read the canonical dictionary's `privacy_classes` list. Confirm every per-spec dictionary uses only values from that list. Confirm Caliper's `depends_on_contents` / `depends_on_entity` style placeholders have been resolved into concrete classes per occurrence.
- **substance_check:** Different specs declaring different privacy class sets fails. A privacy class used in only one spec without justification fails.
- **traces_to:** If the canonical privacy class list is undecided, fail `decisions_complete` for the missing privacy-class-enumeration decision.
- **blocked_if:** never.

### dictionary_carries_relational_graph

- **requirement:** Foreign keys, cardinalities, and ownership relationships live in the dictionary, not only in `supabase/migrations/*.sql`. The migrations are generated from the dictionary's relational graph.
- **how_to_verify:** Confirm the dictionary's object records carry `relationships` (or equivalent) declaring FK targets and cardinality. Confirm a generator produces the migrations from this graph. Confirm running the generator on a clean checkout produces zero diff against committed migrations.
- **substance_check:** Migrations that exist independently of the dictionary fail. Relationships present only as prose in the decision register fail.
- **traces_to:** If undecided, fail `decisions_complete` for the missing migration-generation-direction decision.
- **blocked_if:** never.

### dictionary_artifacts_cite_decisions

- **requirement:** Every dictionary field, object, enum, and privacy class carries a `decision_id` (or equivalent) reference to the decision that produced it. Anything without a citation is an orphan.
- **how_to_verify:** For each field/object/enum/privacy class, confirm a `decision_id` reference exists. A `decision_id` that does not match any decision in `docs/decisions/` fails (broken link).
- **substance_check:** A field with `decision_id: "none"` is acceptable only if `decisions-pending.md` or a per-field exemption explains why no decision applies.
- **traces_to:** Orphans imply missing decisions; fail `decisions_complete` for each.
- **blocked_if:** never.

---

## 3. Documentation is great

### docs_generated_from_dictionary

- **requirement:** Every documentation page that describes objects, fields, enums, relationships, or APIs is generated from the dictionary. No prose-only architecture; if a doc claim isn't backed by a dictionary entry or a decision, it can't be in the docs as a load-bearing claim.
- **how_to_verify:** For each generated page (object reference, field reference, enum reference, API reference), confirm a generator produces it from the dictionary. Confirm running the generator on a clean checkout produces zero diff against committed pages. Confirm hand-edited descriptive prose pages link to dictionary anchors for every load-bearing claim.
- **substance_check:** A docs page that describes a field the dictionary doesn't have, or describes a field with different semantics than the dictionary says, fails. Generated pages with stale content (dictionary changed but doc didn't regenerate) fail.
- **traces_to:** Mismatch between doc and dictionary traces back to either the dictionary (regenerate it) or a decision (decide it).
- **blocked_if:** never.

### docs_explain_why_not_only_what

- **requirement:** For every concept that exists because of a decision (e.g. why there's a separate `agent` from `person`, why `enrollment` and `membership` are different, why CASE is canonical), the docs explain the decision in plain language and link to the decision register.
- **how_to_verify:** For each decision in `docs/decisions/`, confirm a doc page references it with the choice and the simplification it produced (in plain language, not just a link). The decision register itself must render as HTML on the portal with anchors per decision.
- **substance_check:** Doc pages that describe what without explaining why fail. A link to a 900-line raw Markdown file as the only explanation fails.
- **traces_to:** Vague or hand-wavy why means the decision itself is vague; fail `decisions_simplify` or `decisions_complete`.
- **blocked_if:** never.

### docs_include_buildability_guide

- **requirement:** `docs/build-an-edtech-app.md` (or equivalent) walks a layperson developer through building a real teaching app on the platform end-to-end. Every step uses copy-pasteable curl/SQL/code against the live runtime. Every claim about a field, an enum value, or an API shape links to the dictionary.
- **how_to_verify:** The guide must walk through, at minimum: (a) creating a school, (b) enrolling a student in a class, (c) posting a grade, (d) linking the grade to a CASE standard, (e) reading a Caliper-style activity stream. Every step must include an executable example. Every field referenced must link to its dictionary entry. Every enum value referenced must link to the global enum in the dictionary.
- **substance_check:** A guide that hand-waves with phrases like "you can also..." or "for more details, see..." for any of the listed steps fails. A guide that requires the reader to read a separate spec to fill in field names fails.
- **traces_to:** If a step can't be written because the dictionary doesn't unify a concept, fail `dictionary_resolves_cross_spec_overlaps`. If it can't be written because no decision was made, fail `decisions_complete`.
- **blocked_if:** never.

### docs_no_dead_links_or_orphans

- **requirement:** Every doc link resolves. Every dictionary entry is reachable from at least one doc page. Every decision is reachable from at least one doc page. No doc page is unreachable from the portal landing.
- **how_to_verify:** Run a link checker over the rendered site. Confirm zero 404s. Confirm the portal navigation reaches every dictionary object, every decision, every API endpoint, and the buildability guide within three clicks.
- **substance_check:** Hidden orphan pages and broken anchors fail.
- **blocked_if:** never.

---

## 4. Buildability (the apex test)

### buildable_by_layperson

- **requirement:** A layperson developer who has never seen this platform can read only `docs/` and produce the curl commands, SQL statements, and data shapes needed to build a real edtech teaching app. The test scenario is fixed so the result is comparable across iterations.
- **how_to_verify:** The evaluator simulates a layperson developer with general web/SQL knowledge but zero prior exposure to the platform. The simulated developer reads only files under `docs/` (no source code, no migrations, no JSON dictionaries directly — only what the docs link to). The simulated developer attempts to write the requests for: (1) create a school org with one teacher and ten students, (2) create a class for that teacher with those students enrolled, (3) post a numeric grade for one student on one assignment, (4) link the assignment to a specific CASE standard URI, (5) read back a Caliper-style activity feed for the class. The evaluator records every gap encountered: missing field name, ambiguous enum, missing endpoint, unclear privacy boundary, required spec conversion, contradictory information.
- **substance_check:** Zero gaps = pass. One or more gaps = fail, with each gap traced to either (a) a doc that needs to exist or be regenerated, (b) a dictionary entry that needs to exist or be unified, or (c) a decision that needs to be made. Vague success criteria like "developer figured it out eventually" fail. The simulated developer must produce executable artifacts (curl/SQL) for each step that, if run, would succeed against the live runtime.
- **traces_to:** Every gap must trace backward to the lowest layer where a fix is needed (decision, dictionary, or doc). The fail report lists every gap with its traced cause.
- **blocked_if:** Live runtime not reachable.

### evaluator_traces_failures_backward

- **requirement:** When any item in layers 2, 3, or 4 fails, the evaluator names (a) the symptom at that layer, (b) the lower-layer cause if any, and (c) the specific decision, dictionary entry, or doc that needs to change. A fail with no traced cause itself fails this item.
- **how_to_verify:** Read the evaluator output for the most recent run. For every non-pass item in layers 2-4, confirm the report includes a `traced_cause` field naming the lower-layer artifact and the change required.
- **substance_check:** "Docs are unclear" without naming which dictionary entry or decision caused it fails. Vague generic causes fail.
- **blocked_if:** never.

---

## 5. Loop and harness hygiene

### evaluator_runs_each_iteration

- **requirement:** `scripts/evaluate_platform.py` runs at the end of each loop iteration and writes `site/api/platform-evaluation.json` with `done` flag, per-item status, per-item traced_cause for non-pass items, and the buildability gap list.
- **how_to_verify:** Read the most recent iteration's logs and confirm a fresh report. Report contains the new `traced_cause` field on every non-pass item, plus a `buildability_gaps` array with each gap's traced cause.
- **substance_check:** Report missing `traced_cause` on a non-pass item fails.
- **blocked_if:** never.

### loop_overrides_respected

- **requirement:** The Codex loop reads `docs/loop-overrides.md` at the start of every iteration and passes its contents to the Codex prompt as authoritative guidance. Loop halts when a `## Pause` section contains the literal token `PAUSE` on its own line.
- **how_to_verify:** Inspect `scripts/codex_loop.py`. Confirm the helper reads the file, the PAUSE check halts the loop before the next iteration runs, and the prompt builder injects overrides under a "Human overrides" section.
- **substance_check:** A loop that reads the file but never injects it fails. PAUSE check that runs after the next iteration fails.
- **blocked_if:** never.

### loop_terminates_on_done

- **requirement:** The loop stops iterating when every rubric item is `pass`, or when every remaining item is `blocked` with a documented prerequisite. Hard caps still apply as safety rails.
- **how_to_verify:** Read the loop driver. Confirm termination references the LLM evaluator's `done` flag.
- **substance_check:** Numeric-threshold gating fails this item.
- **blocked_if:** never.

---

## Summary

| Category | Count |
|---|---|
| Decisions are great | 4 |
| Dictionary is great | 7 |
| Documentation is great | 4 |
| Buildability (the apex test) | 2 |
| Loop and harness hygiene | 3 |
| **Total** | **20** |

The loop is "done" when all 20 are `pass`, or when every remaining item is `blocked` with a documented external prerequisite.

## What this rubric replaces

The previous rubric had 11 items organized around decisions as the spine. That structure was correct as far as it went, but it allowed a platform to pass with a stub shared dictionary, hand-written per-spec dictionaries, prose-only cross-spec resolution, and documentation that described what without explaining why. The buildability test never existed.

This rubric adds the dictionary layer (7 items) and the documentation layer (4 items) explicitly, with backward traceability required: every dictionary failure either traces to a decision or a missing one, and every doc failure either traces to the dictionary or to a decision. The apex item — `buildable_by_layperson` — gates the whole stack on the outcome that actually matters: a developer reads the docs and ships a teaching app.

A platform can no longer pass by having sharp decisions if the dictionary doesn't project them as data, or by having a complete dictionary if the docs don't make it usable. Each layer is accountable to the layer above it, and the apex test is accountable to the user.
