# Standards Overlap Decisions

Research date: 2026-04-24

This record captures places where 1EdTech standards describe the same real-world idea differently. Each decision names the involved specs, the ambiguity, the platform choice, how that choice maps back to each spec, and the tradeoff.

## 1. Person, User, Actor, Profile, and Subject

Decision ID: `DEC-001-person-agent-subject`

Specs involved: OneRoster User, Caliper Person/Actor, LTI launch user claims, Open Badges Profile, CLR Subject.

Conflict: each standard identifies a person in a different context. OneRoster centers school roster users. LTI uses launch-time OIDC claims and roles. Caliper uses an actor that may be a person, software agent, or group. Open Badges and CLR use profile/subject objects for credentials, where the subject may be privacy-preserving or externally controlled.

Choice: the platform has a canonical `person` for known school people and a broader `agent` concept for non-person actors. Credential subjects and Caliper actors resolve to `person` only when policy and identifiers allow it; otherwise they remain linked external agents.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster User | Maps to `person` plus source identifiers and role/enrollment records. |
| LTI launch info | Maps launch `sub`, names, email, roles, and deployment context to a `person` when trusted crosswalks exist. |
| Caliper Person/Actor | Maps to `person` when the actor is a known school user; otherwise remains an event actor. |
| Open Badges Profile | Maps to issuer, creator, or recipient profile; recipient profiles do not automatically become platform people. |
| CLR Subject | Maps to credential subject first, and to `person` only when learner-controlled or institution-authorized linking exists. |

Tradeoff: this avoids merging credential or analytics identities into school records too aggressively, but every API must expose identity confidence and source lineage.

## 2. Class, Course, Context, Group, Course Section, and Organization

Decision ID: `DEC-002-learning-context`

Specs involved: OneRoster Course and Class, LTI Context, Caliper Group/CourseSection, Common Cartridge organization.

Conflict: a "class" can mean a course template, a scheduled section, a launch context, a group in an event, or a content-outline organization.

Choice: the platform separates `course` from `class`. `course` is the catalog/template. `class` is the scheduled teaching section. LTI contexts and Caliper groups can map to a class, course, or other learning context. Common Cartridge organizations are content outlines, not school organizations or scheduled classes.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster Course | Maps to `course`. |
| OneRoster Class | Maps to `class`. |
| LTI Context | Maps to `learning_context`, normally crosswalked to `class` for K-12 course launches. |
| Caliper CourseSection | Maps to `class` when it describes a scheduled section. |
| Caliper Group | Maps to `learning_context` or group membership, not always a class. |
| Common Cartridge organization | Maps to cartridge outline/navigation, not to school organization. |

Tradeoff: app developers get clearer joins, but importers must preserve source-specific context IDs and cannot assume every context is a class.

## 3. Roles

Decision ID: `DEC-003-role-vocabulary`

Specs involved: OneRoster roles, LTI roles, Caliper actor roles, Open Badges/CLR profile roles.

Conflict: roles are named differently and have different scopes. OneRoster roles often describe school or class roles. LTI roles are URI-based and context-specific. Caliper may include LIS roles. Credential profiles can describe issuer/creator/subject relationships rather than classroom roles.

Choice: store source roles exactly, then map them to a small platform role family for authorization and UI: learner, educator, administrator, guardian, mentor, staff, tool, issuer, unknown.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster `student` | Platform `learner`. |
| OneRoster `teacher` | Platform `educator`. |
| LTI `Learner` | Platform `learner` in the launch context. |
| LTI `Instructor` or `TeachingAssistant` | Platform `educator` in the launch context. |
| Caliper LIS role values | Stored as event role evidence and mapped when known. |
| Open Badges/CLR issuer/creator | Platform `issuer` or organization profile, not classroom teacher by default. |

Tradeoff: preserving source roles supports conformance and debugging; platform role families keep policy manageable.

## 4. Enrollment and Membership

Decision ID: `DEC-004-enrollment-membership`

Specs involved: OneRoster Enrollment, LTI NRPS Membership, Caliper Membership.

Conflict: OneRoster enrollments are roster records. LTI NRPS memberships are launch/service views of who belongs to a context. Caliper Membership describes relationship state in an event model.

Choice: `enrollment` is the canonical roster participation record. `membership` is a contextual service/event view that may be derived from enrollment or captured from an external system.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster Enrollment | Canonical `enrollment`. |
| LTI NRPS membership | Read model over class/context membership; crosswalked to enrollment when possible. |
| Caliper Membership | Event/entity evidence about a person or agent belonging to a group/context. |

Tradeoff: this keeps roster truth separate from launch-time and event-time snapshots, but membership APIs must explain whether they return canonical roster state or observed service state.

## 5. Results, Scores, Outcomes, and Grade Events

Decision ID: `DEC-005-results-scores`

Specs involved: OneRoster gradebook Result, LTI AGS Score and Result, QTI outcome variables/results, Caliper GradeEvent.

Conflict: "result" can mean a gradebook record, a tool-submitted score update, an assessment outcome variable, or an event showing grading activity.

Choice: the platform uses `line_item` as the gradebook target and `result` as the learner's current gradebook state. LTI AGS Score is an incoming write/update message. LTI AGS Result and OneRoster Result map to current result state. QTI outcomes are assessment-runtime variables projected into results only when a delivery or scoring workflow declares that mapping. Caliper GradeEvent is event history, not the gradebook source of truth.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster LineItem | `line_item`. |
| OneRoster Result | `result`. |
| LTI AGS Score | Score update command/event that may create or update `result`. |
| LTI AGS Result | API view of `result`. |
| QTI outcome declaration/result | Assessment outcome variable, mapped to result only through scoring metadata. |
| Caliper GradeEvent | Immutable grading activity event linked to line item/result when possible. |

Tradeoff: gradebook state is easy to query, while event and assessment provenance remains available for audit and analytics.

## 6. Standards Alignment

Decision ID: `DEC-006-standards-alignment`

Specs involved: CASE items and associations, QTI item metadata, Common Cartridge resource metadata, Open Badges achievement alignment, CLR achievement/result alignment.

Conflict: content, assessments, credentials, and results all describe standards alignment differently.

Choice: CASE is the canonical standards graph. Other standards store alignment as source metadata and resolve known targets to CASE item identifiers or URIs.

Mappings:

| Spec | Mapping |
| --- | --- |
| CASE CFItem/association | Canonical standards and competency graph. |
| QTI metadata alignment | Assessment/item alignment to CASE where target is known. |
| Common Cartridge metadata | Resource alignment to CASE URI/GUID where present. |
| Open Badges alignment | Achievement alignment target, resolved to CASE when possible. |
| CLR alignment | Achievement/result alignment, resolved to CASE when possible. |

Tradeoff: CASE-first alignment enables cross-product reporting and AI reasoning, but importers must keep original alignment labels/URLs when they cannot be resolved.

## 7. Identifiers

Decision ID: `DEC-007-identifier-crosswalk`

Specs involved: OneRoster sourcedId, CASE GUID, LTI `sub` and `deployment_id`, Caliper IRIs, Open Badges IRIs, CLR credential IDs, internal UUIDs.

Conflict: each standard has its own identity and persistence rules.

Choice: internal records have platform IDs. Standard-shaped endpoints expose the standard-native ID as the primary contract when required. Every external ID is stored in a source identifier crosswalk with source system, identifier type, and object relationship.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster `sourcedId` | Primary ID on OneRoster-shaped endpoints; crosswalked internally. |
| CASE GUID/URI | Canonical ID for CASE items and associations. |
| LTI `sub` | Launch-scoped user ID, crosswalked to person only within issuer/deployment trust boundaries. |
| LTI `deployment_id` | Tool deployment identifier and security boundary. |
| Caliper IRI | Event/entity ID retained as event lineage. |
| Open Badges/CLR IDs | Credential/profile/achievement IDs retained as credential source IDs. |

Tradeoff: this is more complex than one ID per object, but it avoids breaking conformance and supports troubleshooting across systems.

## 8. Time, School Sessions, and Event Timestamps

Decision ID: `DEC-008-time-session`

Specs involved: OneRoster AcademicSession, LTI context/term hints, Caliper timestamps/timezones, QTI assessment timing, credential validFrom/validUntil dates.

Conflict: time can mean school calendar, launch context, event time, assessment time limit, submission time, or credential validity.

Choice: separate calendar periods, event timestamps, availability windows, and validity periods. Store timestamps in UTC with source timezone/offset when provided. Store OneRoster AcademicSession as the school calendar backbone.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster AcademicSession | Calendar period and school-year backbone. |
| LTI context/line item dates | Availability, due, or launch-context dates. |
| Caliper event time | Immutable event timestamp. |
| QTI time limits/session timing | Assessment runtime timing metadata. |
| Open Badges/CLR validFrom/validUntil | Credential validity period. |

Tradeoff: date queries are more explicit, but developers do not confuse school terms with event timestamps or credential expiration.

## 9. Content, Resources, Packages, and Launch Links

Decision ID: `DEC-009-content-resource`

Specs involved: OneRoster Resource, Common Cartridge resources/items, QTI packages/items/tests, LTI ResourceLink, Caliper DigitalResource.

Conflict: "resource" can mean a roster-linked resource, a content package file, an assessment package, a launchable tool link, or an event target.

Choice: the platform uses a broad `resource` concept for discoverable learning objects, with subtype-specific records for cartridge resources, QTI packages/items/tests, LTI resource links, and Caliper event entities.

Mappings:

| Spec | Mapping |
| --- | --- |
| OneRoster Resource | Roster-associated learning resource metadata. |
| Common Cartridge resource/item | Package manifest resource and outline item. |
| QTI package/item/test | Assessment content subtype and package artifact. |
| LTI ResourceLink | Launchable external tool/activity resource. |
| Caliper DigitalResource | Event target/entity describing content used. |

Tradeoff: search and catalog workflows get one resource layer, while standards-specific package/launch/assessment details remain intact.

## 10. Tenant-Owned Data and Shared Reference Data

Decision ID: `DEC-010-tenancy-reference-data`

Specs involved: all tenant data specs, especially OneRoster, LTI, CASE, QTI, Common Cartridge.

Conflict: schools own roster, grades, launches, and private content; many standards frameworks and public content references should be shared.

Choice: tenant-owned operational records carry tenant boundaries and row-level policy. Public CASE frameworks, public standards metadata, public certification fixtures, and optionally public item banks live in shared reference namespaces. Tenants adopt, pin, override, or privately extend shared reference data through explicit records.

Tradeoff: one integration can serve many schools, while privacy and local control remain enforceable.
## Machine-Readable Decision Trace

Field references use `dictionary/<file>#<object_key>.<field_key>`. Each `decision_id` also appears on the corresponding dictionary field object and in generated OpenAPI/Markdown/HTML dictionary artifacts.

<!-- decision-trace:start -->
```json
[
  {
    "decision_id": "DEC-001-person-agent-subject",
    "produces_fields": [
      "dictionary/caliper-core.v1.json#caliper_actor.actor_type",
      "dictionary/caliper-core.v1.json#caliper_actor.display_name",
      "dictionary/caliper-core.v1.json#caliper_actor.identifier_type",
      "dictionary/caliper-core.v1.json#caliper_actor.identifier_value",
      "dictionary/caliper-core.v1.json#caliper_actor.resolution_status",
      "dictionary/caliper-core.v1.json#caliper_profile_rule.actor_type",
      "dictionary/oneroster-core.v1.json#person.display_name",
      "dictionary/oneroster-core.v1.json#person.email",
      "dictionary/oneroster-core.v1.json#person.enabled_user",
      "dictionary/oneroster-core.v1.json#person.family_name",
      "dictionary/oneroster-core.v1.json#person.given_name",
      "dictionary/oneroster-core.v1.json#person.status"
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
