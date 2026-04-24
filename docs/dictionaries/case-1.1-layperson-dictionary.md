# CASE 1.1 Layperson Data Dictionary

Research date: 2026-04-24

Sources:

- CASE overview: https://www.1edtech.org/standards/case
- CASE 1.1 information model: https://www.imsglobal.org/sites/default/files/spec/case/v1p1/information_model/caseservicev1p1_infomodelv1p0.html
- CASE 1.1 REST binding: https://www.imsglobal.org/sites/default/files/spec/case/v1p1/rest_binding/caseservicev1p1_restbindv1p0.html

## What CASE Does

CASE is the platform's standards and competency graph.

In plain terms, CASE lets a standards publisher, state agency, institution, workforce body, or district publish an official digital framework of:

- Academic standards.
- Competencies.
- Skills.
- Learning objectives.
- Course codes or other framework item types.
- Rubrics and rubric levels.
- Relationships between items and frameworks.

The platform should use CASE identifiers as the backbone for connecting content, assessments, assignments, results, credentials, and analytics to the same learning goals.

## Platform Modeling Guidance

Use the package-level objects as the storage model:

- `CFPackage` becomes a standards framework package.
- `CFPckgDocument` becomes the root framework document.
- `CFPckgItem` becomes a framework item, such as a standard, competency, skill, learning objective, or course code.
- `CFPckgAssociation` becomes a relationship edge between framework documents/items.
- `CFDefinition` and its child records become lookup definitions used by the framework.
- `CFRubric`, `CFRubricCriterion`, and `CFRubricCriterionLevel` become rubric structures.

Standalone `CFDocument`, `CFItem`, and `CFAssociation` records mostly point to the package form and are useful for API exchange, but the platform should normalize around the package form.

## Common CASE Field Concepts

| CASE field | Plain name | Privacy | Layperson meaning | Platform guidance |
| --- | --- | --- | --- | --- |
| `identifier` | CASE UUID | Public or directory | The official globally unique ID for this CASE object. | Store as an external identifier and keep stable forever. |
| `uri` | CASE URI | Public or directory | A web-resolvable identifier for the object. | Store and expose when available; use for linked data and cross-system references. |
| `lastChangeDateTime` | Last changed time | Operational | When the publisher last changed this object. | Use for sync, versioning, and cache invalidation. |
| `extensions` | Extensions | Depends on contents | Extra fields supplied by the publisher or implementation. | Store as governed namespaced extension data. |
| `LinkURI` | Link to another CASE object | Public or directory | A URI plus enough context to point at another object. | Resolve to platform object IDs when possible, but preserve the original URI. |

## CFPackage

A CASE package is the full bundle for one framework: the root document, all framework items, relationship edges, definitions, and rubrics.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `CFDocument` | Root framework document | Yes | Public or directory | The main standards or competency document for this package. |
| `CFItems` | Framework items | Optional, many | Public or directory | The standards, competencies, skills, objectives, course codes, or grouping nodes inside the framework. |
| `CFAssociations` | Framework relationships | Optional, many | Public or directory | Links that explain how framework items relate to each other or to other frameworks. |
| `CFDefinitions` | Framework definitions | Optional | Public or directory | Shared lookup definitions used by the framework, such as subjects, concepts, item types, association groups, and licenses. |
| `CFRubrics` | Rubrics | Optional, many | Public or directory | Rubrics connected to the framework. |
| `extensions` | Package extensions | Optional | Depends on contents | Extra package-level data supplied by the publisher. |

## CFPckgDocument

A framework document is the root of a CASE framework. Examples: a state's Grade 6 Math Standards, a district course catalog, or a workforce skill framework.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Framework document ID | Yes | Public or directory | The official CASE UUID for this framework document. |
| `uri` | Framework document URI | Yes | Public or directory | A web identifier for this framework document. |
| `frameworkType` | Framework type | Optional | Public or directory | What kind of framework this is, such as academic standards or course codes. |
| `caseVersion` | CASE version | Optional | Operational | The CASE version used by the document. In CASE 1.1 this may be `1.1`. |
| `creator` | Creator | Yes | Public | The organization with authority over the framework. |
| `title` | Framework title | Yes | Public | The name of the framework document. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the framework document last changed. |
| `officialSourceURL` | Official source URL | Optional | Public | A link to the human-readable official source document. |
| `publisher` | Publisher | Optional | Public | The organization that makes the framework available. |
| `description` | Description | Optional | Public | A summary of what the framework covers. |
| `subject` | Subjects | Optional, many | Public | Subject labels such as Mathematics, Reading, or Biology. |
| `subjectURI` | Subject URIs | Optional, many | Public | Linked subject identifiers supplied by the publisher. |
| `language` | Language | Optional | Public | Default language used in the framework text. |
| `version` | Publisher version | Optional | Public | The publisher's revision/version label for the framework. |
| `adoptionStatus` | Adoption status | Optional | Public | Local publication or adoption status, such as draft, adopted, retired, or superseded. |
| `statusStartDate` | Status start date | Optional | Public | When the adoption/publication status began. |
| `statusEndDate` | Status end date | Optional | Public | When the adoption/publication status ended or changed. |
| `licenseURI` | License link | Optional | Public | Link to legal permissions for using the framework. |
| `notes` | Notes | Optional | Public | Publisher comments or explanatory notes. |
| `extensions` | Document extensions | Optional | Depends on contents | Extra document data supplied by the publisher. |

### CASE Version Values

| Value | Layperson meaning |
| --- | --- |
| `1.1` | The framework document uses CASE 1.1 rules. |

## CFPckgItem

A framework item is one node in the framework. It may be a standard, competency, skill, learning objective, course code, strand, domain, cluster, or other grouping.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Framework item ID | Yes | Public or directory | The official CASE UUID for this item. |
| `fullStatement` | Full statement | Yes | Public | The complete text of the standard, competency, skill, objective, or grouping statement. |
| `alternativeLabel` | Alternate label | Optional | Public | Another word the publisher uses for this kind of item, such as outcome or objective. |
| `CFItemType` | Item type label | Optional | Public | Publisher label for what kind of item this is. |
| `uri` | Framework item URI | Yes | Public | A web identifier for this item. |
| `humanCodingScheme` | Printed code | Optional | Public | The short code people see in standards documents, such as RL.6.1. |
| `listEnumeration` | List position label | Optional | Public | The item's visible position in a list or outline. |
| `abbreviatedStatement` | Short statement | Optional | Public | A shortened version of the full statement. |
| `conceptKeywords` | Concept keywords | Optional, many | Public | Free-text topic keywords connected to the item. |
| `conceptKeywordsURI` | Concept keyword URI | Optional | Public | Linked-data identifier for controlled concept keywords. |
| `notes` | Notes | Optional | Public | Publisher notes about where the statement came from or how it should be understood. |
| `subject` | Subjects | Optional, many | Public | Subject labels for this item. |
| `subjectURI` | Subject URIs | Optional, many | Public | Linked subject identifiers for this item. |
| `language` | Language | Optional | Public | Language used for this item's text. |
| `educationLevel` | Education levels | Optional, many | Public | Intended grade, education level, or instructional level. |
| `CFItemTypeURI` | Item type URI | Optional | Public | Linked-data identifier for the item type. |
| `licenseURI` | License link | Optional | Public | License that applies to this item. |
| `statusStartDate` | Status start date | Optional | Public | When this item's status began. |
| `statusEndDate` | Status end date | Optional | Public | When this item's status ended or changed. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When this item last changed. |
| `extensions` | Item extensions | Optional | Depends on contents | Extra item data supplied by the publisher. |

## CFPckgAssociation

An association is a relationship edge between two framework documents or framework items. This is how CASE represents hierarchy, mappings, replacements, translations, skill levels, and other relationships.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Association ID | Yes | Public or directory | The official CASE UUID for this relationship. |
| `associationType` | Relationship type | Yes | Public | What kind of relationship this is. |
| `sequenceNumber` | Order number | Optional | Public | The display or processing order for this relationship. |
| `uri` | Association URI | Yes | Public | A web identifier for this relationship. |
| `originNodeURI` | From item/document | Yes | Public | The item or document where the relationship starts. |
| `destinationNodeURI` | To item/document | Yes | Public | The item or document where the relationship points. |
| `CFAssociationGroupingURI` | Association group | Optional | Public | A group label for related associations. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When this association last changed. |
| `notes` | Notes | Optional | Public | Publisher notes about the relationship. |
| `extensions` | Association extensions | Optional | Depends on contents | Extra association data supplied by the publisher. |

### Association Type Values

| Value | Layperson meaning | Platform guidance |
| --- | --- | --- |
| `isChildOf` | The origin item is a child of the destination item. | Use for framework hierarchy, such as standard under strand. |
| `isPeerOf` | The origin item is a peer of the destination item. | Use for sibling/equivalent-level relationships. |
| `isPartOf` | The origin item is included in the destination item. | Use when an item is part of a larger item but not just a tree child. |
| `exactMatchOf` | The origin item is equivalent to the destination item. | Use for crosswalks and derived frameworks. |
| `precedes` | The origin item comes before the destination item. | Use for sequence/order relationships. |
| `isRelatedTo` | The origin item is related to the destination item in a general way. | Use only when a more specific relationship type does not fit. |
| `replacedBy` | The origin item has been replaced by the destination item. | Use for versioning/supersession. |
| `exemplar` | The destination is an example of the origin. | Use for examples or best-practice references. |
| `hasSkillLevel` | The destination defines a skill or difficulty level for the origin. | Use for levels such as Lexile, depth of knowledge, or cognitive level. |
| `isTranslationOf` | The destination is a translation of the origin. | Use for multilingual frameworks. |

## CFDefinition

Definitions are reusable lookup lists for the framework.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `CFConcepts` | Concepts | Optional, many | Public | Topic concepts used by the framework. |
| `CFSubjects` | Subjects | Optional, many | Public | Subject definitions used by the framework. |
| `CFLicenses` | Licenses | Optional, many | Public | License definitions used by the framework. |
| `CFItemTypes` | Item types | Optional, many | Public | Item type definitions, such as domain, standard, skill, or course code. |
| `CFAssociationGroupings` | Association groups | Optional, many | Public | Named groups for relationships. |
| `extensions` | Definition extensions | Optional | Depends on contents | Extra definition data supplied by the publisher. |

## CFConcept

A concept is a topic or idea addressed by the framework.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Concept ID | Yes | Public | The official CASE UUID for the concept. |
| `uri` | Concept URI | Yes | Public | A web identifier for the concept. |
| `title` | Concept title | Yes | Public | The concept name. |
| `keywords` | Keywords | Optional | Public | Keywords connected to the concept. |
| `hierarchyCode` | Hierarchy code | Yes | Public | The publisher's code showing where the concept fits in a concept hierarchy. |
| `description` | Description | Optional | Public | Explanation of the concept. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the concept last changed. |
| `extensions` | Concept extensions | Optional | Depends on contents | Extra concept data supplied by the publisher. |

## CFSubject

A subject is an academic or topical subject used by the framework.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Subject ID | Yes | Public | The official CASE UUID for the subject. |
| `uri` | Subject URI | Yes | Public | A web identifier for the subject. |
| `title` | Subject title | Yes | Public | The subject name, such as Mathematics. |
| `hierarchyCode` | Hierarchy code | Yes | Public | The publisher's code for where the subject fits in a subject hierarchy. |
| `description` | Description | Optional | Public | Explanation of the subject. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the subject last changed. |
| `extensions` | Subject extensions | Optional | Depends on contents | Extra subject data supplied by the publisher. |

## CFItemType

An item type explains what kind of framework item something is.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Item type ID | Yes | Public | The official CASE UUID for the item type. |
| `uri` | Item type URI | Yes | Public | A web identifier for the item type. |
| `title` | Item type title | Yes | Public | The item type name, such as Standard, Domain, Skill, Competency, or Course Code. |
| `description` | Description | Yes | Public | Explanation of the item type. |
| `hierarchyCode` | Hierarchy code | Yes | Public | The publisher's code for where the item type fits in the item type hierarchy. |
| `typeCode` | Type code | Optional | Public | A short type-identification code. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the item type last changed. |
| `extensions` | Item type extensions | Optional | Depends on contents | Extra item type data supplied by the publisher. |

## CFLicense

A license defines permissions for using a framework, item, or related content.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | License ID | Yes | Public | The official CASE UUID for the license record. |
| `uri` | License URI | Yes | Public | A web identifier for the license record. |
| `title` | License title | Yes | Public | The license name. |
| `description` | Description | Optional | Public | Explanation of the license. |
| `licenseText` | License text | Yes | Public | The legal text or a reference to legal text for the license. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the license record last changed. |
| `extensions` | License extensions | Optional | Depends on contents | Extra license data supplied by the publisher. |

## CFAssociationGrouping

An association grouping labels a set of associations so people can understand why those relationships belong together.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Group ID | Yes | Public | The official CASE UUID for the association group. |
| `uri` | Group URI | Yes | Public | A web identifier for the association group. |
| `title` | Group title | Yes | Public | The group name. |
| `description` | Description | Optional | Public | Explanation of the group. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the group last changed. |
| `extensions` | Group extensions | Optional | Depends on contents | Extra group data supplied by the publisher. |

## CFRubric

A rubric describes criteria and performance levels for judging work or mastery.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Rubric ID | Yes | Public or directory | The official CASE UUID for the rubric. |
| `uri` | Rubric URI | Yes | Public or directory | A web identifier for the rubric. |
| `title` | Rubric title | Optional | Public | The rubric name. |
| `description` | Description | Optional | Public | Explanation of the rubric. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the rubric last changed. |
| `CFRubricCriteria` | Rubric criteria | Optional, many | Public | The criteria used in the rubric. |
| `extensions` | Rubric extensions | Optional | Depends on contents | Extra rubric data supplied by the publisher. |

## CFRubricCriterion

A rubric criterion is one thing being judged, such as evidence, reasoning, fluency, accuracy, or collaboration.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Criterion ID | Yes | Public | The official CASE UUID for the criterion. |
| `uri` | Criterion URI | Yes | Public | A web identifier for the criterion. |
| `category` | Criterion category | Optional | Public | A label used to group criteria. |
| `description` | Description | Optional | Public | What this criterion measures. |
| `CFItemURI` | Aligned framework item | Optional | Public | The standard, competency, or skill this criterion connects to. |
| `weight` | Weight | Optional | Public | How much this criterion counts in scoring. |
| `position` | Position | Optional | Public | Display order of this criterion in the rubric. |
| `rubricId` | Parent rubric ID | Optional | Public | The rubric this criterion belongs to. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the criterion last changed. |
| `CFRubricCriterionLevels` | Criterion levels | Optional, many | Public | The performance levels for this criterion. |
| `extensions` | Criterion extensions | Optional | Depends on contents | Extra criterion data supplied by the publisher. |

## CFRubricCriterionLevel

A criterion level describes one performance level for a criterion, such as beginning, developing, proficient, or advanced.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `identifier` | Level ID | Yes | Public | The official CASE UUID for the level. |
| `uri` | Level URI | Yes | Public | A web identifier for the level. |
| `description` | Description | Optional | Public | Explanation of the performance level. |
| `quality` | Quality label | Optional | Public | The label for the level, such as proficient. |
| `score` | Points | Optional | Public | Points awarded for this level. |
| `feedback` | Feedback | Optional | Public | Pre-written feedback or guidance for this level. |
| `position` | Position | Optional | Public | Display order of this level. |
| `rubricCriterionId` | Parent criterion ID | Optional | Public | The criterion this level belongs to. |
| `lastChangeDateTime` | Last changed time | Yes | Operational | When the level last changed. |
| `extensions` | Level extensions | Optional, many | Depends on contents | Extra level data supplied by the publisher. |

## Target Type Values

| Value | Layperson meaning |
| --- | --- |
| `CASE` | The link target points to a CASE framework object. |

## API Status Objects

CASE service responses can include status objects for failed or partial operations. These are operational records.

| Field | Plain name | Required | Privacy | Layperson meaning |
| --- | --- | --- | --- | --- |
| `imsx_codeMajor` | Major status | Yes | Operational | Broad result of the API request. |
| `imsx_severity` | Severity | Yes | Operational | Whether the status is informational, warning, or error. |
| `imsx_description` | Status description | Optional | Operational | Human-readable details about the status. |
| `imsx_CodeMinor` | Minor status details | Optional | Operational | More specific status codes. |

## Platform Modeling Notes

- Treat CASE objects as mostly public or directory metadata, but still track tenant/source ownership and licenses.
- Use CASE UUIDs and URIs as stable external identifiers, not as the platform primary key.
- Store hierarchy through `CFAssociation` records, especially `isChildOf`.
- Store crosswalks through `exactMatchOf`, `isRelatedTo`, `replacedBy`, and similar association types.
- Use CASE items as the join point for QTI items/tests, OneRoster line items/results, Caliper analytics, Common Cartridge resources, Open Badges, and CLR achievements.
- CASE 1.1 introduced broader framework metadata, including framework type and support for course-code-style frameworks. Do not assume every CASE package is a K-12 academic standards document.
