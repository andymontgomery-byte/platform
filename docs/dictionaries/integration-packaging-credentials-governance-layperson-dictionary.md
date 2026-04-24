# Integration, Packaging, Credentials, and Governance Layperson Data Dictionary

Research date: 2026-04-24

This companion dictionary covers the platform objects that connect the core education model to external tools, content packages, digital credentials, security, and privacy governance.

The platform rule is simple:

- Store the original standards payload exactly enough to re-export or audit it.
- Project the fields below into normal tables, views, and API resources only when the platform needs to search, join, govern, or explain them.
- Use plain field names internally, but retain the standards-native claim, XML element, JSON-LD property, or vocabulary value in mapping metadata.

## Sources

- LTI overview: https://www.1edtech.org/standards/lti
- LTI Core 1.3: https://www.imsglobal.org/spec/lti/v1p3/
- LTI Assignment and Grade Services 2.0: https://www.imsglobal.org/spec/lti-ags/v2p0/
- LTI Names and Role Provisioning Services 2.0: https://www.imsglobal.org/spec/lti-nrps/v2p0/
- LTI Deep Linking 2.0: https://www.imsglobal.org/spec/lti-dl/v2p0/
- Common Cartridge overview: https://www.1edtech.org/standards/cc
- Common Cartridge specification index: https://www.imsglobal.org/cc/index.html
- Open Badges 3.0: https://www.imsglobal.org/spec/ob/v3p0
- CLR 2.0: https://www.imsglobal.org/spec/clr/v2p0
- 1EdTech Security Framework 1.1: https://www.imsglobal.org/spec/security/v1p1/
- Data Privacy: https://www.1edtech.org/standards/data-privacy

## Privacy Classes Used Here

| Class | Layperson meaning |
| --- | --- |
| `public` | Safe to publish without exposing a private learner record. |
| `directory` | Name, email, picture, role, or organization information that schools often share but still control. |
| `education_record` | Enrollment, grade, progress, submission, achievement, or transcript data about a learner. |
| `sensitive` | Data needing extra care, including security data, private identifiers, demographics, accommodations, or proof material. |
| `credential` | Verifiable achievement, badge, endorsement, or learner-record data. |
| `behavioral` | Activity or usage data created by using a tool or resource. |
| `operational` | Import/export, package, launch, validation, or processing data. |
| `system` | Platform configuration, keys, tokens, scopes, secrets metadata, or infrastructure data. |

## LTI 1.3 and LTI Advantage

LTI is the launch and service layer. It lets a school platform open an outside learning tool, tell the tool who the user is, what course or activity they came from, what role they have, and which services the tool may call.

### LTI Object Map

| Platform object | What it means to a layperson | Privacy class |
| --- | --- | --- |
| `lti_platform` | The system that launches tools, usually an LMS or this platform. | System |
| `lti_tool` | The outside app or service being launched. | System |
| `lti_registration` | The security agreement between a platform and tool. | System |
| `lti_deployment` | A particular installation of a tool for a district, school, course, or tenant. | System |
| `lti_resource_link` | The clickable tool link placed in a course or activity. | Operational |
| `lti_launch` | One launch event from the platform to a tool. | Behavioral |
| `lti_launch_user` | The user identity and role information included with a launch. | Directory or education_record |
| `lti_context` | The course, section, group, or other learning space where the launch happened. | Education_record |
| `lti_launch_presentation` | Display preferences, such as opening in a window, tab, or embedded frame. | Operational |
| `lti_custom_parameters` | School or placement-specific key-value settings sent to the tool. | Depends on value |
| `lti_nrps_service` | A service endpoint where a tool can ask for course membership. | System |
| `lti_membership_container` | The roster response returned by NRPS. | Education_record |
| `lti_member` | One person in the NRPS roster response. | Education_record |
| `lti_ags_service` | A service endpoint where a tool can read or write gradebook line items, scores, and results. | System |
| `lti_line_item` | A gradebook column managed or used by a tool. | Education_record |
| `lti_score` | A score update sent by a tool. | Education_record |
| `lti_result` | A gradebook result returned to a tool. | Education_record |
| `lti_deep_linking_request` | A launch where an instructor is choosing content from a tool. | Operational |
| `lti_deep_linking_response` | The content selection response returned by a tool. | Operational |
| `lti_deep_link_item` | One selected content item, such as a link, file, HTML snippet, or tool activity. | Operational |
| `lti_media_descriptor` | Icon, thumbnail, iframe, window, or embed display settings for a deep-linked item. | Operational |

### LTI Platform, Tool, Registration, and Deployment Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `platform_id` | `lti_platform` | Yes | System | Internal ID for the launching platform record. |
| `issuer` | `lti_platform`, launch JWT `iss` | Yes | System | The stable web identifier for the platform that signed the launch. |
| `platform_name` | `lti_platform` | Optional | Operational | Human-readable platform name. |
| `client_id` | `lti_registration` | Yes | System | OAuth client ID assigned to the tool by the platform. |
| `tool_id` | `lti_tool` | Yes | System | Internal ID for the external tool. |
| `tool_name` | `lti_tool` | Yes | Operational | Name shown to administrators or instructors. |
| `initiate_login_uri` | `lti_tool` | Yes | System | Tool URL where the platform starts the LTI login flow. |
| `redirect_uris` | `lti_registration` | Yes | System | Allowed tool URLs that can receive launch responses. |
| `jwks_uri` | `lti_platform`, `lti_tool` | Required for key-set based verification | System | URL where public signing keys can be fetched. |
| `public_jwk` | `lti_platform`, `lti_tool` | Optional | System | A public key object used to verify signatures. |
| `token_endpoint` | `lti_platform` | Required for services | System | URL where the tool asks for an access token. |
| `authorization_endpoint` | `lti_platform` | Required for launches | System | URL used during OpenID Connect authentication. |
| `deployment_id` | `lti_deployment`, launch claim | Yes | System | Immutable ID for one installation of a tool. |
| `deployment_scope` | `lti_deployment` | Recommended | Operational | Where the tool is available, such as district, school, course, or account. |
| `enabled` | `lti_registration`, `lti_deployment` | Yes | Operational | Whether this integration can currently be used. |
| `allowed_scopes` | `lti_registration`, `lti_deployment` | Required for services | System | Service permissions the tool may request. |
| `created_at` | all configuration objects | Yes | Operational | When the record was created. |
| `updated_at` | all configuration objects | Yes | Operational | When the record was last changed. |

### LTI Launch Fields

| Field | Standards-native claim | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `launch_id` | local | Yes | Behavioral | Internal ID for one launch attempt. |
| `id_token_hash` | local | Recommended | Sensitive | Fingerprint of the signed launch token for audit without storing a raw token everywhere. |
| `iss` | `iss` | Yes | System | Platform issuer that sent the launch. |
| `sub` | `sub` | Usually yes unless anonymous | Education_record | User ID from the platform. |
| `aud` | `aud` | Yes | System | Intended receiver, usually the tool client ID. |
| `azp` | `azp` | Sometimes | System | Authorized party when there are multiple audiences. |
| `exp` | `exp` | Yes | System | Expiration time of the launch token. |
| `iat` | `iat` | Yes | System | Time the launch token was issued. |
| `nonce` | `nonce` | Yes | Sensitive | One-time value used to prevent replay attacks. |
| `message_type` | LTI message type claim | Yes | Operational | What kind of LTI workflow this launch represents. |
| `version` | LTI version claim | Yes | Operational | LTI version, normally `1.3.0`. |
| `deployment_id` | LTI deployment claim | Yes | System | Tool installation that governs this launch. |
| `target_link_uri` | LTI target link URI claim | Yes | System | Final tool URL that should receive the launch. |
| `resource_link_id` | `resource_link.id` | Required for resource link launch | Operational | Platform ID for the course activity link. |
| `resource_link_title` | `resource_link.title` | Optional | Operational | Title of the tool activity link. |
| `resource_link_description` | `resource_link.description` | Optional | Operational | Description of the linked tool activity. |
| `context_id` | `context.id` | Recommended | Education_record | Course, section, or group ID. |
| `context_type` | `context.type` | Optional | Education_record | Kind of learning space. |
| `context_label` | `context.label` | Optional | Education_record | Short course or section label. |
| `context_title` | `context.title` | Optional | Education_record | Full course or section name. |
| `roles` | `roles` | Recommended | Education_record | User roles in this launch context. |
| `role_scope_mentor` | `role_scope_mentor` | Optional | Sensitive | Learners this user may view as a mentor, parent, or advisor. |
| `given_name` | OIDC user claim | Optional | Directory | User first name. |
| `family_name` | OIDC user claim | Optional | Directory | User last name. |
| `name` | OIDC user claim | Optional | Directory | User display name. |
| `email` | OIDC user claim | Optional | Directory | User email address. |
| `picture` | OIDC user claim | Optional | Directory | User profile image URL. |
| `launch_presentation` | LTI launch presentation claim | Optional | Operational | Display hints for how the tool should appear. |
| `lis` | LTI LIS claim | Optional | Education_record | Legacy or SIS-linked course and person identifiers. |
| `custom` | LTI custom claim | Optional | Depends on value | Extra key-value settings for this tool placement. |
| `tool_platform` | LTI tool platform claim | Optional | Operational | Information about the platform software. |
| `nrps` | NRPS claim | Optional | System | Membership service URL and supported versions. |
| `ags` | AGS claim | Optional | System | Grade service URLs and scopes. |
| `deep_linking_settings` | Deep Linking claim | Required for deep linking | Operational | Rules for what content the tool may return. |
| `raw_claims` | local | Yes | Sensitive | Full launch claims retained for audit and standards troubleshooting. |

### LTI Launch Presentation Fields

| Field | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- |
| `document_target` | Optional | Operational | Whether the tool should open in a frame, window, or other target. |
| `height` | Optional | Operational | Suggested display height. |
| `width` | Optional | Operational | Suggested display width. |
| `return_url` | Optional | System | URL where the tool can send the user back. |
| `locale` | Optional | Operational | Language or locale hint. |
| `css_url` | Optional | Operational | Optional stylesheet URL for matching platform presentation. |

### LTI NRPS Membership Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `context_memberships_url` | `lti_nrps_service` | Yes when NRPS is offered | System | API URL where a tool can ask for roster membership. |
| `service_versions` | `lti_nrps_service` | Yes | Operational | Supported NRPS versions, usually `2.0`. |
| `membership_id` | `lti_membership_container` | Yes | Education_record | ID or URL for one membership response. |
| `context_id` | `lti_membership_container` | Yes | Education_record | Course, section, or group represented by the roster. |
| `context_label` | `lti_membership_container` | Optional | Education_record | Short context label. |
| `context_title` | `lti_membership_container` | Optional | Education_record | Full context title. |
| `members` | `lti_membership_container` | Yes | Education_record | People in the returned roster. |
| `status` | `lti_member` | Optional | Education_record | Whether the membership is active or inactive. |
| `name` | `lti_member` | Optional | Directory | Member display name. |
| `picture` | `lti_member` | Optional | Directory | Member picture URL. |
| `given_name` | `lti_member` | Optional | Directory | Member first name. |
| `family_name` | `lti_member` | Optional | Directory | Member last name. |
| `middle_name` | `lti_member` | Optional | Directory | Member middle name. |
| `email` | `lti_member` | Optional | Directory | Member email. |
| `user_id` | `lti_member` | Yes | Education_record | LTI user ID for the member. |
| `lis_person_sourcedid` | `lti_member` | Optional | Education_record | SIS or LIS person identifier. |
| `lti11_legacy_user_id` | `lti_member` | Optional | Education_record | Older LTI user identifier for migration. |
| `roles` | `lti_member` | Optional | Education_record | Roles this member has in the context. |
| `message` | `lti_member` | Optional | Sensitive | Per-member launch data that would be sent for a resource link. |

### LTI AGS Line Item, Score, and Result Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `lineitems_url` | `lti_ags_service` | Optional | System | API URL for all gradebook columns available to the tool. |
| `lineitem_url` | `lti_ags_service` | Optional | System | API URL for one gradebook column tied to this launch. |
| `scope` | `lti_ags_service` | Yes | System | Grade service permissions available to the tool. |
| `id` | `lti_line_item` | Required when returned | Education_record | URL or ID for one gradebook column. |
| `scoreMaximum` | `lti_line_item` | Yes | Education_record | Maximum possible score for the column. |
| `label` | `lti_line_item` | Yes | Education_record | Human-readable gradebook column name. |
| `resourceId` | `lti_line_item` | Optional | Operational | Tool's stable ID for the resource or activity. |
| `tag` | `lti_line_item` | Optional | Operational | Tool's category label for the line item. |
| `resourceLinkId` | `lti_line_item` | Optional | Operational | LTI resource link this gradebook column is attached to. |
| `startDateTime` | `lti_line_item` | Optional | Education_record | When the activity starts. |
| `endDateTime` | `lti_line_item` | Optional | Education_record | When the activity ends or is due. |
| `gradesReleased` | `lti_line_item` | Optional | Education_record | Whether grades are visible to learners. |
| `timestamp` | `lti_score` | Yes | Education_record | Time the tool created the score update. |
| `scoreGiven` | `lti_score` | Optional | Education_record | Points or score earned. |
| `scoreMaximum` | `lti_score` | Required when scoreGiven is present | Education_record | Denominator for the score being sent. |
| `comment` | `lti_score`, `lti_result` | Optional | Education_record | Teacher or tool feedback. |
| `activityProgress` | `lti_score` | Yes | Education_record | Learner progress through the activity. |
| `gradingProgress` | `lti_score` | Yes | Education_record | Grading state of the work. |
| `userId` | `lti_score`, `lti_result` | Yes | Education_record | Learner who receives the score or result. |
| `scoringUserId` | `lti_score`, `lti_result` | Optional | Education_record | Person who assigned the score. |
| `submission.startedAt` | `lti_score` | Optional | Behavioral | When the learner started the submitted activity. |
| `submission.submittedAt` | `lti_score` | Optional | Behavioral | When the learner submitted the activity. |
| `scoreOf` | `lti_result` | Yes | Education_record | Line item this result belongs to. |
| `resultScore` | `lti_result` | Optional | Education_record | Score currently stored by the platform. |
| `resultMaximum` | `lti_result` | Optional | Education_record | Maximum score used by the platform result. |

### LTI Deep Linking Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `deep_link_return_url` | `lti_deep_linking_request` | Yes | System | Platform URL where selected content should be returned. |
| `accept_types` | `lti_deep_linking_request` | Yes | Operational | Types of content the platform will accept. |
| `accept_presentation_document_targets` | `lti_deep_linking_request` | Yes | Operational | Display modes the platform supports. |
| `accept_media_types` | `lti_deep_linking_request` | Optional | Operational | File media types the platform will accept. |
| `accept_multiple` | `lti_deep_linking_request` | Optional | Operational | Whether the tool can return more than one item. |
| `auto_create` | `lti_deep_linking_request` | Optional | Operational | Whether the platform can create the returned items automatically. |
| `title` | `lti_deep_linking_request` | Optional | Operational | Suggested title for the selection workflow. |
| `text` | `lti_deep_linking_request` | Optional | Operational | Suggested text or instructions for the selection workflow. |
| `data` | `lti_deep_linking_request`, response | Optional | Sensitive | Opaque value returned unchanged to connect request and response. |
| `content_items` | `lti_deep_linking_response` | Optional | Operational | Selected content items returned by the tool. |
| `type` | `lti_deep_link_item` | Yes | Operational | Kind of item being added. |
| `title` | `lti_deep_link_item` | Optional | Operational | Content title shown to users. |
| `text` | `lti_deep_link_item` | Optional | Operational | Description or display text. |
| `url` | `lti_deep_link_item` | Required for link-like items | System | URL to the content or tool activity. |
| `html` | `lti_deep_link_item` | Required for HTML items | Sensitive | HTML snippet to place in the platform. |
| `lineItem` | `lti_deep_link_item` | Optional | Education_record | Gradebook column details to create with the item. |
| `custom` | `lti_deep_link_item` | Optional | Depends on value | Custom settings attached to the created link. |
| `iframe` | `lti_media_descriptor` | Optional | Operational | Embedded-frame display settings. |
| `window` | `lti_media_descriptor` | Optional | Operational | New-window display settings. |
| `embed` | `lti_media_descriptor` | Optional | Operational | Embedded HTML display settings. |
| `thumbnail` | `lti_media_descriptor` | Optional | Operational | Small preview image. |
| `icon` | `lti_media_descriptor` | Optional | Operational | Small icon image. |
| `available.startDateTime` | `lti_deep_link_item` | Optional | Education_record | When the item becomes available. |
| `available.endDateTime` | `lti_deep_link_item` | Optional | Education_record | When the item stops being available. |
| `submission.startDateTime` | `lti_deep_link_item` | Optional | Education_record | When learners may start submitting. |
| `submission.endDateTime` | `lti_deep_link_item` | Optional | Education_record | Submission deadline. |

### LTI Values

| Value set | Value | Layperson meaning |
| --- | --- | --- |
| LTI message type | `LtiResourceLinkRequest` | Normal launch from a course activity link. |
| LTI message type | `LtiDeepLinkingRequest` | Instructor is choosing content from a tool. |
| LTI message type | `LtiDeepLinkingResponse` | Tool is returning selected content to the platform. |
| LTI version | `1.3.0` | LTI 1.3 launch message version. |
| Context type | `CourseTemplate` | A reusable course design. |
| Context type | `CourseOffering` | A scheduled offering of a course. |
| Context type | `CourseSection` | A section or class instance. |
| Context type | `Group` | A group inside or outside a course. |
| Common context role | `Administrator` | User administers the context. |
| Common context role | `ContentDeveloper` | User creates or manages content. |
| Common context role | `Instructor` | User teaches or leads the context. |
| Common context role | `Learner` | User learns in the context. |
| Common context role | `Mentor` | User can observe or advise learners. |
| Common context role | `TeachingAssistant` | User assists instruction. |
| Membership status | `Active` | Membership is currently active. |
| Membership status | `Inactive` | Membership exists but is not active. |
| AGS activityProgress | `Initialized` | Activity record exists but work has not started. |
| AGS activityProgress | `Started` | Learner started the activity. |
| AGS activityProgress | `InProgress` | Learner is still working. |
| AGS activityProgress | `Submitted` | Learner submitted work. |
| AGS activityProgress | `Completed` | Activity is complete. |
| AGS gradingProgress | `FullyGraded` | Final grade is ready. |
| AGS gradingProgress | `Pending` | Grade is not ready yet. |
| AGS gradingProgress | `PendingManual` | A person still needs to grade it. |
| AGS gradingProgress | `Failed` | Grading failed. |
| AGS gradingProgress | `NotReady` | There is not enough information to grade yet. |
| Deep link accept/content type | `link` | A normal web link. |
| Deep link accept/content type | `file` | A downloadable or imported file. |
| Deep link accept/content type | `html` | HTML content. |
| Deep link accept/content type | `ltiResourceLink` | A launchable LTI activity. |
| Deep link accept/content type | `image` | An image item. |
| Deep link target | `iframe` | Open inside an embedded frame. |
| Deep link target | `window` | Open in a new browser window or tab. |
| Deep link target | `embed` | Embed directly in page content. |

## Common Cartridge and Thin Common Cartridge

Common Cartridge is the import/export package layer for learning content. A full cartridge can carry files, web content, links, assessments, metadata, and alignments. A thin cartridge mainly carries links and metadata so content can stay hosted by the publisher or tool.

### Cartridge Object Map

| Platform object | What it means to a layperson | Privacy class |
| --- | --- | --- |
| `cc_package` | The uploaded or exported cartridge file. | Operational |
| `cc_manifest` | The package table of contents and metadata file, usually `imsmanifest.xml`. | Operational |
| `cc_metadata` | Descriptive tags about the package or resource. | Operational |
| `cc_organization` | A content outline or table-of-contents structure. | Operational |
| `cc_item` | One entry in the content outline. | Operational |
| `cc_resource` | One actual content resource referenced by the manifest. | Operational |
| `cc_file` | One file inside the package. | Operational |
| `cc_dependency` | A resource that another resource depends on. | Operational |
| `cc_web_link` | A web link resource. | Operational |
| `cc_lti_link` | A launchable LTI link packaged inside a cartridge. | System |
| `cc_qti_resource` | QTI assessment content included in the cartridge. | Education_record or operational |
| `cc_accessibility_metadata` | Accessibility tags, such as WCAG or accommodation-related metadata. | Sensitive |
| `cc_curriculum_alignment` | Link from content to a standard, competency, or CASE URI. | Public |
| `cc_line_item` | Gradebook setup information attached to an LTI link in newer cartridge profiles. | Education_record |
| `cc_variant` | Alternate representation of the same content for systems with different capabilities. | Operational |

### Cartridge Package and Manifest Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `package_id` | `cc_package` | Yes | Operational | Internal ID for the cartridge import/export. |
| `source_filename` | `cc_package` | Yes | Operational | Name of the uploaded or generated file. |
| `package_profile` | `cc_package` | Yes | Operational | Whether this is full Common Cartridge or Thin Common Cartridge. |
| `package_version` | `cc_package` | Yes | Operational | Cartridge version, such as `1.3.0` or `1.4`. |
| `checksum` | `cc_package` | Recommended | Operational | File fingerprint used to detect duplicates or tampering. |
| `import_status` | `cc_package` | Yes | Operational | Current processing status. |
| `validation_status` | `cc_package` | Yes | Operational | Whether the package passed validation. |
| `validation_errors` | `cc_package` | Optional | Operational | Problems found during import or export. |
| `manifest_identifier` | `cc_manifest` | Yes | Operational | Package manifest ID. |
| `manifest_version` | `cc_manifest` | Required in CC 1.3 | Operational | Version string declared in the manifest metadata. |
| `schema` | `cc_metadata` | Optional | Operational | Metadata schema name used by the package. |
| `schemaversion` | `cc_metadata` | Optional | Operational | Version of the metadata schema. |
| `title` | `cc_metadata`, `cc_item`, `cc_resource` | Recommended | Operational | Name users see for the package, item, or resource. |
| `description` | `cc_metadata`, `cc_resource` | Optional | Operational | Plain description of the package or resource. |
| `keyword` | `cc_metadata` | Optional | Operational | Search terms. |
| `language` | `cc_metadata` | Optional | Operational | Language of the content. |
| `author` | `cc_metadata` | Optional | Operational | Person or organization that authored the content. |
| `license` | `cc_metadata` | Optional | Operational | Terms under which the content can be used. |
| `publisher` | `cc_metadata` | Optional | Operational | Organization that published the content. |
| `created_at` | local | Yes | Operational | When the platform imported or created the package. |

### Cartridge Outline and Resource Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `organization_identifier` | `cc_organization` | Yes | Operational | ID for a table-of-contents structure. |
| `default_organization` | `cc_manifest` | Optional | Operational | Which outline should be used first. |
| `item_identifier` | `cc_item` | Yes | Operational | ID for an item in the outline. |
| `parent_item_identifier` | `cc_item` | Optional | Operational | Parent item in the outline tree. |
| `identifierref` | `cc_item` | Optional | Operational | Resource that this outline item opens. |
| `isvisible` | `cc_item` | Optional | Operational | Whether the item should be shown to users. |
| `parameters` | `cc_item` | Optional | Operational | Extra URL or launch parameters. |
| `resource_identifier` | `cc_resource` | Yes | Operational | ID for a resource in the manifest. |
| `resource_type` | `cc_resource` | Yes | Operational | Kind of resource, such as web content, LTI link, or QTI. |
| `href` | `cc_resource`, `cc_file` | Optional | Operational | Main file or URL for the resource. |
| `intendeduse` | `cc_resource` | Optional | Operational | Intended instructional use, such as assignment or syllabus. |
| `file_href` | `cc_file` | Yes | Operational | Path to one file inside the package. |
| `dependency_identifierref` | `cc_dependency` | Yes | Operational | Resource required by another resource. |
| `web_link_url` | `cc_web_link` | Yes | System | URL opened by the web link resource. |
| `lti_launch_url` | `cc_lti_link` | Yes | System | Tool launch URL stored in the cartridge. |
| `lti_title` | `cc_lti_link` | Optional | Operational | Title shown for the LTI link. |
| `lti_custom_parameters` | `cc_lti_link` | Optional | Depends on value | Settings sent to the LTI tool. |
| `qti_package_href` | `cc_qti_resource` | Optional | Operational | QTI package or assessment file path. |
| `qti_version` | `cc_qti_resource` | Optional | Operational | QTI version included in the cartridge. |
| `alignment_target_url` | `cc_curriculum_alignment` | Recommended | Public | Standards or competency URI the resource supports. |
| `alignment_target_name` | `cc_curriculum_alignment` | Optional | Public | Human-readable aligned standard name. |
| `accessibility_feature` | `cc_accessibility_metadata` | Optional | Sensitive | Accessibility support provided by the resource. |
| `accessibility_hazard` | `cc_accessibility_metadata` | Optional | Sensitive | Accessibility risk, such as flashing content. |
| `line_item_label` | `cc_line_item` | Optional | Education_record | Gradebook column name requested by an LTI link. |
| `line_item_score_maximum` | `cc_line_item` | Optional | Education_record | Maximum score requested by an LTI link. |
| `variant_resource_identifier` | `cc_variant` | Optional | Operational | Preferred alternate resource for capable importers. |

### Cartridge Values

| Value set | Value | Layperson meaning |
| --- | --- | --- |
| Package profile | `common_cartridge` | Full package that may include local files and resources. |
| Package profile | `thin_common_cartridge` | Lightweight package mostly containing links and metadata. |
| Manifest version | `1.3.0` | Common Cartridge 1.3 manifest version. |
| CC 1.4 status | `Candidate Final` | Implementable candidate version, but treat conformance posture carefully. |
| Resource family | `webcontent` | HTML, image, PDF, media, or other web files in the package. |
| Resource family | `associatedcontent` | Supporting files collected for another resource. |
| Resource family | `weblink` | URL resource. |
| Resource family | `lti_link` | Launchable external tool link. |
| Resource family | `qti` | Assessment item, question bank, or test resource. |
| Resource family | `epub3` | EPUB 3 digital book resource. |
| Resource family | `iwb` | Interactive whiteboard resource. |
| Resource family | `apip` | Accessible Portable Item Protocol assessment resource. |
| Resource family | `openvideo` | OpenVideo resource in newer profile work. |
| Intended use | `lessonplan` | Resource is a lesson plan. |
| Intended use | `syllabus` | Resource is a syllabus. |
| Intended use | `assignment` | Resource is an assignment. |
| Intended use | `unspecified` | The package did not say how the resource should be used. |
| Import status | `received` | Package has been uploaded or discovered. |
| Import status | `validating` | Platform is checking the package. |
| Import status | `imported` | Package was imported successfully. |
| Import status | `failed` | Import failed. |
| Import status | `exported` | Platform generated a package. |
| Validation status | `not_checked` | Validation has not run. |
| Validation status | `valid` | Package passed validation. |
| Validation status | `warning` | Package has issues that may still be usable. |
| Validation status | `invalid` | Package does not meet requirements. |

## Open Badges 3.0 and CLR 2.0

Open Badges represents achievements and their awarded credentials. CLR bundles achievements and credentials into a broader learner record. Both use verifiable credential patterns, so proof, issuer, subject, status, and evidence fields must be governed carefully.

### Credential Object Map

| Platform object | What it means to a layperson | Privacy class |
| --- | --- | --- |
| `achievement` | The thing a learner can earn, such as a badge, skill, certificate, or course completion. | Public or credential |
| `achievement_credential` | A verifiable credential saying a learner earned an achievement. | Credential |
| `achievement_subject` | The person or identity that earned the achievement. | Credential |
| `clr_credential` | A verifiable learner record that can contain many achievements or credentials. | Credential |
| `clr_subject` | The learner identity and included achievements inside a CLR. | Credential |
| `association` | A relationship between two achievements or records. | Public or credential |
| `address` | Mailing or physical address for a profile. | Sensitive |
| `alignment` | Connection to an external skill, standard, competency, or framework. | Public |
| `criteria` | Description of what had to be done to earn the achievement. | Public |
| `endorsement_credential` | A verifiable statement supporting another credential, issuer, or achievement. | Credential |
| `endorsement_subject` | The thing being endorsed and the endorsement comment. | Credential |
| `evidence` | Work, artifact, observation, or explanation supporting the award. | Education_record or credential |
| `geo_coordinates` | Latitude and longitude for an address or place. | Sensitive |
| `identifier_entry` | An identifier for a person, organization, achievement, or credential. | Depends on identifier |
| `identity_object` | Hashed or direct identity information used to identify a badge recipient. | Sensitive |
| `image` | Badge, issuer, profile, thumbnail, or credential image. | Public or credential |
| `profile` | Person, organization, issuer, or achievement creator profile. | Directory or credential |
| `related` | Link to a related achievement or resource. | Public |
| `result` | Score, grade, level, rubric result, or status within a credential. | Credential |
| `result_description` | Defines what kind of result can be recorded and how to interpret it. | Public or credential |
| `rubric_criterion_level` | One level in a rubric, such as "Proficient". | Public or credential |
| `verifiable_credential` | Shared credential base fields used by badge, endorsement, and CLR credentials. | Credential |
| `credential_schema` | Schema that explains how to validate the credential shape. | Operational |
| `credential_status` | Status or revocation service for the credential. | Credential |
| `credential_subject` | Generic credential subject base object. | Credential |
| `proof` | Cryptographic proof or signature metadata. | Sensitive |
| `refresh_service` | Service that can refresh a credential. | System |
| `terms_of_use` | Rules that apply to use of the credential. | Credential |
| `service_description_document` | OpenAPI-based description of a credential service. | System |
| `get_open_badge_credentials_response` | API response containing badge credentials. | Credential |
| `get_clr_credentials_response` | API response containing CLR credentials. | Credential |

### Achievement Fields

| Field | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- |
| `id` | Yes | Public | Stable ID or URL for the achievement definition. |
| `type` | Yes | Public | Object type, usually including `Achievement`. |
| `alignment` | Optional | Public | Standards, skills, or frameworks this achievement aligns to. |
| `achievementType` | Recommended | Public | Kind of achievement, such as badge, certificate, or course. |
| `creator` | Optional | Directory | Person or organization that created the achievement definition. |
| `creditsAvailable` | Optional | Public | Credits that can be earned. |
| `criteria` | Recommended | Public | Requirements for earning the achievement. |
| `description` | Yes | Public | Plain description of what the achievement means. |
| `endorsement` | Optional | Credential | Endorsements about the achievement. |
| `endorsementJwt` | Optional | Sensitive | Signed endorsement token. |
| `fieldOfStudy` | Optional | Public | Academic or skill area. |
| `humanCode` | Optional | Public | Human-friendly code, such as a course or catalog code. |
| `image` | Optional | Public | Image representing the achievement. |
| `inLanguage` | Optional | Public | Language of the achievement text. |
| `name` | Yes | Public | Achievement name. |
| `otherIdentifier` | Optional | Depends on identifier | Other IDs for the achievement. |
| `related` | Optional | Public | Related achievements or resources. |
| `resultDescription` | Optional | Public | Results that may be recorded for this achievement. |
| `specialization` | Optional | Public | More specific focus area. |
| `tag` | Optional | Public | Search or grouping tags. |
| `version` | Optional | Public | Version of this achievement definition. |
| `extension` | Optional | Depends on contents | Extension data not covered by the base model. |

### Achievement Credential Fields

| Field | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- |
| `@context` | Yes | Operational | JSON-LD contexts that define credential terms. |
| `id` | Optional but recommended | Credential | Stable credential ID or URL. |
| `type` | Yes | Credential | Credential types, such as VerifiableCredential and AchievementCredential. |
| `name` | Optional | Credential | Credential display name. |
| `description` | Optional | Credential | Credential description. |
| `image` | Optional | Credential | Credential image. |
| `awardedDate` | Optional | Credential | Date the credential was awarded. |
| `credentialSubject` | Yes | Credential | Learner or subject that received the credential. |
| `endorsement` | Optional | Credential | Endorsements attached to the credential. |
| `endorsementJwt` | Optional | Sensitive | Signed endorsement token. |
| `issuer` | Yes | Credential | Organization or person that issued the credential. |
| `validFrom` | Optional | Credential | Date/time the credential becomes valid. |
| `validUntil` | Optional | Credential | Date/time the credential expires. |
| `proof` | Optional | Sensitive | Cryptographic proof or signature. |
| `credentialSchema` | Optional | Operational | Schema used to validate the credential. |
| `credentialStatus` | Optional | Credential | Status or revocation information. |
| `refreshService` | Optional | System | Service that can refresh credential data. |
| `termsOfUse` | Optional | Credential | Rules for using the credential. |
| `evidence` | Optional | Education_record or credential | Evidence supporting the award. |
| `extension` | Optional | Depends on contents | Extension data not covered by the base model. |

### Achievement Subject and CLR Subject Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `id` | AchievementSubject, ClrSubject | Optional | Credential | ID for the credential subject. |
| `type` | AchievementSubject, ClrSubject | Yes | Credential | Subject object type. |
| `activityEndDate` | AchievementSubject | Optional | Credential | When the learning activity ended. |
| `activityStartDate` | AchievementSubject | Optional | Credential | When the learning activity started. |
| `creditsEarned` | AchievementSubject | Optional | Credential | Credits the learner earned. |
| `achievement` | AchievementSubject, ClrSubject | Yes for badge subject; optional in CLR subject | Credential | Achievement being awarded or included. |
| `identifier` | AchievementSubject, ClrSubject | Optional | Sensitive | Identifiers for the learner or subject. |
| `image` | AchievementSubject | Optional | Credential | Image associated with the subject or evidence. |
| `licenseNumber` | AchievementSubject | Optional | Sensitive | License number issued with the credential. |
| `narrative` | AchievementSubject | Optional | Education_record | Story or explanation of the learner's evidence. |
| `result` | AchievementSubject | Optional | Credential | Score, level, or status result. |
| `role` | AchievementSubject | Optional | Credential | Learner role while earning it, such as intern or team lead. |
| `source` | AchievementSubject | Optional | Credential | Person, organization, or system that assessed it. |
| `term` | AchievementSubject | Optional | Credential | Academic term or time period. |
| `verifiableCredential` | ClrSubject | Optional | Credential | Credentials bundled inside the CLR subject. |
| `association` | ClrSubject | Optional | Credential | Relationships among included achievements or credentials. |
| `extension` | AchievementSubject, ClrSubject | Optional | Depends on contents | Extension data not covered by the base model. |

### CLR Credential and Association Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `@context` | `clr_credential` | Yes | Operational | JSON-LD contexts that define CLR terms. |
| `type` | `clr_credential` | Yes | Credential | Credential type, including CLR credential type. |
| `id` | `clr_credential` | Optional but recommended | Credential | Stable ID or URL for the CLR. |
| `name` | `clr_credential` | Optional | Credential | CLR display name. |
| `description` | `clr_credential` | Optional | Credential | CLR description. |
| `endorsement` | `clr_credential` | Optional | Credential | Endorsements attached to the CLR. |
| `endorsementJwt` | `clr_credential` | Optional | Sensitive | Signed endorsement token. |
| `image` | `clr_credential` | Optional | Credential | Image for the CLR. |
| `partial` | `clr_credential` | Optional | Credential | Whether this is only part of the learner record. |
| `credentialSubject` | `clr_credential` | Yes | Credential | Learner and included achievements or credentials. |
| `awardedDate` | `clr_credential` | Optional | Credential | Date the CLR was awarded or issued. |
| `issuer` | `clr_credential` | Yes | Credential | Organization or person that issued the CLR. |
| `validFrom` | `clr_credential` | Optional | Credential | Date/time the CLR becomes valid. |
| `validUntil` | `clr_credential` | Optional | Credential | Date/time the CLR expires. |
| `proof` | `clr_credential` | Optional | Sensitive | Cryptographic proof or signature. |
| `credentialSchema` | `clr_credential` | Optional | Operational | Schema used to validate the CLR. |
| `credentialStatus` | `clr_credential` | Optional | Credential | Status or revocation information. |
| `refreshService` | `clr_credential` | Optional | System | Service that can refresh the CLR. |
| `termsOfUse` | `clr_credential` | Optional | Credential | Rules for using the CLR. |
| `evidence` | `clr_credential` | Optional | Education_record or credential | Evidence supporting the CLR. |
| `extension` | `clr_credential` | Optional | Depends on contents | Extension data not covered by the base model. |
| `associationType` | `association` | Yes | Credential | Relationship type between source and target. |
| `sourceId` | `association` | Yes | Credential | ID of the record the relationship starts from. |
| `targetId` | `association` | Yes | Credential | ID of the record the relationship points to. |

### Shared Credential Support Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `addressCountry` | Address | Optional | Sensitive | Country name. |
| `addressCountryCode` | Address | Optional | Sensitive | Country code. |
| `addressRegion` | Address | Optional | Sensitive | State, province, or region. |
| `addressLocality` | Address | Optional | Sensitive | City or locality. |
| `streetAddress` | Address | Optional | Sensitive | Street address. |
| `postOfficeBoxNumber` | Address | Optional | Sensitive | PO box. |
| `postalCode` | Address | Optional | Sensitive | ZIP or postal code. |
| `geo` | Address | Optional | Sensitive | Geographic coordinates. |
| `latitude` | GeoCoordinates | Optional | Sensitive | Latitude. |
| `longitude` | GeoCoordinates | Optional | Sensitive | Longitude. |
| `targetCode` | Alignment | Optional | Public | Code for the aligned standard or competency. |
| `targetDescription` | Alignment | Optional | Public | Description of the aligned target. |
| `targetName` | Alignment | Yes | Public | Name of the aligned target. |
| `targetFramework` | Alignment | Optional | Public | Framework the target belongs to. |
| `targetType` | Alignment | Optional | Public | Kind of alignment target. |
| `targetUrl` | Alignment | Yes | Public | URL for the aligned target. |
| `narrative` | Criteria, Evidence | Optional | Public or education_record | Explanation written for people. |
| `endorsementComment` | EndorsementSubject | Optional | Credential | Comment explaining the endorsement. |
| `genre` | Evidence | Optional | Education_record | Kind of evidence, such as portfolio or project. |
| `audience` | Evidence | Optional | Education_record | Intended audience for the evidence. |
| `identifier` | IdentifierEntry | Yes | Depends on identifier | Actual identifier value. |
| `identifierType` | IdentifierEntry | Yes | Depends on identifier | What kind of identifier it is. |
| `hashed` | IdentityObject | Yes | Sensitive | Whether the identity value is hashed. |
| `identityHash` | IdentityObject | Yes | Sensitive | Hash or direct identity value. |
| `identityType` | IdentityObject | Yes | Sensitive | Type of identity, such as email. |
| `salt` | IdentityObject | Optional | Sensitive | Extra random value used for hashing. |
| `caption` | Image | Optional | Public or credential | Accessible image caption. |
| `url` | Profile | Optional | Directory | Profile website. |
| `phone` | Profile | Optional | Directory or sensitive | Profile phone number. |
| `email` | Profile | Optional | Directory or sensitive | Profile email. |
| `official` | Profile | Optional | Directory | Authorized official represented by the profile. |
| `parentOrg` | Profile | Optional | Directory | Parent organization. |
| `familyName` | Profile | Optional | Directory | Family or last name. |
| `givenName` | Profile | Optional | Directory | Given or first name. |
| `additionalName` | Profile | Optional | Directory | Additional name. |
| `patronymicName` | Profile | Optional | Directory | Patronymic name. |
| `honorificPrefix` | Profile | Optional | Directory | Prefix, such as Dr. |
| `honorificSuffix` | Profile | Optional | Directory | Suffix, such as PhD. |
| `familyNamePrefix` | Profile | Optional | Directory | Prefix that belongs with the family name. |
| `dateOfBirth` | Profile | Optional | Sensitive | Date of birth. |
| `inLanguage` | Related | Optional | Public | Language of the related resource. |
| `version` | Related | Optional | Public | Version of the related resource. |
| `achievedLevel` | Result | Optional | Credential | Level achieved. |
| `resultDescription` | Result | Optional | Credential | Definition for this result. |
| `status` | Result | Optional | Credential | Status of the result. |
| `value` | Result | Optional | Credential | Result value, such as score or grade. |
| `allowedValue` | ResultDescription | Optional | Public | Allowed text values. |
| `requiredLevel` | ResultDescription | Optional | Public | Required level to pass or complete. |
| `requiredValue` | ResultDescription | Optional | Public | Required score or value. |
| `resultType` | ResultDescription | Yes | Public | Kind of result expected. |
| `rubricCriterionLevel` | ResultDescription | Optional | Public | Allowed rubric levels. |
| `valueMax` | ResultDescription | Optional | Public | Maximum allowed value. |
| `valueMin` | ResultDescription | Optional | Public | Minimum allowed value. |
| `level` | RubricCriterionLevel | Optional | Public | Rubric level value. |
| `points` | RubricCriterionLevel | Optional | Public | Points for this rubric level. |
| `credential` | GetOpenBadgeCredentialsResponse, GetClrCredentialsResponse | Optional | Credential | Returned credentials. |
| `compactJwsString` | GetOpenBadgeCredentialsResponse, GetClrCredentialsResponse | Optional | Sensitive | Credential serialized as a signed compact token. |

### Verification, Status, Proof, and API Service Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `id` | CredentialSchema, CredentialStatus, RefreshService, TermsOfUse | Yes | System or credential | URL or ID for the supporting service or rule. |
| `type` | CredentialSchema, CredentialStatus, RefreshService, TermsOfUse | Yes | System or credential | Type of schema, status service, refresh service, or terms. |
| `created` | Proof | Optional | Sensitive | When the proof was created. |
| `cryptosuite` | Proof | Optional | Sensitive | Cryptographic suite used by the proof. |
| `challenge` | Proof | Optional | Sensitive | Challenge value used by verifier workflows. |
| `domain` | Proof | Optional | Sensitive | Domain where the proof is intended to be used. |
| `nonce` | Proof | Optional | Sensitive | One-time value used in proof creation. |
| `proofPurpose` | Proof | Optional | Sensitive | Why the proof exists, such as assertion or authentication. |
| `proofValue` | Proof | Optional | Sensitive | Signature value. |
| `verificationMethod` | Proof | Optional | Sensitive | Key or method used to verify the proof. |
| `openapi` | ServiceDescriptionDocument | Yes | System | OpenAPI version used by the service description. |
| `info` | ServiceDescriptionDocument | Yes | System | API title and version metadata. |
| `components` | ServiceDescriptionDocument | Optional | System | Shared OpenAPI components, including security schemes. |
| `extension` | Credential support objects | Optional | Depends on contents | Extension data not covered by the base model. |

### Credential Values

| Value set | Value | Layperson meaning |
| --- | --- | --- |
| AchievementType | `Achievement` | General achievement. |
| AchievementType | `ApprenticeshipCertificate` | Apprenticeship credential. |
| AchievementType | `Assessment` | Assessment achievement. |
| AchievementType | `Assignment` | Assignment completion or performance. |
| AchievementType | `AssociateDegree` | Associate degree. |
| AchievementType | `Award` | Award. |
| AchievementType | `Badge` | Badge or microcredential. |
| AchievementType | `BachelorDegree` | Bachelor's degree. |
| AchievementType | `Certificate` | Certificate. |
| AchievementType | `CertificateOfCompletion` | Completion certificate. |
| AchievementType | `Certification` | Certification. |
| AchievementType | `CommunityService` | Community service achievement. |
| AchievementType | `Competency` | Competency or skill. |
| AchievementType | `Course` | Course completion or achievement. |
| AchievementType | `CoCurricular` | Co-curricular achievement. |
| AchievementType | `Degree` | Degree. |
| AchievementType | `Diploma` | Diploma. |
| AchievementType | `DoctoralDegree` | Doctoral degree. |
| AchievementType | `Fieldwork` | Fieldwork achievement. |
| AchievementType | `GeneralEducationDevelopment` | GED-style achievement. |
| AchievementType | `JourneymanCertificate` | Journeyman certificate. |
| AchievementType | `LearningProgram` | Program completion. |
| AchievementType | `License` | License. |
| AchievementType | `Membership` | Membership credential. |
| AchievementType | `ProfessionalDoctorate` | Professional doctorate. |
| AchievementType | `QualityAssuranceCredential` | Quality assurance credential. |
| AchievementType | `MasterCertificate` | Master certificate. |
| AchievementType | `MasterDegree` | Master's degree. |
| AchievementType | `MicroCredential` | Microcredential. |
| AchievementType | `ResearchDoctorate` | Research doctorate. |
| AchievementType | `SecondarySchoolDiploma` | High school or secondary diploma. |
| AchievementType | `ext:*` | Extension achievement type defined outside the base vocabulary. |
| AlignmentTargetType | `ceasn:Competency` | CEASN competency. |
| AlignmentTargetType | `ceterms:Credential` | Credential Engine credential. |
| AlignmentTargetType | `CFItem` | CASE framework item. |
| AlignmentTargetType | `CFRubric` | CASE rubric. |
| AlignmentTargetType | `CFRubricCriterion` | CASE rubric criterion. |
| AlignmentTargetType | `CFRubricCriterionLevel` | CASE rubric level. |
| AlignmentTargetType | `CTDL` | CTDL target. |
| AlignmentTargetType | `ext:*` | Extension alignment type. |
| IdentifierTypeEnum | `name` | Name identifier. |
| IdentifierTypeEnum | `sourcedId` | Source system identifier. |
| IdentifierTypeEnum | `systemId` | System identifier. |
| IdentifierTypeEnum | `productId` | Product identifier. |
| IdentifierTypeEnum | `userName` | Username. |
| IdentifierTypeEnum | `accountId` | Account identifier. |
| IdentifierTypeEnum | `emailAddress` | Email address. |
| IdentifierTypeEnum | `nationalIdentityNumber` | National identity number. |
| IdentifierTypeEnum | `isbn` | Book ISBN. |
| IdentifierTypeEnum | `issn` | Serial ISSN. |
| IdentifierTypeEnum | `lisSourcedId` | LIS source identifier. |
| IdentifierTypeEnum | `oneRosterSourcedId` | OneRoster source identifier. |
| IdentifierTypeEnum | `sisSourcedId` | SIS source identifier. |
| IdentifierTypeEnum | `ltiContextId` | LTI context/course ID. |
| IdentifierTypeEnum | `ltiDeploymentId` | LTI deployment ID. |
| IdentifierTypeEnum | `ltiToolId` | LTI tool ID. |
| IdentifierTypeEnum | `ltiPlatformId` | LTI platform ID. |
| IdentifierTypeEnum | `ltiUserId` | LTI user ID. |
| IdentifierTypeEnum | `identifier` | Generic identifier. |
| IdentifierTypeEnum | `ext:*` | Extension identifier type. |
| ResultType | `GradePointAverage` | GPA. |
| ResultType | `LetterGrade` | Letter grade. |
| ResultType | `Percent` | Percent score. |
| ResultType | `PerformanceLevel` | Performance level. |
| ResultType | `PredictedScore` | Predicted score. |
| ResultType | `RawScore` | Raw score. |
| ResultType | `Result` | General result. |
| ResultType | `RubricCriterion` | Rubric criterion result. |
| ResultType | `RubricCriterionLevel` | Rubric level result. |
| ResultType | `RubricScore` | Rubric score. |
| ResultType | `ScaledScore` | Scaled score. |
| ResultType | `Status` | Completion or enrollment status. |
| ResultType | `ext:*` | Extension result type. |
| ResultStatusType | `Completed` | Completed. |
| ResultStatusType | `Enrolled` | Enrolled. |
| ResultStatusType | `Failed` | Failed. |
| ResultStatusType | `InProgress` | In progress. |
| ResultStatusType | `OnHold` | On hold. |
| ResultStatusType | `Provisional` | Temporary or not final. |
| ResultStatusType | `Withdrew` | Learner withdrew. |
| CLR AssociationType | `exactMatchOf` | Same meaning as another record. |
| CLR AssociationType | `isChildOf` | More specific child of another record. |
| CLR AssociationType | `isParentOf` | More general parent of another record. |
| CLR AssociationType | `isPartOf` | Part of another record. |
| CLR AssociationType | `isPeerOf` | Peer or sibling of another record. |
| CLR AssociationType | `isRelatedTo` | Related but relationship is broad. |
| CLR AssociationType | `precedes` | Comes before another record. |
| CLR AssociationType | `replacedBy` | Superseded by another record. |

## Security, Service Access, and Privacy Governance

Security and privacy records explain who can connect, which scopes they have, what keys and tokens are used, what data is shared, and why that sharing is allowed.

### Governance Object Map

| Platform object | What it means to a layperson | Privacy class |
| --- | --- | --- |
| `security_profile` | Security posture for one standard integration. | System |
| `oauth_client_registration` | OAuth client configuration for a tool, app, or service. | System |
| `oidc_login` | Browser-based login or launch flow metadata. | Sensitive |
| `oauth_token_request` | Request for an access token. | Sensitive |
| `access_token_grant` | Issued token metadata, without storing raw token unnecessarily. | Sensitive |
| `jwk` | One public or private key record. | System or sensitive |
| `jwks` | A set of JSON Web Keys. | System |
| `security_scope` | One permission string an integration can request. | System |
| `service_description_document` | OpenAPI document that describes service endpoints and security schemes. | System |
| `privacy_classification` | The privacy label assigned to an object or field. | Operational |
| `data_sharing_rule` | Rule saying when data may be shared with a tool or partner. | Sensitive |
| `consent_record` | Learner, guardian, institution, or admin consent record when required. | Sensitive |
| `retention_rule` | Rule for how long data is kept. | Operational |
| `audit_event` | Record of a security, privacy, launch, import, or credential action. | Operational or sensitive |

### Security and Privacy Fields

| Field | Applies to | Required? | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `profile_key` | `security_profile` | Yes | System | Stable key for a security pattern, such as LTI launch or credential API. |
| `standard_family` | `security_profile` | Yes | Operational | Standard this security profile supports. |
| `security_pattern` | `security_profile` | Yes | System | OAuth/OIDC/JWT pattern used. |
| `client_id` | `oauth_client_registration` | Yes | System | OAuth client identifier. |
| `client_name` | `oauth_client_registration` | Optional | Operational | Human-readable client name. |
| `client_uri` | `oauth_client_registration` | Optional | Operational | Website for the client app. |
| `redirect_uris` | `oauth_client_registration` | Required for browser flows | System | Allowed callback URLs. |
| `grant_types` | `oauth_client_registration` | Yes | System | OAuth flows this client may use. |
| `response_types` | `oauth_client_registration` | Required for browser flows | System | OAuth/OIDC response modes this client may request. |
| `token_endpoint_auth_method` | `oauth_client_registration` | Yes | System | How the client proves its identity at the token endpoint. |
| `scope` | OAuth requests and grants | Yes | System | Permissions requested or granted. |
| `issuer` | OIDC/JWT | Yes | System | Entity that issued a token or message. |
| `subject` | OIDC/JWT | Yes when user-bound | Sensitive | User or client the token is about. |
| `audience` | OIDC/JWT | Yes | System | Intended recipient of the token or message. |
| `expires_at` | tokens and grants | Yes | Sensitive | When access ends. |
| `issued_at` | tokens and grants | Yes | Sensitive | When the token or grant was issued. |
| `token_type` | `access_token_grant` | Yes | Sensitive | Type of token, usually bearer. |
| `token_fingerprint` | `access_token_grant` | Recommended | Sensitive | Non-secret fingerprint for audit and lookup. |
| `refresh_token_fingerprint` | `access_token_grant` | Optional | Sensitive | Non-secret fingerprint for a refresh token. |
| `revoked_at` | `access_token_grant` | Optional | Sensitive | When the grant was revoked. |
| `kid` | `jwk` | Recommended | System | Key ID. |
| `kty` | `jwk` | Yes | System | Key type, such as RSA or EC. |
| `alg` | `jwk` | Recommended | System | Intended signing algorithm. |
| `use` | `jwk` | Optional | System | Whether the key is for signing or encryption. |
| `key_ops` | `jwk` | Optional | System | Operations allowed for the key. |
| `public_key_material` | `jwk` | Required for public keys | System | Public values needed to verify signatures. |
| `private_key_reference` | `jwk` | Required for private keys | Sensitive | Reference to a protected secret, not the raw key in app tables. |
| `jwks_uri` | `jwks` | Optional | System | URL where a key set can be fetched. |
| `purpose` | `data_sharing_rule`, `consent_record` | Yes | Sensitive | Why data is being used or shared. |
| `data_category` | `data_sharing_rule` | Yes | Sensitive | Kind of data being shared. |
| `privacy_class` | `privacy_classification` | Yes | Operational | Platform privacy label. |
| `legal_basis` | `data_sharing_rule`, `consent_record` | Recommended | Sensitive | Why processing is allowed. |
| `recipient` | `data_sharing_rule` | Yes | Sensitive | Tool, vendor, school, or party receiving data. |
| `access_scope` | `data_sharing_rule` | Yes | Sensitive | Maximum data access allowed. |
| `retention_period` | `retention_rule` | Yes | Operational | How long data should be kept. |
| `delete_after` | `retention_rule` | Optional | Operational | Date after which data should be deleted or anonymized. |
| `export_allowed` | `data_sharing_rule` | Yes | Sensitive | Whether data can leave the platform. |
| `redisclosure_allowed` | `data_sharing_rule` | Yes | Sensitive | Whether the recipient can share it onward. |
| `consented_by` | `consent_record` | Optional | Sensitive | Person or authority that granted consent. |
| `consent_status` | `consent_record` | Yes | Sensitive | Current consent state. |
| `audit_actor_id` | `audit_event` | Optional | Sensitive | User, client, or system that performed the action. |
| `audit_action` | `audit_event` | Yes | Operational | What happened. |
| `audit_target` | `audit_event` | Optional | Sensitive | Object acted upon. |
| `audit_time` | `audit_event` | Yes | Operational | When it happened. |
| `audit_outcome` | `audit_event` | Yes | Operational | Whether the action succeeded. |

### Security and Privacy Values

| Value set | Value | Layperson meaning |
| --- | --- | --- |
| Security pattern | `oauth2_client_credentials` | Server-to-server API access between trusted systems. |
| Security pattern | `oauth2_authorization_code` | User-approved API access. |
| Security pattern | `openid_connect_launch` | Browser-based signed launch or login. |
| Security pattern | `jwt_bearer` | Signed JWT used as part of authentication or authorization. |
| Grant type | `client_credentials` | Client gets a token for its own service access. |
| Grant type | `authorization_code` | Client exchanges a user-approved code for a token. |
| Grant type | `refresh_token` | Client refreshes access without making the user log in again. |
| Response type | `code` | Authorization code response. |
| Response type | `id_token` | ID token response for OIDC-style message flow. |
| Token type | `Bearer` | Whoever presents the token can use it, so it must be protected. |
| JWK use | `sig` | Key is used for signatures. |
| JWK use | `enc` | Key is used for encryption. |
| Common signing algorithm | `RS256` | RSA SHA-256 signature algorithm. |
| Common signing algorithm | `PS256` | RSA-PSS SHA-256 signature algorithm. |
| Common signing algorithm | `ES256` | ECDSA P-256 SHA-256 signature algorithm. |
| Consent status | `not_required` | Consent is not required for this processing rule. |
| Consent status | `requested` | Consent has been requested. |
| Consent status | `granted` | Consent has been granted. |
| Consent status | `denied` | Consent was denied. |
| Consent status | `revoked` | Consent was granted and later withdrawn. |
| Audit outcome | `succeeded` | Action completed. |
| Audit outcome | `failed` | Action failed. |
| Audit outcome | `denied` | Action was blocked by policy. |
| Audit outcome | `partial` | Action partly completed. |
| Data category | `directory` | Names, emails, roles, organizations, or similar directory data. |
| Data category | `education_record` | Enrollment, grades, submissions, progress, or achievements. |
| Data category | `credential` | Badge, CLR, endorsement, or proof data. |
| Data category | `behavioral` | Usage and activity event data. |
| Data category | `security` | Tokens, keys, scopes, login, or audit data. |
| Data category | `metadata` | Package, content, standard, or operational metadata. |
| Legal basis | `school_official` | Access is allowed because the recipient acts for the institution. |
| Legal basis | `consent` | Access is based on consent. |
| Legal basis | `contract` | Access is required by contract or service delivery. |
| Legal basis | `legal_obligation` | Access is needed to comply with law or regulation. |
| Legal basis | `legitimate_interest` | Access is based on a documented legitimate institutional interest. |

### Common LTI Service Scopes

| Scope | Layperson meaning |
| --- | --- |
| `https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly` | Tool may read course/context membership through NRPS. |
| `https://purl.imsglobal.org/spec/lti-ags/scope/lineitem` | Tool may create, read, update, and delete gradebook line items it is allowed to manage. |
| `https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly` | Tool may read gradebook line items. |
| `https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly` | Tool may read results from gradebook line items. |
| `https://purl.imsglobal.org/spec/lti-ags/scope/score` | Tool may send scores to gradebook line items. |

## Cross-Standard Relationships

| Relationship | Layperson meaning | Platform handling |
| --- | --- | --- |
| LTI launch to OneRoster user | The launched user should resolve to a known school user when allowed. | Match by LTI user ID, OneRoster sourcedId, SIS ID, or governed email match. |
| LTI context to OneRoster class | The launched course or section may be a OneRoster class. | Keep a crosswalk rather than overwriting either source ID. |
| LTI AGS line item to OneRoster line item | A tool gradebook column may map to a platform/OneRoster gradebook item. | Preserve AGS IDs and OneRoster sourcedIds separately. |
| Common Cartridge resource to QTI assessment | A cartridge may include a QTI package or assessment file. | Store package lineage and QTI item/test identifiers. |
| Common Cartridge LTI link to LTI resource link | A cartridge may create launchable tool links. | Create LTI resource link records during import, subject to registration/deployment approval. |
| Common Cartridge metadata to CASE item | A resource may align to a CASE standard or competency. | Store CASE URI/GUID alignment, not just text. |
| Open Badge achievement to CASE item | A badge may represent a competency or standard. | Store alignment target URLs and resolve known CASE identifiers. |
| CLR achievement to Open Badge credential | A CLR may bundle badge credentials. | Preserve each credential's ID, issuer, subject, status, and proof. |
| Credential issuer to organization | A badge or CLR issuer may be a school, district, vendor, or other organization. | Link to organization/profile records and preserve issuer URL/DID. |
| Security scope to dictionary field | A service permission grants access to specific objects and fields. | Map scopes to field-level policy, not just endpoint names. |
| Privacy rule to every public field | Every exposed field must know its privacy class and sharing rules. | Enforce dictionary coverage before API or SQL exposure. |

## Implementation Notes

- LTI launch claims, credential JSON-LD, Common Cartridge XML, and proof material should be retained as canonical source payloads with careful access controls.
- Normalized platform fields should be treated as projections. If a standard field is not projected yet, it still belongs in raw payload storage and dictionary mapping backlog.
- Fields that look harmless can become sensitive when combined. For example, a course title, role, and launch time can identify a student's education activity.
- Credential proof and token values should not be broadly queryable. Prefer fingerprints, references, and verification status fields for normal operations.
- The dictionary should eventually generate SQL comments, OpenAPI descriptions, field policy docs, and review checklists from the same metadata source.
