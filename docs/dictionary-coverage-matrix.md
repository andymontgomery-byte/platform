# Dictionary Coverage Matrix

Research date: 2026-04-24

This matrix separates four different claims:

- Structured source: the dictionary exists as JSON or another machine-readable source artifact.
- Generated artifacts: a script emits SQL comments, OpenAPI descriptions, and portal docs from that source.
- Runnable slice: the repo exposes actual demo data through SQL and JSON.
- Unsupported ledger: unsupported or deferred parts are explicitly listed with reasons.

`scripts/check_dictionary_artifacts.py` currently verifies that the structured OneRoster and QTI dictionaries are represented in generated SQL comments, OpenAPI schemas, Markdown docs, and HTML docs.

| Area | Posture | Structured source | Generated artifacts | Runnable slice | Unsupported ledger | Current judgment |
| --- | --- | --- | --- | --- | --- | --- |
| OneRoster core | Lead | Yes: `dictionary/oneroster-core.v1.json` | Yes | Yes: SQLite, local Express, hosted static JSON, browser SQL | Partial | Strongest current slice. Needs expansion to full OneRoster 1.2. |
| OneRoster full 1.2 | Lead | Partial | Partial | Partial | Partial | Core works, but demographics, resources, score scales, agents, and full REST conformance are not complete. |
| QTI 3 repository model | Lead | Yes: `dictionary/qti-core.v1.json` | Yes | No | Yes for current repository projection | Generated dictionary coverage now exists for the platform's QTI repository model. Runtime import/projection is still pending. |
| CASE 1.1 | Lead | No | No | No | Partial | Good Markdown coverage, but not generator-backed or executable. |
| Caliper 1.2 | Lead | No | No | No | Partial | Good Markdown coverage, but not generator-backed or executable. |
| LTI 1.3/LTI Advantage | Lead | No | No | No | Partial | Good Markdown coverage, but no launch/API sandbox yet. |
| Security Framework 1.1 | Lead/Governance | No | No | No | Partial | Documented as a required backend layer; GitHub Pages cannot implement token issuance or secrets. |
| Data Privacy 1.0 | Lead/Governance | No | No | No | Partial | Privacy classes exist, but consent, retention, and data-sharing workflows are not implemented. |
| Common Cartridge/Thin Common Cartridge | Prepare | No | No | No | Partial | Covered in integration dictionary and decisions; not a Lead executable slice yet. |
| Open Badges 3.0/CLR 2.0 | Prepare | No | No | No | Partial | Covered in integration dictionary and overlap decisions; not a Lead executable slice yet. |

## Rule For Future Model Work

No new public SQL column, API field, object, relationship, enum value, scope, event type, or controlled vocabulary should be added unless one of these is true:

- It exists in a structured dictionary source and is generated into SQL/API/site docs.
- It is listed in an unsupported/deferred ledger with a reason.
- It is a private implementation detail that is not part of the public platform model.
