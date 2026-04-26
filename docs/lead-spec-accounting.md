# Lead Spec Accounting

Research date: 2026-04-24

This page explains how every standard currently marked `Lead` is accounted for. "Accounted for" means every exposed object, field, and controlled value has a dictionary `sourceStandard` reference, and every intentionally unsupported or deferred object/field/value is listed in a structured ledger with a business, scope, or downstream-impact reason.

## SourceStandard Control

`scripts/check_dictionary_artifacts.py` now fails unless every generated dictionary object, field, and controlled vocabulary value carries `sourceStandard`, and every unsupported/deferred ledger row carries `sourceStandard` plus a non-empty `sourceFieldsOrValues` list. The generators emit the same field and value accounting into OpenAPI (`x-sourceStandard`, `x-valueSourceStandards`) and generated Markdown/HTML dictionary pages.

| Accounting evidence | Location |
| --- | --- |
| OneRoster supported fields and unsupported full-1.2 ledger | `dictionary/oneroster-core.v1.json` |
| QTI repository fields, interaction values, and preserved/deferred XML/runtime ledger | `dictionary/qti-core.v1.json` |
| CASE framework graph fields and deferred live/certification ledger | `dictionary/case-core.v1.json` |
| Caliper event/profile/action/entity values and deferred full Sensor API ledger | `dictionary/caliper-core.v1.json` |
| LTI, Security Framework, and Data Privacy fields plus deferred production workflow ledger | `dictionary/integration-governance-core.v1.json` |

## Decision Citation Map

Each Lead-spec accounting entry below is a projection of the decision register, not a standalone coverage claim.

| Lead area | decision_id | What the decision fixes for this accounting entry |
| --- | --- | --- |
| OneRoster 1.2 runtime/core accounting | `DEC-010-tenancy-reference-data` | Tenant-owned roster and gradebook records are isolated by RLS; shared reference data is separate. |
| OneRoster 1.2 score/result accounting | `DEC-005-results-scores` | Gradebook line items and results use a stable result contract while richer score-scale/profile fields stay deferred. |
| CASE 1.1 accounting | `DEC-006-standards-alignment` | Standards frameworks and alignments are modeled as governed graph/reference data; the teaching-app runtime stores a known CASE target URI on gradebook line items. |
| QTI 3 accounting | `DEC-009-content-resource` | QTI packages and items remain content/resource artifacts until runtime delivery is implemented. |
| Caliper 1.2 accounting | `DEC-012-runtime-coverage-per-spec` | Caliper is partial runtime through the authenticated receipt path and the build-guide `caliper_events`/`class_activity_feed` projection. |
| LTI 1.3/LTI Advantage accounting | `DEC-012-runtime-coverage-per-spec` | LTI is partial runtime only through the authenticated launch receipt path. |
| Security Framework 1.1 accounting | `DEC-015-service-role-policy` | Request-scoped runtime code must use caller JWTs, with service-role use limited to admin/test operations. |
| Data Privacy 1.0 accounting | `DEC-011-privacy-surfaces` | Privacy classes determine which fields may appear on docs, static mirrors, live REST, and audited Edge Functions. |

## Explicit Unsupported Field/Value Ledger

The tables below make the structured `unsupported_or_deferred[].sourceFieldsOrValues` ledgers visible without relying on large JSON files. Supported items are exhaustive through `sourceStandard` on every dictionary object, field, and controlled vocabulary value; unsupported items are exhaustive through these field/value lists plus the reasons in the same row.

### OneRoster 1.2 Unsupported or Deferred Items

| Area | Source fields or values | Reason |
| --- | --- | --- |
| OneRoster Demographics object fields | `Demographics.birthDate`, `Demographics.sex`, `Demographics.americanIndianOrAlaskaNative`, `Demographics.asian`, `Demographics.blackOrAfricanAmerican`, `Demographics.nativeHawaiianOrOtherPacificIslander`, `Demographics.white`, `Demographics.demographicRaceTwoOrMoreRaces`, `Demographics.hispanicOrLatinoEthnicity`, `Demographics.countryOfBirthCode`, `Demographics.stateOfBirthAbbreviation`, `Demographics.cityOfBirth`, `Demographics.publicSchoolResidenceStatus`, `sex value female`, `sex value male`, `sex value other`, `sex value unspecified` | Highly sensitive demographic fields are not needed for the current roster/gradebook slice and should only be exposed after tenant policy, purpose limitation, and audited access rules are implemented for that data category. |
| OneRoster User agent, profile, credential, password, and contact fields | `User.userMasterIdentifier`, `User.username`, `User.userIds`, `User.middleName`, `User.preferredFirstName`, `User.preferredMiddleName`, `User.preferredLastName`, `User.pronouns`, `User.roles`, `User.userProfiles`, `User.primaryOrg`, `User.identifier`, `User.sms`, `User.phone`, `User.agents`, `User.grades`, `User.password`, `User.resources`, `UserProfile.profileId`, `UserProfile.profileType`, `UserProfile.vendorId`, `UserProfile.applicationId`, `UserProfile.description`, `UserProfile.credentials`, `Credential.type`, `Credential.username`, `Credential.password`, `Credential.extensions`, `Role.roleType`, `Role.role`, `Role.org`, `Role.userProfile`, `Role.beginDate`, `Role.endDate` | The runnable model exposes directory-safe user identity and one primary role first. Relationship, profile, credential, password, phone, pronoun, and organization-role details have higher privacy and integration impact, so they need a dedicated identity/account slice with field-level authorization before exposure. |
| OneRoster Resource object and resource references | `Resource.title`, `Resource.roles`, `Resource.importance`, `Resource.vendorResourceId`, `Resource.vendorId`, `Resource.applicationId`, `Course.resources`, `Class.resources`, `User.resources`, `importance value primary`, `importance value secondary`, `resource role value administrator`, `resource role value aide`, `resource role value guardian`, `resource role value parent`, `resource role value proctor`, `resource role value relative`, `resource role value student`, `resource role value teacher` | Resource records overlap with QTI packages, Common Cartridge content, LTI links, and content licensing. They are deferred until the content/resource slice can preserve package lineage and avoid treating resource metadata as the actual content asset. |
| OneRoster ScoreScale, Assessment Results Profile, and learning-objective result fields | `ScoreScale.title`, `ScoreScale.type`, `ScoreScale.course`, `ScoreScale.class`, `ScoreScale.scoreScaleValue`, `ScoreScaleValue.itemValueLHS`, `ScoreScaleValue.itemValueRHS`, `LineItem.scoreScale`, `LineItem.learningObjectiveSet`, `Result.class`, `Result.scoreScale`, `Result.textScore`, `Result.learningObjectiveSet`, `Result.inProgress`, `Result.incomplete`, `Result.late`, `Result.missing`, `AssessmentLineItem.title`, `AssessmentLineItem.description`, `AssessmentLineItem.class`, `AssessmentLineItem.parentAssessmentLineItem`, `AssessmentLineItem.scoreScale`, `AssessmentLineItem.resultValueMin`, `AssessmentLineItem.resultValueMax`, `AssessmentLineItem.learningObjectiveSet`, `AssessmentResult.assessmentLineItem`, `AssessmentResult.student`, `AssessmentResult.score`, `AssessmentResult.textScore`, `AssessmentResult.scoreDate`, `AssessmentResult.scoreScale`, `AssessmentResult.scorePercentile`, `AssessmentResult.scoreStatus`, `AssessmentResult.comment`, `AssessmentResult.learningObjectiveSet`, `AssessmentResult.inProgress`, `AssessmentResult.incomplete`, `AssessmentResult.late`, `AssessmentResult.missing`, `LearningObjectiveSet.source`, `LearningObjectiveSet.learningObjectiveIds`, `LearningObjectiveResult.learningObjectiveId`, `LearningObjectiveResult.score`, `LearningObjectiveResult.textScore` | The current gradebook slice supports line items and numeric results. Score-scale mapping, assessment-result profile records, and per-standard mastery scores depend on QTI/CASE alignment and assessment runtime choices, so exposing them now would create unstable contracts. |
| OneRoster extended object fields, references, and organization values outside the core slice | `common metadata`, `reference.href`, `reference.type`, `AcademicSession.parent`, `AcademicSession.children`, `Org.identifier`, `Org.children`, `Org type value local`, `Org type value national`, `Org type value state`, `Course.grades`, `Course.subjects`, `Course.subjectCodes`, `Class.location`, `Class.grades`, `Class.subjects`, `Class.subjectCodes`, `Class.periods`, `API status imsx_codeMajor`, `API status imsx_severity`, `API status imsx_description`, `API status imsx_CodeMinor`, `API status imsx_codeMinorFieldName`, `API status imsx_codeMinorFieldValue` | The core runnable model keeps the fields needed for roster membership, gradebook joins, tenant isolation, and hosted smoke tests. Extra metadata, references, org-level values, subjects, grade arrays, periods, and API status payloads are deferred until full REST/CSV provider behavior and filtering/error semantics are implemented. |
| Full OneRoster REST provider/consumer and CSV bulk-exchange binding behavior | `pagination`, `filtering`, `sorting`, `field selection`, `bulk CSV import/export`, `provider certification fixtures`, `consumer certification fixtures`, `delete/write endpoints` | The hosted demo is intentionally read-mostly and tenant-scoped. Full binding behavior requires production auth, pagination/filter semantics, write policy, certification fixtures, and operational import/export jobs beyond the current vertical slice. |

### QTI 3 Unsupported or Deferred Items

| Area | Source fields or values | Reason |
| --- | --- | --- |
| QTI assessment delivery/runtime behavior | `session state`, `candidate responses`, `attempt lifecycle`, `delivery navigation`, `runtime scoring` | The platform is first modeling repository, import, search, alignment, and governance. Delivery requires a tested QTI runtime engine before learner session behavior should become a platform contract. |
| QTI low-level XML and item-body child nodes not promoted to SQL/API fields | `HTML/ARIA/MathML children`, `qti-content-body children`, `object/img/picture media children`, `data-* extensions`, `package-local XML order and namespaces` | The original QTI XML and package files remain the legal source artifact. Only public platform fields useful for search, governance, alignment, accessibility review, and delivery planning are projected into relational/API fields. |
| QTI interaction-specific child fields below the normalized interaction index | `SimpleChoice.identifier`, `SimpleChoice.fixed`, `SimpleChoice.templateIdentifier`, `SimpleChoice.showHide`, `GapChoice`, `InlineChoice`, `HotspotChoice.coords`, `AssociableHotspot.matchMax`, `PositionObjectStage`, `SliderInteraction.lowerBound`, `SliderInteraction.upperBound`, `SliderInteraction.step`, `UploadInteraction.type`, `MediaInteraction.autostart`, `MediaInteraction.minPlays`, `MediaInteraction.maxPlays`, `EndAttemptInteraction.countAttempt`, `PortableCustomInteraction.module`, `PortableCustomInteraction.customInteractionTypeIdentifier`, `CustomInteraction.extension` | The dictionary accounts for every interaction family as controlled values and projects common interaction planning fields. Interaction-specific rendering and response mechanics stay in preserved QTI XML until a delivery/runtime service can validate and execute them. |
| QTI response-processing execution and rule tree decomposition | `responseRuleGroup`, `outcomeRule`, `templateRule`, `branchRule logic tree`, `preCondition logic tree`, `lookupTable execution` | Processing logic is preserved and summarized for search and review. Executing it safely belongs to a QTI runtime service with conformance fixtures. |
| QTI computer-adaptive testing and vendor extension semantics | `CAT runtime configuration`, `adaptive item/session algorithms`, `vendor extension semantics` | CAT and vendor-specific behavior depend on mature item metadata, delivery services, psychometric configuration, and reviewed extension contracts beyond this repository dictionary. |

### CASE 1.1 Unsupported or Deferred Items

| Area | Source fields or values | Reason |
| --- | --- | --- |
| Formal CASE certification claim | `official certification test evidence`, `member certification workflow` | Requires official conformance testing and certification process beyond generated dictionary artifacts. |
| Live CASE import/search API beyond assignment URI alignment | `package upload`, `validation service`, `tenant adoption records`, `search indexing` | The teaching-app slice can attach a known CASE URI to a gradebook line item. Full framework import/search still needs validation, indexing, and tenant/shared-reference policy before public workflows are useful. |
| Publisher extension semantics | `publisher extension fields`, `custom payload semantics` | Extensions are preserved as governed metadata, but not promoted to core fields until intentionally modeled. |
| Full graph diff/merge workflow | `version diff`, `framework merge`, `tenant override reconciliation` | Version comparison and merge tooling should be implemented after persistent backend storage exists. |

### Caliper 1.2 Unsupported or Deferred Items

| Area | Source fields or values | Reason |
| --- | --- | --- |
| Full Sensor API validation, immutable storage, and replay/idempotency handling | `profile validation`, `immutable raw-event store`, `rate limits`, `retention policy`, `idempotency/replay controls` | A minimal authenticated receipt Edge Function and build-guide event table/view exist. Full Sensor API conformance still needs profile validation, replay handling, retention policy, and operational controls. |
| Full profile-specific relational decomposition | `profile-specific metric fields`, `profile-specific object extensions`, `profile-specific generated/target fields` | The first generated slice indexes core event/entity fields and preserves raw JSON-LD while profile-specific projections are added incrementally based on product value. |
| Analytics warehouse and dashboards | `warehouse fact tables`, `aggregations`, `de-identification jobs`, `dashboards` | Requires retention, aggregation, access control, and de-identification decisions beyond the event receipt path. |
| Formal Caliper certification claim | `official certification fixtures`, `profile conformance reports` | Requires conformance testing and organizational certification work beyond these generated dictionary artifacts. |

### LTI/Security/Data Privacy Unsupported or Deferred Items

| Area | Source fields or values | Reason |
| --- | --- | --- |
| Full LTI OIDC/JWT launch validation | `nonce storage`, `state storage`, `JWKS validation`, `deployment lookup`, `id_token signature validation` | A minimal authenticated launch receipt path exists. Production launch validation requires key management, nonce/state storage, deployment records, signature validation, and certification fixtures. |
| Public AGS, NRPS, and Deep Linking runtime services | `AGS line items`, `AGS scores`, `AGS results`, `NRPS memberships`, `Deep Linking responses` | Need production token issuance, tenant row-level authorization, gradebook write policy, and service-specific conformance tests before public exposure. |
| Production OAuth/OIDC server | `client assertion validation`, `token issuance`, `secret/key rotation`, `introspection/revocation` | A minimal authenticated token-exchange receipt path exists. Production token issuance requires server-side auth state, client assertion validation, and managed secret/key storage. |
| Automated privacy enforcement workflows | `consent enforcement`, `retention jobs`, `deletion workflow`, `export workflow`, `data-sharing agreement approvals` | The dictionary and audit slices model policy and sensitive-read audit rows. Automated consent checks, retention jobs, deletion, export, and data-sharing agreements need broader backend workflow services. |
| Formal certification claims | `LTI certification fixtures`, `Security Framework certification fixtures`, `Data Privacy organizational review` | LTI, Security Framework, and Data Privacy certification require conformance testing and organizational review beyond generated dictionary artifacts. |

## Summary

| Lead area | Current status | Dictionary/accounting location |
| --- | --- | --- |
| OneRoster 1.2 | Runnable core slice plus full sourceStandard/unsupported ledger for the remaining 1.2 objects, fields, and values. | `dictionary/oneroster-core.v1.json`, generated OneRoster docs, OneRoster layperson dictionary. |
| CASE 1.1 | Structured/generated framework graph projection plus runtime assignment-to-CASE URI alignment; full import/search is not yet executable. | `dictionary/case-core.v1.json`, generated CASE docs/OpenAPI/SQL comments, CASE layperson dictionary, `dictionary/oneroster-core.v1.json#line_item.case_target_uri`, overlap decisions for alignment. |
| QTI 3 | Structured/generated repository projection exists; not yet executable. | `dictionary/qti-core.v1.json`, generated QTI docs/OpenAPI/SQL comments, QTI layperson dictionary, QTI projection decision, overlap decisions for results, alignment, resources, time. |
| Caliper 1.2 | Structured/generated event projection plus a minimal authenticated ingestion receipt path and build-guide event/feed runtime projection. | `dictionary/caliper-core.v1.json`, generated Caliper docs/OpenAPI/SQL comments, Caliper layperson dictionary, overlap decisions for actor, membership, grade events, time, `supabase/functions/caliper-event-ingestion`, `supabase/migrations/0001_oneroster_core_demo.sql#caliper_events`. |
| LTI 1.3/LTI Advantage | Structured/generated integration projection plus a minimal authenticated launch handler. | `dictionary/integration-governance-core.v1.json`, generated integration/governance docs/OpenAPI/SQL comments, integration layperson dictionary, overlap decisions for launch context, roles, membership, IDs, resources, `supabase/functions/lti-launch-handler`. |
| Security Framework 1.1 | Structured/generated OAuth and scope-policy projection plus a minimal authenticated token-exchange receipt path. | `dictionary/integration-governance-core.v1.json`, generated integration/governance docs/OpenAPI/SQL comments, tenancy and privacy/security decisions, `supabase/functions/oauth-token-exchange`. |
| Data Privacy 1.0 | Structured/generated policy projection exists; audited sensitive reads are live for the OneRoster slice, while consent/deletion/export jobs are explicitly deferred. | `dictionary/integration-governance-core.v1.json`, privacy classes, generated integration/governance docs/OpenAPI/SQL comments, tenancy and privacy/security decisions. |

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

Accounted for in the structured unsupported/deferred ledger:

- Demographics fields and sex/race/ethnicity values
- Agent, user profile, credential, password, contact, role-detail, and relationship fields
- Resource objects, resource references, resource role values, and resource importance values
- ScoreScale, ScoreScaleValue, Assessment Results Profile, and learning-objective result fields
- Extended organization/reference/status fields and organization values outside the core slice
- Full REST provider/consumer and CSV bulk-exchange behavior

Deferred or not supported in the runnable slice:

| Area | Ledger detail | Reason |
| --- | --- | --- |
| Write APIs and full REST/CSV binding behavior | `dictionary/oneroster-core.v1.json` lists pagination, filtering, sorting, field selection, bulk CSV import/export, provider/consumer certification fixtures, and delete/write endpoints. | The hosted demo is tenant-scoped and read-mostly; full binding behavior needs production auth, write policy, certification fixtures, and operational jobs. |
| Demographics execution | `dictionary/oneroster-core.v1.json` lists each demographics field plus sex/race/ethnicity values. | These highly sensitive fields are not needed for the roster/gradebook slice and require purpose-limited, audited access rules before exposure. |
| Agents, profiles, credentials, and contact details | `dictionary/oneroster-core.v1.json` lists each user/profile/credential/role/contact field. | These fields need a dedicated identity/account slice with field-level authorization because they have higher privacy and integration impact. |
| Resources, score scales, and Assessment Results Profile | `dictionary/oneroster-core.v1.json` lists each resource, score-scale, assessment-result, and learning-objective field/value. | These overlap QTI, CASE, content packages, and assessment runtime behavior; exposing them now would create unstable contracts. |

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
- The current framework graph projection is generated dictionary/API-schema coverage. The runtime teaching-app slice stores a known CASE URI on `line_items.case_target_uri`; full live import, validation, tenant adoption, and search need a broader backend.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| CASE import/search API beyond assignment URI alignment | Needs validation, framework storage/search, and tenant adoption policy beyond the line-item CASE URI used by the teaching-app guide. |
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
| QTI delivery/runtime | Repository/search/import/export is separate from assessment delivery conformance; the ledger lists session state, candidate responses, attempt lifecycle, navigation, and runtime scoring as deferred. |
| Full XML decomposition | The original XML is preserved as the source artifact; the ledger lists low-level XML/content-body children and package-local details as preserved rather than promoted to SQL fields. |
| Interaction-specific child fields | All interaction families are controlled values with `sourceStandard`; per-interaction child mechanics such as choice children, hotspot coordinates, upload MIME details, media play limits, PCI modules, and custom extensions remain in preserved XML until a runtime exists. |
| CAT/runtime extensions | Depends on mature QTI repository, assessment delivery services, psychometric configuration, and reviewed extension contracts. |

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
- `supabase/functions/caliper-event-ingestion` accepts authenticated Caliper envelopes, forwards the caller's JWT to Supabase, and writes tenant-scoped database receipts.
- `supabase/migrations/0001_oneroster_core_demo.sql` creates `caliper_events` and `class_activity_feed` so the teaching-app guide can write and read a grade event through the platform runtime. Full Sensor API validation, replay, retention, and warehouse analytics need a broader backend slice.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| Full Sensor API conformance | Needs profile validation, retention policy, and replay/idempotency handling beyond the receipt path and build-guide event table. |
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
- `supabase/functions/lti-launch-handler` accepts an authenticated launch payload, forwards the caller's JWT to Supabase, resolves the LTI context through tenant-scoped `source_identifiers`, and writes a database receipt. Full OIDC/JWT launch validation and live LTI Advantage services need a broader backend.

Deferred or not supported yet:

| Area | Reason |
| --- | --- |
| Full LTI OIDC/JWT launch validation | Requires key management, nonce/state storage, deployment records, signature validation, and certification fixtures beyond the receipt path. |
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
- `supabase/functions/oauth-token-exchange` accepts an authenticated token-exchange request, forwards the caller's JWT to Supabase, and writes a tenant-scoped database receipt. Production OAuth/OIDC token issuance remains deferred until there is broader hosted auth infrastructure.

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
