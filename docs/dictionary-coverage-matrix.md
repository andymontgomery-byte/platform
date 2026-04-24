# Dictionary Coverage Matrix

Research date: 2026-04-24

This matrix separates four different claims:

- Structured source: the dictionary exists as JSON or another machine-readable source artifact.
- Generated artifacts: a script emits SQL comments, OpenAPI descriptions, and portal docs from that source.
- Runnable slice: the repo exposes actual demo data through SQL and JSON.
- Unsupported ledger: unsupported or deferred parts are explicitly listed with reasons.

`scripts/check_dictionary_artifacts.py` currently verifies that the structured OneRoster, QTI, CASE, Caliper, and integration/governance dictionaries are represented in generated SQL comments, OpenAPI schemas, Markdown docs, and HTML docs.

| Area | Posture | Structured source | Generated artifacts | Runnable slice | Unsupported ledger | Current judgment |
| --- | --- | --- | --- | --- | --- | --- |
| OneRoster core | Lead | Yes: `dictionary/oneroster-core.v1.json` | Yes | Yes: SQLite, local Express, hosted static JSON, browser SQL | Partial | Strongest current slice. Needs expansion to full OneRoster 1.2. |
| OneRoster full 1.2 | Lead | Partial | Partial | Partial | Partial | Core works, but demographics, resources, score scales, agents, and full REST conformance are not complete. |
| QTI 3 repository model | Lead | Yes: `dictionary/qti-core.v1.json` | Yes | No | Yes for current repository projection | Generated dictionary coverage now exists for the platform's QTI repository model. Runtime import/projection is still pending. |
| CASE 1.1 | Lead | Yes: `dictionary/case-core.v1.json` | Yes | No | Yes for current framework graph projection | Generated dictionary coverage now exists for the platform's CASE framework graph model. Runtime import/search is still pending. |
| Caliper 1.2 | Lead | Yes: `dictionary/caliper-core.v1.json` | Yes | No | Yes for current event projection | Generated dictionary coverage now exists for the platform's Caliper event, entity, actor, context, profile-rule, and extension model. Runtime ingestion is still pending. |
| LTI 1.3/LTI Advantage | Lead | Yes: `dictionary/integration-governance-core.v1.json` | Yes | No | Yes for launch/service projection | Generated dictionary coverage now exists for registration, deployment, launch, NRPS, AGS, and Deep Linking projections. Runtime launch/API sandbox is still pending. |
| Security Framework 1.1 | Lead/Governance | Yes: `dictionary/integration-governance-core.v1.json` | Yes | No | Yes for OAuth/scope projection | Generated dictionary coverage now exists for OAuth clients and scope policies. Token issuance, secrets, and enforcement require a backend. |
| Data Privacy 1.0 | Lead/Governance | Yes: `dictionary/integration-governance-core.v1.json` | Yes | No | Yes for policy projection | Generated dictionary coverage now exists for sharing rules, consent records, retention rules, and privacy audit events. Live workflows are still pending. |
| Common Cartridge/Thin Common Cartridge | Prepare | No | No | No | Partial | Covered in integration dictionary and decisions; not a Lead executable slice yet. |
| Open Badges 3.0/CLR 2.0 | Prepare | No | No | No | Partial | Covered in integration dictionary and overlap decisions; not a Lead executable slice yet. |

## Rule For Future Model Work

No new public SQL column, API field, object, relationship, enum value, scope, event type, or controlled vocabulary should be added unless one of these is true:

- It exists in a structured dictionary source and is generated into SQL/API/site docs.
- It is listed in an unsupported/deferred ledger with a reason.
- It is a private implementation detail that is not part of the public platform model.
