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

- **Rubric was restructured a second time around buildability** (2026-04-26 16:50 UTC). The previous 11-item rubric organized around decisions as the spine is replaced by a 20-item three-layer rubric: decisions are great -> dictionary is great (because decisions are great) -> docs are great (because dictionary is great). The apex item is `buildable_by_layperson`. Read `docs/eval-rubric.md` from scratch.
- **Backward traceability is required.** When any item in layers 2-4 fails, the evaluator output must name the lower-layer cause (a specific decision to add/sharpen, a specific dictionary entry to add/unify, or a specific doc to write/regenerate). A failure with no traced cause itself fails `evaluator_traces_failures_backward`. Update `scripts/evaluate_platform.py` to emit a `traced_cause` field on every non-pass item and a `buildability_gaps` array.
- **Priority order for the next iterations:** work top-down, layer by layer. Do not jump ahead.
  1. `decisions_complete` — add the missing decisions the new rubric demands. At minimum: dictionary generation direction (shared dictionary is upstream, per-spec are projections), cross-spec field reconciliation (canonical_field_id is required on every overlapping spec field), allowed-value vocabulary unification (one shared enum table with crosswalk), privacy-class enumeration closure (one closed list, no `depends_on_*` escape hatches), migration generation direction (migrations generated from the dictionary's relational graph). Five new decisions, each with the full six fields and a non-empty `projects_to`.
  2. `decisions_simplify` and `decisions_have_real_alternatives` — sweep DEC-001 through DEC-015 and the new ones. For each: `consequences` must name a concrete artifact, code path, or category this decision deletes or collapses. `options_considered` must include at least one credible architectural alternative more aggressive than the chosen option (not a strawman like "allow everything because it's a demo").
  3. `dictionary_single_source_of_truth` — invert the dictionary direction. Expand `data/data-dictionary.seed.json` to be the canonical model with enough objects, fields, enums, privacy classes, and relationships to project every per-spec dictionary. Write `scripts/generate_spec_dictionaries.py` that reads the canonical seed and produces `dictionary/*.v1.json`. CI must fail if the generator output diverges from the committed per-spec files.
  4. `dictionary_resolves_cross_spec_overlaps` and `dictionary_unifies_identity` — every per-spec field that overlaps another spec's field must carry `canonical_field_id`. Every spec-side identity object must carry `canonical_object_id` pointing to one canonical identity entity. Resolve at the data level, not in DEC-prose.
  5. `dictionary_global_enums`, `dictionary_closed_privacy_classes`, `dictionary_carries_relational_graph` — global enum table with bidirectional crosswalks, closed privacy class list (resolve Caliper's `depends_on_contents` / `depends_on_entity` per occurrence), relational graph in the dictionary that generates `supabase/migrations/*.sql`.
  6. `docs_generated_from_dictionary` — write generators that produce object/field/enum/API reference pages from the dictionary. Hand-edited prose must link to dictionary anchors for every load-bearing claim.
  7. `docs_include_buildability_guide` — write `docs/build-an-edtech-app.md` that walks a layperson developer end-to-end through: create a school org with one teacher and ten students, create a class for that teacher with those students enrolled, post a numeric grade for one student on one assignment, link the assignment to a specific CASE standard URI, read back a Caliper-style activity feed for the class. Every step must include copy-pasteable curl/SQL against the live runtime. Every field must link to its dictionary entry. Every enum value must link to the global enum.
  8. `buildable_by_layperson` — the apex test. Once the lower layers are in place, this should pass. If gaps remain, each gap must trace backward to the layer that caused it.
- **Stop adding rubric items.** If you find a problem the current rubric does not catch, the answer is a missing decision, a missing dictionary unification, or a missing doc page — not a new check. Add the cause, not the symptom.



## Unblocks

<!--
One bullet per unblock signal. Format:
- <timestamp ET>: <prereq that is now satisfied>. Retry items previously blocked on this.
Codex should re-attempt the listed blocked items on the next iteration.
-->

- 2026-04-26 15:47 ET: `docs/build-an-edtech-app.md` now exists on main (PR #5, merge `d47ebb1`). Workflow 4's `line_items.case_framework_item_uri` column and workflow 5's `caliper_event_receipts` table are added in `supabase/migrations/0002_case_alignment_and_caliper_receipts.sql`. Tenant-scoped INSERT/UPDATE RLS policies for organizations, people, courses, classes, enrollments, and line_items are added in `0003_buildability_write_policies.sql`. Re-evaluate `docs_include_buildability_guide` and `buildable_by_layperson`; if either still fails the gap is in the guide itself, not the platform — tighten the guide rather than reverting.
- 2026-04-26 16:00 ET: The next leverage point is the three dictionary partials (`dictionary_resolves_cross_spec_overlaps`, `dictionary_unifies_identity`, `dictionary_global_enums`). All three trace to the same root cause: per-spec field-level `canonical_field_id` values are spec-prefixed (e.g., `canonical.oneroster-core.person.email`) instead of pointing to the shared canonical entry (`canonical.identity.person.email`). Fix this in `data/data-dictionary.seed.json` and the generator, in one iteration. Then `dictionary_global_enums` needs a top-level `shared_enums` table with bidirectional spec-native crosswalks and `shared_enum_id` references replacing inline `allowed_values` on overlapping enums (DEC-003 role family, DEC-018 status, identifier_type). After that, only `dictionary_carries_relational_graph` remains as a hard dictionary fail and it requires a `relationships[]` array per object plus `scripts/generate_supabase_migrations.py`.
- 2026-04-26 17:00 ET: The loop has been silent on main for ~2 hours after iter8 (last commit `03b6986`, pass=11/20). The previous three iterations (6, 7, 8) all stayed at pass<=11 by raw count even though substantive structural work landed (closed privacy classes, dictionary single source of truth, canonical identity unification). The stall safety rail likely tripped. When the loop restarts, bundle linked fixes in a single iteration whenever they share one root cause. Specifically: in one iteration, rewrite per-spec `canonical_field_id` values to shared canonical entries AND add the top-level `shared_enums` table AND replace inline `allowed_values` on overlapping enums with `shared_enum_id` references. That single iteration should flip `dictionary_resolves_cross_spec_overlaps`, `dictionary_unifies_identity`, and `dictionary_global_enums` to pass simultaneously. After that, the only remaining dictionary fail is `dictionary_carries_relational_graph`, which is a separate, larger lift (relationships[] schema + `scripts/generate_supabase_migrations.py`).
- 2026-04-26 17:00 ET: Reminder for the buildability re-eval: `docs/build-an-edtech-app.md`, `supabase/migrations/0002_case_alignment_and_caliper_receipts.sql`, and `supabase/migrations/0003_buildability_write_policies.sql` are all on main as of merge `33b0d7c`. The live evaluator at 19:11Z predates these merges and still reports `docs_include_buildability_guide` and `buildable_by_layperson` as fail. Re-running `python3 scripts/evaluate_platform.py` against current main should flip both items toward pass without any code changes.


## Notes to Codex

<!--
Free-form guidance: hints about which file to look at, what NOT to try, what we already ruled out.
Keep entries short. Stale entries belong in git history, not here — delete when no longer relevant.
-->


