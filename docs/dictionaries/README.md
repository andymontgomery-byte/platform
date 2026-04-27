# Layperson Data Dictionary Index

Research date: 2026-04-24

This folder is the human-readable dictionary for the platform. Each file explains standards objects, fields, and vocabulary values in school-friendly language, with privacy classes and implementation notes.

## Coverage

| Dictionary | Primary standards | Main coverage |
| --- | --- | --- |
| [OneRoster 1.2](oneroster-1.2-layperson-dictionary.md) | OneRoster 1.2 Rostering, Gradebook, Resources, CSV binding | Academic sessions, organizations, courses, classes, users, roles, enrollments, demographics, resources, categories, line items, results, score scales, and OneRoster values. |
| [CASE 1.1](case-1.1-layperson-dictionary.md) | CASE 1.1 information model and REST binding | Framework packages, documents, items, associations, concepts, subjects, item types, licenses, rubrics, rubric criteria, rubric levels, and CASE values. |
| [QTI 3](qti-3-layperson-dictionary.md) | QTI 3 assessment/item/test model | Assessment packages, items, stimuli, tests, sections, item references, declarations, processing rules, interactions, feedback, rubrics, accessibility, support tools, and QTI values. |
| [Caliper 1.2](caliper-1.2-layperson-dictionary.md) | Caliper Analytics 1.2 | Event envelopes, base events, entities, event types, profiles, actions, roles, statuses, LTI session fields, and Caliper values. |
| [Integration, Packaging, Credentials, and Governance](integration-packaging-credentials-governance-layperson-dictionary.md) | LTI 1.3, LTI Advantage, Common Cartridge, Open Badges 3.0, CLR 2.0, Security Framework 1.1, Data Privacy | Tool launch, memberships, grade passback, deep linking, cartridge packages, badge and CLR credentials, proofs, scopes, OAuth/OIDC security, privacy rules, and governance values. |

## How To Use These Dictionaries

Start with the file for the standard that owns the data you are modeling. If a workflow crosses standards, use the cross-standard relationship sections to keep source IDs and meanings separate.

Examples:

- A course roster import starts in OneRoster, then may link to LTI launches and Caliper activity.
- A standards-aligned quiz starts in QTI, links to CASE, may be packaged in Common Cartridge, and may produce OneRoster or LTI AGS results.
- A microcredential starts as an Open Badges achievement, may align to CASE, and may later be bundled inside a CLR credential.

## Why The Concepts Stay Separate

These decisions explain the "why" behind the dictionary shapes, not just the fields they contain.

| Decision | Plain-language reason |
| --- | --- |
| [DEC-001 person and agent](decisions-standards-overlap-decisions.html#DEC-001-person-agent-subject) | A learner, teacher, guardian, or staff member is a person because the platform can apply roster privacy and identity policy to them. Tools, groups, issuers, and unresolved actors stay agents so analytics and LTI events do not accidentally merge software or unknown subjects into student records. |
| [DEC-002 learning context](decisions-standards-overlap-decisions.html#DEC-002-learning-context) | Courses, classes, groups, and launch contexts overlap, but they answer different scheduling and authorization questions. The dictionary keeps their source meaning while giving apps stable context IDs for joins. |
| [DEC-003 role vocabulary](decisions-standards-overlap-decisions.html#DEC-003-role-vocabulary) | OneRoster, LTI, Caliper, and governance scopes use different role words. A shared role-family enum lets policy reason over learner, educator, guardian, staff, tool, and issuer without deleting the source value. |
| [DEC-004 enrollment and membership](decisions-standards-overlap-decisions.html#DEC-004-enrollment-membership) | Enrollment is the school roster relationship that says a person belongs to a class. Membership is the context-specific participation view exposed through LTI or another service. Keeping both avoids using a tool roster as the legal roster of record. |
| [DEC-005 results and scores](decisions-standards-overlap-decisions.html#DEC-005-results-scores) | A line item is the assignment or gradebook column, while a result is a learner's score or feedback on it. This split makes grade passback and reporting predictable. |
| [DEC-006 standards alignment](decisions-standards-overlap-decisions.html#DEC-006-standards-alignment) | CASE standards are reference data. Assignments and resources point to CASE URIs instead of copying framework text into every gradebook or content record. |
| [DEC-007 identifier crosswalk](decisions-standards-overlap-decisions.html#DEC-007-identifier-crosswalk) | Every source system has its own IDs. The platform keeps source IDs in a crosswalk so apps can match records without treating an SIS ID, LTI subject, CASE URI, or QTI identifier as the same thing. |
| [DEC-008 time and sessions](decisions-standards-overlap-decisions.html#DEC-008-time-session) | Academic terms, assignment dates, event times, and record-modified timestamps serve different workflows, so the dictionary names each time concept explicitly. |
| [DEC-009 content and resources](decisions-standards-overlap-decisions.html#DEC-009-content-resource) | Content packages, resources, and launch targets are modeled separately from roster and results so apps can connect learning materials without making every resource a gradebook item. |
| [DEC-010 tenancy](decisions-standards-overlap-decisions.html#DEC-010-tenancy-reference-data) | Tenant-owned rows are isolated by RLS, while shared reference data can be reused. This keeps demo and production data from crossing district boundaries. |
| [DEC-011 privacy surfaces](decisions-standards-overlap-decisions.html#DEC-011-privacy-surfaces) | A field may be safe in generated docs but unsafe in public JSON or anonymous REST. Privacy class plus surface rules decide where each field may appear. |
| [DEC-012 runtime coverage](decisions-standards-overlap-decisions.html#DEC-012-runtime-coverage-per-spec) | The platform is honest about which specs have hosted runtime slices now and which are dictionary-only until later implementation. |
| [DEC-013 audit truth](decisions-standards-overlap-decisions.html#DEC-013-audit-response-truth) | Edge Functions must not claim audit rows were written unless the response reflects what the platform actually recorded. |
| [DEC-014 static mirrors](decisions-standards-overlap-decisions.html#DEC-014-static-mirror-policy) | Static JSON and HTML are documentation mirrors, not the live system of record. They are kept for review but must not bypass runtime privacy rules. |
| [DEC-015 service role](decisions-standards-overlap-decisions.html#DEC-015-service-role-policy) | Service-role access is powerful enough to bypass user policy, so it is limited to named admin or test-fixture operations. Runtime examples use caller JWTs. |
| [DEC-016 dictionary generation](decisions-standards-overlap-decisions.html#DEC-016-dictionary-generation-direction) | The shared seed is upstream and per-spec dictionaries are generated projections. This prevents hand-edited spec files from drifting apart. |
| [DEC-017 canonical fields](decisions-standards-overlap-decisions.html#DEC-017-canonical-field-reconciliation) | Overlapping fields point to shared canonical field IDs so OneRoster, LTI, Caliper, QTI, CASE, and governance docs agree on the concept behind each source field. |
| [DEC-018 global enums](decisions-standards-overlap-decisions.html#DEC-018-global-enum-crosswalks) | Shared enum tables preserve source-native values and map them to canonical values, giving apps one policy vocabulary without hiding the original spec term. |
| [DEC-019 privacy classes](decisions-standards-overlap-decisions.html#DEC-019-closed-privacy-classes) | Privacy classes are a closed list. Placeholder classes such as "depends on contents" are resolved per field so enforcement can be deterministic. |
| [DEC-020 relational graph](decisions-standards-overlap-decisions.html#DEC-020-relational-graph-migrations) | Relationships live in the dictionary graph and generate Supabase migrations, so docs, schema, and API behavior describe the same joins. |

## Dictionary Rule

Every public SQL table, API resource, field, enum value, and relationship should have:

- A plain-language description.
- A source standard and version when known.
- A privacy class.
- Allowed values when the field is controlled by a vocabulary.
- A note explaining what not to confuse it with when the risk is obvious.

The Markdown files are the readable research layer. The seed JSON and SQL schema are the governed machine-readable starting point that should eventually absorb these definitions as implementation scope becomes concrete.
