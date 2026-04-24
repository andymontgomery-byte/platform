# Standards Overlap Decisions

Research date: 2026-04-24

This record captures places where 1EdTech standards describe the same real-world idea differently. Each decision names the involved specs, the ambiguity, the platform choice, how that choice maps back to each spec, and the tradeoff.

## 1. Person, User, Actor, Profile, and Subject

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

Specs involved: all tenant data specs, especially OneRoster, LTI, CASE, QTI, Common Cartridge.

Conflict: schools own roster, grades, launches, and private content; many standards frameworks and public content references should be shared.

Choice: tenant-owned operational records carry tenant boundaries and row-level policy. Public CASE frameworks, public standards metadata, public certification fixtures, and optionally public item banks live in shared reference namespaces. Tenants adopt, pin, override, or privately extend shared reference data through explicit records.

Tradeoff: one integration can serve many schools, while privacy and local control remain enforceable.
