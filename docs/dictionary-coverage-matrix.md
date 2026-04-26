# Dictionary Coverage Matrix

Research date: 2026-04-24

This matrix separates four different claims:

- Structured source: the shared seed exists as the upstream JSON source, with committed per-spec JSON files generated from it.
- Generated artifacts: a script emits SQL comments, OpenAPI descriptions, and portal docs from that source.
- Runnable slice: the repo exposes actual demo data through SQL and JSON.
- Unsupported ledger: unsupported or deferred parts are explicitly listed with reasons.

`data/data-dictionary.seed.json` is the upstream source for the committed per-spec dictionary projections under `dictionary/*.v1.json`. `scripts/generate_spec_dictionaries.py --check` fails when those projections drift, and `scripts/check_dictionary_artifacts.py` verifies that the generated OneRoster, QTI, CASE, Caliper, and integration/governance dictionaries are represented in generated SQL comments, OpenAPI schemas, Markdown docs, and HTML docs.

| Area | Posture | Structured source | Generated artifacts | Runnable slice | Unsupported ledger | Current judgment |
| --- | --- | --- | --- | --- | --- | --- |
| OneRoster core | Lead | Yes: `data/data-dictionary.seed.json` projects `dictionary/oneroster-core.v1.json` | Yes, including `sourceStandard` in generated docs/OpenAPI | Yes: SQLite, local Express, hosted static JSON, browser SQL, hosted Supabase REST | Yes | Strongest current slice; all exposed fields/values carry sourceStandard. |
| OneRoster full 1.2 | Lead | Yes for accounting: shared seed projection includes generated core fields plus explicit unsupported/deferred ledger | Yes for accounting surfaces | Partial: runnable core only | Yes | Demographics, resources, score scales, agents, Assessment Results Profile fields, and full REST/CSV behavior are explicitly listed in the structured ledger with reasons. |
| QTI 3 repository model | Lead | Yes: `data/data-dictionary.seed.json` projects `dictionary/qti-core.v1.json` | Yes, including interaction-value sourceStandard | No | Yes for current repository projection and preserved XML/runtime areas | Generated dictionary coverage now exists for the platform's QTI repository model, with every interaction family value accounted for. Runtime import/projection is still pending. |
| CASE 1.1 | Lead | Yes: `data/data-dictionary.seed.json` projects `dictionary/case-core.v1.json` | Yes | Partial: assignment-to-CASE URI alignment on `line_items.case_target_uri` | Yes for current framework graph projection | Generated dictionary coverage now exists for the platform's CASE framework graph model, and the teaching-app runtime can attach a CASE URI to a gradebook line item. Runtime import/search is still pending. |
| Caliper 1.2 | Lead | Yes: `data/data-dictionary.seed.json` projects `dictionary/caliper-core.v1.json` | Yes | Partial: authenticated Edge Function receipt path plus `caliper_events`/`class_activity_feed` for the teaching-app slice | Yes for current event projection | Generated dictionary coverage now exists for the platform's Caliper event, entity, actor, context, profile-rule, and extension model. Full Sensor API validation, replay, retention, and warehouse projections are still pending. |
| LTI 1.3/LTI Advantage | Lead | Yes: `data/data-dictionary.seed.json` projects `dictionary/integration-governance-core.v1.json` | Yes | Partial: authenticated launch handler | Yes for launch/service projection | Generated dictionary coverage now exists for registration, deployment, launch, NRPS, AGS, and Deep Linking projections. Full OIDC launch validation and Advantage services are still pending. |
| Security Framework 1.1 | Lead/Governance | Yes: `data/data-dictionary.seed.json` projects `dictionary/integration-governance-core.v1.json` | Yes | Partial: authenticated token-exchange receipt path | Yes for OAuth/scope projection | Generated dictionary coverage now exists for OAuth clients and scope policies. Production token issuance, secrets, and enforcement require a broader auth backend. |
| Data Privacy 1.0 | Lead/Governance | Yes: `data/data-dictionary.seed.json` projects `dictionary/integration-governance-core.v1.json` | Yes | No | Yes for policy projection | Generated dictionary coverage now exists for sharing rules, consent records, retention rules, and privacy audit events. Live workflows are still pending. |
| Common Cartridge/Thin Common Cartridge | Prepare | No | No | No | Partial | Covered in integration dictionary and decisions; not a Lead executable slice yet. |
| Open Badges 3.0/CLR 2.0 | Prepare | No | No | No | Partial | Covered in integration dictionary and overlap decisions; not a Lead executable slice yet. |

## Rule For Future Model Work

No new public SQL column, API field, object, relationship, enum value, scope, event type, or controlled vocabulary should be added unless one of these is true:

- It exists in `data/data-dictionary.seed.json`, is generated into `dictionary/*.v1.json`, and is generated into SQL/API/site docs.
- It is listed in an unsupported/deferred ledger with a reason.
- It is a private implementation detail that is not part of the public platform model.
