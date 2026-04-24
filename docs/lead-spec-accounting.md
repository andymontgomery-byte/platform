# Lead Spec Accounting

Research date: 2026-04-24

This page explains how every standard currently marked `Lead` is accounted for. "Accounted for" means the standard is either covered by a layperson dictionary entry, represented in the current runnable model, or explicitly deferred with a reason.

## Summary

| Lead area | Current status | Dictionary/accounting location |
| --- | --- | --- |
| OneRoster 1.2 | Runnable core slice plus broader layperson dictionary. | `dictionary/oneroster-core.v1.json`, generated OneRoster docs, OneRoster layperson dictionary. |
| CASE 1.1 | Researched and documented; not yet executable. | CASE layperson dictionary; overlap decisions for alignment. |
| QTI 3 | Researched and documented; repository model decisions tightened; not yet executable. | QTI layperson dictionary; QTI projection decision; overlap decisions for results, alignment, resources, time. |
| Caliper 1.2 | Researched and documented; event ingestion not yet executable. | Caliper layperson dictionary; overlap decisions for actor, membership, grade events, time. |
| LTI 1.3/LTI Advantage | Researched and documented; launch/API-context decision recorded; not yet executable. | Integration dictionary; overlap decisions for launch context, roles, membership, IDs, resources. |
| Security Framework 1.1 | Governance/accounting coverage; implementation deferred until auth layer exists. | Integration/governance dictionary; tenancy and privacy/security decisions. |
| Data Privacy 1.0 | Governance/accounting coverage; implementation deferred until tenant/auth layer exists. | Privacy classes, integration/governance dictionary, tenancy and privacy/security decisions. |

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
- 69 entity types
- Profile matrix
- Action vocabulary
- Role/status values
- LTI message/session identifier values
- System identifier values
- Cross-standard joins

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

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| Live consent enforcement | Needs auth, tenant policy, and data-sharing agreement workflows. |
| Automated deletion/export workflows | Requires persistent backend and job execution. |
| Formal TrustEd Apps posture | Requires organizational review beyond code artifacts. |

## Rule Going Forward

No new public model object, field, enum value, API response field, SQL column, or relationship should be added unless it has a dictionary entry or an explicit unsupported/deferred entry with a reason.
