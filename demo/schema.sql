PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS class_roster;
DROP VIEW IF EXISTS gradebook_results;
DROP TABLE IF EXISTS source_identifiers;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS line_items;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS academic_sessions;
DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS organizations;

CREATE TABLE organizations (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  organization_type TEXT NOT NULL CHECK (organization_type IN ('district', 'school', 'department', 'program')),
  parent_organization_id TEXT REFERENCES organizations(id),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE people (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  given_name TEXT,
  family_name TEXT,
  email TEXT,
  primary_role TEXT NOT NULL CHECK (primary_role IN ('student', 'teacher', 'administrator', 'guardian')),
  enabled_user TEXT NOT NULL CHECK (enabled_user IN ('true', 'false')),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE academic_sessions (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  session_type TEXT NOT NULL CHECK (session_type IN ('schoolYear', 'term', 'semester', 'quarter', 'gradingPeriod')),
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  school_year INTEGER,
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE courses (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  course_code TEXT,
  org_id TEXT NOT NULL REFERENCES organizations(id),
  school_year_id TEXT REFERENCES academic_sessions(id),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE classes (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  class_type TEXT NOT NULL CHECK (class_type IN ('scheduled', 'homeroom')),
  class_code TEXT,
  course_id TEXT NOT NULL REFERENCES courses(id),
  school_id TEXT NOT NULL REFERENCES organizations(id),
  term_id TEXT REFERENCES academic_sessions(id),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE enrollments (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  class_id TEXT NOT NULL REFERENCES classes(id),
  person_id TEXT NOT NULL REFERENCES people(id),
  school_id TEXT NOT NULL REFERENCES organizations(id),
  role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'administrator', 'aide')),
  begin_date TEXT,
  end_date TEXT,
  primary_flag TEXT CHECK (primary_flag IN ('true', 'false')),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE line_items (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  class_id TEXT NOT NULL REFERENCES classes(id),
  category TEXT CHECK (category IN ('assignment', 'quiz', 'test', 'participation')),
  assign_date TEXT,
  due_date TEXT,
  result_value_min REAL,
  result_value_max REAL,
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE results (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  line_item_id TEXT NOT NULL REFERENCES line_items(id),
  person_id TEXT NOT NULL REFERENCES people(id),
  score_status TEXT NOT NULL CHECK (score_status IN ('notSubmitted', 'submitted', 'partiallyGraded', 'fullyGraded')),
  score REAL,
  score_date TEXT,
  comment TEXT,
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE source_identifiers (
  id TEXT PRIMARY KEY,
  object_type TEXT NOT NULL,
  object_id TEXT NOT NULL,
  source_system TEXT NOT NULL,
  external_id TEXT NOT NULL,
  identifier_type TEXT NOT NULL CHECK (identifier_type IN ('oneRosterSourcedId', 'sisSourcedId', 'ltiContextId', 'ltiUserId', 'emailAddress')),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted'))
);

CREATE VIEW class_roster AS
SELECT
  e.id AS enrollment_id,
  c.id AS class_id,
  c.title AS class_title,
  p.id AS person_id,
  p.display_name,
  p.primary_role,
  e.role AS class_role,
  o.name AS school_name,
  e.status
FROM enrollments e
JOIN classes c ON c.id = e.class_id
JOIN people p ON p.id = e.person_id
JOIN organizations o ON o.id = e.school_id;

CREATE VIEW gradebook_results AS
SELECT
  r.id AS result_id,
  li.title AS line_item_title,
  c.title AS class_title,
  p.display_name AS learner_name,
  r.score_status,
  r.score,
  li.result_value_max,
  r.comment,
  r.score_date
FROM results r
JOIN line_items li ON li.id = r.line_item_id
JOIN classes c ON c.id = li.class_id
JOIN people p ON p.id = r.person_id;
