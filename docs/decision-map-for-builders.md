# Decision Map For Builders

Use this page when a generated dictionary field or build guide step raises a "why is it modeled this way?" question. The full decision register remains the canonical source, but this map repeats each choice in builder language and names the work the choice removes.

## DEC-001 Identity: Person And Agent

- Decision link: [DEC-001 Person, User, Actor, Profile, and Subject](decisions-standards-overlap-decisions.html#DEC-001-person-agent-subject).
- Plain-language choice: Known school people use the canonical `person` model, while external actors, tool clients, issuers, and low-confidence subjects stay as broader agents until policy and identifiers justify linking them.
- Simplification produced: Apps do not need separate identity merge rules for roster users, Caliper actors, QTI candidates, and LTI subjects; they can follow canonical identity fields such as [person.email](oneroster-core-dictionary.html#person.email), [caliper_actor.email](caliper-core-dictionary.html#caliper_actor.email), [qti_candidate.email](qti-core-dictionary.html#qti_candidate.email), and [lti_launch.subject_id](integration-governance-core-dictionary.html#lti_launch.subject_id).

## DEC-002 Learning Contexts: Course, Class, And Context

- Decision link: [DEC-002 Class, Course, Context, Group, Course Section, and Organization](decisions-standards-overlap-decisions.html#DEC-002-learning-context).
- Plain-language choice: `course` is the catalog template, `class` is the scheduled teaching section, and broader launch or event contexts map to those records only when that is true.
- Simplification produced: Roster, gradebook, launch, and analytics code no longer guesses what a "context" means; class workflows join through explicit fields such as [class.course](oneroster-core-dictionary.html#class.course), [class.school](oneroster-core-dictionary.html#class.school), and [lti_launch.context_id](integration-governance-core-dictionary.html#lti_launch.context_id).

## DEC-003 Roles: Source Roles And Role Families

- Decision link: [DEC-003 Roles](decisions-standards-overlap-decisions.html#DEC-003-role-vocabulary).
- Plain-language choice: The platform stores source role values exactly and also maps them to a small shared role-family vocabulary for authorization and UI.
- Simplification produced: Each API does not need its own parser for OneRoster roles, LTI role URIs, Caliper evidence, or credential relationships; shared role fields such as [person.primary_role](oneroster-core-dictionary.html#person.primary_role), [enrollment.role](oneroster-core-dictionary.html#enrollment.role), and [lti_launch.roles](integration-governance-core-dictionary.html#lti_launch.roles) carry the common policy meaning.

## DEC-004 Participation: Enrollment And Membership

- Decision link: [DEC-004 Enrollment and Membership](decisions-standards-overlap-decisions.html#DEC-004-enrollment-membership).
- Plain-language choice: `enrollment` is the canonical roster relationship, while LTI membership and Caliper membership are service or event evidence unless explicitly derived from roster truth.
- Simplification produced: Gradebook and roster features do not choose between competing participation sources at runtime; they use canonical fields such as [enrollment.class](oneroster-core-dictionary.html#enrollment.class), [enrollment.user](oneroster-core-dictionary.html#enrollment.user), and [lti_membership.platform_person_id](integration-governance-core-dictionary.html#lti_membership.platform_person_id).

## DEC-005 Outcomes: Line Items And Results

- Decision link: [DEC-005 Results, Scores, Outcomes, and Grade Events](decisions-standards-overlap-decisions.html#DEC-005-results-scores).
- Plain-language choice: A `line_item` is the assignment or gradebook target, a `result` is the learner's current grade state, and scores, QTI outcomes, and Caliper grade events are inputs or history.
- Simplification produced: Dashboards do not rebuild current grades from command payloads or event streams; they read current gradebook fields such as [line_item.id](oneroster-core-dictionary.html#line_item.id), [result.line_item](oneroster-core-dictionary.html#result.line_item), [result.score](oneroster-core-dictionary.html#result.score), and [lti_grade_exchange.score_given](integration-governance-core-dictionary.html#lti_grade_exchange.score_given).

## DEC-006 Standards Alignment: CASE As Anchor

- Decision link: [DEC-006 Standards Alignment](decisions-standards-overlap-decisions.html#DEC-006-standards-alignment).
- Plain-language choice: CASE is the canonical standards graph, while source alignment labels and URLs are preserved when a known CASE target cannot be resolved.
- Simplification produced: Reporting and AI workflows do not reconcile QTI, cartridge, badge, CLR, and local alignment strings separately; cross-product alignment points at CASE fields such as [case_item.identifier](case-core-dictionary.html#case_item.identifier), [case_item.uri](case-core-dictionary.html#case_item.uri), [line_item.case_target_uri](oneroster-core-dictionary.html#line_item.case_target_uri), and [qti_alignment.target_identifier](qti-core-dictionary.html#qti_alignment.target_identifier).

## DEC-007 Identifiers: Stable IDs Plus Source Crosswalks

- Decision link: [DEC-007 Identifiers](decisions-standards-overlap-decisions.html#DEC-007-identifier-crosswalk).
- Plain-language choice: Internal records keep stable platform IDs, while source-native IDs are preserved in crosswalk fields and standard-shaped responses where required.
- Simplification produced: Each table no longer grows separate SIS, LTI, email, CASE URI, or vendor-ID columns for reconciliation; shared identifier fields such as [source_identifier.external_id](oneroster-core-dictionary.html#source_identifier.external_id), [person.sourced_id](oneroster-core-dictionary.html#person.sourced_id), and [caliper_event.event_iri](caliper-core-dictionary.html#caliper_event.event_iri) carry source identity.

## DEC-008 Time: Calendar Periods And Event Times

- Decision link: [DEC-008 Time, School Sessions, and Event Timestamps](decisions-standards-overlap-decisions.html#DEC-008-time-session).
- Plain-language choice: School calendar periods, event timestamps, availability windows, assessment timing, and credential validity are separate meanings instead of one generic timestamp bucket.
- Simplification produced: Features do not infer whether a date means term boundary, assignment due date, Caliper event time, QTI time limit, or credential validity; fields such as [academic_session.start_date](oneroster-core-dictionary.html#academic_session.start_date), [academic_session.end_date](oneroster-core-dictionary.html#academic_session.end_date), [line_item.due_date](oneroster-core-dictionary.html#line_item.due_date), and [caliper_event.event_time](caliper-core-dictionary.html#caliper_event.event_time) state the meaning directly.

## DEC-009 Resources: Broad Resource With Specific Projections

- Decision link: [DEC-009 Content, Resources, Packages, and Launch Links](decisions-standards-overlap-decisions.html#DEC-009-content-resource).
- Plain-language choice: Discovery can use a broad resource concept, while QTI packages, cartridge resources, LTI links, and Caliper entities keep their standard-specific details.
- Simplification produced: Search and catalog features do not maintain separate discovery indexes for each standard; they can share resource identity while preserving fields such as [qti_package.package_identifier](qti-core-dictionary.html#qti_package.package_identifier), [qti_assessment_item.identifier](qti-core-dictionary.html#qti_assessment_item.identifier), [lti_deep_link_item.url](integration-governance-core-dictionary.html#lti_deep_link_item.url), and [caliper_entity.entity_type](caliper-core-dictionary.html#caliper_entity.entity_type).

## DEC-010 Tenancy: Tenant Records And Shared References

- Decision link: [DEC-010 Tenant-Owned Data and Shared Reference Data](decisions-standards-overlap-decisions.html#DEC-010-tenancy-reference-data).
- Plain-language choice: Operational school records are tenant-owned and RLS-protected, while public reference data such as standards frameworks can live in governed shared namespaces.
- Simplification produced: App requests do not add their own `tenant_id` filters or send tenant IDs in request bodies; RLS and tenant-scoped rows protect records such as [organization.id](oneroster-core-dictionary.html#organization.id), while reference fields such as [case_document.uri](case-core-dictionary.html#case_document.uri) can be reused.

## DEC-011 Privacy Surfaces: One Gate By Privacy Class

- Decision link: [DEC-011 Privacy Surfaces](decisions-standards-overlap-decisions.html#DEC-011-privacy-surfaces).
- Plain-language choice: Generated docs may describe all fields, live APIs expose records through JWT and RLS, audited functions protect sensitive reads, and static mirrors contain only allowed synthetic demo data.
- Simplification produced: Builders do not reason from per-file exception lists; privacy class plus surface decides what can appear, with examples such as [person.email](oneroster-core-dictionary.html#person.email), [privacy_data_sharing_rule.privacy_class](integration-governance-core-dictionary.html#privacy_data_sharing_rule.privacy_class), and [privacy_audit_event.privacy_class](integration-governance-core-dictionary.html#privacy_audit_event.privacy_class).

## DEC-012 Runtime Coverage: Generated Accounting Versus Runtime

- Decision link: [DEC-012 Runtime Coverage Per Spec](decisions-standards-overlap-decisions.html#DEC-012-runtime-coverage-per-spec).
- Plain-language choice: OneRoster core is runtime-backed, the buildability guide has narrow CASE and Caliper runtime paths, and other Lead specs are generated, partial, or deferred as documented.
- Simplification produced: Generated dictionary pages do not pretend every spec is already a deployed API; builders can distinguish runtime-backed fields such as [line_item.case_target_uri](oneroster-core-dictionary.html#line_item.case_target_uri) and [caliper_event.action](caliper-core-dictionary.html#caliper_event.action) from doc-only projections.

## DEC-013 Audit Truth: Read Back What Was Logged

- Decision link: [DEC-013 Audit Response Truth](decisions-standards-overlap-decisions.html#DEC-013-audit-response-truth).
- Plain-language choice: An audited Edge Function may claim audit metadata only after it can read back the matching `audit_log` rows under the caller request.
- Simplification produced: Tests and clients do not trust hard-coded audit counts; sensitive reads prove audit evidence through the runtime and fields such as [privacy_audit_event.object_id](integration-governance-core-dictionary.html#privacy_audit_event.object_id), [privacy_audit_event.outcome](integration-governance-core-dictionary.html#privacy_audit_event.outcome), and [privacy_audit_event.reason](integration-governance-core-dictionary.html#privacy_audit_event.reason).

## DEC-014 Static Mirrors: Fixtures, Not Runtime Contract

- Decision link: [DEC-014 Static Mirror Policy](decisions-standards-overlap-decisions.html#DEC-014-static-mirror-policy).
- Plain-language choice: `site/api/*.json` files are generated documentation fixtures for GitHub Pages and offline review, while live Supabase REST and Edge Functions are the runtime contract.
- Simplification produced: Reviewers can inspect example JSON without running a backend, but apps do not treat static files as production responses; generated API metadata points back to runtime fields such as [person.id](oneroster-core-dictionary.html#person.id), [class.id](oneroster-core-dictionary.html#class.id), and [result.score](oneroster-core-dictionary.html#result.score).

## DEC-015 Service Role: Allowlisted Bootstrap Only

- Decision link: [DEC-015 Service-Role Policy](decisions-standards-overlap-decisions.html#DEC-015-service-role-policy).
- Plain-language choice: Runtime request code passes the caller's JWT so RLS applies, and service-role credentials are allowed only for named admin or test fixture setup operations.
- Simplification produced: Builders do not audit every Edge Function for hidden RLS bypasses; after bootstrap, app requests use user-JWT access to tenant rows such as [enrollment.id](oneroster-core-dictionary.html#enrollment.id), [result.id](oneroster-core-dictionary.html#result.id), and [caliper_event.id](caliper-core-dictionary.html#caliper_event.id).

## DEC-016 Dictionary Direction: Shared Seed Generates Projections

- Decision link: [DEC-016 Dictionary Generation Direction](decisions-standards-overlap-decisions.html#DEC-016-dictionary-generation-direction).
- Plain-language choice: `data/data-dictionary.seed.json` is upstream, and per-spec `dictionary/*.v1.json` files are generated projections.
- Simplification produced: Developers do not reconcile five hand-edited dictionaries; generated pages such as [OneRoster core](oneroster-core-dictionary.html), [CASE core](case-core-dictionary.html), [Caliper core](caliper-core-dictionary.html), [QTI core](qti-core-dictionary.html), and [integration governance](integration-governance-core-dictionary.html) all trace back to the same seed.

## DEC-017 Field Reconciliation: Canonical Field IDs

- Decision link: [DEC-017 Canonical Field Reconciliation](decisions-standards-overlap-decisions.html#DEC-017-canonical-field-reconciliation).
- Plain-language choice: Spec-native names stay intact for conformance, but overlapping fields carry `canonical_field_id` so apps can recognize the same meaning across standards.
- Simplification produced: Docs, adapters, and APIs do not carry field-name conversion tables for common meanings; overlap examples such as [person.email](oneroster-core-dictionary.html#person.email), [lti_membership.email](integration-governance-core-dictionary.html#lti_membership.email), [caliper_actor.email](caliper-core-dictionary.html#caliper_actor.email), and [qti_candidate.email](qti-core-dictionary.html#qti_candidate.email) point to the same canonical concept.

## DEC-018 Enums: Shared Vocabularies With Crosswalks

- Decision link: [DEC-018 Global Enum Crosswalks](decisions-standards-overlap-decisions.html#DEC-018-global-enum-crosswalks).
- Plain-language choice: Allowed values are shared enum objects with bidirectional mappings between canonical values and spec-native values.
- Simplification produced: Each API does not duplicate enum docs or parse role/status vocabularies alone; enum-bearing fields such as [person.primary_role](oneroster-core-dictionary.html#person.primary_role), [enrollment.role](oneroster-core-dictionary.html#enrollment.role), [lti_launch.roles](integration-governance-core-dictionary.html#lti_launch.roles), and [result.score_status](oneroster-core-dictionary.html#result.score_status) use shared vocabulary references.

## DEC-019 Privacy Classes: Closed List

- Decision link: [DEC-019 Closed Privacy Classes](decisions-standards-overlap-decisions.html#DEC-019-closed-privacy-classes).
- Plain-language choice: Privacy classes are a closed list, and every field occurrence receives a concrete class instead of `depends_on_entity` or `depends_on_contents`.
- Simplification produced: Generators and surface gates do not branch on open-ended placeholders; privacy-bearing fields such as [caliper_entity.name](caliper-core-dictionary.html#caliper_entity.name), [caliper_entity.extensions](caliper-core-dictionary.html#caliper_entity.extensions), and [privacy_data_sharing_rule.privacy_class](integration-governance-core-dictionary.html#privacy_data_sharing_rule.privacy_class) carry concrete classes.

## DEC-020 Relationships: Dictionary Graph Generates Migrations

- Decision link: [DEC-020 Relational Graph Migrations](decisions-standards-overlap-decisions.html#DEC-020-relational-graph-migrations).
- Plain-language choice: Dictionary objects own foreign-key targets, cardinalities, ownership, and delete behavior, and Supabase migrations are generated from that graph.
- Simplification produced: SQL, docs, examples, and dictionary prose no longer each carry their own FK truth; relationships behind fields such as [class.course](oneroster-core-dictionary.html#class.course), [enrollment.user](oneroster-core-dictionary.html#enrollment.user), [result.line_item](oneroster-core-dictionary.html#result.line_item), and [result.student](oneroster-core-dictionary.html#result.student) come from one graph.
