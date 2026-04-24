# OneRoster 1.2 Layperson Data Dictionary

Research date: 2026-04-24

Sources:

- OneRoster 1.2 overview: https://www.imsglobal.org/spec/oneroster/v1p2/
- Rostering information model: https://www.imsglobal.org/spec/oneroster/v1p2/rostering/info
- Gradebook information model: https://www.imsglobal.org/spec/oneroster/v1p2/gradebook/info
- Resources information model: https://www.imsglobal.org/spec/oneroster/v1p2/resource/info
- CSV binding: https://www.imsglobal.org/spec/oneroster/v1p2/bind/csv/

## How to Read This Dictionary

OneRoster is mostly about moving K-12 operational data between systems. In plain terms, it answers:

- What schools and districts exist?
- What school year, term, semester, or grading period is active?
- Which courses and classes exist?
- Which students and teachers are in each class?
- Which assignments, scores, and gradebook categories exist?
- Which learning resources are assigned to classes, courses, or users?

The platform should keep OneRoster's standard fields, but explain them in friendlier names and protect them with privacy rules.

## Common Fields on Most OneRoster Records

OneRoster calls these common fields the base fields. They appear on most first-class records.

| OneRoster field | Plain name | Required | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- | --- |
| `sourcedId` | Source record ID | Yes | Operational, sometimes education record | The ID that the sending system uses for this exact record. | Store it in `source_identifier`. Do not use it as the platform primary key because different systems can use different IDs. |
| `status` | Record status | Yes | Operational | Whether the record is active or marked for deletion. | Keep active records available. Treat `tobedeleted` as a delete/tombstone signal, not as proof that historical records should disappear everywhere. |
| `dateLastModified` | Last changed time | Yes | Operational | When the source system says the record last changed. | Use for incremental imports and sync troubleshooting. |
| `metadata` | Extra metadata | Optional | Depends on contents | Extra information added by a local implementation. | Store as namespaced extension data. Do not depend on it for core platform behavior unless governed. |

### Common Status Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `active` | The record is currently usable. | Default state for normal records. |
| `tobedeleted` | The source system says the record can be deleted. | Treat as a deletion signal. Preserve audit and lineage. |

## Reference Objects

OneRoster frequently uses reference objects instead of embedding a full object.

| Field | Plain name | Required | Layperson meaning |
| --- | --- | --- | --- |
| `href` | Link URL | Yes on generic references | A URL that can be used to fetch or identify the referenced object. |
| `sourcedId` | Referenced source ID | Yes | The source ID of the object being referenced. |
| `type` | Referenced object type | Yes on typed references | Says whether the referenced object is a class, course, org, user, line item, score scale, or another known object. |

Common reference `type` values:

| Value | Meaning |
| --- | --- |
| `academicSession` | Points to a school year, term, semester, or grading period. |
| `class` | Points to a scheduled class section. |
| `course` | Points to a course definition. |
| `org` | Points to a school, district, department, or other organization. |
| `resource` | Points to a learning resource description. |
| `user` | Points to a person/user record. |
| `category` | Points to a gradebook category. |
| `lineItem` | Points to a gradebook assignment/line item. |
| `assessmentLineItem` | Points to an assessment line item, often outside a normal class gradebook. |
| `scoreScale` | Points to a score scale mapping. |

## Academic Session

An academic session is a time period used by a school, such as a school year, term, semester, or grading period.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Session name | Yes | Directory | The label people use, such as "2026 Spring Semester" or "Quarter 1". |
| `startDate` | Start date | Yes | Directory | The first date included in the session. |
| `endDate` | End date | Yes | Directory | The date when the session stops being active. |
| `type` | Session type | Yes | Directory | The kind of school time period this is. |
| `parent` | Parent session | Optional | Directory | A larger time period that contains this one, such as a school year containing a semester. |
| `children` | Child sessions | Optional, many | Directory | Smaller time periods inside this one, such as grading periods inside a term. |
| `schoolYear` | School year | Yes | Directory | The calendar year that identifies the school year, usually the ending year. |

### Academic Session Type Values

| Value | Layperson meaning |
| --- | --- |
| `schoolYear` | The full school year. |
| `semester` | A large part of the school year, often one of two halves. |
| `term` | A school term. Some schools use terms instead of semesters. |
| `gradingPeriod` | A period used for grading assignments and results. |

## Organization

An organization is a district, school, department, state agency, national agency, or similar education organization.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `name` | Organization name | Yes | Directory | The name of the school, district, department, or agency. |
| `type` | Organization type | Yes | Directory | The kind of organization. |
| `identifier` | Human-readable organization ID | Yes | Directory or operational | A familiar outside ID, such as a state ID or NCES ID. |
| `parent` | Parent organization | Optional | Directory | The larger organization this one belongs to, such as a district above a school. |
| `children` | Child organizations | Optional, many | Directory | Smaller organizations underneath this one, such as schools in a district. |

### Organization Type Values

| Value | Layperson meaning |
| --- | --- |
| `department` | A department or subdivision inside an organization, such as Mathematics. |
| `district` | A school district. |
| `local` | A local education organization. Older OneRoster integrations may use this for districts. |
| `national` | A national-level organization. |
| `school` | A school where learning happens. Classes and enrollments usually attach here. |
| `state` | A state-level organization. |

## Course

A course is the shared course definition, not one specific scheduled class. For example, "Grade 9 English" is a course; Period 2 Grade 9 English is a class.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Course title | Yes | Directory | The course name people recognize. |
| `schoolYear` | Course school year | Optional | Directory | The school year this course belongs to. |
| `courseCode` | Course code | Yes | Directory | The local course code used by the school or district. |
| `grades` | Intended grade levels | Optional, many | Directory | The grade levels this course is intended for. |
| `subjects` | Subject names | Optional, many | Directory | Human-readable subject labels such as English or Chemistry. |
| `org` | Owning organization | Optional | Directory | The school, district, or department that owns this course. |
| `subjectCodes` | Subject codes | Optional, many | Directory | Machine-readable codes that match the subject names. |
| `resources` | Linked resources | Optional, many | Education record or operational | Learning resources associated with the course. |

## Class

A class is a scheduled instance of a course that students and teachers join. A course can have many classes.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Class title | Yes | Directory | The class name shown to users. |
| `classCode` | Class code | Optional | Directory | A local code for the scheduled class. |
| `classType` | Class type | Optional | Directory | Whether this is a normal scheduled class or a homeroom. |
| `location` | Location | Optional | Directory | Where the class meets, such as Room 19 or an online location. |
| `grades` | Grade levels in class | Optional, many | Education record | The grade levels of students in this class. |
| `subjects` | Subject names | Optional, many | Directory | Human-readable subject labels for the class. |
| `course` | Course | Yes | Directory | The course this class is an instance of. |
| `school` | School | Yes | Directory | The school where this class belongs. |
| `terms` | Terms | Yes, many | Directory | The terms or semesters when the class takes place. |
| `subjectCodes` | Subject codes | Optional, many | Directory | Machine-readable subject codes matching the subject names. |
| `periods` | Periods | Optional, many | Directory | Timetable periods, such as 1, 3, or 5. |
| `resources` | Linked resources | Optional, many | Education record or operational | Learning resources assigned to the class. |

### Class Type Values

| Value | Layperson meaning |
| --- | --- |
| `homeroom` | A homeroom or advisory-style class. |
| `scheduled` | A normal scheduled class from the timetable. |

## User

A user is a person known to the education environment. OneRoster uses the same `User` object for students, teachers, staff, guardians, and other people. Roles explain what the person does.

| Field | Plain name | Required | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- | --- |
| `userMasterIdentifier` | Master person ID | Optional | Education record | A stable person identifier used to match the same person across systems. | Treat as sensitive matching data. |
| `username` | Username | Optional | Directory or sensitive | The login name assigned to the user. | Legacy field; prefer governed profile/account records. |
| `userIds` | External user IDs | Optional, many | Education record | Other machine-readable IDs for this person. | Store in `source_identifier` with source system and type. |
| `enabledUser` | Login enabled | Yes | Education record | Whether the user account is enabled in the local system. | Do not confuse with OneRoster `status`; a user can be an active record but disabled for login. |
| `givenName` | First name | Yes | Directory | The person's first/given name. | Follow tenant directory policy. |
| `familyName` | Last name | Yes | Directory | The person's last/family name. | Follow tenant directory policy. |
| `middleName` | Middle name | Optional | Directory | The person's middle name or names. | Some districts avoid sharing this. |
| `preferredFirstName` | Preferred first name | Optional | Directory | The first name the person prefers to use. | Prefer for display when allowed. |
| `preferredMiddleName` | Preferred middle name | Optional | Directory | The middle name the person prefers to use. | Use only where display needs it. |
| `preferredLastName` | Preferred last name | Optional | Directory | The last name the person prefers to use. | Use only where display needs it. |
| `pronouns` | Pronouns | Optional | Sensitive | The pronouns the person uses. | Treat as sensitive directory data; share only when authorized. |
| `roles` | Organization roles | Yes, many | Education record | The person's role or roles in specific organizations. | A user can have different roles in different organizations. |
| `userProfiles` | Tool/app profiles | Optional, many | Sensitive | Account/profile records for external tools or systems. | Do not expose broadly. |
| `primaryOrg` | Primary organization | Optional | Education record | The main organization for the user. | Useful for default school or district context. |
| `identifier` | Legacy user identifier | Optional | Education record | Older OneRoster-style identifier for a user. | Keep for compatibility; prefer `userIds`. |
| `email` | Email | Optional | Directory | The user's email address. | Share only with apps allowed to contact or identify the user. |
| `sms` | SMS number | Optional | Sensitive | A phone number for text messages. | Treat as sensitive contact data. |
| `phone` | Phone number | Optional | Sensitive | A phone number for the user. | Treat as sensitive contact data. |
| `agents` | Related people | Optional, many | Education record | Other people connected to this user, often guardians for a student. | Relationship direction can be subtle; document it in API responses. |
| `grades` | Student grade levels | Optional, many | Education record | Grade levels for a user when the user is a student. | Do not use for non-students unless tenant policy defines it. |
| `password` | Password | Optional | Sensitive | A password value. | Do not store or expose plaintext passwords. Prefer not to support this field except for tightly controlled legacy import. |
| `resources` | User resources | Optional, many | Education record | Learning resources assigned directly to the user. | Often better represented through resource allocation tables. |

## User ID

`UserId` records hold external identifiers for a user.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `type` | ID type | Yes | Operational | What kind of outside ID this is, such as SIS ID, LTI ID, or Active Directory ID. |
| `identifier` | ID value | Yes | Education record | The actual identifier value. |

## User Profile

A user profile describes an account or profile a user has in a particular system, app, or tool.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `profileId` | Profile ID | Yes | Sensitive | The ID for this user's profile in a tool or system. |
| `profileType` | Profile type | Yes | Sensitive | A label for the kind of profile or account. |
| `vendorId` | Vendor ID | Yes | Operational | The vendor that owns or uses this profile. |
| `applicationId` | Application ID | Optional | Operational | The specific application associated with the profile. |
| `description` | Profile description | Optional | Sensitive | Human-readable notes about what the profile is for. |
| `credentials` | Credentials | Optional, many | Sensitive | Login credential records for this profile. |

## Credential

A credential is a login credential for a profile. This is high-risk data.

| Field | Plain name | Required | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- | --- |
| `type` | Credential type | Yes | Sensitive | What kind of credential this is. | Use only for legacy compatibility. |
| `username` | Credential username | Yes | Sensitive | The username for this credential set. | Avoid exposing in APIs unless there is a clear need. |
| `password` | Credential password | Optional | Sensitive | The password for the credential set. | Do not store plaintext. Prefer not to ingest. |
| `extensions` | Credential extensions | Optional, many | Sensitive | Vendor-specific credential details. | Must be explicitly reviewed before use. |

## Role

A role says what a user does in an organization.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `roleType` | Primary or secondary role | Yes | Education record | Whether this role is the user's main role for the organization. |
| `role` | Role | Yes | Education record | The user's job or relationship in the organization. |
| `org` | Organization | Yes | Education record | The organization where the user has this role. |
| `userProfile` | Related user profile | Optional | Sensitive | The tool/app profile that applies to this role. |
| `beginDate` | Role start date | Optional | Education record | The first date the role is active. |
| `endDate` | Role end date | Optional | Education record | The date the role stops being active. |

### Role Type Values

| Value | Layperson meaning |
| --- | --- |
| `primary` | The user's main role for that organization. |
| `secondary` | Another role the user also has in that organization. |

### User Role Values

| Value | Layperson meaning |
| --- | --- |
| `aide` | A person who helps a user but is not better described by another listed role. |
| `counselor` | A counselor or pastoral-care staff member. |
| `districtAdministrator` | A district-level administrator. |
| `guardian` | A guardian of a learner who is not simply listed as parent. |
| `parent` | A parent of a learner. |
| `principal` | The principal or very senior school administrator. |
| `proctor` | A person supervising an exam or assessment. |
| `relative` | A learner's relative who is not a parent. |
| `siteAdministrator` | A school/site administrator. |
| `student` | A learner. |
| `systemAdministrator` | A system administrator for school systems. |
| `teacher` | A teacher. |

## Demographics

Demographics are highly sensitive. In OneRoster, this data is separated because not every app should be allowed to request it.

| Field | Plain name | Required | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- | --- |
| `birthDate` | Birth date | Optional | Sensitive | The user's date of birth. | Restrict strongly. |
| `sex` | Sex/gender category | Optional | Sensitive | The sex/gender value supplied by the source. | Preserve source meaning; do not infer identity from it. |
| `americanIndianOrAlaskaNative` | American Indian or Alaska Native indicator | Optional | Sensitive | Whether the record indicates this race category. | Use only for authorized reporting. |
| `asian` | Asian indicator | Optional | Sensitive | Whether the record indicates this race category. | Use only for authorized reporting. |
| `blackOrAfricanAmerican` | Black or African American indicator | Optional | Sensitive | Whether the record indicates this race category. | Use only for authorized reporting. |
| `nativeHawaiianOrOtherPacificIslander` | Native Hawaiian or Other Pacific Islander indicator | Optional | Sensitive | Whether the record indicates this race category. | Use only for authorized reporting. |
| `white` | White indicator | Optional | Sensitive | Whether the record indicates this race category. | Use only for authorized reporting. |
| `demographicRaceTwoOrMoreRaces` | Two or more races indicator | Optional | Sensitive | Whether the record indicates two or more race categories. | Use only for authorized reporting. |
| `hispanicOrLatinoEthnicity` | Hispanic or Latino ethnicity indicator | Optional | Sensitive | Whether the record indicates Hispanic or Latino ethnicity. | Use only for authorized reporting. |
| `countryOfBirthCode` | Country of birth code | Optional | Sensitive | Code for the country where the user was born. | Use only when required and authorized. |
| `stateOfBirthAbbreviation` | State of birth | Optional | Sensitive | State or extra-state jurisdiction where the user was born. | Use only when required and authorized. |
| `cityOfBirth` | City of birth | Optional | Sensitive | City where the user was born. | Use only when required and authorized. |
| `publicSchoolResidenceStatus` | Public school residence status | Optional | Sensitive | Whether the user's legal residence is inside or outside relevant public school boundaries. | Use only when required and authorized. |

### Sex/Gender Values

| Value | Layperson meaning |
| --- | --- |
| `female` | The source records the person as female. |
| `male` | The source records the person as male. |
| `other` | The source records a known value that is not male or female. |
| `unspecified` | No value was entered or supplied. |

### Boolean Values

| Value | Layperson meaning |
| --- | --- |
| `true` | Yes, the statement is true. |
| `false` | No, the statement is false. |

## Enrollment

An enrollment connects a user to a class with a role, usually student or teacher.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `user` | Enrolled user | Yes | Education record | The person participating in the class. |
| `class` | Class | Yes | Education record | The class the person is participating in. |
| `school` | School | Yes | Education record | The school where the class is provided. |
| `role` | Class role | Yes | Education record | What the person does in this class. |
| `primary` | Primary teacher flag | Optional | Education record | For teachers, whether this teacher is the main teacher for the class. |
| `beginDate` | Enrollment start date | Optional | Education record | The first date the enrollment is active. |
| `endDate` | Enrollment end date | Optional | Education record | The date the enrollment stops being active. |

### Enrollment Role Values

| Value | Layperson meaning |
| --- | --- |
| `administrator` | A person with administrative responsibility for the class. |
| `proctor` | A person supervising an assessment or exam in the class. |
| `student` | A learner enrolled in the class. |
| `teacher` | A teacher assigned to the class. |

## Resource

A resource is a description of learning content used by a course, class, or user. OneRoster resource records describe the resource; they do not necessarily contain the resource itself.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Resource title | Optional | Directory | The human-readable name of the learning resource. |
| `roles` | Intended roles | Optional, many | Directory | Which kinds of users are expected to use the resource. |
| `importance` | Resource importance | Optional | Directory | Whether this is a primary or secondary resource. |
| `vendorResourceId` | Vendor resource ID | Yes | Operational | The vendor's unique ID for the resource. |
| `vendorId` | Vendor ID | Optional | Operational | The vendor that created or supplies the resource. |
| `applicationId` | Application ID | Optional | Operational | The specific app associated with the resource. |

### Resource Importance Values

| Value | Layperson meaning |
| --- | --- |
| `primary` | A main resource for the learning experience. |
| `secondary` | A supporting or optional resource. |

### Resource Role Values

| Value | Layperson meaning |
| --- | --- |
| `administrator` | Intended for an administrator. |
| `aide` | Intended for an aide. |
| `guardian` | Intended for a guardian. |
| `parent` | Intended for a parent. |
| `proctor` | Intended for a proctor. |
| `relative` | Intended for a relative. |
| `student` | Intended for a student. |
| `teacher` | Intended for a teacher. |

## Gradebook Category

A category groups gradebook line items. For example, homework, quizzes, tests, or projects.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Category title | Yes | Education record | The category name shown in the gradebook. |
| `weight` | Category weight | Optional | Education record | How much this category counts toward a final score. |

## Line Item

A line item is a gradebook assignment or activity that students complete and receive results for.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Assignment title | Yes | Education record | The name of the assignment or activity. |
| `description` | Assignment description | Optional | Education record | Notes explaining the assignment or its purpose. |
| `assignDate` | Assigned time | Yes | Education record | When the assignment was assigned. |
| `dueDate` | Due time | Yes | Education record | When the assignment is due. |
| `class` | Class | Yes | Education record | The class receiving the assignment. |
| `school` | School | Yes | Education record | The school connected to the assignment. |
| `category` | Gradebook category | Yes | Education record | The category this assignment belongs to. |
| `gradingPeriod` | Grading period | Optional | Education record | The grading period for this assignment. |
| `academicSession` | Academic session | Optional | Education record | The broader academic session when no grading period is used. |
| `scoreScale` | Score scale | Optional | Education record | The score scale used to interpret scores. |
| `resultValueMin` | Minimum score | Optional | Education record | The smallest numeric score allowed for results. |
| `resultValueMax` | Maximum score | Optional | Education record | The largest numeric score allowed for results. |
| `learningObjectiveSet` | Learning objectives | Optional, many | Education record | Standards or learning goals the assignment is aligned to. |

## Result

A result is a student's score or status for one line item.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `lineItem` | Line item | Yes | Education record | The assignment or activity being scored. |
| `student` | Student | Yes | Education record | The learner receiving the result. |
| `class` | Class | Optional | Education record | The class context for the result. |
| `scoreScale` | Score scale | Optional | Education record | The scale used to interpret the score. |
| `scoreStatus` | Score status | Yes | Education record | Whether the work is submitted, graded, exempt, or in another score state. |
| `score` | Numeric score | Optional | Education record | The numeric score. |
| `textScore` | Text score | Optional | Education record | A non-numeric score such as a letter, level, or rubric value. |
| `scoreDate` | Score date | Yes | Education record | The date when the score or score status was assigned or updated. |
| `comment` | Score comment | Optional | Education record | Teacher or system comment about the result. |
| `learningObjectiveSet` | Learning objective scores | Optional, many | Education record | Standards or competencies connected to this result, possibly with mastery scores. |
| `inProgress` | In progress flag | Optional | Education record | The work has been assigned and is not expected to be submitted yet. |
| `incomplete` | Incomplete flag | Optional | Education record | The work was submitted but is not complete. |
| `late` | Late flag | Optional | Education record | The work was submitted late or is past due. |
| `missing` | Missing flag | Optional | Education record | The work has not been submitted. |

### Score Status Values

| Value | Layperson meaning |
| --- | --- |
| `exempt` | The result does not count toward a summary/final score. |
| `fully graded` | Grading is complete and the score can be used. |
| `not submitted` | The learner has not submitted the work. |
| `partially graded` | Grading has started but is not complete, so it should not be used as final. |
| `submitted` | The learner submitted the work, but it has not been graded yet. |

## Learning Objective Set

A learning objective set records which standards, competencies, or learning objectives an assignment, assessment, or result relates to.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `source` | Objective source | Yes | Education record | Who created the objective identifiers. |
| `learningObjectiveIds` | Objective IDs | Yes, many | Education record | The specific standards or competency IDs. |

### Objective Source Values

| Value | Layperson meaning |
| --- | --- |
| `case` | The IDs are CASE identifiers. |
| `unknown` | The system does not know who created the IDs. |
| extension value | A local or vendor-specific source. | Use a namespaced value so it will not be confused with official values. |

## Learning Objective Results

This records mastery scores for specific standards or competencies.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `learningObjectiveId` | Learning objective ID | Yes | Education record | The standard, competency, or objective being scored. |
| `score` | Numeric mastery score | Optional | Education record | Numeric mastery score for that objective. |
| `textScore` | Text mastery score | Optional | Education record | Non-numeric mastery score, such as mastered or developing. |

## Assessment Line Item

An assessment line item is like a gradebook line item, but it can represent assessment structures that are not tied to a normal class assignment.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Assessment line item title | Yes | Education record | The name of this assessment scoring item. |
| `description` | Description | Optional | Education record | Notes explaining the assessment line item. |
| `class` | Class | Optional | Education record | A class connected to the assessment line item, if any. |
| `parentAssessmentLineItem` | Parent assessment line item | Optional | Education record | The larger assessment line item above this one. |
| `scoreScale` | Score scale | Optional | Education record | The scale used to interpret scores. |
| `resultValueMin` | Minimum score | Optional | Education record | The smallest numeric score allowed. |
| `resultValueMax` | Maximum score | Optional | Education record | The largest numeric score allowed. |
| `learningObjectiveSet` | Learning objectives | Optional, many | Education record | Standards or learning goals this assessment line item measures. |

## Assessment Result

An assessment result is a student's score/status for an assessment line item.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `assessmentLineItem` | Assessment line item | Yes | Education record | The assessment scoring item being reported. |
| `student` | Student | Yes | Education record | The learner receiving the result. |
| `score` | Numeric score | Optional | Education record | Numeric score for the assessment result. |
| `textScore` | Text score | Optional | Education record | Non-numeric score value. |
| `scoreDate` | Score date | Yes | Education record | The date when the score or score status was assigned or updated. |
| `scoreScale` | Score scale | Optional | Education record | The scale used to interpret the score. |
| `scorePercentile` | Percentile | Optional | Education record | The percentile rank of the score. |
| `scoreStatus` | Score status | Yes | Education record | Whether the work is submitted, graded, exempt, or in another score state. |
| `comment` | Score comment | Optional | Education record | Comment about the result. |
| `learningObjectiveSet` | Learning objective scores | Optional, many | Education record | Standards or competencies connected to this result, possibly with mastery scores. |
| `inProgress` | In progress flag | Optional | Education record | The work is underway and not expected to be submitted yet. |
| `incomplete` | Incomplete flag | Optional | Education record | The submitted work is incomplete. |
| `late` | Late flag | Optional | Education record | The work is late or past due. |
| `missing` | Missing flag | Optional | Education record | The work has not been submitted. |

## Score Scale

A score scale explains how to map one score value or range to another, such as numeric points to a letter grade.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `title` | Score scale title | Yes | Education record | The name of the score scale. |
| `type` | Score scale type | Yes | Education record | A local label for what kind of scale this is. |
| `course` | Course | Optional | Education record | The course this score scale applies to. |
| `class` | Class | Yes | Education record | The class this score scale applies to. |
| `scoreScaleValue` | Score scale values | Yes, many | Education record | The mappings that make up the scale. |

## Score Scale Value

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `itemValueLHS` | Source score value | Yes | Education record | The score or score range being mapped from, such as 90-100. |
| `itemValueRHS` | Mapped score value | Yes | Education record | The value being mapped to, such as A. |

## API Status Objects

OneRoster responses can include status objects for failed or partial operations. These are operational records, not school domain records.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `imsx_codeMajor` | Major status | Yes | Operational | Broad result of the API request. |
| `imsx_severity` | Severity | Yes | Operational | Whether the status is informational, warning, or error. |
| `imsx_description` | Status description | Optional | Operational | Human-readable details about the status. |
| `imsx_CodeMinor` | Minor status details | Optional | Operational | More specific status codes. |
| `imsx_codeMinorFieldName` | Minor status source | Yes inside a minor field | Operational | The system or component reporting the minor status. |
| `imsx_codeMinorFieldValue` | Minor status value | Yes inside a minor field | Operational | The specific minor status code. |

### Major Status Values

| Value | Layperson meaning |
| --- | --- |
| `success` | The request succeeded. |
| `processing` | The request is being processed. |
| `failure` | The request failed. |
| `unsupported` | The request or feature is not supported. |

### Severity Values

| Value | Layperson meaning |
| --- | --- |
| `status` | Informational status. |
| `warning` | Something may need attention, but it is not a complete failure. |
| `error` | Something failed. |

### Common Minor Status Values

| Value | Layperson meaning |
| --- | --- |
| `fullsuccess` | The whole operation succeeded. |
| `unknownobject` | The requested record could not be found. |
| `invaliddata` | The request contained invalid data. |
| `forbidden` | The requester is not allowed to do this. |
| `unauthorisedrequest` | The requester is not properly authorized. |
| `server_busy` | The server is busy. |
| `internal_server_error` | The server failed unexpectedly. |
| `invalid_filter_field` | The filter named a field that cannot be filtered. |
| `invalid_selection_field` | The fields request named a field that cannot be selected. |
| `invalid_sort_field` | The sort request named a field that cannot be sorted. |
| `deletefailure` | A delete operation failed. |
| `unsupported` | The specific requested feature is unsupported. |

## Platform Modeling Notes

- Use internal UUIDs for primary keys. Keep `sourcedId` in identifier crosswalk tables.
- Treat demographics, pronouns, contact details, credentials, passwords, and raw grade/result data as restricted data.
- Do not store plaintext `password` values. If legacy ingestion requires the field, isolate and encrypt it or reject it by policy.
- CASE identifiers inside learning objective fields should connect to the platform CASE graph.
- OneRoster resource records describe resources. They are not a substitute for Common Cartridge, QTI packages, or actual content storage.
- Score status and work-state flags are different. For example, a result can be `submitted` and also `late`.
