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



## Notes to Codex

<!--
Free-form guidance: hints about which file to look at, what NOT to try, what we already ruled out.
Keep entries short. Stale entries belong in git history, not here — delete when no longer relevant.
-->


