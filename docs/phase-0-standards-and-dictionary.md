# Phase 0: Standards Registry and Data Dictionary

## Purpose

The first platform asset is not an app server. It is governed metadata.

The platform needs a trusted source of truth for:

- Which 1EdTech standards and versions we implement, prepare for, or support as legacy.
- Which data domains exist in the platform.
- What every object and field means in plain school language.
- Which SQL tables/views and JSON API fields expose each concept.
- Which privacy class, source standard, and access scope apply to each field.

This lets a human developer, school administrator, or AI agent understand the platform without reading every standard specification.

## Files

| File | Role |
| --- | --- |
| `schema/0001_registry_and_dictionary.sql` | Postgres schema for the standards registry and data dictionary. |
| `data/standards-registry.seed.json` | Machine-readable seed of researched 1EdTech standards and platform posture. |
| `data/data-dictionary.seed.json` | Machine-readable seed of platform domains, objects, fields, enums, and relationships. |
| `openapi/dictionary.v0.yaml` | Initial OpenAPI contract for serving dictionary metadata over JSON/HTTP. |
| `docs/dictionaries/` | Layperson Markdown dictionaries for standards objects, fields, values, privacy classes, and cross-standard relationships. |

## Design Rules

1. Every public SQL table, public SQL view, API resource, API field, enum value, and relationship must have a dictionary entry.
2. Dictionary descriptions must be understandable by someone who has been to school, not just by standards implementers.
3. Every standard-bound field must identify its source standard family and version when known.
4. Every field must carry a privacy classification.
5. Every identifier must explain whose identifier it is: platform, school, SIS, LMS, assessment provider, credential issuer, standards publisher, or another external source.
6. API docs and SQL docs should be generated from dictionary metadata, not separately rewritten.

## Privacy Classes

| Class | Meaning |
| --- | --- |
| `public` | Safe to publish without identifying a learner or private institution record. |
| `directory` | Common school directory information that may still be access-controlled. |
| `education_record` | Student education record data such as enrollment, grade, result, or progress. |
| `sensitive` | Data needing heightened handling, such as accommodations, demographics, or security-related values. |
| `credential` | Verifiable achievement or learner-record data. |
| `behavioral` | Activity, usage, clickstream, time-on-task, or engagement data. |
| `operational` | Import/export status, source lineage, validation results, or system metadata. |
| `system` | Internal platform configuration, secrets metadata, or infrastructure records. |

## Implementation Postures

| Posture | Meaning |
| --- | --- |
| `lead` | Build into the initial platform architecture. |
| `prepare` | Shape schemas so this can be implemented cleanly later. |
| `support` | Account for import/export, metadata, or customer-specific use. |
| `legacy` | Recognize for migration/history, but do not make it a new product contract. |
| `governance` | Use to guide trust, compliance, privacy, or security posture. |

## Acceptance Criteria

Phase 0 is complete when:

- The standards registry can answer "which standards do we support, why, and from which source links?"
- The dictionary can answer "what does this field mean, where does it appear, who may access it, and what standard does it map to?"
- The dictionary API can expose standards, objects, fields, enums, and relationships.
- Future schema migrations can fail review if new public fields lack dictionary entries.

## Next Build Step

After Phase 0, build Phase 1 around OneRoster 1.2:

- `organizations`
- `people`
- `users`
- `academic_sessions`
- `courses`
- `classes`
- `enrollments`
- `source_identifiers`
- CSV import/export lineage
- basic gradebook line items and results
