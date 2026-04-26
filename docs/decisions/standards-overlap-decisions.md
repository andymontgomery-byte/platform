# Standards Overlap Decisions

Research date: 2026-04-24

This record captures places where 1EdTech standards, platform runtime choices, or privacy/security surfaces would otherwise force the codebase to make silent choices. Each decision is written in the rubric-required shape: `id`, `question`, `options_considered`, `choice`, `consequences`, and `projects_to`.

## DEC-001 Person, User, Actor, Profile, and Subject

- id: `DEC-001-person-agent-subject`
- question: When standards describe people, actors, profiles, and subjects differently, what is the platform's identity model?
- options_considered:
  - Treat every standard-specific identity as a separate table and let callers reconcile them.
  - Collapse every user, actor, profile, and credential subject into one `person`.
  - Keep a canonical `person` for known school people and a broader `agent` concept for non-person or externally controlled identities.
- choice: The platform has a canonical `person` for known school people and a broader `agent` concept for non-person actors. Credential subjects and Caliper actors resolve to `person` only when policy and identifiers allow it; otherwise they remain linked external agents.
- consequences:
  - Removes the need for every roster, launch, analytics, and credential API to invent its own identity merge rules.
  - Removes per-function subject-to-person merge branches from `supabase/functions/lti-launch-handler/index.ts`, `supabase/functions/caliper-event-ingestion/index.ts`, and future credential importers; those paths read `people` plus source lineage instead of performing their own merge.
  - Eliminates automatic merging of credential subjects or analytics actors into school records when confidence or policy is missing.
  - Why not collapse: forcing every actor, tool client, issuer, sensor, and low-confidence credential subject into `public.people` would delete the `agent` distinction but create false roster people and expand tenant RLS/audit obligations for identities the school does not own.
  - Creates the constraint that APIs must expose identity confidence and source lineage when an actor is not certainly a known person.
- projects_to:
  - `data/data-dictionary.seed.json#canonical.identity.person`
  - `dictionary/oneroster-core.v1.json#person.display_name`
  - `dictionary/oneroster-core.v1.json#person.email`
  - `dictionary/caliper-core.v1.json#caliper_actor.email`
  - `dictionary/caliper-core.v1.json#caliper_actor.identifier_value`
  - `dictionary/qti-core.v1.json#qti_candidate.email`
  - `dictionary/integration-governance-core.v1.json#lti_launch.subject_id`
  - `supabase/migrations/0001_oneroster_core_demo.sql#people`
  - `site/api/people.json`

## DEC-002 Class, Course, Context, Group, Course Section, and Organization

- id: `DEC-002-learning-context`
- question: How should the platform distinguish course templates, scheduled classes, launch contexts, groups, and content organizations?
- options_considered:
  - Model everything named "course", "class", "group", or "context" as one generic context.
  - Preserve only the source-specific structures and make cross-standard joins caller-owned.
  - Separate catalog `course`, scheduled `class`, and broader `learning_context` while preserving source IDs.
- choice: The platform separates `course` from `class`. `course` is the catalog/template. `class` is the scheduled teaching section. LTI contexts and Caliper groups can map to a class, course, or other learning context. Common Cartridge organizations are content outlines, not school organizations or scheduled classes.
- consequences:
  - Removes the need for app code to guess whether a launch context is a course template, section, or content outline.
  - Removes a generic `contexts` table plus subtype switch logic from `public.class_roster`, `public.gradebook_results`, and `demo/server.js`; scheduled-section queries join through `classes.course_id` and `classes.term_id` instead.
  - Lets class roster, gradebook, and launch surfaces derive joins from the same course/class/context model.
  - Why not collapse: a single `learning_contexts` table with `context_type` and JSON source payload is a credible LMS design, but here it would move course/class distinction out of foreign keys and into runtime branches in every roster, gradebook, launch, and Caliper query.
  - Creates the constraint that importers must preserve source-specific context IDs and cannot assume every context is a class.
- projects_to:
  - `dictionary/oneroster-core.v1.json#course.title`
  - `dictionary/oneroster-core.v1.json#class.course_id`
  - `dictionary/oneroster-core.v1.json#academic_session.session_type`
  - `dictionary/integration-governance-core.v1.json#lti_launch.context_id`
  - `dictionary/caliper-core.v1.json#caliper_context.lti_context_id`
  - `supabase/migrations/0001_oneroster_core_demo.sql#classes`
  - `site/api/classes.json`

## DEC-003 Roles

- id: `DEC-003-role-vocabulary`
- question: How should the platform reconcile OneRoster roles, LTI role URIs, Caliper role evidence, and credential profile relationships?
- options_considered:
  - Use OneRoster role names everywhere.
  - Use LTI URI roles everywhere.
  - Store exact source roles and map them to a small platform role family for authorization and UI.
- choice: Store source roles exactly, then map them to platform role families: `learner`, `educator`, `administrator`, `guardian`, `mentor`, `staff`, `tool`, `issuer`, and `unknown`.
- consequences:
  - Removes the need for each authorization check to parse every standard's role vocabulary.
  - Removes separate OneRoster role-name, LTI URI-role, and Caliper actor-role parsers from `supabase/functions/lti-launch-handler/index.ts`, `supabase/functions/oauth-token-exchange/index.ts`, and scope policy generation; those paths consume a shared role-family mapping.
  - Makes role-family policy reusable across roster, launch, gradebook, and analytics surfaces.
  - Why not collapse: publishing only platform role families would simplify authorization, but it would erase spec-native role values required for OneRoster/LTI conformance, troubleshooting, and lossless export.
  - Creates the constraint that source role values must be preserved for conformance, debugging, and lossless export.
- projects_to:
  - `dictionary/oneroster-core.v1.json#person.primary_role`
  - `dictionary/oneroster-core.v1.json#enrollment.role`
  - `dictionary/integration-governance-core.v1.json#lti_launch.roles`
  - `dictionary/integration-governance-core.v1.json#lti_membership.roles`
  - `supabase/migrations/0001_oneroster_core_demo.sql#people.primary_role`
  - `supabase/migrations/0001_oneroster_core_demo.sql#enrollments.role`

## DEC-004 Enrollment and Membership

- id: `DEC-004-enrollment-membership`
- question: What is canonical roster participation when standards also expose launch/service memberships and event-time memberships?
- options_considered:
  - Treat every membership record as an enrollment.
  - Treat enrollment as just one membership source.
  - Keep `enrollment` as canonical roster participation and `membership` as contextual service or event evidence.
- choice: `enrollment` is the canonical roster participation record. `membership` is a contextual service/event view that may be derived from enrollment or captured from an external system.
- consequences:
  - Removes the need for gradebook and roster APIs to choose among launch-time and event-time snapshots as the source of truth.
  - Removes peer `lti_memberships` or `caliper_memberships` truth tables from the gradebook join path; `public.enrollments`, `public.class_roster`, and `site/api/views/class-roster.json` stay the canonical participation artifacts.
  - Lets LTI NRPS and Caliper membership projections be labeled as derived or observed instead of overwriting roster truth.
  - Why not collapse: treating every observed membership as enrollment would make imports simpler, but launch-time or event-time service membership can be transient and would corrupt school roster truth if written directly into `public.enrollments`.
  - Creates the constraint that membership APIs must say whether they return canonical roster state or observed service state.
- projects_to:
  - `dictionary/oneroster-core.v1.json#enrollment.person_id`
  - `dictionary/oneroster-core.v1.json#enrollment.class_id`
  - `dictionary/integration-governance-core.v1.json#lti_membership.context_id`
  - `dictionary/integration-governance-core.v1.json#lti_membership.platform_person_id`
  - `supabase/migrations/0001_oneroster_core_demo.sql#enrollments`
  - `site/api/enrollments.json`

## DEC-005 Results, Scores, Outcomes, and Grade Events

- id: `DEC-005-results-scores`
- question: How should the platform separate gradebook state, score update commands, assessment outcome variables, and grading activity events?
- options_considered:
  - Use LTI AGS line items and results as the only canonical gradebook model, projecting OneRoster results, QTI outcomes, and Caliper grade events into AGS-shaped records.
  - Keep OneRoster Results, LTI AGS Scores/Results, QTI outcomes, and Caliper GradeEvents as peer source-native stores joined only by source identifiers.
  - Keep `result` as current gradebook state and model AGS scores, QTI outcomes, and Caliper grade events as inputs or history.
- choice: The platform uses `line_item` as the gradebook target and `result` as the learner's current gradebook state. LTI AGS Score is an incoming write/update message. LTI AGS Result and OneRoster Result map to current result state. QTI outcomes are assessment-runtime variables projected into results only when a delivery or scoring workflow declares that mapping. Caliper GradeEvent is event history, not the gradebook source of truth.
- consequences:
  - Removes the need for dashboards to reconstruct current grades from raw event streams.
  - Removes current-grade reconstruction over `caliper_event` receipts, AGS Score command payloads, and QTI outcome variables; dashboards and demos read `public.results`, `public.gradebook_results`, and `site/api/views/gradebook-results.json`.
  - Makes event provenance and assessment scoring history available without letting those histories overwrite current gradebook state by accident.
  - Why not collapse: using AGS or Caliper as the only gradebook model would simplify one importer, but it would force OneRoster result reads and classroom dashboards to replay command/event history whenever they need the learner's current score.
  - Creates the constraint that imports must record whether a value is current state, a command, an assessment variable, or event history.
- projects_to:
  - `dictionary/oneroster-core.v1.json#line_item.id`
  - `dictionary/oneroster-core.v1.json#result.score`
  - `dictionary/integration-governance-core.v1.json#lti_grade_exchange.score_given`
  - `dictionary/qti-core.v1.json#qti_variable_declaration.identifier`
  - `dictionary/caliper-core.v1.json#caliper_event.action`
  - `supabase/functions/gradebook-bulk-submit/index.ts`
  - `site/api/views/gradebook-results.json`

## DEC-006 Standards Alignment

- id: `DEC-006-standards-alignment`
- question: Which standards graph should anchor alignment across content, assessment, credentials, and results?
- options_considered:
  - Let each artifact store only its own alignment strings.
  - Normalize all alignment into a platform-only taxonomy.
  - Use CASE as the canonical standards graph while preserving source alignment labels and URLs.
- choice: CASE is the canonical standards graph. Other standards store alignment as source metadata and resolve known targets to CASE item identifiers or URIs.
- consequences:
  - Removes the need for each reporting workflow to reconcile QTI, cartridge, badge, and CLR alignment formats separately.
  - Removes per-standard alignment bridge tables from reports; generated CASE artifacts (`dictionary/case-core.v1.json#case_item`, `dictionary/case-core.v1.json#case_association`) and QTI alignment fields carry the shared target when it is known.
  - Lets cross-product reporting and AI reasoning use one standards graph where a CASE target is known.
  - Why not collapse: replacing CASE with a platform-only taxonomy would simplify internal labels, but it would break interoperability with state frameworks and partner payloads that already reference CASE URIs.
  - Creates the constraint that importers must keep original alignment labels and URLs when they cannot be resolved.
- projects_to:
  - `dictionary/case-core.v1.json#case_item.identifier`
  - `dictionary/case-core.v1.json#case_association.origin_node_uri`
  - `dictionary/qti-core.v1.json#qti_alignment.target_identifier`
  - `dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.data_category`
  - `docs/generated/case-core-dictionary.md`
  - `site/docs/case-core-dictionary.html`

## DEC-007 Identifiers

- id: `DEC-007-identifier-crosswalk`
- question: How should the platform preserve standard-native identifiers while keeping stable internal joins?
- options_considered:
  - Use one platform UUID as the only public identifier.
  - Use each standard's ID as the physical database key.
  - Store internal platform IDs plus source identifier crosswalks and expose standard-native IDs where the standard requires them.
- choice: Internal records have platform IDs. Standard-shaped endpoints expose the standard-native ID as the primary contract when required. Every external ID is stored in a source identifier crosswalk with source system, identifier type, and object relationship.
- consequences:
  - Removes the need to choose between conformance IDs and durable internal join IDs.
  - Removes duplicate source-ID columns from every public table; `public.source_identifiers` owns `object_type`, `object_id`, `source_system`, `identifier_type`, and `external_id` instead of each table growing its own SIS/LTI/email columns.
  - Eliminates one-off per-table ID reconciliation logic by making source identifiers a shared crosswalk pattern.
  - Why not collapse: using source-native IDs as physical database keys would make one export path shorter, but it would couple internal joins to mutable vendor identifiers and make multi-source identity repair a table-by-table migration.
  - Creates the constraint that every source ID must carry source system, identifier type, and object relationship.
- projects_to:
  - `dictionary/oneroster-core.v1.json#source_identifier.external_id`
  - `dictionary/oneroster-core.v1.json#person.sourced_id`
  - `dictionary/case-core.v1.json#case_document.uri`
  - `dictionary/integration-governance-core.v1.json#lti_deployment.deployment_id`
  - `dictionary/caliper-core.v1.json#caliper_event.event_iri`
  - `supabase/migrations/0001_oneroster_core_demo.sql#source_identifiers`

## DEC-008 Time, School Sessions, and Event Timestamps

- id: `DEC-008-time-session`
- question: How should the platform distinguish school calendar periods, event timestamps, availability windows, assessment timing, and credential validity?
- options_considered:
  - Store every time-like value as a generic timestamp.
  - Use OneRoster AcademicSession as the only time model.
  - Separate calendar periods, event timestamps, availability windows, assessment timing, and validity periods.
- choice: Separate calendar periods, event timestamps, availability windows, and validity periods. Store timestamps in UTC with source timezone/offset when provided. Store OneRoster AcademicSession as the school calendar backbone.
- consequences:
  - Removes the need for developers to infer whether a date is a term, due date, event time, time limit, or credential expiry.
  - Removes generic timestamp metadata parsing from roster, gradebook, Caliper, QTI, and credential projections; `academic_sessions`, `line_items`, `caliper_event.event_time`, QTI timing fields, and validity fields each own their time semantics.
  - Lets school-year queries use AcademicSession without losing event and validity semantics.
  - Why not collapse: storing all time-like values as timestamps would reduce field count, but school-year filters, assessment timing, event ordering, and credential validity would all need side tables or fragile naming conventions to recover meaning.
  - Creates the constraint that timestamp imports must retain source timezone or offset when provided.
- projects_to:
  - `dictionary/oneroster-core.v1.json#academic_session.start_date`
  - `dictionary/oneroster-core.v1.json#academic_session.end_date`
  - `dictionary/oneroster-core.v1.json#person.date_last_modified`
  - `dictionary/caliper-core.v1.json#caliper_event.event_time`
  - `dictionary/qti-core.v1.json#qti_assessment_test.time_limit_seconds`
  - `supabase/migrations/0001_oneroster_core_demo.sql#academic_sessions`

## DEC-009 Content, Resources, Packages, and Launch Links

- id: `DEC-009-content-resource`
- question: What is the shared model for roster resources, content packages, QTI artifacts, LTI links, and Caliper digital resources?
- options_considered:
  - Use QTI package, item, and test structures as the canonical content model, projecting cartridge resources, LTI links, and Caliper digital entities into QTI-shaped records where possible.
  - Keep cartridge resources, QTI artifacts, LTI deep-link items, and Caliper entities as separate source-native catalogs joined only by URLs or source identifiers.
  - Use a broad `resource` concept with subtype-specific records for package, assessment, launch, and event details.
- choice: The platform uses a broad `resource` concept for discoverable learning objects, with subtype-specific records for cartridge resources, QTI packages/items/tests, LTI resource links, and Caliper event entities.
- consequences:
  - Removes the need for search and catalog workflows to query separate content models for every standard.
  - Removes separate discovery indexes for QTI packages, LTI deep links, cartridge resources, and Caliper digital entities; generated docs keep subtype fields while a broad `resource` layer carries search-facing identity.
  - Lets standards-specific package, launch, assessment, and event details remain intact under a shared discovery layer.
  - Why not collapse: making QTI the canonical content catalog is credible for an assessment-first platform, but it would turn LTI links, cartridge resources, and Caliper digital entities into fake QTI artifacts and force non-assessment payloads through assessment-only identifiers.
  - Creates the constraint that subtype-specific details must remain in their standard-aware projections instead of being lost in a generic resource row.
- projects_to:
  - `dictionary/qti-core.v1.json#qti_package.package_identifier`
  - `dictionary/qti-core.v1.json#qti_assessment_item.identifier`
  - `dictionary/integration-governance-core.v1.json#lti_deep_link_item.url`
  - `dictionary/caliper-core.v1.json#caliper_entity.entity_type`
  - `dictionary/caliper-core.v1.json#caliper_extension.extension_key`
  - `docs/generated/qti-core-dictionary.md`
  - `site/docs/qti-core-dictionary.html`

## DEC-010 Tenant-Owned Data and Shared Reference Data

- id: `DEC-010-tenancy-reference-data`
- question: Which data is tenant-owned and isolated, and which data may live in shared reference namespaces?
- options_considered:
  - Put every record in tenant-owned tables.
  - Put standards, content, and roster data in global shared tables.
  - Tenant-isolate operational school records while using governed shared namespaces for public reference data.
- choice: Tenant-owned operational records carry tenant boundaries and row-level policy. Public CASE frameworks, public standards metadata, public certification fixtures, and optionally public item banks live in shared reference namespaces. Tenants adopt, pin, override, or privately extend shared reference data through explicit records.
- consequences:
  - Removes the need for application code to perform per-table tenant filtering; PostgreSQL RLS is the single runtime gate for tenant-owned records.
  - Removes duplicated tenant `where tenant_id = ...` guard code from PostgREST callers, `demo/server.js` examples, and Edge Function database reads; `supabase/migrations/0001_oneroster_core_demo.sql` owns the tenant predicate through forced RLS policies.
  - Makes global public reference data reusable without copying it into every tenant.
  - Why not collapse: tenant-isolating every public reference record would simplify the policy model, but it would copy CASE frameworks and public certification fixtures into every tenant and make version pinning harder.
  - Creates the constraint that tenant-owned runtime tables must carry tenant identity and cannot use permissive `using (true)` policies.
- projects_to:
  - `supabase/migrations/0001_oneroster_core_demo.sql#tenant_id columns`
  - `supabase/migrations/0001_oneroster_core_demo.sql#tenant_isolation policies`
  - `supabase/policies/pg_policies.snapshot.json`
  - `dictionary/oneroster-core.v1.json#organization.id`
  - `dictionary/caliper-core.v1.json#caliper_extension.allowed_by_policy`
  - `tests/supabase_tenant_rls_test.py`

## DEC-011 Privacy Surfaces

- id: `DEC-011-privacy-surfaces`
- question: Which privacy classes may appear on live APIs, Edge Functions, static mirrors, and generated docs?
- options_considered:
  - Publish only schema descriptions and non-record fixtures on unauthenticated static/generated surfaces; require every record-like example, even synthetic directory data, to come from authenticated live APIs.
  - Permit full synthetic fixture payloads, including education-record and behavioral examples, in static mirrors when each file is marked as non-live demo data and generated from a scrubbed seed.
  - Define per-surface gates by privacy class and treat static mirrors as synthetic documentation fixtures.
- choice: Generated docs may describe every field and privacy class because they are schema documentation, not records. Live PostgREST may expose tenant-owned `public`, `operational`, `directory`, and `education_record` records only through tenant RLS and scope policy. Edge Functions may expose `directory`, `education_record`, `behavioral`, or sensitive operational fields only through caller JWT, purpose, scope, tenant RLS, and audit logging when the read is sensitive. Static `site/api/*.json` mirrors may contain only synthetic demo records from the seeded `.test` tenant and may include `public`, `operational`, and `directory` fields such as demo email; they may not contain real tenant data, `education_record`, `behavioral`, `sensitive_pii`, or secret/system values.
- consequences:
  - Removes the need to delete synthetic directory fields like `site/api/people.json` email while still forbidding real unauthenticated PII mirrors.
  - Removes per-file privacy exception lists from `scripts/build_static_api.py`, `site/api/*.json`, and generated OpenAPI descriptions; surface eligibility comes from privacy class plus runtime gate.
  - Eliminates per-file privacy guessing by making the gate a function of privacy class plus surface.
  - Why not collapse: banning every record-like example from static docs would simplify privacy review, but it would make the GitHub Pages portal unable to demonstrate schema-shaped payloads offline.
  - Creates the constraint that future static mirrors must either stay synthetic/documentation-only or drop fields whose privacy class requires live RLS or audited Edge Functions.
- projects_to:
  - `dictionary/oneroster-core.v1.json#person.email`
  - `dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.privacy_class`
  - `site/api/people.json`
  - `site/api/classes.json`
  - `site/api/views/gradebook-results.json`
  - `supabase/functions/audited-roster-read/index.ts`
  - `tests/supabase_audit_log_test.py`

## DEC-012 Runtime Coverage Per Spec

- id: `DEC-012-runtime-coverage-per-spec`
- question: Which Lead specs are runtime-backed now, which are doc-only, and which have partial receipt or governance slices?
- options_considered:
  - Claim runtime support for every generated dictionary.
  - Mark everything except OneRoster as unsupported.
  - Separate generated accounting from runtime coverage and state each Lead spec's current runtime posture.
- choice: OneRoster core is runtime-backed now through local SQLite, hosted Supabase PostgREST, RLS, and live tests. QTI and CASE are doc-only/generated dictionary projections until runtime slices are built. Caliper, LTI, Security Framework, and Data Privacy have partial runtime backing through authenticated Edge Function receipt/governance paths, but not full standard conformance flows. Full runtime for QTI import, CASE search, Caliper raw-event projection, LTI Advantage services, production OAuth, and privacy workflows remains future work with target dates in the decision/pending work queue.
- consequences:
  - Removes the need for generated dictionary pages to pretend they are deployed runtime APIs.
  - Removes runtime claims from generated docs, `docs/lead-spec-accounting.md`, and portal copy unless a table, Edge Function, hosted REST path, and test exercise that spec-shaped behavior.
  - Makes the coverage matrix honest by separating source dictionary, generated artifacts, runtime slice, and deferred ledger.
  - Why not collapse: marking every non-OneRoster spec unsupported would be simpler, but it would hide useful generated dictionary/API accounting and the partial Caliper/LTI/security runtime receipts that already exist.
  - Creates the constraint that a spec cannot be called runtime-backed unless live tables or Edge Functions and tests exercise that spec-shaped behavior.
- projects_to:
  - `docs/dictionary-coverage-matrix.md`
  - `docs/lead-spec-accounting.md`
  - `docs/decisions/decisions-pending.md`
  - `scripts/check_spec_conformance.py`
  - `site/api/spec-conformance.json`
  - `tests/supabase_tenant_rls_test.py`
  - `tests/supabase_audit_log_test.py`

## DEC-013 Audit Response Truth

- id: `DEC-013-audit-response-truth`
- question: What may an audited Edge Function response claim about audit logging?
- options_considered:
  - Silent response: do the audited read but return no audit block.
  - Advisory response: return best-effort audit intent without claiming rows were written.
  - Truthful response: return audit metadata only after reading back the rows written to `audit_log`.
- choice: Audited Edge Functions must use truthful responses when they include an `audit` block. If the function cannot read the written `audit_log` rows back under the caller's JWT and request identifier, it must omit the audit block or return an explicit error; it must not hard-code `logged` counts or field lists.
- consequences:
  - Removes the need for callers and tests to trust a response that may not match the database.
  - Removes response-only audit assertions from `tests/supabase_audit_log_test.py`; the regression must read matching `audit_log` rows before accepting the Edge Function's claim.
  - Eliminates hard-coded audit counts such as `logged: 5` as acceptable evidence.
  - Creates the constraint that audited read functions must carry a request ID through the database write and read back matching audit rows before claiming success.
- projects_to:
  - `supabase/functions/audited-roster-read/index.ts`
  - `supabase/migrations/0001_oneroster_core_demo.sql#audit_log`
  - `supabase/migrations/0001_oneroster_core_demo.sql#read_people_sensitive_audited`
  - `tests/supabase_audit_log_test.py`
  - `docs/admin-operations.md`
  - `site/api/platform-evaluation.json`

## DEC-014 Static Mirror Policy

- id: `DEC-014-static-mirror-policy`
- question: Are `site/api/*.json` files contract surfaces, documentation fixtures, or removable build artifacts?
- options_considered:
  - Delete all static mirrors now that hosted Supabase REST exists.
  - Treat static mirrors as canonical public API responses.
  - Keep static mirrors as documentation fixtures generated from the same demo seed and clearly subordinate to the live runtime.
- choice: Static mirrors are allowed as documentation fixtures for GitHub Pages and offline inspection. They are not the canonical runtime contract; live Supabase REST and Edge Functions are the runtime contract. Mirrors must be generated from the same synthetic demo seed as the local demo, must carry source metadata, and may only include privacy classes allowed by `DEC-011-privacy-surfaces`.
- consequences:
  - Removes the need to run a backend just to inspect example JSON from the portal.
  - Removes `site/api/*.json` from the canonical API contract surface; `scripts/build_static_api.py` emits documentation fixtures with source metadata while live Supabase REST and Edge Functions own runtime behavior.
  - Makes static/runtime drift a documentation freshness problem, not a second source of truth.
  - Why not collapse: deleting static mirrors entirely would simplify publish artifacts, but it would make GitHub Pages and offline review lose copyable JSON payload examples for the core OneRoster slice.
  - Creates the constraint that each mirror must remain generated, cite its source dictionary/decision, and avoid privacy classes not allowed on static surfaces.
- projects_to:
  - `scripts/build_static_api.py`
  - `site/api/index.json`
  - `site/api/people.json`
  - `site/api/organizations.json`
  - `site/api/classes.json`
  - `site/api/enrollments.json`
  - `site/api/views/class-roster.json`
  - `site/api/views/gradebook-results.json`

## DEC-015 Service-Role Policy

- id: `DEC-015-service-role-policy`
- question: When may code use Supabase service-role access without weakening the user-JWT and RLS story?
- options_considered:
  - Remove service-role credentials from repository automation entirely by running tests only against pre-provisioned tenants, users, and seed data.
  - Centralize service-role use in a privileged admin data-access module that Edge Functions and tests may call for audited setup and repair operations.
  - Allow service-role only for named admin/test fixture operations in `docs/admin-operations.md`, never for request-scoped reads or writes.
- choice: Request-scoped runtime code and Edge Functions must pass the caller's `Authorization` bearer token to Supabase so RLS applies. Service-role access is allowed only for allowlisted admin or test fixture operations in `docs/admin-operations.md`, with a named operation ID, caller, why-user-JWT-insufficient reason, guardrails, and recent review date. Tests may use service role to create temporary Auth users, but not to read tenant data or satisfy the assertion under test.
- consequences:
  - Removes the need to audit every Edge Function for hidden bypass behavior once the allowlist and no-service-role-in-functions check pass.
  - Removes Supabase service-role client construction from `supabase/functions/gradebook-bulk-submit/index.ts`, `supabase/functions/audited-roster-read/index.ts`, `supabase/functions/lti-launch-handler/index.ts`, `supabase/functions/caliper-event-ingestion/index.ts`, and `supabase/functions/oauth-token-exchange/index.ts`.
  - Eliminates service-role fixtures as evidence for tenant isolation or audit behavior; only user-JWT calls count for those regressions.
  - Creates the constraint that any new service-role use must be documented before it lands and must not appear under `supabase/functions/*`.
- projects_to:
  - `docs/admin-operations.md`
  - `supabase/functions/gradebook-bulk-submit/index.ts`
  - `supabase/functions/audited-roster-read/index.ts`
  - `supabase/functions/lti-launch-handler/index.ts`
  - `supabase/functions/caliper-event-ingestion/index.ts`
  - `supabase/functions/oauth-token-exchange/index.ts`
  - `tests/supabase_tenant_rls_test.py`
  - `tests/supabase_audit_log_test.py`

## DEC-016 Dictionary Generation Direction

- id: `DEC-016-dictionary-generation-direction`
- question: Which dictionary artifact is authoritative: the shared platform dictionary or the per-spec dictionaries?
- options_considered:
  - Commit only the shared dictionary and generate all spec views on demand.
  - Keep per-spec JSON files canonical and synthesize shared docs from them.
  - Use the shared dictionary as canonical and generate committed per-spec projection JSON.
- choice: `data/data-dictionary.seed.json` is upstream. `dictionary/*.v1.json` files are generated projections; hand-editing a per-spec projection is a build error once the generator lands.
- consequences:
  - Removes five-way hand-edited dictionary reconciliation.
  - Removes direct edits to `dictionary/oneroster-core.v1.json`, `dictionary/qti-core.v1.json`, `dictionary/case-core.v1.json`, `dictionary/caliper-core.v1.json`, and `dictionary/integration-governance-core.v1.json` as an accepted workflow once `scripts/generate_spec_dictionaries.py --check` owns projection drift.
  - Lets CI compare generated projection JSON instead of relying on review memory.
  - Requires every projected object, field, enum, privacy class, and relationship to live in the shared seed or be marked `spec_only`.
- projects_to:
  - `data/data-dictionary.seed.json#objects`
  - `dictionary/oneroster-core.v1.json`
  - `dictionary/qti-core.v1.json`
  - `scripts/check_dictionary_artifacts.py#CONFIGS`

## DEC-017 Canonical Field Reconciliation

- id: `DEC-017-canonical-field-reconciliation`
- question: How should fields with the same platform meaning across different standards be reconciled?
- options_considered:
  - Publish only canonical platform fields and keep spec-native names in adapters.
  - Preserve only spec-native names and let callers infer overlaps.
  - Preserve spec-native fields but require overlapping fields to carry `canonical_field_id`.
- choice: Every overlapping spec field carries `canonical_field_id` pointing at the shared dictionary. Spec-native names remain for conformance; cross-spec app code uses the canonical field identity.
- consequences:
  - Removes runtime/docs conversion between `email`, LTI email claims, actor identifiers, and candidate labels.
  - Removes field-name conversion tables from docs, OpenAPI examples, and future API adapters; `canonical_field_id` on each per-spec field becomes the join contract.
  - Eliminates prose-only overlap claims; each overlapping field points to a concrete shared field or a `spec_only` exception.
  - Requires new per-spec fields to be classified before docs or OpenAPI can publish them.
- projects_to:
  - `data/data-dictionary.seed.json#person`
  - `dictionary/oneroster-core.v1.json#person.email`
  - `dictionary/integration-governance-core.v1.json#lti_membership.email`
  - `dictionary/caliper-core.v1.json#caliper_actor.email`
  - `dictionary/caliper-core.v1.json#caliper_actor.identifier_value`
  - `dictionary/qti-core.v1.json#qti_candidate.email`

## DEC-018 Global Enum Crosswalks

- id: `DEC-018-global-enum-crosswalks`
- question: How should allowed-value vocabularies be unified across standards?
- options_considered:
  - Replace spec-native enum values with platform values everywhere.
  - Let each spec dictionary keep independent enum lists.
  - Maintain shared enums with `shared_enum_id` references and bidirectional spec crosswalks.
- choice: Allowed values are global dictionary objects. Each enum field references `shared_enum_id`; the shared enum maps every spec-native value to and from a canonical value.
- consequences:
  - Removes per-API parsers for OneRoster names, LTI URIs, Caliper roles, and QTI values.
  - Removes duplicated `shared_allowed_values` / inline enum blocks as the vocabulary source in per-spec dictionaries; `shared_enum_id` plus crosswalk rows own canonical and spec-native values.
  - Eliminates duplicate enum docs for the same platform vocabulary.
  - Requires every allowed value to crosswalk to a shared enum or be marked spec-only with a reason.
- projects_to:
  - `data/data-dictionary.seed.json#person.primary_role`
  - `dictionary/oneroster-core.v1.json#person.primary_role`
  - `dictionary/oneroster-core.v1.json#enrollment.role`
  - `dictionary/integration-governance-core.v1.json#lti_launch.roles`

## DEC-019 Closed Privacy Classes

- id: `DEC-019-closed-privacy-classes`
- question: What is the closed privacy-class vocabulary, and how are content-dependent placeholders resolved?
- options_considered:
  - Collapse every non-public field into one protected class.
  - Allow placeholders such as `depends_on_entity` and `depends_on_contents`.
  - Maintain one closed privacy-class list and assign a concrete class to every field occurrence.
- choice: Closed keys are `public`, `operational`, `directory`, `education_record`, `behavioral`, `sensitive`, `credential`, `privacy_governance`, and `system`. `depends_on_entity` and `depends_on_contents` are invalid.
- consequences:
  - Removes generator branches that interpret open-ended privacy placeholders per spec.
  - Removes `depends_on_entity` and `depends_on_contents` handling from `scripts/generate_caliper_core.py`, generated Caliper docs, and runtime surface gates; each field occurrence has one concrete class.
  - Eliminates `depends_on_entity` and `depends_on_contents` from generated dictionaries.
  - Requires a decision update before a new privacy class can appear in fields, docs, or runtime surfaces.
- projects_to:
  - `data/data-dictionary.seed.json#privacy_classes`
  - `dictionary/caliper-core.v1.json#caliper_entity.name`
  - `dictionary/caliper-core.v1.json#caliper_entity.extensions`
  - `dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.privacy_class`

## DEC-020 Relational Graph Migrations

- id: `DEC-020-relational-graph-migrations`
- question: Where should foreign keys, cardinalities, and ownership relationships live for generated Supabase migrations?
- options_considered:
  - Generate database DDL from the dictionary at deploy time and stop committing SQL.
  - Keep migrations hand-written and document relationships separately.
  - Store relationships in the shared dictionary and generate committed Supabase migration SQL.
- choice: Shared dictionary objects own source field, target object, target field, cardinality, ownership, and delete behavior. Supabase migrations are generated from that graph.
- consequences:
  - Removes duplicated FK truth across SQL, dictionary prose, docs, and examples.
  - Removes hand-maintained foreign-key blocks in `supabase/migrations/0001_oneroster_core_demo.sql` as the authoritative relationship source; the dictionary graph owns targets, cardinality, ownership, and delete behavior.
  - Lets generators derive table order, FK clauses, and ownership constraints from the graph.
  - Requires each public SQL relationship to have a dictionary entry.
- projects_to:
  - `data/data-dictionary.seed.json#objects`
  - `dictionary/oneroster-core.v1.json#class.course_id`
  - `dictionary/oneroster-core.v1.json#enrollment.person_id`
  - `supabase/migrations/0001_oneroster_core_demo.sql#references public.classes`

## Machine-Readable Decision Trace

Field references use the dictionary file, object key, and field key. Each `decision_id` also appears on the corresponding dictionary field object and in generated OpenAPI/Markdown/HTML dictionary artifacts.

<!-- decision-trace:start -->
```json
[
  {
    "decision_id": "DEC-001-person-agent-subject",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_actor.actor_type",
      "dictionary/caliper-core.v1.json#caliper_actor.display_name",
      "dictionary/caliper-core.v1.json#caliper_actor.email",
      "dictionary/caliper-core.v1.json#caliper_actor.identifier_type",
      "dictionary/caliper-core.v1.json#caliper_actor.identifier_value",
      "dictionary/caliper-core.v1.json#caliper_actor.resolution_status",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.actor_type",
      "dictionary/oneroster-core.v1.json#person.display_name",
      "dictionary/oneroster-core.v1.json#person.email",
      "dictionary/oneroster-core.v1.json#person.enabled_user",
      "dictionary/oneroster-core.v1.json#person.family_name",
      "dictionary/oneroster-core.v1.json#person.given_name",
      "dictionary/oneroster-core.v1.json#person.status",
      "dictionary/qti-core.v1.json#qti_candidate.display_name",
      "dictionary/qti-core.v1.json#qti_candidate.email",
      "dictionary/qti-core.v1.json#qti_candidate.platform_person_id"
    ]
  },
  {
    "decision_id": "DEC-002-learning-context",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_context.lti_message_type",
      "dictionary/caliper-core.v1.json#caliper_extension.privacy_classification",
      "dictionary/integration-governance-core.v1.json#lti_deployment.deployment_scope",
      "dictionary/integration-governance-core.v1.json#lti_deployment.service_scopes",
      "dictionary/integration-governance-core.v1.json#lti_deployment.status",
      "dictionary/integration-governance-core.v1.json#lti_registration.allowed_scopes",
      "dictionary/integration-governance-core.v1.json#lti_registration.status",
      "dictionary/integration-governance-core.v1.json#lti_registration.tool_name",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.policy_status",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.required_scope",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.service_type",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.service_versions",
      "dictionary/oneroster-core.v1.json#academic_session.session_type",
      "dictionary/oneroster-core.v1.json#academic_session.status",
      "dictionary/oneroster-core.v1.json#academic_session.title",
      "dictionary/oneroster-core.v1.json#class.class_code",
      "dictionary/oneroster-core.v1.json#class.class_type",
      "dictionary/oneroster-core.v1.json#class.status",
      "dictionary/oneroster-core.v1.json#class.title",
      "dictionary/oneroster-core.v1.json#course.course_code",
      "dictionary/oneroster-core.v1.json#course.status",
      "dictionary/oneroster-core.v1.json#course.title",
      "dictionary/oneroster-core.v1.json#organization.name",
      "dictionary/oneroster-core.v1.json#organization.organization_type",
      "dictionary/oneroster-core.v1.json#organization.status",
      "dictionary/qti-core.v1.json#qti_assessment_test.class_tokens"
    ]
  },
  {
    "decision_id": "DEC-003-role-vocabulary",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_context.membership_role",
      "dictionary/integration-governance-core.v1.json#lti_launch.roles",
      "dictionary/integration-governance-core.v1.json#lti_membership.roles",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.allowed_roles",
      "dictionary/oneroster-core.v1.json#enrollment.role",
      "dictionary/oneroster-core.v1.json#person.primary_role"
    ]
  },
  {
    "decision_id": "DEC-004-enrollment-membership",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_context.membership_status",
      "dictionary/integration-governance-core.v1.json#lti_membership.display_name",
      "dictionary/integration-governance-core.v1.json#lti_membership.email",
      "dictionary/integration-governance-core.v1.json#lti_membership.lis_person_sourcedid",
      "dictionary/integration-governance-core.v1.json#lti_membership.status",
      "dictionary/oneroster-core.v1.json#enrollment.primary_flag",
      "dictionary/oneroster-core.v1.json#enrollment.status"
    ]
  },
  {
    "decision_id": "DEC-005-results-scores",
    "produces_fields": [
      "dictionary/case-core.v1.json#case_rubric_criterion.weight",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.feedback",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.quality",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.score",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.line_item_json",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.activity_progress",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.exchange_status",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.grading_progress",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.line_item_label",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.score_given",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.score_maximum",
      "dictionary/oneroster-core.v1.json#line_item.category",
      "dictionary/oneroster-core.v1.json#line_item.result_value_max",
      "dictionary/oneroster-core.v1.json#line_item.result_value_min",
      "dictionary/oneroster-core.v1.json#line_item.status",
      "dictionary/oneroster-core.v1.json#line_item.title",
      "dictionary/oneroster-core.v1.json#result.comment",
      "dictionary/oneroster-core.v1.json#result.score",
      "dictionary/oneroster-core.v1.json#result.score_status",
      "dictionary/oneroster-core.v1.json#result.status",
      "dictionary/qti-core.v1.json#qti_assessment_item.has_correct_response",
      "dictionary/qti-core.v1.json#qti_assessment_item.max_score",
      "dictionary/qti-core.v1.json#qti_assessment_test.outcome_processing_summary",
      "dictionary/qti-core.v1.json#qti_feedback.access",
      "dictionary/qti-core.v1.json#qti_feedback.body_summary",
      "dictionary/qti-core.v1.json#qti_feedback.feedback_identifier",
      "dictionary/qti-core.v1.json#qti_feedback.feedback_kind",
      "dictionary/qti-core.v1.json#qti_feedback.outcome_identifier",
      "dictionary/qti-core.v1.json#qti_feedback.owner_object_type",
      "dictionary/qti-core.v1.json#qti_feedback.rubric_use",
      "dictionary/qti-core.v1.json#qti_feedback.show_hide",
      "dictionary/qti-core.v1.json#qti_feedback.title",
      "dictionary/qti-core.v1.json#qti_feedback.view",
      "dictionary/qti-core.v1.json#qti_item_ref.weight",
      "dictionary/qti-core.v1.json#qti_processing_rule.logic_summary",
      "dictionary/qti-core.v1.json#qti_processing_rule.owner_object_type",
      "dictionary/qti-core.v1.json#qti_processing_rule.processing_kind",
      "dictionary/qti-core.v1.json#qti_processing_rule.target_identifier",
      "dictionary/qti-core.v1.json#qti_processing_rule.template_uri",
      "dictionary/qti-core.v1.json#qti_variable_declaration.correct_response_summary",
      "dictionary/qti-core.v1.json#qti_variable_declaration.mapping_summary"
    ]
  },
  {
    "decision_id": "DEC-006-standards-alignment",
    "produces_fields": [
      "dictionary/case-core.v1.json#case_api_status.imsx_code_major",
      "dictionary/case-core.v1.json#case_api_status.imsx_code_minor",
      "dictionary/case-core.v1.json#case_api_status.imsx_description",
      "dictionary/case-core.v1.json#case_api_status.imsx_severity",
      "dictionary/case-core.v1.json#case_association.association_grouping_uri",
      "dictionary/case-core.v1.json#case_association.association_type",
      "dictionary/case-core.v1.json#case_association.destination_node_uri",
      "dictionary/case-core.v1.json#case_association.notes",
      "dictionary/case-core.v1.json#case_association.origin_node_uri",
      "dictionary/case-core.v1.json#case_association.sequence_number",
      "dictionary/case-core.v1.json#case_association_grouping.description",
      "dictionary/case-core.v1.json#case_association_grouping.title",
      "dictionary/case-core.v1.json#case_concept.description",
      "dictionary/case-core.v1.json#case_concept.hierarchy_code",
      "dictionary/case-core.v1.json#case_concept.keywords",
      "dictionary/case-core.v1.json#case_concept.title",
      "dictionary/case-core.v1.json#case_definition.concept_count",
      "dictionary/case-core.v1.json#case_definition.item_type_count",
      "dictionary/case-core.v1.json#case_definition.license_count",
      "dictionary/case-core.v1.json#case_definition.subject_count",
      "dictionary/case-core.v1.json#case_document.adoption_status",
      "dictionary/case-core.v1.json#case_document.case_version",
      "dictionary/case-core.v1.json#case_document.creator",
      "dictionary/case-core.v1.json#case_document.description",
      "dictionary/case-core.v1.json#case_document.framework_type",
      "dictionary/case-core.v1.json#case_document.language",
      "dictionary/case-core.v1.json#case_document.publisher_version",
      "dictionary/case-core.v1.json#case_document.subject",
      "dictionary/case-core.v1.json#case_document.title",
      "dictionary/case-core.v1.json#case_item.abbreviated_statement",
      "dictionary/case-core.v1.json#case_item.alternative_label",
      "dictionary/case-core.v1.json#case_item.concept_keywords",
      "dictionary/case-core.v1.json#case_item.education_level",
      "dictionary/case-core.v1.json#case_item.full_statement",
      "dictionary/case-core.v1.json#case_item.human_coding_scheme",
      "dictionary/case-core.v1.json#case_item.item_type",
      "dictionary/case-core.v1.json#case_item.item_type_uri",
      "dictionary/case-core.v1.json#case_item.list_enumeration",
      "dictionary/case-core.v1.json#case_item.subject",
      "dictionary/case-core.v1.json#case_item_type.description",
      "dictionary/case-core.v1.json#case_item_type.hierarchy_code",
      "dictionary/case-core.v1.json#case_item_type.title",
      "dictionary/case-core.v1.json#case_item_type.type_code",
      "dictionary/case-core.v1.json#case_license.description",
      "dictionary/case-core.v1.json#case_license.license_text",
      "dictionary/case-core.v1.json#case_license.title",
      "dictionary/case-core.v1.json#case_package.source_system",
      "dictionary/case-core.v1.json#case_package.validation_status",
      "dictionary/case-core.v1.json#case_rubric.description",
      "dictionary/case-core.v1.json#case_rubric.title",
      "dictionary/case-core.v1.json#case_rubric_criterion.case_item_uri",
      "dictionary/case-core.v1.json#case_rubric_criterion.category",
      "dictionary/case-core.v1.json#case_rubric_criterion.description",
      "dictionary/case-core.v1.json#case_rubric_criterion.position",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.description",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.position",
      "dictionary/case-core.v1.json#case_subject.description",
      "dictionary/case-core.v1.json#case_subject.hierarchy_code",
      "dictionary/case-core.v1.json#case_subject.title",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.document_target",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.item_type",
      "dictionary/qti-core.v1.json#qti_alignment.alignment_label",
      "dictionary/qti-core.v1.json#qti_alignment.owner_object_type",
      "dictionary/qti-core.v1.json#qti_alignment.target_identifier",
      "dictionary/qti-core.v1.json#qti_alignment.target_type",
      "dictionary/qti-core.v1.json#qti_interaction.max_associations",
      "dictionary/qti-core.v1.json#qti_interaction.min_associations"
    ]
  },
  {
    "decision_id": "DEC-007-identifier-crosswalk",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_actor.entity_id",
      "dictionary/caliper-core.v1.json#caliper_actor.id",
      "dictionary/caliper-core.v1.json#caliper_actor.platform_person_id",
      "dictionary/caliper-core.v1.json#caliper_context.event_id",
      "dictionary/caliper-core.v1.json#caliper_context.federated_session_entity_id",
      "dictionary/caliper-core.v1.json#caliper_context.group_entity_id",
      "dictionary/caliper-core.v1.json#caliper_context.id",
      "dictionary/caliper-core.v1.json#caliper_context.lti_context_id",
      "dictionary/caliper-core.v1.json#caliper_context.lti_deployment_id",
      "dictionary/caliper-core.v1.json#caliper_context.lti_platform_id",
      "dictionary/caliper-core.v1.json#caliper_context.membership_entity_id",
      "dictionary/caliper-core.v1.json#caliper_context.session_entity_id",
      "dictionary/caliper-core.v1.json#caliper_entity.canonical_person_id",
      "dictionary/caliper-core.v1.json#caliper_entity.canonical_resource_id",
      "dictionary/caliper-core.v1.json#caliper_entity.id",
      "dictionary/caliper-core.v1.json#caliper_envelope.id",
      "dictionary/caliper-core.v1.json#caliper_envelope.sensor_id",
      "dictionary/caliper-core.v1.json#caliper_envelope.tenant_id",
      "dictionary/caliper-core.v1.json#caliper_event.actor_id",
      "dictionary/caliper-core.v1.json#caliper_event.ed_app_id",
      "dictionary/caliper-core.v1.json#caliper_event.envelope_id",
      "dictionary/caliper-core.v1.json#caliper_event.federated_session_id",
      "dictionary/caliper-core.v1.json#caliper_event.generated_id",
      "dictionary/caliper-core.v1.json#caliper_event.group_id",
      "dictionary/caliper-core.v1.json#caliper_event.id",
      "dictionary/caliper-core.v1.json#caliper_event.membership_id",
      "dictionary/caliper-core.v1.json#caliper_event.object_id",
      "dictionary/caliper-core.v1.json#caliper_event.referrer_id",
      "dictionary/caliper-core.v1.json#caliper_event.session_id",
      "dictionary/caliper-core.v1.json#caliper_event.target_id",
      "dictionary/caliper-core.v1.json#caliper_extension.id",
      "dictionary/caliper-core.v1.json#caliper_extension.owner_id",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.id",
      "dictionary/case-core.v1.json#case_api_status.id",
      "dictionary/case-core.v1.json#case_api_status.operation_id",
      "dictionary/case-core.v1.json#case_association.document_id",
      "dictionary/case-core.v1.json#case_association.id",
      "dictionary/case-core.v1.json#case_association.identifier",
      "dictionary/case-core.v1.json#case_association.uri",
      "dictionary/case-core.v1.json#case_association_grouping.document_id",
      "dictionary/case-core.v1.json#case_association_grouping.id",
      "dictionary/case-core.v1.json#case_association_grouping.identifier",
      "dictionary/case-core.v1.json#case_association_grouping.uri",
      "dictionary/case-core.v1.json#case_concept.document_id",
      "dictionary/case-core.v1.json#case_concept.id",
      "dictionary/case-core.v1.json#case_concept.identifier",
      "dictionary/case-core.v1.json#case_concept.uri",
      "dictionary/case-core.v1.json#case_definition.document_id",
      "dictionary/case-core.v1.json#case_definition.id",
      "dictionary/case-core.v1.json#case_document.id",
      "dictionary/case-core.v1.json#case_document.identifier",
      "dictionary/case-core.v1.json#case_document.license_uri",
      "dictionary/case-core.v1.json#case_document.official_source_url",
      "dictionary/case-core.v1.json#case_document.uri",
      "dictionary/case-core.v1.json#case_item.document_id",
      "dictionary/case-core.v1.json#case_item.id",
      "dictionary/case-core.v1.json#case_item.identifier",
      "dictionary/case-core.v1.json#case_item.license_uri",
      "dictionary/case-core.v1.json#case_item.uri",
      "dictionary/case-core.v1.json#case_item_type.document_id",
      "dictionary/case-core.v1.json#case_item_type.id",
      "dictionary/case-core.v1.json#case_item_type.identifier",
      "dictionary/case-core.v1.json#case_item_type.uri",
      "dictionary/case-core.v1.json#case_license.document_id",
      "dictionary/case-core.v1.json#case_license.id",
      "dictionary/case-core.v1.json#case_license.identifier",
      "dictionary/case-core.v1.json#case_license.uri",
      "dictionary/case-core.v1.json#case_package.document_id",
      "dictionary/case-core.v1.json#case_package.id",
      "dictionary/case-core.v1.json#case_package.package_uri",
      "dictionary/case-core.v1.json#case_rubric.document_id",
      "dictionary/case-core.v1.json#case_rubric.id",
      "dictionary/case-core.v1.json#case_rubric.identifier",
      "dictionary/case-core.v1.json#case_rubric.uri",
      "dictionary/case-core.v1.json#case_rubric_criterion.id",
      "dictionary/case-core.v1.json#case_rubric_criterion.identifier",
      "dictionary/case-core.v1.json#case_rubric_criterion.rubric_id",
      "dictionary/case-core.v1.json#case_rubric_criterion.uri",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.criterion_id",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.id",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.identifier",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.uri",
      "dictionary/case-core.v1.json#case_subject.document_id",
      "dictionary/case-core.v1.json#case_subject.id",
      "dictionary/case-core.v1.json#case_subject.identifier",
      "dictionary/case-core.v1.json#case_subject.uri",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.id",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.launch_id",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.url",
      "dictionary/integration-governance-core.v1.json#lti_deployment.context_id",
      "dictionary/integration-governance-core.v1.json#lti_deployment.deployment_id",
      "dictionary/integration-governance-core.v1.json#lti_deployment.id",
      "dictionary/integration-governance-core.v1.json#lti_deployment.registration_id",
      "dictionary/integration-governance-core.v1.json#lti_deployment.resource_link_id",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.id",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.line_item_url",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.service_endpoint_id",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.user_id",
      "dictionary/integration-governance-core.v1.json#lti_launch.context_id",
      "dictionary/integration-governance-core.v1.json#lti_launch.deployment_id",
      "dictionary/integration-governance-core.v1.json#lti_launch.id",
      "dictionary/integration-governance-core.v1.json#lti_launch.id_token_hash",
      "dictionary/integration-governance-core.v1.json#lti_launch.nonce_hash",
      "dictionary/integration-governance-core.v1.json#lti_launch.registration_id",
      "dictionary/integration-governance-core.v1.json#lti_launch.subject_id",
      "dictionary/integration-governance-core.v1.json#lti_launch.target_link_uri",
      "dictionary/integration-governance-core.v1.json#lti_launch.tenant_id",
      "dictionary/integration-governance-core.v1.json#lti_membership.context_id",
      "dictionary/integration-governance-core.v1.json#lti_membership.id",
      "dictionary/integration-governance-core.v1.json#lti_membership.platform_person_id",
      "dictionary/integration-governance-core.v1.json#lti_membership.service_endpoint_id",
      "dictionary/integration-governance-core.v1.json#lti_membership.user_id",
      "dictionary/integration-governance-core.v1.json#lti_registration.authorization_endpoint",
      "dictionary/integration-governance-core.v1.json#lti_registration.client_id",
      "dictionary/integration-governance-core.v1.json#lti_registration.id",
      "dictionary/integration-governance-core.v1.json#lti_registration.initiate_login_uri",
      "dictionary/integration-governance-core.v1.json#lti_registration.issuer",
      "dictionary/integration-governance-core.v1.json#lti_registration.jwks_uri",
      "dictionary/integration-governance-core.v1.json#lti_registration.redirect_uris",
      "dictionary/integration-governance-core.v1.json#lti_registration.tenant_id",
      "dictionary/integration-governance-core.v1.json#lti_registration.token_endpoint",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.context_id",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.deployment_id",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.endpoint_url",
      "dictionary/integration-governance-core.v1.json#lti_service_endpoint.id",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.actor_person_id",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.client_id",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.id",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.object_id",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.policy_id",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.tenant_id",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.evidence_uri",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.guardian_person_id",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.id",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.person_id",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.rule_id",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.tenant_id",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.id",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.tenant_id",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.id",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.tenant_id",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.client_id",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.id",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.jwks_uri",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.tenant_id",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.id",
      "dictionary/oneroster-core.v1.json#academic_session.id",
      "dictionary/oneroster-core.v1.json#academic_session.sourced_id",
      "dictionary/oneroster-core.v1.json#class.course_id",
      "dictionary/oneroster-core.v1.json#class.id",
      "dictionary/oneroster-core.v1.json#class.school_id",
      "dictionary/oneroster-core.v1.json#class.sourced_id",
      "dictionary/oneroster-core.v1.json#class.term_id",
      "dictionary/oneroster-core.v1.json#course.id",
      "dictionary/oneroster-core.v1.json#course.org_id",
      "dictionary/oneroster-core.v1.json#course.school_year_id",
      "dictionary/oneroster-core.v1.json#course.sourced_id",
      "dictionary/oneroster-core.v1.json#enrollment.class_id",
      "dictionary/oneroster-core.v1.json#enrollment.id",
      "dictionary/oneroster-core.v1.json#enrollment.person_id",
      "dictionary/oneroster-core.v1.json#enrollment.school_id",
      "dictionary/oneroster-core.v1.json#enrollment.sourced_id",
      "dictionary/oneroster-core.v1.json#line_item.class_id",
      "dictionary/oneroster-core.v1.json#line_item.id",
      "dictionary/oneroster-core.v1.json#line_item.sourced_id",
      "dictionary/oneroster-core.v1.json#organization.id",
      "dictionary/oneroster-core.v1.json#organization.parent_organization_id",
      "dictionary/oneroster-core.v1.json#organization.sourced_id",
      "dictionary/oneroster-core.v1.json#person.id",
      "dictionary/oneroster-core.v1.json#person.sourced_id",
      "dictionary/oneroster-core.v1.json#result.id",
      "dictionary/oneroster-core.v1.json#result.line_item_id",
      "dictionary/oneroster-core.v1.json#result.person_id",
      "dictionary/oneroster-core.v1.json#result.sourced_id",
      "dictionary/oneroster-core.v1.json#source_identifier.external_id",
      "dictionary/oneroster-core.v1.json#source_identifier.id",
      "dictionary/oneroster-core.v1.json#source_identifier.object_id",
      "dictionary/qti-core.v1.json#qti_accessibility_support.id",
      "dictionary/qti-core.v1.json#qti_accessibility_support.owner_id",
      "dictionary/qti-core.v1.json#qti_alignment.id",
      "dictionary/qti-core.v1.json#qti_alignment.owner_id",
      "dictionary/qti-core.v1.json#qti_alignment.source_metadata_uri",
      "dictionary/qti-core.v1.json#qti_assessment_item.accessibility_catalog_id",
      "dictionary/qti-core.v1.json#qti_assessment_item.id",
      "dictionary/qti-core.v1.json#qti_assessment_item.identifier",
      "dictionary/qti-core.v1.json#qti_assessment_item.package_id",
      "dictionary/qti-core.v1.json#qti_assessment_item.source_href",
      "dictionary/qti-core.v1.json#qti_assessment_section.id",
      "dictionary/qti-core.v1.json#qti_assessment_section.identifier",
      "dictionary/qti-core.v1.json#qti_assessment_section.parent_section_id",
      "dictionary/qti-core.v1.json#qti_assessment_section.test_id",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.accessibility_catalog_id",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.id",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.identifier",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.package_id",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.source_href",
      "dictionary/qti-core.v1.json#qti_assessment_test.id",
      "dictionary/qti-core.v1.json#qti_assessment_test.identifier",
      "dictionary/qti-core.v1.json#qti_assessment_test.package_id",
      "dictionary/qti-core.v1.json#qti_assessment_test.source_href",
      "dictionary/qti-core.v1.json#qti_companion_material.id",
      "dictionary/qti-core.v1.json#qti_companion_material.item_id",
      "dictionary/qti-core.v1.json#qti_candidate.candidate_identifier",
      "dictionary/qti-core.v1.json#qti_candidate.id",
      "dictionary/qti-core.v1.json#qti_feedback.id",
      "dictionary/qti-core.v1.json#qti_feedback.owner_id",
      "dictionary/qti-core.v1.json#qti_interaction.id",
      "dictionary/qti-core.v1.json#qti_interaction.item_id",
      "dictionary/qti-core.v1.json#qti_item_ref.href",
      "dictionary/qti-core.v1.json#qti_item_ref.id",
      "dictionary/qti-core.v1.json#qti_item_ref.identifier",
      "dictionary/qti-core.v1.json#qti_item_ref.item_id",
      "dictionary/qti-core.v1.json#qti_item_ref.section_id",
      "dictionary/qti-core.v1.json#qti_package.id",
      "dictionary/qti-core.v1.json#qti_package.manifest_path",
      "dictionary/qti-core.v1.json#qti_package.original_file_uri",
      "dictionary/qti-core.v1.json#qti_package_artifact.href",
      "dictionary/qti-core.v1.json#qti_package_artifact.id",
      "dictionary/qti-core.v1.json#qti_package_artifact.package_id",
      "dictionary/qti-core.v1.json#qti_package_artifact.sha256",
      "dictionary/qti-core.v1.json#qti_package_artifact.storage_uri",
      "dictionary/qti-core.v1.json#qti_processing_rule.id",
      "dictionary/qti-core.v1.json#qti_processing_rule.owner_id",
      "dictionary/qti-core.v1.json#qti_test_part.id",
      "dictionary/qti-core.v1.json#qti_test_part.identifier",
      "dictionary/qti-core.v1.json#qti_test_part.item_session_control_id",
      "dictionary/qti-core.v1.json#qti_test_part.test_id",
      "dictionary/qti-core.v1.json#qti_variable_declaration.id",
      "dictionary/qti-core.v1.json#qti_variable_declaration.identifier",
      "dictionary/qti-core.v1.json#qti_variable_declaration.owner_id"
    ]
  },
  {
    "decision_id": "DEC-008-time-session",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_entity.date_created",
      "dictionary/caliper-core.v1.json#caliper_entity.date_modified",
      "dictionary/caliper-core.v1.json#caliper_envelope.received_at",
      "dictionary/caliper-core.v1.json#caliper_envelope.send_time",
      "dictionary/caliper-core.v1.json#caliper_event.event_time",
      "dictionary/case-core.v1.json#case_association.last_change_date_time",
      "dictionary/case-core.v1.json#case_association_grouping.last_change_date_time",
      "dictionary/case-core.v1.json#case_concept.last_change_date_time",
      "dictionary/case-core.v1.json#case_document.last_change_date_time",
      "dictionary/case-core.v1.json#case_item.last_change_date_time",
      "dictionary/case-core.v1.json#case_item_type.last_change_date_time",
      "dictionary/case-core.v1.json#case_license.last_change_date_time",
      "dictionary/case-core.v1.json#case_package.imported_at",
      "dictionary/case-core.v1.json#case_rubric.last_change_date_time",
      "dictionary/case-core.v1.json#case_rubric_criterion.last_change_date_time",
      "dictionary/case-core.v1.json#case_rubric_criterion_level.last_change_date_time",
      "dictionary/case-core.v1.json#case_subject.last_change_date_time",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.availability_start_at",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.submission_end_at",
      "dictionary/integration-governance-core.v1.json#lti_deployment.created_at",
      "dictionary/integration-governance-core.v1.json#lti_grade_exchange.timestamp",
      "dictionary/integration-governance-core.v1.json#lti_launch.launched_at",
      "dictionary/integration-governance-core.v1.json#lti_registration.created_at",
      "dictionary/integration-governance-core.v1.json#lti_registration.updated_at",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.occurred_at",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.effective_at",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.expires_at",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.reviewed_at",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.retention_period_days",
      "dictionary/oneroster-core.v1.json#academic_session.date_last_modified",
      "dictionary/oneroster-core.v1.json#academic_session.end_date",
      "dictionary/oneroster-core.v1.json#academic_session.school_year",
      "dictionary/oneroster-core.v1.json#academic_session.start_date",
      "dictionary/oneroster-core.v1.json#class.date_last_modified",
      "dictionary/oneroster-core.v1.json#course.date_last_modified",
      "dictionary/oneroster-core.v1.json#enrollment.begin_date",
      "dictionary/oneroster-core.v1.json#enrollment.date_last_modified",
      "dictionary/oneroster-core.v1.json#enrollment.end_date",
      "dictionary/oneroster-core.v1.json#line_item.assign_date",
      "dictionary/oneroster-core.v1.json#line_item.date_last_modified",
      "dictionary/oneroster-core.v1.json#line_item.due_date",
      "dictionary/oneroster-core.v1.json#organization.date_last_modified",
      "dictionary/oneroster-core.v1.json#person.date_last_modified",
      "dictionary/oneroster-core.v1.json#result.date_last_modified",
      "dictionary/oneroster-core.v1.json#result.score_date",
      "dictionary/qti-core.v1.json#qti_assessment_item.time_dependent",
      "dictionary/qti-core.v1.json#qti_assessment_section.visible_to_candidate",
      "dictionary/qti-core.v1.json#qti_assessment_test.time_limit_seconds",
      "dictionary/qti-core.v1.json#qti_item_ref.time_limit_seconds",
      "dictionary/qti-core.v1.json#qti_package.imported_at",
      "dictionary/qti-core.v1.json#qti_test_part.max_time_seconds"
    ]
  },
  {
    "decision_id": "DEC-009-content-resource",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_entity.description",
      "dictionary/caliper-core.v1.json#caliper_entity.entity_iri",
      "dictionary/caliper-core.v1.json#caliper_entity.entity_type",
      "dictionary/caliper-core.v1.json#caliper_entity.extensions",
      "dictionary/caliper-core.v1.json#caliper_entity.name",
      "dictionary/caliper-core.v1.json#caliper_entity.other_identifiers",
      "dictionary/caliper-core.v1.json#caliper_envelope.data_version",
      "dictionary/caliper-core.v1.json#caliper_envelope.event_count",
      "dictionary/caliper-core.v1.json#caliper_envelope.raw_payload",
      "dictionary/caliper-core.v1.json#caliper_event.action",
      "dictionary/caliper-core.v1.json#caliper_event.event_iri",
      "dictionary/caliper-core.v1.json#caliper_event.event_type",
      "dictionary/caliper-core.v1.json#caliper_event.profile",
      "dictionary/caliper-core.v1.json#caliper_event.raw_event",
      "dictionary/caliper-core.v1.json#caliper_extension.extension_key",
      "dictionary/caliper-core.v1.json#caliper_extension.extension_value",
      "dictionary/caliper-core.v1.json#caliper_extension.namespace",
      "dictionary/caliper-core.v1.json#caliper_extension.owner_type",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.allowed_action",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.event_type",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.generated_or_target_type",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.object_type",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.platform_guidance",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.profile",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.html",
      "dictionary/integration-governance-core.v1.json#lti_deep_link_item.title",
      "dictionary/integration-governance-core.v1.json#lti_launch.lti_version",
      "dictionary/integration-governance-core.v1.json#lti_launch.message_type",
      "dictionary/integration-governance-core.v1.json#lti_launch.raw_claims",
      "dictionary/oneroster-core.v1.json#source_identifier.identifier_type",
      "dictionary/oneroster-core.v1.json#source_identifier.object_type",
      "dictionary/qti-core.v1.json#qti_accessibility_support.catalog_idref",
      "dictionary/qti-core.v1.json#qti_accessibility_support.content_summary",
      "dictionary/qti-core.v1.json#qti_accessibility_support.owner_object_type",
      "dictionary/qti-core.v1.json#qti_accessibility_support.sensitive",
      "dictionary/qti-core.v1.json#qti_accessibility_support.support_type",
      "dictionary/qti-core.v1.json#qti_accessibility_support.tts_suppression",
      "dictionary/qti-core.v1.json#qti_assessment_item.adaptive",
      "dictionary/qti-core.v1.json#qti_assessment_item.authoring_tool_name",
      "dictionary/qti-core.v1.json#qti_assessment_item.authoring_tool_version",
      "dictionary/qti-core.v1.json#qti_assessment_item.item_body_summary",
      "dictionary/qti-core.v1.json#qti_assessment_item.label",
      "dictionary/qti-core.v1.json#qti_assessment_item.language",
      "dictionary/qti-core.v1.json#qti_assessment_item.primary_interaction_type",
      "dictionary/qti-core.v1.json#qti_assessment_item.title",
      "dictionary/qti-core.v1.json#qti_assessment_section.fixed_in_shuffle",
      "dictionary/qti-core.v1.json#qti_assessment_section.keep_together",
      "dictionary/qti-core.v1.json#qti_assessment_section.ordering_shuffle",
      "dictionary/qti-core.v1.json#qti_assessment_section.required_in_selection",
      "dictionary/qti-core.v1.json#qti_assessment_section.selection_count",
      "dictionary/qti-core.v1.json#qti_assessment_section.title",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.language",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.stimulus_body_summary",
      "dictionary/qti-core.v1.json#qti_assessment_stimulus.title",
      "dictionary/qti-core.v1.json#qti_assessment_test.authoring_tool_name",
      "dictionary/qti-core.v1.json#qti_assessment_test.authoring_tool_version",
      "dictionary/qti-core.v1.json#qti_assessment_test.title",
      "dictionary/qti-core.v1.json#qti_companion_material.calculator_type",
      "dictionary/qti-core.v1.json#qti_companion_material.material_type",
      "dictionary/qti-core.v1.json#qti_companion_material.material_uri",
      "dictionary/qti-core.v1.json#qti_companion_material.required_for_delivery",
      "dictionary/qti-core.v1.json#qti_companion_material.title",
      "dictionary/qti-core.v1.json#qti_interaction.expected_length",
      "dictionary/qti-core.v1.json#qti_interaction.interaction_type",
      "dictionary/qti-core.v1.json#qti_interaction.max_choices",
      "dictionary/qti-core.v1.json#qti_interaction.min_choices",
      "dictionary/qti-core.v1.json#qti_interaction.orientation",
      "dictionary/qti-core.v1.json#qti_interaction.prompt_summary",
      "dictionary/qti-core.v1.json#qti_interaction.response_identifier",
      "dictionary/qti-core.v1.json#qti_interaction.shape",
      "dictionary/qti-core.v1.json#qti_interaction.shuffle",
      "dictionary/qti-core.v1.json#qti_interaction.text_format",
      "dictionary/qti-core.v1.json#qti_item_ref.category",
      "dictionary/qti-core.v1.json#qti_item_ref.fixed_in_shuffle",
      "dictionary/qti-core.v1.json#qti_item_ref.required_in_selection",
      "dictionary/qti-core.v1.json#qti_package.package_identifier",
      "dictionary/qti-core.v1.json#qti_package.qti_version",
      "dictionary/qti-core.v1.json#qti_package.source_system",
      "dictionary/qti-core.v1.json#qti_package.validation_error_count",
      "dictionary/qti-core.v1.json#qti_package_artifact.artifact_role",
      "dictionary/qti-core.v1.json#qti_package_artifact.media_type",
      "dictionary/qti-core.v1.json#qti_test_part.navigation_mode",
      "dictionary/qti-core.v1.json#qti_test_part.submission_mode",
      "dictionary/qti-core.v1.json#qti_test_part.title",
      "dictionary/qti-core.v1.json#qti_variable_declaration.base_type",
      "dictionary/qti-core.v1.json#qti_variable_declaration.cardinality",
      "dictionary/qti-core.v1.json#qti_variable_declaration.declaration_kind",
      "dictionary/qti-core.v1.json#qti_variable_declaration.default_value_summary",
      "dictionary/qti-core.v1.json#qti_variable_declaration.owner_object_type",
      "dictionary/qti-core.v1.json#qti_variable_declaration.view"
    ]
  },
  {
    "decision_id": "DEC-010-tenancy-reference-data",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_envelope.validation_status",
      "dictionary/caliper-core.v1.json#caliper_extension.allowed_by_policy",
      "dictionary/integration-governance-core.v1.json#lti_launch.validation_status",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.event_type",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.object_type",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.outcome",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.privacy_class",
      "dictionary/integration-governance-core.v1.json#privacy_audit_event.reason",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.consent_status",
      "dictionary/integration-governance-core.v1.json#privacy_consent_record.source_method",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.data_category",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.field_patterns",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.legal_basis",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.minimization_note",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.privacy_class",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.purpose",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.recipient_type",
      "dictionary/integration-governance-core.v1.json#privacy_data_sharing_rule.status",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.action_on_expiry",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.data_category",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.legal_hold",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.raw_payload_policy",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.source_standard",
      "dictionary/integration-governance-core.v1.json#privacy_retention_rule.status",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.allowed_scopes",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.auth_method",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.client_name",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.grant_types",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.public_jwk",
      "dictionary/integration-governance-core.v1.json#security_oauth_client.status",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.allowed_action",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.api_resource",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.field_patterns",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.policy_status",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.privacy_ceiling",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.requires_launch_context",
      "dictionary/integration-governance-core.v1.json#security_scope_policy.scope",
      "dictionary/oneroster-core.v1.json#source_identifier.source_system",
      "dictionary/oneroster-core.v1.json#source_identifier.status",
      "dictionary/qti-core.v1.json#qti_package.validation_status"
    ]
  }
]
```
<!-- decision-trace:end -->
