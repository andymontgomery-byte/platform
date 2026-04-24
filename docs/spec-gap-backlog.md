# Spec Gap Backlog

Research date: 2026-04-24

This backlog is ordered from easiest to hardest. "Done" means the repository and public portal demonstrate the requirement, not just that a paragraph says it will happen later.

## Current Honest Status

The repository meets the GitHub Pages demonstration layer for OneRoster core, but it does not yet fully meet the whole platform spec. The biggest remaining gaps are full OneRoster 1.2 accounting, runnable backend slices beyond OneRoster, a real hosted database/API runtime, and implemented tenancy/auth/security controls.

## Easiest-First Work List

| Order | Work item | Why it is needed | Current status | Done when |
| --- | --- | --- | --- | --- |
| 1 | Publish this explicit gap backlog. | Keeps the portal honest about what is done versus planned. | Done. | Rendered in the portal docs and linked from the main site. |
| 2 | Add a dictionary coverage matrix. | Shows which specs are generated, hand-documented, executable, or deferred. | Done. | Each Lead spec has a row with generated source, generated artifacts, runnable status, and unsupported ledger status. |
| 3 | Move QTI into a structured source dictionary. | QTI currently has a Markdown dictionary, but not a generator-backed dictionary source. | Done for repository projection. | `dictionary/qti-core.v1.json` covers the platform's QTI repository model objects, fields, and controlled values. |
| 4 | Generate QTI SQL comments, OpenAPI schemas, and HTML/Markdown docs from that QTI source. | Proves the shared dictionary pattern beyond OneRoster. | Done for repository projection. | One script emits QTI SQL comments, OpenAPI field descriptions, and portal pages. |
| 5 | Add an unsupported/deferred ledger for QTI. | Full QTI is too large to flatten blindly; unsupported or preserved-in-artifact areas must be explicit. | Done for current projection. | Every non-modeled QTI area has a reason: preserved as XML, deferred delivery/runtime, or unsupported. |
| 6 | Add coverage checks for generated dictionaries. | Prevents new fields/enums from appearing without layperson explanations. | Done for structured OneRoster, QTI, CASE, Caliper, and integration/governance dictionaries. | A test fails when generated SQL/API/site artifacts miss an object, field, or value in a structured dictionary. |
| 7 | Convert CASE to a structured source dictionary and generated artifacts. | CASE is Lead and should be generator-backed, not only Markdown. | Done for framework graph projection. | CASE source emits SQL comments, OpenAPI schemas, and portal pages. |
| 8 | Convert Caliper to a structured source dictionary and generated artifacts. | Caliper is Lead and has many event/entity/action values. | Done for event projection. | Caliper source emits SQL comments, OpenAPI schemas, and portal pages, including event/action values. |
| 9 | Convert LTI/LTI Advantage, Security Framework, and Data Privacy to structured source dictionaries. | These are Lead/Governance surfaces and drive API scopes, auth, launch, consent, and policy. | Done for integration/governance projection. | `dictionary/integration-governance-core.v1.json` emits SQL comments, OpenAPI schemas, and portal pages for launch, AGS, NRPS, Deep Linking, OAuth, privacy, and governance objects. |
| 10 | Expand OneRoster from core demo to full OneRoster 1.2 accounting. | Current executable model is core, not the whole OneRoster standard. | Core slice generated; broader Markdown exists. | Every OneRoster object/field/value is generated, supported, or explicitly deferred with reason. |
| 11 | Add generated cross-spec decision traces. | Decisions should connect fields across specs, not live only as prose. | Prose decisions exist. | Dictionary entries expose cross-standard mappings and decisions link to the affected objects/fields. |
| 12 | Add a public machine-readable status manifest. | AI agents need a simple way to know what is runnable, generated, planned, or unsupported. | Not done. | `site/api/platform-status.json` or equivalent lists coverage and runnable surfaces. |
| 13 | Add a stronger browser "try it" workflow. | The current SQL console works, but examples should cover roster, class roster, and gradebook queries. | Basic SQL works. | Site includes selectable queries and JSON endpoint previews for the complete OneRoster demo slice. |
| 14 | Implement a real hosted relational database. | GitHub Pages cannot host a database; the spec asks for database access as a real layer. | Not done. | Postgres or equivalent is hosted with seeded demo data and read-only access path. |
| 15 | Implement a real hosted JSON API server. | Static JSON is not enough for filtering, auth, POSTs, or computed responses. | Static JSON plus local Express API. | Public API endpoints run at a real URL with OpenAPI matching behavior. |
| 16 | Add real SQL query endpoint against the hosted database. | Browser SQLite proves the idea but not shared hosted data access. | Browser-only SQL console. | Site can run read-only SQL against the hosted demo database through a safe server endpoint. |
| 17 | Implement tenant model and row-level isolation. | Tenancy is a central architectural decision, not just documentation. | Documented only. | Tenant IDs, policies, tests, and sample cross-tenant isolation are implemented. |
| 18 | Implement OAuth scopes and auth boundaries. | API access must reflect Security Framework and privacy decisions. | Documented only. | Demo clients/tokens/scopes control access to fields and endpoints. |
| 19 | Implement CASE import/search slice. | CASE is the canonical standards graph. | Docs only. | Demo can load a CASE framework, query items/associations, and expose API/search. |
| 20 | Implement QTI package import/projection slice. | QTI is not usable until packages can be stored, validated, and searched. | Docs only. | Demo imports fixture QTI package metadata, stores artifacts, and exposes projected items/tests/interactions/alignment. |
| 21 | Implement Caliper event ingestion slice. | Event/state decision is not proven until events can be accepted and projected. | Docs only. | Demo accepts sample Caliper events, stores immutable raw events, and exposes projections. |
| 22 | Implement LTI launch/Advantage sandbox. | LTI decision is not proven until tools can launch and call scoped services. | Docs only. | Demo supports launch validation plus sample NRPS/AGS/Deep Linking flows. |
| 23 | Add conformance-style fixtures and reports. | 1EdTech developers expect clear compatibility evidence. | Not done. | Repo has repeatable fixture tests and public conformance/support notes per spec. |
| 24 | Add production deployment docs. | Developers need to understand how the demo becomes an actual service. | Partial README only. | Deployment guide covers database, server, secrets, auth, migrations, and Pages/portal build. |
| 25 | Audit generated dictionary portal pages for duplicate or orphaned HTML. | Generators emit direct HTML pages while `build_site_docs.py` also renders generated Markdown into slugged pages. | Existing pattern; needs cleanup. | Each generated dictionary page has one canonical portal URL, or secondary generated pages are intentionally linked/redirected. |
| 26 | Add a harness runbook and smoke tests for `scripts/codex_loop.py`. | The loop now gates commit/push decisions with deterministic scoring, LLM judging, and timeouts. | Minimal CLI help and this backlog. | A runbook explains unattended operation, and smoke tests cover dry-run, timeout handling, score gates, and judge request construction without spending API tokens. |

## Immediate Execution Order

Items 1 through 9 are now cleared for the structured OneRoster, QTI, CASE, Caliper, and integration/governance dictionaries. The next cheapest high-leverage work is item 10: expand OneRoster from the core demo to full OneRoster 1.2 accounting.
