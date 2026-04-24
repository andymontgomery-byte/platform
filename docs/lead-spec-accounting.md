# Lead Spec Accounting

Research date: 2026-04-24

This page explains how every standard currently marked `Lead` is accounted for. "Accounted for" means the standard is either covered by a layperson dictionary entry, represented in the current runnable model, or explicitly deferred with a reason.

## Summary

| Lead area | Current status | Dictionary/accounting location |
| --- | --- | --- |
| OneRoster 1.2 | Runnable core slice plus broader layperson dictionary. | `dictionary/oneroster-core.v1.json`, generated OneRoster docs, OneRoster layperson dictionary. |
| CASE 1.1 | Structured/generated framework graph projection exists; not yet executable. | `dictionary/case-core.v1.json`, generated CASE docs/OpenAPI/SQL comments, CASE layperson dictionary, overlap decisions for alignment. |
| QTI 3 | Structured/generated repository projection exists; not yet executable. | `dictionary/qti-core.v1.json`, generated QTI docs/OpenAPI/SQL comments, QTI layperson dictionary, QTI projection decision, overlap decisions for results, alignment, resources, time. |
| Caliper 1.2 | Structured/generated event projection exists; event ingestion not yet executable. | `dictionary/caliper-core.v1.json`, generated Caliper docs/OpenAPI/SQL comments, Caliper layperson dictionary, overlap decisions for actor, membership, grade events, time. |
| LTI 1.3/LTI Advantage | Structured/generated integration projection exists; launch and services are not yet executable. | `dictionary/integration-governance-core.v1.json`, generated integration/governance docs/OpenAPI/SQL comments, integration layperson dictionary, overlap decisions for launch context, roles, membership, IDs, resources. |
| Security Framework 1.1 | Structured/generated OAuth and scope-policy projection exists; token issuance and enforcement are deferred until auth layer exists. | `dictionary/integration-governance-core.v1.json`, generated integration/governance docs/OpenAPI/SQL comments, tenancy and privacy/security decisions. |
| Data Privacy 1.0 | Structured/generated policy projection exists; live privacy workflows are deferred until tenant/auth layer exists. | `dictionary/integration-governance-core.v1.json`, privacy classes, generated integration/governance docs/OpenAPI/SQL comments, tenancy and privacy/security decisions. |

## OneRoster 1.2

Covered in the current runnable model:

- Organizations
- People/users
- Academic sessions
- Courses
- Classes
- Enrollments
- Gradebook line items
- Gradebook results
- Source identifiers/crosswalks
- Controlled values for organization type, status, role, class type, session type, enabled user, categories, score status, identifier type, and true/false fields

Covered in the broader dictionary but not yet executable:

- Demographics
- Agents/relationships
- Resources
- Categories beyond the demo set
- Score scales
- Assessment Results Profile fields
- CSV bulk-exchange operational details beyond the schema/dictionary seed

Deferred or not supported in the runnable slice:

| Area | Reason |
| --- | --- |
| Write APIs | The public demo is read-only to make GitHub Pages hosting safe. |
| Full OneRoster REST provider/consumer conformance | Requires hosted auth, certification testing, pagination, filtering, and full binding behavior. |
| Demographics execution | Sensitive data should wait for tenant policy, auth, and row-level controls. |

## CASE 1.1

Accounted for in the CASE dictionary:

- CFPackage
- CFPckgDocument
- CFPckgItem
- CFPckgAssociation
- CFDefinition
- CFConcept
- CFSubject
- CFItemType
- CFLicense
- CFAssociationGrouping
- CFRubric
- CFRubricCriterion
- CFRubricCriterionLevel
- CASE association values and target/version values

Committed platform projection:

- The generated framework graph dictionary now lives at `dictionary/case-core.v1.json`.
- `scripts/generate_case_core.py` emits SQL comments, OpenAPI schemas, Markdown docs, and portal HTML from that single source.
- The projection covers CASE packages, framework documents, framework items, associations, definition sets, concepts, subjects, item types, licenses, association groups, rubrics, rubric criteria, rubric criterion levels, and CASE API status records.
- The current projection is documentation/API-schema coverage only; live import, validation, tenant adoption, and search need a backend.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| CASE import API | Needs a persistent database and validation service. |
| Full framework graph execution | Planned after the OneRoster core slice. |
| CASE certification claim | Requires conformance testing and membership/certification process. |

## QTI 3

Accounted for in the QTI dictionary:

- QTI package
- Assessment item
- Assessment stimulus
- Assessment test
- Test part
- Assessment section
- Item reference
- Response/outcome/template/context declarations
- Response processing and outcome processing concepts
- Time limits and item session control
- Interaction families and interaction-specific values
- Feedback, rubrics, accessibility, companion materials, support tools, TTS, calculator, and cross-standard links

Committed platform projection:

- First-class rows for package, test, section, item, stimulus, item reference, interaction, declarations, scoring/rubric metadata, accessibility/support metadata, CASE alignment, and package artifact.
- Search/report fields for identifiers, title, language, interaction type, response cardinality, base type, scoring method, max score, time limits, adaptive/dependent flags, accessibility features, support tools, rubric/feedback presence, CASE target identifiers, and package lineage.
- The generated repository dictionary now lives at `dictionary/qti-core.v1.json` and emits SQL comments, OpenAPI schemas, and portal documentation.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| QTI delivery/runtime | Repository/search/import/export is separate from assessment delivery conformance. |
| Full XML decomposition | Too broad for the first platform slice; preserve original artifacts and project developer-useful fields first. |
| CAT runtime | Depends on mature QTI repository and assessment delivery services. |

## Caliper 1.2

Accounted for in the Caliper dictionary:

- Event envelope fields
- Base event fields
- Base entity fields
- 21 event types
- 71 entity types
- Profile matrix
- Action vocabulary
- Role/status values
- LTI message/session identifier values
- System identifier values
- Cross-standard joins

Committed platform projection:

- The generated event projection dictionary now lives at `dictionary/caliper-core.v1.json`.
- `scripts/generate_caliper_core.py` emits SQL comments, OpenAPI schemas, Markdown docs, and portal HTML from that single source.
- The projection covers Sensor API envelopes, immutable events, indexed entities, actors, group/session/LTI context, profile rules, governed extensions, event types, profiles, actions, entity types, roles, statuses, and identifier values.
- The current projection is documentation/API-schema coverage only; live ingestion, validation, retention, and analytics queries need a backend.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| Live event ingestion endpoint | Needs auth, tenant isolation, event validation, retention, and raw-event policy. |
| Profile-specific relational projections | Planned after core roster and auth boundaries. |
| Event warehouse/analytics dashboards | Requires retention and aggregation decisions. |

## LTI 1.3 and LTI Advantage

Accounted for in the integration dictionary:

- Platform, tool, registration, deployment
- Launch claims
- Resource link
- Launch presentation
- Custom parameters
- NRPS service, membership container, member fields
- AGS service, line item, score, result fields
- Deep Linking request/response/content item/media descriptor fields
- Message type, role, membership status, AGS progress, deep-link content/target, and scope values

Committed platform projection:

- The generated integration/governance dictionary now lives at `dictionary/integration-governance-core.v1.json`.
- `scripts/generate_integration_governance_core.py` emits SQL comments, OpenAPI schemas, Markdown docs, and portal HTML from that single source.
- The projection covers LTI registrations, deployments, launches, service endpoints, NRPS memberships, AGS grade exchanges, Deep Linking items, and required LTI values.
- The current projection is documentation/API-schema coverage only; launch validation and live LTI Advantage services need a backend.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| LTI launch validation | Requires hosted auth/OIDC, key management, nonce/state storage, and tenant deployment records. |
| AGS/NRPS/Deep Linking live services | Need auth and tenant data boundaries before public exposure. |
| Certification claim | Requires formal conformance tests. |

## Security Framework 1.1

Accounted for in the integration/governance dictionary:

- OAuth client registration
- OIDC login
- Token request/grant metadata
- JWK/JWKS fields
- Security scopes
- Service description documents
- Audit and access-policy concepts

Committed platform projection:

- The integration/governance source includes OAuth clients and scope policies for Security Framework accounting.
- Generated SQL/OpenAPI/docs connect scopes to API resources, actions, launch context requirements, roles, and privacy ceilings.
- The current projection is not a token server; production OAuth/OIDC behavior remains deferred until there is hosted backend infrastructure.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| Production OAuth/OIDC server | GitHub Pages cannot host server-side auth state or token issuance. |
| Secret/key storage | Requires managed backend or cloud secret manager. |
| Row-level authorization enforcement | Requires hosted Postgres or equivalent server-side database. |

## Data Privacy 1.0

Accounted for in platform metadata:

- Privacy classes
- Data sharing rules
- Consent records
- Retention rules
- Audit events
- Data categories
- Legal basis values
- Tenant policy and data minimization decisions

Committed platform projection:

- The integration/governance source includes privacy sharing rules, consent records, retention rules, and privacy audit events.
- Generated SQL/OpenAPI/docs connect privacy classes, data categories, legal basis, recipients, consent state, retention actions, and audit outcomes.
- The current projection is policy/accounting coverage only; live enforcement, deletion, export, and consent workflows need tenant-aware backend services.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| Live consent enforcement | Needs auth, tenant policy, and data-sharing agreement workflows. |
| Automated deletion/export workflows | Requires persistent backend and job execution. |
| Formal TrustEd Apps posture | Requires organizational review beyond code artifacts. |

## Rule Going Forward

No new public model object, field, enum value, API response field, SQL column, or relationship should be added unless it has a dictionary entry or an explicit unsupported/deferred entry with a reason.
