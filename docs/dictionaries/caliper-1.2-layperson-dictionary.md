# Caliper 1.2 Layperson Data Dictionary

Research date: 2026-04-24

Sources:

- Caliper overview: https://www.1edtech.org/standards/caliper
- Caliper Analytics 1.2 specification: https://www.imsglobal.org/spec/caliper/v1p2/

## What Caliper Does

Caliper is the platform's learning activity event standard.

In plain terms, Caliper records things people and tools do in digital learning environments:

- A learner starts an assessment.
- A learner answers a question.
- A teacher grades an attempt.
- A learner opens a reading page.
- A learner pauses a video.
- A user launches an LTI tool.
- A learner searches, posts, comments, rates, annotates, or submits work.

Caliper events are behavioral data. They can be powerful for learning analytics, but raw event streams can reveal detailed student behavior. The platform should store them with strong access controls, retention rules, tenant scoping, and a preference for aggregated reporting.

## Platform Modeling Guidance

Use these first-class platform objects:

- `caliper_envelope`: one Sensor API payload received from a tool or platform.
- `caliper_event`: one learning activity event from the envelope.
- `caliper_entity`: a normalized index of people, tools, content, attempts, sessions, scores, and other event objects.
- `caliper_actor`: the person, app, or agent who did the action.
- `caliper_context`: the optional app, group, membership, session, LTI session, target, and referrer fields around the event.
- `caliper_extension`: governed custom fields found under `extensions`.

Store the original JSON-LD event payload. Project the fields below into database/API columns used for search, governance, analytics, and cross-standard joins.

## Caliper Envelope

An envelope is the JSON wrapper a sensor sends to a Caliper endpoint. It contains who sent the data, when it was sent, which Caliper version governs it, and the event/entity data.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `sensor` | Sensor ID | Yes | Operational | The tool, platform, app, or sensor that sent the payload. |
| `sendTime` | Sent time | Yes | Operational | When the sensor sent the payload. |
| `dataVersion` | Caliper context/version | Yes | Operational | The Caliper version/context used to interpret the payload. For Caliper 1.2 this is the v1p2 context IRI. |
| `data` | Payload data | Yes | Behavioral or operational | One or more events and/or entity descriptions. |

## Base Event

Every Caliper event inherits these fields. Event subtypes add restrictions about which event type, action, actor, object, generated entity, target, or referrer is valid.

| Field | Plain name | Required | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- | --- |
| `id` | Event ID | Yes | Behavioral | A globally unique event identifier, normally a UUID URN. | Deduplicate on this value within tenant/source. |
| `type` | Event type | Yes | Behavioral | The kind of event, such as `AssessmentEvent` or `MediaEvent`. | Must match a Caliper event term. |
| `profile` | Profile | Optional | Behavioral | The Caliper profile that explains the event's rules. | Strongly prefer sensors to send it; default generic events to `GeneralProfile`. |
| `actor` | Actor | Yes | Education record or behavioral | The person or app that did the action. | Usually a `Person`; can be an app for some events. |
| `action` | Action | Yes | Behavioral | What happened. | Must be allowed for the event/profile. |
| `object` | Object | Yes | Behavioral | The thing acted on, such as an assessment, page, video, assignment, session, or tool. | Can be an entity object or IRI. |
| `eventTime` | Event time | Yes | Behavioral | When the activity happened. | Store in UTC with source precision. |
| `edApp` | Education app | Optional | Operational or behavioral | The app where the event happened. | Use to group events by tool/application. |
| `generated` | Generated entity | Optional | Depends on entity | Something created by the action, such as an attempt, response, score, annotation, comment, rating, or search response. | Keep typed; do not treat all generated entities as scores. |
| `target` | Target/location | Optional | Behavioral | A specific part or location inside the object. | Common for media locations, page targets, and LTI launch targets. |
| `referrer` | Referrer | Optional | Behavioral | The previous page, resource, app, or context that led to this event. | Useful for navigation/path analysis. |
| `group` | Group context | Optional | Education record | The course, class, group, or organization context. | Join to OneRoster organization/class where possible. |
| `membership` | Membership context | Optional | Education record | The actor's role/status in the group. | Use for role-aware analytics. |
| `session` | Session | Optional | Behavioral | The current app/user session. | Helps group events into visits. |
| `federatedSession` | LTI session | Optional or required for some launch events | Behavioral or operational | The LTI launch/session context. | Join to LTI launches when available. |
| `extensions` | Extensions | Optional | Depends on contents | Custom fields not defined by Caliper. | Store under governed namespaces only. |

## Base Entity

Entities are the people, tools, resources, sessions, scores, attempts, and other objects that participate in events. Most entity fields are descriptive; entity IDs are IRIs.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `id` | Entity IRI | Yes when entity is an object | Depends on entity | A unique IRI for the person, tool, resource, session, attempt, or other object. |
| `type` | Entity type | Yes when entity is an object | Depends on entity | The Caliper entity term, such as `Person`, `Assessment`, or `Score`. |
| `name` | Name | Optional | Depends on entity | A human-readable name for the entity. |
| `description` | Description | Optional | Depends on entity | Short explanation of the entity. |
| `dateCreated` | Created time | Optional | Operational | When the entity was created. |
| `dateModified` | Modified time | Optional | Operational | When the entity was last changed. |
| `otherIdentifiers` | Other identifiers | Optional | Depends on entity | Other IDs known for this entity, such as SIS, LTI, OneRoster, or system IDs. |
| `extensions` | Extensions | Optional | Depends on contents | Custom fields not defined by Caliper. |

## Event Types and Fields

These event types inherit all base event fields. The listed fields are the subtype-specific fields/restrictions to index and explain.

| Event type | Plain meaning | Specific fields | Allowed actions |
| --- | --- | --- | --- |
| `AnnotationEvent` | A person creates or shares an annotation on a digital resource. | `type`, `actor`, `action`, `object`, `target`, `generated` | `Bookmarked`, `Highlighted`, `Shared`, `Tagged` |
| `AssessmentEvent` | A person works with a whole assessment. | `type`, `actor`, `action`, `object`, `generated` | `Started`, `Paused`, `Resumed`, `Restarted`, `Reset`, `Submitted` |
| `AssessmentItemEvent` | A person works with one assessment item/question. | `type`, `actor`, `action`, `object`, `generated`, `referrer` | `Started`, `Skipped`, `Completed` |
| `AssignableEvent` | A person works with assigned digital content. | `type`, `actor`, `action`, `object`, `target`, `generated` | `Activated`, `Deactivated`, `Started`, `Completed`, `Submitted`, `Reviewed` |
| `FeedbackEvent` | A person comments on or rates something. | `type`, `actor`, `action`, `object`, `target`, `generated` | `Commented`, `Ranked` |
| `ForumEvent` | A person subscribes or unsubscribes from a forum. | `type`, `actor`, `action`, `object` | `Subscribed`, `Unsubscribed` |
| `GradeEvent` | A person or app grades an attempt. | `type`, `actor`, `action`, `object`, `generated` | `Graded` |
| `MediaEvent` | A person interacts with audio/video/media. | `type`, `actor`, `action`, `object`, `target` | `Started`, `Ended`, `Paused`, `Resumed`, `Restarted`, `ForwardedTo`, `JumpedTo`, `ChangedResolution`, `ChangedSize`, `ChangedSpeed`, `ChangedVolume`, `EnabledClosedCaptioning`, `DisabledClosedCaptioning`, `EnteredFullScreen`, `ExitedFullScreen`, `Muted`, `Unmuted`, `OpenedPopout`, `ClosedPopout` |
| `MessageEvent` | A person posts or marks a message. | `type`, `actor`, `action`, `object` | `MarkedAsRead`, `MarkedAsUnread`, `Posted` |
| `NavigationEvent` | A person navigates to a resource, app, or part of a resource. | `type`, `actor`, `action`, `object`, `target`, `referrer` | `NavigatedTo` |
| `QuestionnaireEvent` | A person starts or submits a questionnaire. | `type`, `actor`, `action`, `object` | `Started`, `Submitted` |
| `QuestionnaireItemEvent` | A person works with one questionnaire item. | `type`, `actor`, `action`, `object`, `generated` | `Started`, `Skipped`, `Completed` |
| `ResourceManagementEvent` | A person manages a digital resource. | `type`, `actor`, `action`, `object`, `generated` | `Archived`, `Copied`, `Created`, `Deleted`, `Described`, `Downloaded`, `Modified`, `Printed`, `Published`, `Restored`, `Retrieved`, `Saved`, `Unpublished`, `Uploaded` |
| `SearchEvent` | A person searches a resource/app. | `type`, `actor`, `action`, `object`, `generated` | `Searched` |
| `SessionEvent` | A person or app starts, ends, or times out a session. | `type`, `actor`, `action`, `object`, `target`, `referrer` | `LoggedIn`, `LoggedOut`, `TimedOut` |
| `SurveyEvent` | A person opts into or out of a survey. | `type`, `actor`, `action`, `object` | `OptedIn`, `OptedOut` |
| `SurveyInvitationEvent` | A person sends or responds to a survey invitation. | `type`, `actor`, `action`, `object` | `Sent`, `Accepted`, `Declined` |
| `ThreadEvent` | A person marks a forum thread read/unread. | `type`, `actor`, `action`, `object` | `MarkedAsRead`, `MarkedAsUnread` |
| `ToolLaunchEvent` | A person launches or returns from a tool. | `type`, `actor`, `action`, `object`, `generated`, `target`, `federatedSession` | `Launched`, `Returned` |
| `ToolUseEvent` | A person uses a software application and aggregate usage can be generated. | `type`, `actor`, `action`, `object`, `target`, `generated` | `Used` |
| `ViewEvent` | A person views something. | `type`, `actor`, `action`, `object` | `Viewed` |

## Profile Event Matrix

Profiles are domain-specific bundles of valid event/action/object combinations.

| Profile | Event | Actor | Action | Object | Generated/target |
| --- | --- | --- | --- | --- | --- |
| `AnnotationProfile` | `AnnotationEvent` | `Person` | `Bookmarked` | `DigitalResource` | `BookmarkAnnotation` |
| `AnnotationProfile` | `AnnotationEvent` | `Person` | `Highlighted` | `DigitalResource` | `HighlightAnnotation` |
| `AnnotationProfile` | `AnnotationEvent` | `Person` | `Shared` | `DigitalResource` | `SharedAnnotation` |
| `AnnotationProfile` | `AnnotationEvent` | `Person` | `Tagged` | `DigitalResource` | `TagAnnotation` |
| `AssessmentProfile` | `AssessmentEvent` | `Person` | `Started`, `Paused`, `Resumed`, `Restarted`, `Submitted` | `Assessment` | `Attempt` |
| `AssessmentProfile` | `AssessmentItemEvent` | `Person` | `Started`, `Skipped`, `Completed` | `AssessmentItem` | `Attempt` or `Response` |
| `AssessmentProfile` | `NavigationEvent`, `ViewEvent` | `Person` | `NavigatedTo`, `Viewed` | `Assessment` or `AssessmentItem` | none |
| `AssignableProfile` | `AssignableEvent` | `Person` | `Activated`, `Deactivated`, `Started`, `Completed`, `Submitted`, `Reviewed` | `AssignableDigitalResource` | `Attempt` for work attempts |
| `AssignableProfile` | `NavigationEvent`, `ViewEvent` | `Person` | `NavigatedTo`, `Viewed` | `AssignableDigitalResource` | none |
| `FeedbackProfile` | `FeedbackEvent` | `Person` | `Commented`, `Ranked` | `Entity` | `Comment` or `Rating` |
| `ForumProfile` | `ForumEvent` | `Person` | `Subscribed`, `Unsubscribed` | `Forum` | none |
| `ForumProfile` | `ThreadEvent`, `MessageEvent` | `Person` | `MarkedAsRead`, `MarkedAsUnread`, `Posted` | `Thread` or `Message` | none |
| `ForumProfile` | `NavigationEvent`, `ViewEvent` | `Person` | `NavigatedTo`, `Viewed` | `Forum`, `Message`, or `Thread` | none |
| `GradingProfile` | `GradeEvent` | `Agent` | `Graded` | `Attempt` | `Score` |
| `GradingProfile` | `ViewEvent` | `Person` | `Viewed` | `Result` | none |
| `MediaProfile` | `MediaEvent` | `Person` | media actions | `MediaObject` | `MediaLocation` target |
| `MediaProfile` | `NavigationEvent`, `ViewEvent` | `Person` | `NavigatedTo`, `Viewed` | `MediaObject` | `MediaLocation` target |
| `ReadingProfile` | `NavigationEvent`, `ViewEvent` | `Person` | `NavigatedTo`, `Viewed` | `DigitalResource` | `DigitalResource` target |
| `ResourceManagementProfile` | `ResourceManagementEvent` | `Person` | resource management actions | `DigitalResource` | copied `DigitalResource` when applicable |
| `SearchProfile` | `SearchEvent` | `Person` | `Searched` | `DigitalResource` or `SoftwareApplication` | `SearchResponse` |
| `SessionProfile` | `SessionEvent` | `Person` or `SoftwareApplication` | `LoggedIn`, `LoggedOut`, `TimedOut` | `SoftwareApplication` or `Session` | `DigitalResource` target when relevant |
| `SurveyProfile` | `SurveyInvitationEvent`, `SurveyEvent`, `QuestionnaireEvent`, `QuestionnaireItemEvent`, `NavigationEvent`, `ViewEvent` | `Person` | survey/questionnaire actions | survey/questionnaire entities | `Attempt` or `Response` for questionnaire work |
| `ToolLaunchProfile` | `ToolLaunchEvent` | `Person` | `Launched`, `Returned` | `SoftwareApplication` | generated `DigitalResource`; target `Link` or `LtiLink` |
| `ToolUseProfile` | `ToolUseEvent` | `Person` | `Used` | `SoftwareApplication` | `AggregateMeasureCollection` |
| `GeneralProfile` | `Event` | `Agent` | any Caliper action | `Entity` | profile-specific if known |

## Entity Types and Specific Fields

Each entity also has the base entity fields when represented as an object. The fields below are the extra fields the platform should understand and document.

| Entity type | Plain meaning | Specific fields and layperson meanings |
| --- | --- | --- |
| `Agent` | A person or software agent. | No extra fields beyond base entity fields. |
| `AggregateMeasure` | A computed usage/learning metric. | `metricValue`: measured value; `maxMetricValue`: maximum possible value; `metric`: metric name; `startedAtTime`/`endedAtTime`: time range covered. |
| `AggregateMeasureCollection` | A set of aggregate measures. | `items`: measures in the collection. |
| `Annotation` | A note/mark connected to a digital resource. | `annotator`: person who annotated; `annotated`: resource that was annotated. |
| `Assessment` | A whole assessment. | `items`: assessment items/questions in the assessment. |
| `AssessmentItem` | One assessment item/question. | `isTimeDependent`: whether time matters for the item. |
| `AssignableDigitalResource` | Digital content assigned to a learner. | `dateToActivate`: when it becomes active; `dateToShow`: when visible; `dateToStartOn`: start date; `dateToSubmit`: due date; `maxAttempts`: allowed attempts; `maxSubmits`: allowed submissions; `maxScore`: maximum score. |
| `Attempt` | One try at an assignment, assessment, or questionnaire. | `assignee`: person assigned; `assignable`: work being attempted; `count`: attempt number; `startedAtTime`/`endedAtTime`: attempt timing; `duration`: time spent. |
| `AudioObject` | Audio media. | `volumeLevel`: current volume; `volumeMin`/`volumeMax`: volume bounds; `muted`: whether muted. |
| `BookmarkAnnotation` | Bookmark note. | `bookmarkNotes`: note text for the bookmark. |
| `Chapter` | Chapter in content/media. | No extra fields beyond base entity fields. |
| `Collection` | Ordered group of entities. | `items`: entities in the collection. |
| `Comment` | Written feedback/comment. | `commenter`: person who commented; `commentedOn`: entity commented on; `value`: comment text. |
| `CourseOffering` | Course offering. | `courseNumber`: human-readable course number; `academicSession`: term/session label. |
| `CourseSection` | Course/class section. | `category`: section purpose, such as lecture/lab/seminar. |
| `DateTimeQuestion` | Question asking for a date/time. | `minDateTime`/`maxDateTime`: allowed bounds; `minLabel`/`maxLabel`: labels for bounds. |
| `DateTimeResponse` | Date/time answer. | `dateTimeSelected`: selected date/time. |
| `DigitalResource` | Digital content/resource. | `storageName`: file/system name; `creators`: creators; `mediaType`: IANA media type; `keywords`: tags; `learningObjectives`: objectives; `isPartOf`: parent resource; `datePublished`: publication time; `version`: version label. |
| `DigitalResourceCollection` | Collection of digital resources. | `items`: digital resources in the collection. |
| `Document` | Document resource. | No extra fields beyond base entity fields. |
| `FillinBlankResponse` | Fill-in-the-blank answer. | `values`: entered words/phrases. |
| `Forum` | Forum. | `items`: threads in the forum. |
| `Frame` | Segment/location in a resource. | `index`: non-negative position. |
| `Group` | Group context. | No extra fields beyond base entity fields. |
| `HighlightAnnotation` | Highlighted text annotation. | `selectionText`: highlighted text. |
| `ImageObject` | Image media. | No extra fields beyond base entity fields. |
| `LearningObjective` | Learning goal/objective. | No extra fields beyond base entity fields. Prefer CASE links when available. |
| `LikertScale` | Likert rating scale. | `scalePoints`: number of points; `itemLabels`: labels; `itemValues`: stored values. |
| `Link` | Web link. | No extra fields beyond base entity fields. |
| `LtiLink` | LTI launch/resource link. | `messageType`: LTI message type used. |
| `LtiSession` | LTI platform/tool session. | `messageParameters`: LTI message parameters/context. |
| `MediaLocation` | Point in media playback. | `currentTime`: playback position. |
| `MediaObject` | Audio/video/media resource. | `duration`: total media duration. |
| `Membership` | Person's relationship to a group/organization. | `organization`: organization/group; `member`: person; `roles`: role terms; `status`: active/inactive status. |
| `Message` | Forum/message post. | `replyTo`: prior message; `body`: message text; `attachments`: attached digital resources. |
| `MultipleChoiceResponse` | Single-choice answer. | `value`: selected option. |
| `MultipleResponseResponse` | Multi-select answer. | `values`: selected options. |
| `MultiselectQuestion` | Multiple-select question definition. | `points`: available points; `itemLabels`: option labels; `itemValues`: option values. |
| `MultiselectResponse` | Multiple-select response. | `selections`: selected values. |
| `MultiselectScale` | Multiple-select rating scale. | `scalePoints`: points; `itemLabels`: labels; `itemValues`: values; `isOrderedSelection`: whether order matters; `minSelections`/`maxSelections`: selection limits. |
| `NumericScale` | Numeric rating scale. | `minValue`/`maxValue`: numeric bounds; `minLabel`/`maxLabel`: labels; `step`: interval. |
| `OpenEndedQuestion` | Open-ended question. | No extra fields beyond base entity fields. |
| `OpenEndedResponse` | Open-ended text response. | `value`: response text. |
| `Organization` | School, district, provider, or other organization. | `subOrganizationOf`: parent organization; `members`: member agents. |
| `Page` | Page in a resource. | No extra fields beyond base entity fields. |
| `Person` | Human actor. | No extra fields beyond base entity fields; identifiers usually appear in `otherIdentifiers`. |
| `Query` | Search query. | `creator`: person who searched; `searchTarget`: thing being searched; `searchTerms`: search text. |
| `Question` | Question prompt. | `questionPosed`: question text. |
| `Questionnaire` | Questionnaire/survey instrument. | `items`: questionnaire items. |
| `QuestionnaireItem` | One questionnaire item. | `question`: question entity; `categories`: category labels; `weight`: item weight. |
| `Rating` | Rating feedback. | `rater`: person rating; `rated`: entity rated; `question`: question asked; `selections`: selected values; `ratingComment`: related comment. |
| `RatingScaleQuestion` | Rating scale question. | `scale`: scale used. |
| `RatingScaleResponse` | Rating scale response. | `selections`: selected response values. |
| `Response` | Learner response. | `attempt`: related attempt; `startedAtTime`/`endedAtTime`: response timing; `duration`: time taken. |
| `Result` | Result score/feedback. | `attempt`: related attempt; `maxResultScore`: maximum possible; `resultScore`: awarded result; `scoredBy`: scorer; `comment`: scorer feedback. |
| `Scale` | Generic scale. | No extra fields beyond base entity fields. |
| `Score` | Score generated by grading. | `attempt`: related attempt; `maxScore`: maximum possible; `scoreGiven`: score awarded; `scoredBy`: scorer; `comment`: scorer feedback. |
| `SearchResponse` | Search result summary. | `searchProvider`: app/provider; `searchTarget`: search target; `query`: submitted query; `searchResultsItemCount`: number of returned results. |
| `SelectTextResponse` | Selected text response. | `values`: selected options/text values. |
| `Session` | User/app session. | `user`: person; `client`: app; `startedAtTime`/`endedAtTime`: timing; `duration`: session length. |
| `SharedAnnotation` | Annotation shared with people. | `withAgents`: people/agents shared with. |
| `SoftwareApplication` | App/tool. | `host`: hosting service/domain; `ipAddress`: app/user-agent IP; `userAgent`: browser/app user agent; `version`: software version. |
| `Survey` | Survey. | `items`: questionnaire entities in the survey. |
| `SurveyInvitation` | Invitation to take a survey. | `rater`: invited person; `survey`: survey; `sentCount`: number of sends; `dateSent`: sent time. |
| `TagAnnotation` | Tag annotation. | `tags`: tag values. |
| `Thread` | Forum thread. | `items`: messages in the thread. |
| `TrueFalseResponse` | True/false response. | `value`: selected true/false or yes/no value. |
| `VideoObject` | Video media. | No extra fields beyond base entity fields. |
| `WebPage` | Web page. | No extra fields beyond base entity fields. |
| `TextPositionSelector` | Text-range selector without entity ID. | `type`: selector type; `start`: first character position; `end`: ending character position. |
| `SystemIdentifier` | Other system identifier without entity ID. | `type`: system identifier entity type; `identifierType`: kind of ID; `identifier`: ID value; `source`: source application; `extensions`: custom ID metadata. |

## Profile Values

| Value | Layperson meaning |
| --- | --- |
| `GeneralProfile` | Generic profile for events not covered by a narrower profile. |
| `AnnotationProfile` | Annotation, bookmark, highlight, share, and tag activity. |
| `AssessmentProfile` | Assessment and assessment-item activity. |
| `AssignableProfile` | Assignment/digital-resource work activity. |
| `FeedbackProfile` | Commenting and rating activity. |
| `ForumProfile` | Forum, thread, and message activity. |
| `GradingProfile` | Grading and score creation activity. |
| `MediaProfile` | Audio/video/media activity. |
| `ReadingProfile` | Reading/navigation/viewing resource activity. |
| `ResourceManagementProfile` | Resource creation, upload, publish, print, download, and similar management activity. |
| `SearchProfile` | Search activity. |
| `SessionProfile` | Login/logout/timeout session activity. |
| `SurveyProfile` | Survey and questionnaire activity. |
| `ToolLaunchProfile` | LTI/tool launch and return activity. |
| `ToolUseProfile` | Software application use metrics. |

## Action Values

| Value | Layperson meaning |
| --- | --- |
| `Abandoned` | A user abandoned something before completion. |
| `Accepted` | A user accepted an invitation/request. |
| `Activated` | Something was made active. |
| `Added` | Something was added. |
| `Archived` | A resource was archived. |
| `Attached` | Something was attached to another thing. |
| `Bookmarked` | A user created a bookmark. |
| `ChangedResolution` | Media resolution changed. |
| `ChangedSize` | Media display size changed. |
| `ChangedSpeed` | Media playback speed changed. |
| `ChangedVolume` | Media volume changed. |
| `Classified` | Something was classified/categorized. |
| `ClosedPopout` | A media popout/window was closed. |
| `Commented` | A user left a comment. |
| `Completed` | A user completed an item/task. |
| `Copied` | A resource was copied. |
| `Created` | A resource/entity was created. |
| `Deactivated` | Something was made inactive. |
| `Declined` | A user declined an invitation/request. |
| `Deleted` | A resource/entity was deleted. |
| `Described` | Metadata/description was added or changed. |
| `DisabledClosedCaptioning` | Closed captions were turned off. |
| `Disliked` | A user disliked something. |
| `Downloaded` | A resource was downloaded. |
| `EnabledClosedCaptioning` | Closed captions were turned on. |
| `Ended` | Activity/media ended. |
| `EnteredFullScreen` | Media entered full screen. |
| `ExitedFullScreen` | Media exited full screen. |
| `ForwardedTo` | Media playback moved forward. |
| `Graded` | An attempt was graded. |
| `Hid` | Something was hidden. |
| `Highlighted` | Text/resource content was highlighted. |
| `Identified` | Something was identified. |
| `JumpedTo` | Media/navigation jumped to a location. |
| `Launched` | A tool/app was launched. |
| `Liked` | A user liked something. |
| `Linked` | Something was linked. |
| `LoggedIn` | A user logged in. |
| `LoggedOut` | A user logged out. |
| `MarkedAsRead` | A message/thread was marked read. |
| `MarkedAsUnread` | A message/thread was marked unread. |
| `Modified` | A resource/entity was changed. |
| `Muted` | Media audio was muted. |
| `NavigatedTo` | A user navigated to a resource/location. |
| `OpenedPopout` | A media popout/window was opened. |
| `OptedIn` | A user opted in. |
| `OptedOut` | A user opted out. |
| `Paused` | Activity/media was paused. |
| `Posted` | A message was posted. |
| `Printed` | A resource was printed. |
| `Published` | A resource was published. |
| `Questioned` | A question was asked. |
| `Ranked` | A user rated/ranked something. |
| `Recommended` | Something was recommended. |
| `Removed` | Something was removed. |
| `Reset` | Activity or attempt was reset. |
| `Restarted` | Activity/media restarted. |
| `Restored` | A resource was restored. |
| `Resumed` | Activity/media resumed. |
| `Retrieved` | A resource was retrieved. |
| `Returned` | A user returned from a launched tool/workflow. |
| `Reviewed` | A user reviewed something. |
| `Rewound` | Media playback moved backward. |
| `Saved` | A resource/work item was saved. |
| `Searched` | A user performed a search. |
| `Sent` | A message/invitation was sent. |
| `Shared` | Something was shared. |
| `Showed` | Something was shown. |
| `Skipped` | A learner skipped an item/task. |
| `Started` | A learner/user started something. |
| `Submitted` | Work or an attempt was submitted. |
| `Subscribed` | A user subscribed. |
| `Tagged` | A user added tags. |
| `TimedOut` | A session timed out. |
| `Unmuted` | Media audio was unmuted. |
| `Unpublished` | A resource was unpublished. |
| `Unsubscribed` | A user unsubscribed. |
| `Uploaded` | A resource/file was uploaded. |
| `Used` | A user used a tool/application. |
| `Viewed` | A user viewed something. |

## Role, Status, and Identifier Values

### LIS Role Values

| Value | Layperson meaning |
| --- | --- |
| `Administrator` | Administrative role. |
| `ContentDeveloper` | Content author/developer role. |
| `Instructor` | Teacher/instructor role. |
| `Learner` | Student/learner role. |
| `Manager` | Manager role. |
| `Member` | General member role. |
| `Mentor` | Mentor/advisor/support role. |
| `Officer` | Officer/official role. |

### LIS Status Values

| Value | Layperson meaning |
| --- | --- |
| `Active` | The membership/status is active. |
| `Inactive` | The membership/status is inactive. |

### LTI Message Type Values

| Value | Layperson meaning |
| --- | --- |
| `LtiDeepLinkingRequest` | LTI deep-linking content selection launch. |
| `LtiResourceLinkRequest` | Normal LTI resource link launch. |

### System Identifier Type Values

| Value | Layperson meaning |
| --- | --- |
| `AccountUserName` | Account username. |
| `EmailAddress` | Email address. |
| `LisSourcedId` | LIS source identifier. |
| `LtiContextId` | LTI context/course ID. |
| `LtiDeploymentId` | LTI deployment ID. |
| `LtiPlatformId` | LTI platform ID. |
| `LtiToolId` | LTI tool ID. |
| `LtiUserId` | LTI user ID. |
| `OneRosterSourcedId` | OneRoster sourcedId. |
| `Other` | Other identifier type. |
| `SisSourcedId` | Student information system sourced ID. |
| `SystemId` | Internal system ID. |

### Use Metric Values

| Value | Layperson meaning |
| --- | --- |
| `AssessmentsPassed` | Count of assessments passed. |
| `AssessmentsSubmitted` | Count of assessments submitted. |
| `MinutesOnTask` | Minutes spent on task. |
| `SkillsMastered` | Count of skills mastered. |
| `StandardsMastered` | Count of standards mastered. |
| `UnitsCompleted` | Count of units completed. |
| `UnitsPassed` | Count of units passed. |
| `WordsRead` | Count of words read. |

## Cross-Standard Links

| Link | Plain meaning | Platform guidance |
| --- | --- | --- |
| Caliper actor to OneRoster user/person | The event actor is a known school user. | Resolve by LTI, OneRoster, SIS, email, or local source identifier. |
| Caliper group/membership to OneRoster class/org | The event happened in a class, course, or organization context. | Use OneRoster as the authoritative roster context when available. |
| Caliper assessment object to QTI item/test | The event happened inside a QTI assessment or item. | Link Caliper `Assessment`/`AssessmentItem` IDs to QTI content IDs. |
| Caliper learning objective to CASE item | Activity relates to a standard/competency. | Prefer CASE UUID/URI for durable alignment. |
| Caliper score/result to OneRoster gradebook | Analytics/grading event corresponds to gradebook result. | Keep event lineage separate from official gradebook result. |
| Caliper LTI session to LTI launch | Event was generated in an LTI launch workflow. | Store LTI session identifiers and message parameters under integration governance. |

