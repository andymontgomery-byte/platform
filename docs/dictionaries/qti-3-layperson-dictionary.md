# QTI 3 Layperson Data Dictionary

Research date: 2026-04-24

Sources:

- QTI overview: https://www.1edtech.org/standards/qti
- QTI 3.0 assessment, section, and item information model: https://www.imsglobal.org/sites/default/files/spec/qti/v3/info/imsqti_asi_v3p0p1_infomodel_v1p0.html
- QTI 3 developer guide: https://developers.imsglobal.org/spec/qti/v3p0/guide

## What QTI Does

QTI is the platform's portable assessment content format.

In plain terms, QTI lets an assessment authoring tool, item bank, publisher, school system, delivery engine, or reporting system move:

- Questions.
- Reading passages and other shared stimulus material.
- Tests made from questions and sections.
- Rules for selecting, ordering, and timing questions.
- Rules for scoring responses.
- Feedback shown to learners, scorers, tutors, proctors, or authors.
- Accessibility alternatives and companion materials.

QTI is XML-based. The platform should store the original validated QTI package, then project the fields below into normal database/API objects so people and apps can search, govern, align, deliver, and report on the assessment content.

## Platform Modeling Guidance

Use these first-class platform objects:

- `qti_package`: the uploaded or imported package and manifest-level metadata.
- `qti_assessment_item`: one question/task that can be delivered and scored.
- `qti_assessment_stimulus`: shared content used by one or more items.
- `qti_assessment_test`: a whole test or assessment form.
- `qti_assessment_section`: a section or group inside a test.
- `qti_test_part`: a major test part with navigation/submission rules.
- `qti_item_ref`: a test's reference to an item file.
- `qti_variable_declaration`: response, outcome, template, and context variables.
- `qti_interaction`: a normalized index of the response interaction types inside item bodies.
- `qti_feedback`: item-level and test-level feedback.
- `qti_accessibility_catalog`: alternative content and support metadata.
- `qti_companion_material`: allowed calculators, rulers, protractors, files, or physical materials.

Store the full QTI XML and package files as the legal/technical source of truth. Do not flatten every HTML, ARIA, MathML, and content-body child into separate relational columns unless the platform exposes it as a public business field. The dictionary requirement for the platform is every public storage/API field; low-level XML fields remain governed inside the validated artifact and generated XML inventory.

## Common QTI Field Concepts

| QTI field | Plain name | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- |
| `identifier` | QTI identifier | Operational or directory | The local ID used inside a QTI item, section, test, variable, choice, or feedback block. | Keep it stable within the QTI artifact. Pair with package/version when storing globally. |
| `title` | Title | Directory | A human-facing label for selecting or browsing the item, test, section, or feedback. | May be shown to learners depending on delivery rules. |
| `label` | Authoring label | Operational | Extra label used by the authoring tool or publisher. | Useful for authoring workflows; do not treat as a learner-facing title. |
| `language` | Language | Public or directory | The natural language of the content, such as English or Spanish. | Store as BCP 47 language tag when provided. |
| `tool-name` | Authoring tool | Operational | The tool that created the QTI content. | Use for debugging imports and vendor-specific interpretation. |
| `tool-version` | Authoring tool version | Operational | The version of the tool that created the QTI content. | Store with `tool-name`. |
| `class` | Style/category classes | Operational | Space-separated tags used for styling or local grouping. | Do not confuse with a school class/course section. |
| `href` | Package file link | Operational | A URI pointing to another file in the package. | Resolve and validate during import, but preserve the original link. |
| `dataExtension` | HTML5 data extension | Depends on contents | Custom `data-*` information added by a tool or implementation. | Store as governed extension data; review before using in core logic. |
| `adaptive` | Adaptive item/section flag | Operational | Whether the item or section can change based on learner responses or test logic. | Important for delivery and analytics interpretation. |
| `time-dependent` | Time affects scoring | Operational | Whether time limits or timing behavior matter for this item. | Use when delivery and scoring depend on time. |
| `required` | Must be included | Operational | Whether a child item/section must be selected when a test selection rule runs. | Applies to test construction, not student completion by itself. |
| `fixed` | Do not shuffle | Operational | Whether the child item/choice keeps its position when nearby content is shuffled. | Preserve for valid randomized delivery. |
| `visible` | Visible to learner | Operational | Whether a section appears as a visible section to the candidate. | Invisible sections can still organize test logic. |
| `keep-together` | Keep group together | Operational | Whether children of an invisible shuffled section move together as a block. | Important for randomization. |
| `category` | Item categories | Directory or operational | Tags used so outcome processing can aggregate groups of items. | Useful for strand, domain, or subscore reporting. |
| `response-identifier` | Response variable link | Education record when delivered | The variable that stores the learner response for an interaction. | Must match a response declaration. |
| `base` | Number base | Operational | How numeric text should be interpreted when a text response is numeric. | Rare; preserve for math/science items. |
| `data-catalog-idref` | Accessibility catalog reference | Sensitive | Points content to alternative accessibility material. | Treat as accommodation/accessibility metadata. |
| `data-qti-suppress-tts` | Text-to-speech suppression | Sensitive | Says whether read-aloud tools should skip content. | Treat as accessibility delivery metadata. |

## QTI Package

A package is the import/export bundle that contains QTI XML, resources, media, metadata, and manifest information.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `package_identifier` | Package ID | Yes | Operational | The platform or publisher ID for this imported QTI package. |
| `qti_version` | QTI version | Yes | Operational | The QTI version claimed by the package, such as `3.0`. |
| `source_system` | Source system | Optional | Operational | The publisher, item bank, LMS, or authoring tool that supplied the package. |
| `validation_status` | Validation status | Yes | Operational | Whether the package passed QTI validation. |
| `validation_errors` | Validation errors | Optional | Operational | Problems found during import or validation. |
| `manifest_path` | Manifest path | Optional | Operational | Location of the manifest file inside the package. |
| `original_file_uri` | Stored package file | Yes | Operational | Where the original package file is stored. |
| `imported_at` | Imported time | Yes | Operational | When the platform received the package. |

### Package Validation Status Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `pending` | The platform has not checked the package yet. | Do not make deliverable until validation finishes. |
| `valid` | The package passed platform validation. | Eligible for indexing and controlled delivery. |
| `invalid` | The package failed validation. | Keep for troubleshooting, but do not deliver as trusted content. |
| `warning` | The package is usable but has non-blocking issues. | Show warnings to assessment managers. |

## Assessment Item

An assessment item is one question, task, or prompt plus its response variables, scoring rules, body content, feedback, and accessibility metadata.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Item ID | Yes | Operational | The local QTI ID for the item. |
| `title` | Item title | Yes | Directory | The title used to find or select the item. |
| `label` | Item label | Optional | Operational | Authoring-system label for the item. |
| `language` | Item language | Optional | Public or directory | The main language for the item. |
| `tool-name` | Authoring tool | Optional | Operational | The tool that created the item. |
| `tool-version` | Authoring tool version | Optional | Operational | The version of that tool. |
| `adaptive` | Adaptive item | Optional | Operational | Whether the item can adapt across attempts. |
| `time-dependent` | Time-dependent item | Yes | Operational | Whether time affects the response/scoring behavior. |
| `qti-context-declaration` | Context variables | Optional, many | Operational | Global values available during processing. |
| `qti-response-declaration` | Response variables | Optional, many | Education record when delivered | Variables that hold learner responses. |
| `qti-outcome-declaration` | Outcome variables | Optional, many | Education record when delivered | Variables that hold scores, status, or other results. |
| `qti-template-declaration` | Template variables | Optional, many | Operational | Variables used to clone or personalize item content. |
| `qti-template-processing` | Template processing | Optional | Operational | Rules for setting template variables before delivery. |
| `qti-assessment-stimulus-ref` | Stimulus references | Optional, many | Directory | Links to shared stimulus content. |
| `qti-companion-materials-info` | Companion materials | Optional | Sensitive or operational | Tools/materials allowed or required while answering. |
| `qti-stylesheet` | Stylesheets | Optional, many | Operational | CSS or style files used to render the item. |
| `qti-item-body` | Item body | Optional | Directory or education record when delivered | The visible question content and interactions. |
| `qti-catalog-info` | Accessibility alternatives | Optional | Sensitive | Alternative content used for accessibility support. |
| `qti-response-processing` | Scoring rules | Optional | Operational | Rules that turn responses into outcomes. |
| `qti-modal-feedback` | Item feedback | Optional, many | Education record when delivered | Feedback shown after scoring based on outcome values. |

## Assessment Stimulus

A stimulus is shared content, such as a reading passage, chart, scenario, or media asset used by more than one item.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Stimulus ID | Yes | Operational | The local QTI ID for the shared stimulus. |
| `title` | Stimulus title | Yes | Directory | The title used to browse or select the stimulus. |
| `label` | Stimulus label | Optional | Operational | Authoring-system label. |
| `language` | Stimulus language | Optional | Public or directory | The natural language of the stimulus. |
| `tool-name` | Authoring tool | Optional | Operational | Tool that created the stimulus. |
| `tool-version` | Authoring tool version | Optional | Operational | Version of that tool. |
| `qti-stylesheet` | Stylesheets | Optional, many | Operational | Styles used to render the stimulus. |
| `qti-stimulus-body` | Stimulus body | Yes | Directory | The passage, media, chart, or other shared content. |
| `qti-catalog-info` | Accessibility alternatives | Optional | Sensitive | Accessibility alternatives for the stimulus. |

## Assessment Test

An assessment test is a whole test definition: its parts, sections, item references, timing, navigation, outcomes, and feedback.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Test ID | Yes | Operational | The local QTI ID for the test. |
| `title` | Test title | Yes | Directory | The human-facing test name. |
| `class` | Test classes | Optional | Operational | Style or grouping tokens for the test. |
| `tool-name` | Authoring tool | Optional | Operational | Tool that created the test. |
| `tool-version` | Authoring tool version | Optional | Operational | Version of that tool. |
| `qti-context-declaration` | Context variables | Optional, many | Operational | Global values available to test logic. |
| `qti-outcome-declaration` | Test outcomes | Optional, many | Education record when delivered | Test-level scores or status values. |
| `qti-time-limits` | Test time limits | Optional | Operational | Minimum/maximum time rules for the test. |
| `qti-stylesheet` | Stylesheets | Optional, many | Operational | Styles used to render test content. |
| `qti-rubric-block` | Test rubric blocks | Optional, many | Directory or sensitive | Directions or information shown to selected audiences. |
| `qti-test-part` | Test parts | Yes, many | Operational | Major divisions of the test. |
| `qti-outcome-processing` | Test outcome processing | Optional | Operational | Rules that calculate test-level outcomes. |
| `qti-test-feedback` | Test feedback | Optional, many | Education record when delivered | Feedback controlled by test outcomes. |

## Test Part

A test part is a major division of a test. It controls how the learner moves and when responses are submitted.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Test part ID | Yes | Operational | The local QTI ID for this part. |
| `title` | Test part title | Optional | Directory | The title for this part, if shown or managed separately. |
| `class` | Test part classes | Optional | Operational | Style or grouping tokens. |
| `navigation-mode` | Navigation mode | Yes | Operational | Whether the learner must go in order or can move around. |
| `submission-mode` | Submission mode | Yes | Operational | Whether responses are submitted item-by-item or all together. |
| `qti-pre-condition` | Skip conditions | Optional, many | Operational | Conditions that can skip this part. |
| `qti-branch-rule` | Branch rules | Optional, many | Operational | Rules that jump to another target. |
| `qti-item-session-control` | Item session controls | Optional | Operational | Attempt, review, skipping, and validation controls. |
| `qti-time-limits` | Part time limits | Optional | Operational | Time limits for this part. |
| `qti-rubric-block` | Part rubric blocks | Optional, many | Directory or sensitive | Directions shown for this part. |
| `assessmentSectionSelection` | Section selection | Yes, many | Operational | Sections included in this test part. |
| `qti-test-feedback` | Part feedback | Optional, many | Education record when delivered | Feedback specific to this part. |

### Navigation Mode Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `linear` | The learner proceeds in order and cannot freely return to earlier items. | Delivery must enforce forward-only movement. |
| `nonlinear` | The learner may navigate items in a freer order. | Branch and pre-condition behavior differs in nonlinear mode. |

### Submission Mode Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `individual` | Each item is submitted and processed separately. | Supports item-by-item scoring and feedback. |
| `simultaneous` | Responses are submitted together at the end of the part. | Use for tests where scoring waits until the section/part is complete. |

## Assessment Section

A section groups item references and/or sub-sections. Sections can organize content, support randomization, and provide section-level rules.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Section ID | Yes | Operational | The local QTI ID for the section. |
| `required` | Required in selection | Optional | Operational | Whether the section must be selected. |
| `fixed` | Fixed in shuffle | Optional | Operational | Whether the section keeps its position when siblings shuffle. |
| `title` | Section title | Yes | Directory | The title used to browse or present the section. |
| `class` | Section classes | Optional | Operational | Style or grouping tokens. |
| `visible` | Visible section | Yes | Operational | Whether the learner can see this as a section. |
| `keep-together` | Keep children together | Optional | Operational | Whether children move together during shuffling. |
| `qti-pre-condition` | Skip conditions | Optional, many | Operational | Conditions that can skip this section. |
| `qti-branch-rule` | Branch rules | Optional, many | Operational | Rules that can jump to another item/section. |
| `qti-item-session-control` | Item session controls | Optional | Operational | Attempt, review, skipping, and validation controls. |
| `qti-time-limits` | Section time limits | Optional | Operational | Time limits for this section. |
| `adaptive` | Adaptive section rules | Optional | Operational | Rules or algorithms for adaptive section behavior. |
| `qti-rubric-block` | Section rubric blocks | Optional, many | Directory or sensitive | Directions shown for items in the section. |
| `sectionPart` | Child section parts | Optional, many | Operational | Child item references, section references, or nested sections. |

## Assessment Item Reference

An item reference is how a test includes an item file. The same item can be referenced more than once in a test with different context.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Item reference ID | Yes | Operational | The test-local ID for this item reference. |
| `required` | Required in selection | Optional | Operational | Whether this referenced item must be selected. |
| `fixed` | Fixed in shuffle | Optional | Operational | Whether this item keeps its position during shuffling. |
| `class` | Item reference classes | Optional | Operational | Style or grouping tokens. |
| `href` | Item file link | Yes | Operational | Link to the item file in the package. |
| `category` | Item categories | Optional | Directory or operational | Category tags for scoring or reporting. |
| `qti-pre-condition` | Skip conditions | Optional, many | Operational | Conditions that can skip this item. |
| `qti-branch-rule` | Branch rules | Optional, many | Operational | Rules that can jump elsewhere after this item. |
| `qti-item-session-control` | Item session controls | Optional | Operational | Attempt, review, skipping, and validation controls. |
| `qti-time-limits` | Item time limits | Optional | Operational | Time limits for this item in this test. |
| `qti-variable-mapping` | Variable mappings | Optional, many | Operational | Renames item outcome variables for test-level use. |
| `qti-weight` | Weights | Optional, many | Operational | Test-specific score weighting for this item. |
| `qti-template-default` | Template defaults | Optional, many | Operational | Test-specific default values for template variables. |

## Variable Declarations

Variables are named containers for responses, outcomes, template values, and context values.

### Response Declaration

A response declaration defines the variable that receives a learner's answer for one interaction.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Response variable ID | Yes | Education record when delivered | The variable name used by an interaction to store the learner's answer. |
| `cardinality` | Number of values | Yes | Operational | Whether the answer is one value, many values, ordered values, or a record. |
| `base-type` | Answer value type | Optional | Operational | The type of each answer value, such as string, integer, point, or file. |
| `qti-default-value` | Default answer | Optional | Operational | The starting answer value, if any. |
| `qti-correct-response` | Correct answer | Optional | Sensitive or operational | The answer considered correct or partly correct. |
| `qti-mapping` | Score mapping | Optional | Operational | Mapping from response values to numeric scores. |
| `qti-area-mapping` | Area score mapping | Optional | Operational | Mapping from selected graphic points/areas to scores. |

### Outcome Declaration

An outcome declaration defines a value produced by scoring, such as `SCORE`, `MAXSCORE`, completion status, mastery, or feedback selector.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Outcome variable ID | Yes | Education record when delivered | The variable name for a score, status, feedback selector, or other result. |
| `cardinality` | Number of values | Yes | Operational | Whether the outcome holds one value, many values, ordered values, or a record. |
| `base-type` | Outcome value type | Optional | Operational | The type of each outcome value. |
| `view` | Intended audience | Optional | Sensitive or operational | Which users this outcome is meant for. |
| `interpretation` | Human interpretation | Optional | Directory or education record | Short explanation of what the outcome means. |
| `long-interpretation` | Extended interpretation link | Optional | Directory | Link to a fuller explanation. |
| `normal-maximum` | Normal maximum | Optional | Operational | Expected maximum numeric value. |
| `normal-minimum` | Normal minimum | Optional | Operational | Expected minimum numeric value. |
| `mastery-value` | Mastery threshold | Optional | Operational | Numeric value at or above which the learner is considered to have mastered the target. |
| `external-scored` | External scoring mode | Optional | Operational | Whether a human or outside machine scorer supplies this outcome. |
| `variable-identifier-ref` | External variable link | Optional | Operational | Name of the external variable used for scoring. |
| `qti-default-value` | Default outcome value | Optional | Operational | Starting value when rules do not set another value. |
| `lookupTable` | Lookup table | Optional | Operational | Rule table that turns a numeric source value into an outcome value. |

### Template Declaration

A template declaration defines a value used to create item variants, such as randomized numbers or personalized content.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Template variable ID | Yes | Operational | The variable name used by template processing. |
| `cardinality` | Number of values | Yes | Operational | Whether the template value is one value, many values, ordered values, or a record. |
| `base-type` | Template value type | Optional | Operational | The type of each template value. |
| `param-variable` | Substitute in parameters | Optional | Operational | Whether this value can replace matching object parameter values. |
| `math-variable` | Substitute in math | Optional | Operational | Whether this value can replace matching identifiers inside MathML. |
| `qti-default-value` | Default template value | Optional | Operational | Starting value for the template variable. |

### Context Declaration

A context declaration defines a global value available during template, response, and outcome processing.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Context variable ID | Yes | Operational | The global variable name. |
| `cardinality` | Number of values | Yes | Operational | Whether the context value is one value, many values, ordered values, or a record. |
| `base-type` | Context value type | Optional | Operational | The type of each context value. |
| `qti-default-value` | Default context value | Optional | Operational | Starting value for the context variable. |

### Cardinality Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `single` | Exactly one value. | Common for one selected choice, one score, or one text response. |
| `multiple` | A list of values where order does not matter. | Common for multiple-select answers. |
| `ordered` | A list of values where order matters. | Common for ordering questions. |
| `record` | A set of named values with their own types. | Use for complex/custom responses. |

### Base Type Values

| Value | Layperson meaning |
| --- | --- |
| `boolean` | True or false. |
| `directedPair` | Two IDs where direction matters, such as source to destination. |
| `duration` | Time length in seconds. |
| `file` | Uploaded file bytes with content type and optional filename. |
| `float` | Decimal number. |
| `identifier` | QTI identifier value. |
| `integer` | Whole number. |
| `pair` | Two IDs where direction does not matter. |
| `point` | Graphic coordinate point. |
| `string` | Text. |
| `uri` | URI or web identifier. |

### View Values

| Value | Layperson meaning |
| --- | --- |
| `author` | Intended for someone authoring the assessment. |
| `candidate` | Intended for the learner/test taker. |
| `proctor` | Intended for the person supervising the assessment. |
| `scorer` | Intended for someone scoring the assessment. |
| `testConstructor` | Intended for someone assembling the test. |
| `tutor` | Intended for an educator/tutor supporting the learner. |

### External Scored Values

| Value | Layperson meaning |
| --- | --- |
| `externalMachine` | An external machine scoring service supplies the value. |
| `human` | A human scorer supplies the value. |

## Processing Rules

Processing rules are QTI logic. They should be preserved as QTI XML and exposed as governed metadata, not hand-translated into application code without a tested QTI engine.

| Object | Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- | --- |
| `ResponseProcessing` | `template` | Response template | Optional | Operational | URI for a reusable scoring template. |
| `ResponseProcessing` | `template-location` | Template location | Optional | Operational | Location where the scoring template can be found. |
| `ResponseProcessing` | `responseRuleGroup` | Response rules | Optional, many | Operational | Rules that calculate item outcomes from learner responses. |
| `OutcomeProcessing` | `outcomeRule` | Outcome rules | Optional, many | Operational | Rules that calculate test outcomes from item outcomes. |
| `BranchRule` | `target` | Branch target | Yes | Operational | The item, section, or special target to jump to when the condition is true. |
| `BranchRule` | `logic` | Branch condition | Yes | Operational | The expression evaluated to decide whether the branch runs. |
| `PreCondition` | `logic` | Skip condition | Yes | Operational | Expression used to decide whether to skip a part, section, or item. |

## Time Limits and Item Session Controls

| Object | Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- | --- |
| `TimeLimits` | `min-time` | Minimum time | Optional | Operational | Minimum time, in seconds, before the learner can finish. |
| `TimeLimits` | `max-time` | Maximum time | Optional | Operational | Maximum time, in seconds, allowed for the test, part, section, or item. |
| `TimeLimits` | `allow-late-submission` | Accept late submission | Optional | Operational | Whether responses after the maximum time may still be accepted. |
| `ItemSessionControl` | `max-attempts` | Maximum attempts | Optional | Operational | Number of attempts allowed for the item in this test context. |
| `ItemSessionControl` | `show-feedback` | Show feedback | Optional | Operational | Whether feedback may be shown after the final attempt. |
| `ItemSessionControl` | `allow-review` | Allow review | Optional | Operational | Whether the learner may review the item after the final attempt. |
| `ItemSessionControl` | `show-solution` | Show solution | Optional | Sensitive | Whether the system may show the solution. |
| `ItemSessionControl` | `allow-comment` | Allow comments | Optional | Education record | Whether the learner may leave comments not counted as answers. |
| `ItemSessionControl` | `allow-skipping` | Allow skipping | Optional | Operational | Whether the learner may submit without answering. |
| `ItemSessionControl` | `validate-responses` | Validate responses | Optional | Operational | Whether invalid responses block submission. |

## Item Body and Interactions

The item body contains visible content and one or more interactions. An interaction is the part the learner answers: choose, type, drag, match, upload, click a graphic, and so on.

### Common Interaction Fields

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `id` | Element ID | Optional | Operational | Local element identifier used by links and accessibility annotations. |
| `response-identifier` | Response variable link | Usually yes | Education record when delivered | The response declaration that stores this interaction's answer. |
| `qti-prompt` | Prompt | Optional | Directory | Instructions or prompt text shown with the interaction. |
| `shuffle` | Shuffle choices | Optional | Operational | Whether choices should appear in randomized order. |
| `min-choices` | Minimum choices | Optional | Operational | Smallest number of choices a learner must select. |
| `max-choices` | Maximum choices | Optional | Operational | Largest number of choices a learner may select; `0` often means no limit. |
| `min-associations` | Minimum associations | Optional | Operational | Smallest number of pairings/matches required. |
| `max-associations` | Maximum associations | Optional | Operational | Largest number of pairings/matches allowed; `0` often means no limit. |
| `orientation` | Orientation | Optional | Operational | Whether layout naturally reads horizontal or vertical. |
| `data-min-selections-message` | Minimum selection message | Optional | Directory | Message to show when too few answers are selected. |
| `data-max-selections-message` | Maximum selection message | Optional | Directory | Message to show when too many answers are selected. |
| `pattern-mask` | Required text pattern | Optional | Operational | Pattern a text response must match to be valid. |
| `placeholder-text` | Placeholder text | Optional | Directory | Hint text shown in an empty text response box. |
| `format` | Text response format | Optional | Operational | Whether text is plain, preformatted, or XHTML. |

### Interaction Object Types

| QTI object | Plain name | Main learner action | Key fields |
| --- | --- | --- | --- |
| `ChoiceInteraction` | Multiple choice/select | Select one or more choices. | `shuffle`, `min-choices`, `max-choices`, `orientation`, `qti-simple-choice`. |
| `SimpleChoice` | Choice option | One selectable option in a choice/order interaction. | `identifier`, `fixed`, `template-identifier`, `show-hide`, content. |
| `OrderInteraction` | Ordering | Put choices in order. | `shuffle`, `min-choices`, `max-choices`, `orientation`, `qti-simple-choice`. |
| `AssociateInteraction` | Pairing | Create associations between choices. | `shuffle`, `min-associations`, `max-associations`, associable choices. |
| `MatchInteraction` | Two-column matching | Match choices from one set to another. | `shuffle`, `min-associations`, `max-associations`, `qti-simple-match-set`. |
| `GapMatchInteraction` | Fill gaps by dragging/selecting choices | Put gap choices into gaps in surrounding content. | `shuffle`, `min-associations`, `max-associations`, `gapChoice`, content with gaps. |
| `TextEntryInteraction` | Short text entry | Type a short answer inline. | `response-identifier`, `expected-length`, `pattern-mask`, `placeholder-text`, `format`. |
| `ExtendedTextInteraction` | Long text entry | Type an essay or longer response. | `expected-length`, `expected-lines`, `min-strings`, `max-strings`, `format`. |
| `InlineChoiceInteraction` | Inline dropdown/select | Choose text inside a sentence or passage. | `shuffle`, `required`, `min-choices`, `qti-inline-choice`. |
| `HotTextInteraction` | Select text in context | Select highlighted/selectable runs of text. | `min-choices`, `max-choices`, surrounding content. |
| `HotspotInteraction` | Select image areas | Click/tap one or more regions on an image. | `min-choices`, `max-choices`, `qti-hotspot-choice`. |
| `SelectPointInteraction` | Select image points | Mark one or more points on an image. | `min-choices`, `max-choices`, image/stage. |
| `GraphicOrderInteraction` | Order image hotspots | Put image regions into order. | `min-choices`, `max-choices`, `qti-hotspot-choice`. |
| `GraphicAssociateInteraction` | Associate image hotspots | Pair image regions with each other. | `min-associations`, `max-associations`, `qti-associable-hotspot`. |
| `GraphicGapMatchInteraction` | Place choices into image gaps | Match choices to image regions. | `min-associations`, `max-associations`, `gapChoice`, `qti-associable-hotspot`. |
| `PositionObjectInteraction` | Position an object on an image | Place an image object onto a stage. | `center-point`, `min-choices`, `max-choices`, image object. |
| `SliderInteraction` | Slider | Choose a number on a range. | `lower-bound`, `upper-bound`, `step`, `step-label`, `orientation`, `reverse`. |
| `UploadInteraction` | File upload | Upload a response file. | `type` MIME list. |
| `DrawingInteraction` | Drawing on image | Mark up a provided image/canvas. | background `object`, `img`, or `picture`. |
| `MediaInteraction` | Media use | Play or interact with audio/video and record play count. | `autostart`, `min-plays`, `max-plays`, `loop`, media object. |
| `EndAttemptInteraction` | End attempt/action button | Trigger response processing, often for a hint. | `response-identifier`, `title`, `count-attempt`. |
| `PortableCustomInteraction` | Portable custom interaction | Use a packaged custom interaction module. | `custom-interaction-type-identifier`, `module`, modules, markup, variables. |
| `CustomInteraction` | Proprietary custom interaction | Use non-standard custom behavior. | `extension` fields/children; deprecated in favor of PCI. |

### Text Format Values

| Value | Layperson meaning |
| --- | --- |
| `plain` | Plain typed text. |
| `preformatted` | Text where spacing and line breaks should be preserved. |
| `xhtml` | Structured rich text marked up as XHTML. |

### Orientation Values

| Value | Layperson meaning |
| --- | --- |
| `horizontal` | Laid out left-to-right or along a horizontal axis. |
| `vertical` | Laid out top-to-bottom or along a vertical axis. |

### Shape Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `circle` | Circular hotspot. | Coordinates describe center and radius. |
| `default` | Entire image area. | Treat the whole image as selected area. |
| `ellipse` | Ellipse hotspot. | Deprecated; preserve for compatibility. |
| `poly` | Polygon hotspot. | Coordinates describe polygon points. |
| `rect` | Rectangular hotspot. | Coordinates describe opposite corners. |

## Feedback and Rubrics

| Object | Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- | --- |
| `ModalFeedback` | `outcome-identifier` | Feedback outcome | Yes | Education record when delivered | Outcome variable that controls whether feedback appears. |
| `ModalFeedback` | `show-hide` | Show/hide mode | Yes | Operational | Whether matching the identifier shows or hides the feedback. |
| `ModalFeedback` | `identifier` | Feedback ID | Yes | Operational | Identifier tested against the outcome value. |
| `ModalFeedback` | `title` | Feedback title | Optional | Directory | Optional title for the feedback. |
| `ModalFeedback` | `qti-content-body` | Feedback body | Yes | Education record when delivered | Feedback content shown to the learner. |
| `TestFeedback` | `access` | Feedback timing | Yes | Operational | Whether feedback appears during the test or at the end. |
| `TestFeedback` | `outcome-identifier` | Feedback outcome | Yes | Education record when delivered | Outcome variable that controls whether test feedback appears. |
| `TestFeedback` | `show-hide` | Show/hide mode | Yes | Operational | Whether matching the identifier shows or hides the feedback. |
| `TestFeedback` | `identifier` | Feedback ID | Yes | Operational | Identifier tested against the outcome value. |
| `TestFeedback` | `qti-content-body` | Feedback body | Optional | Education record when delivered | Test-level feedback content. |
| `RubricBlock` | `use` | Rubric purpose | Yes | Directory or sensitive | What the rubric block is for. |
| `RubricBlock` | `view` | Rubric audience | Yes | Sensitive or operational | Who should see the rubric block. |
| `RubricBlock` | `qti-content-body` | Rubric content | Yes | Directory or sensitive | Directions, scoring information, or navigation information. |

### Show/Hide Values

| Value | Layperson meaning |
| --- | --- |
| `show` | Hidden by default; show when the condition matches. |
| `hide` | Shown by default; hide when the condition matches. |

### Test Feedback Access Values

| Value | Layperson meaning |
| --- | --- |
| `during` | Feedback may appear during the test. |
| `atEnd` | Feedback appears at the end of the test. |

### Rubric Use Values

| Value | Layperson meaning |
| --- | --- |
| `instructions` | Directions for the assessment. |
| `navigation` | Information about moving around the assessment. |
| `scoring` | Information about scoring. |

## Accessibility Catalog and Companion Materials

Accessibility catalog information describes alternative content used to support learner needs. Treat it as sensitive because it can reveal accommodations or accessibility preferences.

| Object | Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- | --- |
| `CatalogInfo` | `qti-catalog` | Accessibility catalog | Yes, many | Sensitive | A set of alternative content cards. |
| `CompanionMaterialsInfo` | `qti-calculator` | Calculator | Optional, many | Sensitive or operational | Calculator allowed/required for the item. |
| `CompanionMaterialsInfo` | `qti-rule` | Ruler | Optional, many | Sensitive or operational | Ruler allowed/required for the item. |
| `CompanionMaterialsInfo` | `qti-protractor` | Protractor | Optional, many | Sensitive or operational | Protractor allowed/required for the item. |
| `CompanionMaterialsInfo` | `qti-digital-material` | Digital material | Optional, many | Sensitive or operational | Extra digital file/material available during the item. |
| `CompanionMaterialsInfo` | `qti-physical-material` | Physical material | Optional, many | Sensitive or operational | Physical item/material needed during the assessment. |
| `CompanionMaterialsInfo` | `extensions` | Extra companion material data | Optional, many | Depends on contents | Vendor-specific material information. |

### Accessibility Support Values

| Value | Layperson meaning |
| --- | --- |
| `additional-directions` | Extra directions are available. |
| `audio-description` | Narration describes important visual details. |
| `braille` | Braille support is available. |
| `glossary-on-screen` | On-screen glossary support is available. |
| `high-contrast` | High-contrast visual alternative is available. |
| `keyboard-directions` | Keyboard-use directions are available. |
| `keyword-translation` | Keyword translation support is available. |
| `linguistic-guidance` | Language guidance is available. |
| `long-description` | Longer description is available. |
| `sign-language` | Sign language support is available. |
| `simplified-graphics` | Simplified graphic alternative is available. |
| `simplified-language-portions` | Simplified language alternative is available. |
| `spoken` | Spoken version/content is available. |
| `tactile` | Tactile alternative is available. |
| `transcript` | Transcript is available. |

### Text-to-Speech Suppression Values

| Value | Layperson meaning |
| --- | --- |
| `all` | Suppress read-aloud on all devices. |
| `computer-read-aloud` | Suppress computer read-aloud tools. |
| `screen-reader` | Suppress screen-reader read-aloud. |

### Calculator Type Values

| Value | Layperson meaning |
| --- | --- |
| `basic` | Basic calculator. |
| `standard` | Standard calculator. |
| `scientific` | Scientific calculator. |
| `graphing` | Graphing calculator. |

## Alignment to Other Platform Standards

| Link | Plain meaning | Platform guidance |
| --- | --- | --- |
| QTI item/test to CASE item | The question or test measures an academic standard, competency, or skill. | Store a many-to-many alignment table using CASE UUID/URI when available. |
| QTI item/test to OneRoster class/course | The assessment is assigned or used in a course/class context. | Use OneRoster structures for enrollment and gradebook context, not QTI. |
| QTI result to OneRoster result | A delivered assessment produces a score/result that may appear in gradebook. | Map to OneRoster gradebook line items/results when grade passback is required. |
| QTI activity to Caliper | Learner actions in assessment delivery produce analytics events. | Emit Caliper assessment/profile events from the delivery engine. |
| QTI package to Common Cartridge | QTI content may be included in a larger learning content package. | Keep package lineage and content-resource references. |

