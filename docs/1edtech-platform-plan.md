# 1EdTech Platform Plan

Research date: 2026-04-24

## Mission

Build an educational platform that third-party edtech providers want to develop against because it gives them a clean, valuable, well-documented foundation for school data, content, assessment, outcomes, learning activity, credentials, privacy, and tool integration.

The platform has two developer-facing layers:

1. A raw relational database layer with a full plain-language data dictionary.
2. A web API layer with full OpenAPI documentation and the same plain-language data dictionary.

The database layer is the SQL interface. The web layer is the JSON/HTTP interface. Both must describe every object, field, status, enum, and relationship in language that a school-experienced non-specialist can understand.

## Official Standards Landscape

Priority standards:

| Standard | Current status found | What it means for the platform |
| --- | --- | --- |
| OneRoster | v1.2 Final, issued September 19, 2022. 1EdTech says OneRoster 1.2 is the most recent version. | Core rostering, organizations, academic sessions, courses, classes, enrollments, resources, gradebook, assessment results profile, REST and CSV exchange. |
| QTI | QTI v3.0 Final Release, May 11, 2022. QTI 2.2 remains important for legacy assessment content. | Assessment package storage, item/test metadata, accessible assessment delivery compatibility, result import/export. |
| CASE | CASE 1.1 Final Release, issued January 24, 2025 and publicly announced April 2, 2025. | Canonical competency, academic standard, course code, rubric, and framework graph. |
| Caliper Analytics | v1.2 Final, March 27, 2020. | Event stream and learning analytics vocabulary for activity, assessment, media, reading, sessions, grading, search, tool use, and more. |

Adjacent standards that should shape the platform early:

| Standard | Current status found | Platform role |
| --- | --- | --- |
| LTI / LTI Advantage | LTI 1.3 Final and LTI Advantage services AGS 2.0, NRPS 2.0, and Deep Linking 2.0 are Final releases issued April 16, 2019. | Launch and connect third-party tools, roster context on launch, deep-link content, and sync grades. |
| Common Cartridge / Thin Common Cartridge | CC 1.3 is final; CC/TCC 1.4 is Candidate Final and adds K-12 profile support, QTI 3, LTI 1.3/LTI Advantage, accessibility metadata, and CASE URIs. | Course/content package import/export and content metadata alignment. |
| Open Badges | Open Badges 3.0 Final Release, Document Version 1.4.3, issued April 22, 2026; Open Badges 2.1 covers Badge Connect API for OB 2.0. | Verifiable microcredentials, achievements, endorsements, wallets, verification. |
| CLR | CLR Standard 2.0 Final Release, Document Version 1.1, issued October 14, 2025. | Bundled longitudinal learner records and transcripts using verifiable credential patterns shared with Open Badges 3.0. |
| Edu-API | Candidate Final Public, moving toward first final release. | Higher-ed enterprise data model direction; use as a future bridge beyond K-12 OneRoster. |
| Data-SSML | v1.0 Final Release, July 1, 2024. | Text-to-speech pronunciation metadata for QTI 3 and HTML content. |
| CAT | v1.0 Public Candidate Final. | Future adaptive assessment interoperability with QTI-aligned item metadata. |
| Security Framework | v1.1 Final, July 19, 2021. | OAuth 2.0, JWT, OpenID Connect security patterns for 1EdTech web services. |
| Data Privacy | v1.0 Final, August 20, 2020. | Product privacy rubric/certification posture and data processing expectations. |
| TrustEd Apps Rubrics | Accessibility, Security Practices, and Generative AI Data rubrics are active self-assessment tools. | Vendor trust surface; document our own posture and expose enough metadata for customers to assess apps built on the platform. |
| Uniform ID Framework | Final framework for did:web-based identifiers in the 1EdTech ecosystem. | Future-proof globally verifiable identifiers for tools, content, credentials, courses, and organizations. |

Legacy and supporting standards to account for, but not lead with: AccessForAll, APIP, Content Packaging, Metadata, LTI Resource Search, Learning Information Services, Enterprise, Learner Information Package, Learning Design, Digital Repositories, Resource List Interoperability, Shareable State Persistence, ePortfolio, General Web Services, Course Planning and Scheduling, and Competency Definitions. These matter for migration, import/export, or historical integrations, but they should not define the core platform architecture unless a customer needs them.

## Broader Standards Inventory

This is the implementation posture for the wider 1EdTech catalog. "Lead" means build into the first platform shape. "Prepare" means design the schema so the standard fits later. "Support/legacy" means account for import/export, migration, or customer-specific compatibility without letting it drive the MVP.

| Standard or practice | Latest public status found | Platform posture |
| --- | --- | --- |
| OneRoster | 1.2 Final | Lead: core K-12 roster, resources, gradebook, REST/CSV, assessment results profile. |
| QTI | 3.0 Final; 2.2 still widely relevant | Lead: QTI 3 repository/projections first; preserve QTI 2.2 migration path. |
| CASE | 1.1 Final | Lead: standards/competency/course-code/rubric graph and alignment backbone. |
| Caliper Analytics | 1.2 Final | Lead: event ingestion, immutable event store, profile projections, privacy-safe aggregates. |
| LTI / LTI Advantage | LTI 1.3 Final; LTI Advantage 1.0 with AGS 2.0, NRPS 2.0, Deep Linking 2.0 Final | Lead: launch, membership, deep linking, and grade passback. |
| Security Framework | 1.1 Final | Lead: OAuth 2.0, JWT, OIDC, scopes, service security. |
| Data Privacy | 1.0 Final | Lead: privacy classifications, vetting posture, audit, data-sharing controls. |
| Common Cartridge / Thin Common Cartridge | CC 1.3 Final; CC/TCC 1.4 Candidate Final | Prepare: package import/export after QTI/CASE/LTI foundations. |
| Open Badges | 3.0 Final Release, issued April 22, 2026; 2.1 Badge Connect API for OB 2.0 | Prepare: credentials and learner-controlled sharing. |
| CLR Standard | 2.0 Final Release, issued October 14, 2025 | Prepare: longitudinal learner record and transcript bundles. |
| Edu-API | Candidate Final Public | Prepare: higher-ed enterprise expansion; do not use as MVP conformance target yet. |
| Data-SSML | 1.0 Final | Prepare inside QTI/content accessibility metadata. |
| CAT | 1.0 Public Candidate Final | Prepare: adaptive assessment engine interoperability after QTI repository maturity. |
| Uniform ID Framework | Final framework | Prepare: did:web identifiers for institutions, tools, credentials, courses, and content. |
| Versioning Framework | 1.0 Final | Support: use as guidance for standard/version registry and API versioning. |
| AccessForAll / Accessibility | AccessForAll 2.0 Final; 3.0 Public Draft | Support: accessibility preferences/context; also use modern TrustEd Apps Accessibility Rubric. |
| APIP | 1.0 Final | Support/legacy: QTI 3 integrates the accessibility direction; import APIP only when needed. |
| Content Packaging | 1.1.4 Final; 1.2 Public Draft v2 | Support: packaging substrate through QTI and Common Cartridge. |
| Metadata | 1.3 Final | Support: package/resource metadata where referenced by CC/QTI. |
| LTI Resource Search | 1.0 Final | Support later: resource discovery if marketplace/search becomes a core product. |
| Learning Information Services | 2.0.1 Final | Support/legacy: higher-ed lineage; prefer Edu-API direction for new work. |
| Enterprise / Enterprise Services | Legacy enterprise exchange family | Support/legacy: useful for migration analysis, not a new platform contract. |
| Learner Information Package | 1.0.1 Final | Support/legacy: avoid broad learner-profile collection unless privacy need is explicit. |
| Learning Design | 1.0 Final | Support/legacy: pedagogical sequencing/content model history, not MVP. |
| Digital Repositories | Version 1 Final | Support/legacy: repository interoperability only if content marketplace needs it. |
| Resource List Interoperability | 1.0 Final | Support/legacy: reading/resource lists only when a customer workflow demands it. |
| Shareable State Persistence | 1.0 Final | Support/legacy: old tool state pattern; modern LTI/platform APIs should cover new work. |
| ePortfolio | 1.0 Final | Support/legacy: credentials/CLR supersede most new portable-record needs. |
| General Web Services | 1.0 Final | Support/legacy: historical service binding guidance. |
| Course Planning and Scheduling | 1.0 Candidate Final | Support/prepare: scheduling/catalog workflows are later-phase unless the buyer persona is higher ed. |
| Competency Definitions / RDCEO | 1.0 Final | Support/legacy: CASE is the practical current competency exchange backbone. |
| TrustEd Apps rubrics | Data Privacy, Accessibility, Security Practices, and Generative AI Data self-assessment tools | Governance: use for our own trust posture and supplier-facing requirements. |

## Product Thesis

Most edtech integrations fail because every vendor has to rediscover school data shape, identifier meaning, privacy constraints, learning standards, assessment payloads, and result semantics. The platform should make those things boring:

- A provider can answer "who is this learner, where are they enrolled, what content are they using, what standards does it align to, what did they do, what did they achieve, and what may I access?" without custom district work.
- A school can onboard tools with a consistent contract and keep control over data sharing.
- AI agents can use SQL or documented JSON APIs to build useful educational applications without reverse-engineering obscure spec documents.

## Architecture Decisions

### 1. What is the canonical data model?

Options:

- Mirror each 1EdTech spec as isolated tables.
- Build one custom education model and only import/export standards at the edges.
- Build a canonical relational education graph that preserves each standard's native identifiers, versions, payloads, and conformance boundaries.

Choice: canonical relational education graph with standard-specific projections.

Tradeoffs:

- This avoids a brittle "OneRoster-only" model while still giving developers normal relational tables.
- It lets QTI packages, Caliper events, CASE frameworks, credentials, and LTI launches coexist without forcing every concept into one spec.
- It costs more upfront because conformance views and adapters must be maintained per standard version.

### 2. Should the database layer expose raw tables or curated views?

Options:

- Raw physical tables only.
- Stable SQL views only.
- Raw tables plus stable documented views.

Choice: raw tables plus stable documented views.

Tradeoffs:

- Raw tables help power users, AI agents, and internal operators inspect everything.
- Stable views give app developers a contract that can survive internal schema changes.
- Documentation must clearly label "storage table", "public SQL contract", and "standard conformance view".

### 3. How should identifiers work?

Options:

- Use only internal UUIDs.
- Use each source system's IDs as primary keys.
- Use internal UUIDs plus a first-class identifier crosswalk.

Choice: internal UUID primary keys plus a first-class crosswalk for OneRoster `sourcedId`, CASE GUIDs, LTI deployment IDs, QTI package identifiers, Caliper IRIs, Open Badge/CLR credential IDs, and future did:web identifiers. Public identifier shape depends on the API surface: OneRoster-shaped endpoints expose `sourcedId` as the primary standards contract and include platform UUIDs as metadata; native platform endpoints use platform UUIDs as primary IDs and include source IDs in documented crosswalk fields.

Tradeoffs:

- Internal IDs keep the platform stable when SIS/LMS/vendor IDs change.
- Crosswalks preserve standard conformance and make troubleshooting possible.
- OneRoster provider/consumer surfaces should not force developers to remap away from `sourcedId`; native platform APIs can use platform IDs for long-lived joins.
- Caliper, LTI, credential, and import pipelines must resolve incoming source identifiers at ingestion time, and unresolved identifiers should be stored as explicit lineage exceptions rather than silently creating duplicate people, classes, or results.

### 4. What is the initial market/data boundary?

Options:

- K-12 first.
- Higher education first.
- Build a generic education model from day one.

Choice: K-12 operational core first, with higher-ed-safe abstractions.

Tradeoffs:

- OneRoster, CASE, QTI, Caliper, Common Cartridge, and LTI give a strong K-12 starting point.
- Edu-API is not final yet, so higher-ed enterprise modeling should be prepared but not hard-coded as the MVP contract.
- The model should avoid K-12-only names where a neutral term works, for example `organization`, `learning_context`, `academic_period`, `offering`, and `enrollment`.

### 5. What API style should be primary?

Options:

- REST/JSON only.
- GraphQL only.
- REST/JSON with OpenAPI first, plus later graph/query endpoints.

Choice: REST/JSON with OpenAPI first.

Tradeoffs:

- 1EdTech REST bindings, OAuth scopes, certification tooling, and implementer expectations fit REST well.
- OpenAPI is easy for humans and AI agents to consume.
- Graph-style joins are useful later, but the initial API should avoid inventing semantics before the relational model is proven.

### 6. How should assessment content be stored?

Options:

- Fully decompose every QTI XML element into relational tables.
- Store QTI packages as opaque files.
- Store canonical package artifacts plus relational projections for searchable and reportable fields.

Choice: package artifacts plus first-class rows for item/test inventory and relational projections for the fields developers actually query.

Tradeoffs:

- QTI is rich and XML-heavy; fully decomposing every element creates a fragile assessment engine by accident.
- Opaque storage alone prevents item banking, item-level reuse, item-level analytics, standards search, accessibility review, and AI-assisted authoring.
- Minimum first-class rows: QTI package, assessment test, assessment section, assessment item, stimulus, item reference, interaction, response declaration, outcome declaration, scoring/rubric metadata, accessibility/support metadata, CASE alignment, and package artifact.
- Minimum projected fields: package/version lineage, item/test identifiers, title, language, interaction type, response cardinality, base type, scoring method, max score, time limits, adaptive/dependent flags, accessibility features, support tools, rubric/feedback presence, and CASE target identifiers.
- The platform should not claim QTI runtime conformance until delivery/session behavior is implemented; repository/search/import/export support is a separate and narrower claim.

### 7. How should learning activity be stored?

Options:

- Only current-state tables.
- Only append-only Caliper events.
- Append-only event store plus curated state/projection tables.

Choice: append-only Caliper event store plus curated projections.

Tradeoffs:

- Caliper's value is event semantics over time, so immutable events are necessary.
- Product dashboards and AI agents also need easy SQL over sessions, attempts, content usage, and activity summaries.
- Event data can contain sensitive behavioral information, so retention, minimization, aggregation, and access controls must be designed up front.

### 8. How should standards alignment work?

Options:

- Store text labels for standards.
- Store CASE GUID/URI links only.
- Store CASE as a full framework graph and link all content, assessments, outcomes, credentials, and analytics back to CASE nodes.

Choice: full CASE graph as the alignment backbone.

Tradeoffs:

- CASE is the cleanest way to connect curriculum, assessment, content, credentials, and reporting.
- Full graph support is more work than flat tags, but it unlocks resource search, mastery reporting, crosswalks, and AI reasoning.
- CASE 1.1 adds broader framework/course-code capability, so design for more than academic standards.

### 9. Do platform API calls require an LTI launch context?

Options:

- Require every platform API call to be tied to an active LTI launch context.
- Make platform APIs independently addressable through OAuth client credentials or authorization code grants.
- Support both, with scopes and policy deciding which data requires launch context.

Choice: support both. LTI 1.3/LTI Advantage is required for launch-time classroom context, deep linking, NRPS, and AGS workflows. Platform APIs are independently addressable through OAuth for server-to-server, administrative, analytics, dictionary, content, and credential use cases. Some calls can require a launch-bound context token when the data should only be available from inside a specific class/activity placement.

Tradeoffs:

- LTI gets vendors into courses securely with familiar platform behavior.
- Independently addressable APIs provide value beyond launch: standards, analytics, QTI packages, resource catalogs, credentials, operational data, and normalized SQL-backed data.
- Launch-bound authorization protects contextual learner/class data when a tool should only act inside a placement.
- Scope design and tenant policy must prevent either model from becoming broad data access by accident.

### 10. How should tenancy and shared standards data work?

Options:

- Single-tenant deployments per institution.
- One shared multi-tenant database with row-level tenant isolation.
- Schema-per-tenant or database-per-tenant, with shared reference datasets copied or synced.

Choice: multi-tenant core with tenant IDs on tenant-owned records and row-level security as the default SQL enforcement model; shared reference data such as public CASE frameworks, public QTI item banks, public standards metadata, and certification fixtures live in governed shared namespaces with explicit adoption/link records per tenant.

Tradeoffs:

- A multi-tenant core is the right default for a platform third parties build against, because vendors need one integration path across many schools.
- Row-level security keeps SQL access viable without forcing every tenant into a separate database, but policy testing becomes a release-critical requirement.
- Shared CASE/QTI/reference data avoids duplication and supports marketplace/search workflows, but tenant adoption, local overrides, and private item banks must be modeled explicitly.
- High-risk or contractually isolated tenants may still need database-per-tenant deployment as an enterprise option, but that should not be the default product architecture.

### 11. How should privacy and security be handled?

Options:

- Add privacy after the data model.
- Use generic SaaS security controls.
- Treat 1EdTech Security Framework, Data Privacy, TrustEd Apps, and least-privilege access as architecture inputs.

Choice: privacy/security by design.

Tradeoffs:

- This is slower early, but education data is high-trust data.
- The platform should support tenant isolation, row-level access policies, audit logs, scoped OAuth, consent/sharing records, PII classification, de-identification, retention policies, and vendor data-sharing agreements.
- TrustEd Apps rubrics are not a substitute for law or institutional policy, but they provide a practical supplier-facing trust vocabulary.

### 12. How should documentation be generated?

Options:

- Hand-written docs.
- Schema-generated docs only.
- Documentation generated from a governed data dictionary that feeds database comments, OpenAPI descriptions, docs pages, and examples.

Choice: governed data dictionary as a source artifact.

Tradeoffs:

- A single dictionary keeps SQL and API docs consistent.
- It enables AI agents to understand the data without private tribal knowledge.
- It requires every schema/API change to include plain-language descriptions, enum meanings, examples, privacy classification, source standard references, and common mistakes.

### 13. What does conformance mean for us?

Options:

- Claim compatibility based on implementation.
- Build to the specs and certify only after market pull.
- Make certification a release gate for standard-provider surfaces.

Choice: build toward conformance from day one; make certification a release gate for public provider/consumer claims.

Tradeoffs:

- 1EdTech's public guidance distinguishes certification from informal compliance claims.
- Certification requires membership and test-suite work, so it should be planned as a product milestone.
- Internal beta APIs can exist before certification, but marketing and developer docs should be precise about what is certified, compatible, experimental, or planned.

## Proposed Domain Model

| Domain | Representative relational objects | Main standards |
| --- | --- | --- |
| Tenancy and governance | tenants, institutions, shared_reference_namespaces, tenant_adoptions, data-sharing agreements, vendor applications, scopes, consents, audits | Security Framework, Data Privacy, TrustEd Apps |
| Identity and organizations | people, users, agents, organizations, schools, districts, departments, roles, identifiers | OneRoster, LTI, Edu-API, Uniform ID |
| Academic structure | academic sessions, courses, course offerings, classes, sections, enrollments | OneRoster, Edu-API, LIS legacy |
| Curriculum and standards | case_frameworks, case_items, case_associations, case_rubrics, alignments | CASE |
| Content packages | resources, cartridges, cartridge_items, metadata, accessibility metadata, resource links | Common Cartridge, Thin CC, Content Packaging, Metadata |
| Assessment content | qti_packages, qti_items, qti_tests, interactions, scoring_metadata, accessibility_features, data_ssml_annotations | QTI, Data-SSML, CAT |
| Outcomes and gradebook | line_items, result_sets, results, attempts, score_scales, assessment_results | OneRoster Gradebook, OneRoster Assessment Results Profile, LTI AGS, QTI Results |
| Learning activity | caliper_events, actors, actions, activities, sessions, generated_objects, event_profiles, aggregates | Caliper |
| Tool integration | lti_platforms, lti_tools, registrations, deployments, launches, deep_links, memberships | LTI 1.3, LTI Advantage |
| Credentials | achievements, badge_classes, open_badge_credentials, clr_credentials, endorsements, verifications | Open Badges 3.0, CLR 2.0, W3C VC |
| Operational metadata | imports, exports, source_systems, standard_versions, validation_results, lineage_records | All standards |

## API Surface

Initial public API groups:

| API group | Purpose |
| --- | --- |
| `/organizations` | Districts, schools, departments, and other education organizations. |
| `/people` and `/users` | Learners, teachers, staff, guardians where permitted, and role/context data. |
| `/academic-sessions`, `/courses`, `/classes`, `/enrollments` | Core roster and academic structure. |
| `/standards` | CASE frameworks, items, associations, rubrics, and crosswalks. |
| `/resources` and `/cartridges` | Content metadata, Common Cartridge imports/exports, resource allocation. |
| `/assessments` | QTI packages, items, tests, metadata, alignment, and validation. |
| `/gradebook` | Line items, categories, score scales, results, and assessment result profiles. |
| `/events` | Caliper event ingestion and authorized event queries. |
| `/lti` | Tool registration, deployment, launch validation, deep linking, NRPS, AGS integration helpers. |
| `/credentials` | Open Badges/CLR issue, store, verify, revoke/status, and learner-controlled sharing workflows. |
| `/dictionary` | Machine-readable and human-readable descriptions for every table, field, endpoint, enum, and relationship. |

API principles:

- Every endpoint has OpenAPI docs with examples.
- Every response field links back to the data dictionary.
- Every resource includes source lineage and relevant standard identifiers.
- Every write path validates standard constraints where the resource claims standard compatibility.
- Every list endpoint supports filtering, pagination, sparse fieldsets, and tenant-safe authorization.

## Data Dictionary Requirements

Each object and field must include:

- Plain-language name.
- Technical name.
- What it means in a school.
- Why it exists.
- Data type and allowed values.
- Required/optional status.
- Example values.
- Source standard and version, if applicable.
- Privacy classification: public, directory, education record, sensitive, credential, behavioral, operational.
- Access rules and common scopes.
- Lineage: source system, import file/API, last seen, validation status.
- Common mistakes.
- Related SQL table/view and API field.

Example style:

| Field | Plain-language description |
| --- | --- |
| `enrollment.role` | The person's job in the class, such as student or teacher. |
| `identifier.external_id` | The ID used by another system, such as an SIS, LMS, assessment platform, or standards publisher. |
| `case_item.human_coding_scheme` | The short standards code people see in curriculum documents, for example a state standard label. |
| `caliper_event.action` | What happened in a learning tool, such as viewed, started, completed, submitted, graded, searched, or logged in. |
| `qti_item.interaction_type` | The kind of question interaction, such as choice, text entry, upload, matching, hotspot, or a portable custom interaction. |

## Implementation Phases

### Phase 0: Standards Corpus and Dictionary Seed

- Create a versioned standards registry table.
- Load official source links, versions, statuses, and implementation notes.
- Define the first data dictionary schema.
- Build documentation generation for Markdown, SQL comments, and OpenAPI descriptions.

### Phase 1: OneRoster Core

- Implement tenants, organizations, users, academic sessions, courses, classes, enrollments, identifiers, and import lineage.
- Support OneRoster 1.2 CSV import/export.
- Add OneRoster REST provider/consumer-compatible API surfaces.
- Add basic gradebook line items and results.

### Phase 2: CASE Backbone

- Implement CASE 1.1 frameworks, items, associations, rubrics, definitions, packages, versions, and crosswalks.
- Link courses, classes, content resources, assessments, gradebook line items, and credentials to CASE items.
- Provide standards search and alignment APIs.

### Phase 3: QTI and Assessment Repository

- Store QTI 3 packages and preserve package artifacts.
- Extract searchable relational projections.
- Validate QTI packages and track validation results.
- Add Data-SSML metadata support and prepare CAT-compatible metadata surfaces.
- Preserve QTI 2.2 import/migration support for legacy content.

### Phase 4: Caliper Event Platform

- Implement Caliper 1.2 event ingestion.
- Store immutable event envelopes and profile-specific parsed projections.
- Build privacy-safe aggregates for product analytics, engagement, assessment attempts, and resource usage.

### Phase 5: LTI and Tool Developer Platform

- Implement LTI 1.3 launch validation and platform/tool registrations.
- Add LTI Advantage helpers for AGS, NRPS, and Deep Linking.
- Expose developer onboarding, OAuth scopes, sandbox tenants, test data, and conformance reports.

### Phase 6: Content, Credentials, and Higher-Ed Expansion

- Add Common Cartridge/Thin Common Cartridge import/export.
- Add Open Badges 3.0 and CLR 2.0 credential services.
- Expand toward Edu-API as it stabilizes and as higher-ed use cases require it.
- Add Uniform ID/did:web support where verifiable identifiers create clear value.

## MVP Release Definition

The first credible MVP should include:

- OneRoster 1.2 rostering import/export and normalized SQL/API access.
- CASE 1.1 framework ingestion and standards alignment APIs.
- QTI 3 package storage with metadata extraction and CASE alignment.
- Caliper 1.2 event ingestion for a small set of high-value profiles: Session, Tool Use, Assessment, Assignable, Grading, Reading/Media as needed.
- LTI 1.3 launch support and LTI Advantage grade passback integration.
- Full generated documentation for SQL tables, SQL views, API endpoints, fields, enums, scopes, and examples.
- Tenant isolation, OAuth scopes, audit logs, privacy classifications, and source lineage.

This MVP gives vendors a reason to integrate: they get roster context, standards, assessment content, grade/outcome exchange, analytics events, and launch/grade workflows through one coherent platform.

## Risks

| Risk | Mitigation |
| --- | --- |
| Standards breadth creates a platform that is too large to ship. | Phase by developer value: OneRoster + CASE + QTI metadata + Caliper ingestion + LTI launch first. |
| QTI becomes an assessment engine project. | Store packages and relational projections first; delivery engine integration can be separate. |
| Caliper data becomes privacy-sensitive exhaust. | Classify behavioral data, restrict raw event access, aggregate by default, and define retention policies. |
| Vendors want custom fields. | Support namespaced extensions and external identifiers, but keep public contracts standard-first. |
| Certification takes longer than expected. | Build conformance tests into CI early and label surfaces accurately until certified. |
| AI agents misunderstand fields. | Make dictionary examples, enum explanations, relationship maps, and "common mistakes" mandatory. |

## Key Open Questions

1. Should the first buyer persona be K-12 district platform teams, assessment providers, LMS/content providers, or AI-edtech app developers?
2. Do we want to become a certified OneRoster provider, consumer, or aggregator first?
3. Should QTI support stop at repository/import/export initially, or should the platform also provide assessment delivery/runtime APIs?
4. What is the default data retention policy for raw Caliper events?
5. How much learner-controlled credential sharing should be in the first credential phase versus delegated to wallets?
6. Will SQL access be direct database access, a governed query service, or both?

## Source Links

- 1EdTech interoperability standards index: https://www.1edtech.org/specifications
- OneRoster overview: https://www.1edtech.org/standards/oneroster
- OneRoster 1.2 specification: https://www.imsglobal.org/spec/oneroster/v1p2/
- QTI overview: https://www.1edtech.org/standards/qti
- QTI specification documents: https://www.1edtech.org/standards/qti/index
- CASE overview: https://www.1edtech.org/standards/case
- CASE 1.1 information model: https://www.imsglobal.org/sites/default/files/spec/case/v1p1/information_model/caseservicev1p1_infomodelv1p0.html
- CASE 1.1 REST binding: https://www.imsglobal.org/sites/default/files/spec/case/v1p1/rest_binding/caseservicev1p1_restbindv1p0.html
- CASE 1.1 announcement: https://www.1edtech.org/1edtech-article/new-case-11-standard-empowers-educators-to-connect-learning-standards-with-courses
- Caliper overview: https://www.1edtech.org/standards/caliper
- Caliper 1.2 specification: https://www.imsglobal.org/spec/caliper/v1p2
- LTI overview: https://www.1edtech.org/standards/lti
- LTI Core 1.3 specification: https://www.imsglobal.org/spec/lti/v1p3/
- LTI Assignment and Grade Services 2.0 specification: https://www.imsglobal.org/spec/lti-ags/v2p0/
- LTI Names and Role Provisioning Services 2.0 specification: https://www.imsglobal.org/spec/lti-nrps/v2p0/
- LTI Deep Linking 2.0 specification: https://www.imsglobal.org/spec/lti-dl/v2p0/
- Common Cartridge overview: https://www.1edtech.org/standards/cc
- Common Cartridge specification index: https://www.imsglobal.org/cc/index.html
- Open Badges overview: https://www.1edtech.org/standards/open-badges
- Open Badges 3.0 specification: https://www.imsglobal.org/spec/ob/v3p0
- CLR overview: https://www.1edtech.org/standards/clr
- CLR 2.0 specification: https://www.imsglobal.org/spec/clr/v2p0
- Edu-API overview: https://www.1edtech.org/standards/edu-api
- Data-SSML overview: https://www.1edtech.org/standards/data-ssml
- CAT overview: https://www.1edtech.org/standards/cat
- Security Framework: https://www.1edtech.org/standards/security-framework
- Data Privacy: https://www.1edtech.org/standards/data-privacy
- Accessibility Rubric: https://www.1edtech.org/standards/accessibility-rubric
- Security Practices Rubric: https://www.1edtech.org/standards/security-practices-rubric
- Generative AI Data Rubric: https://www.1edtech.org/standards/ai-rubric
- Uniform ID Framework: https://www.1edtech.org/standards/uniform-id-framework
