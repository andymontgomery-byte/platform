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

## Dictionary Rule

Every public SQL table, API resource, field, enum value, and relationship should have:

- A plain-language description.
- A source standard and version when known.
- A privacy class.
- Allowed values when the field is controlled by a vocabulary.
- A note explaining what not to confuse it with when the risk is obvious.

The Markdown files are the readable research layer. The seed JSON and SQL schema are the governed machine-readable starting point that should eventually absorb these definitions as implementation scope becomes concrete.
