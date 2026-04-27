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
  type TEXT NOT NULL CHECK (type IN ('district', 'school', 'department', 'program')),
  parent TEXT REFERENCES organizations(id),
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
  type TEXT NOT NULL CHECK (type IN ('schoolYear', 'term', 'semester', 'quarter', 'gradingPeriod')),
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
  org TEXT NOT NULL REFERENCES organizations(id),
  school_year TEXT REFERENCES academic_sessions(id),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE classes (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  class_type TEXT NOT NULL CHECK (class_type IN ('scheduled', 'homeroom')),
  class_code TEXT,
  course TEXT NOT NULL REFERENCES courses(id),
  school TEXT NOT NULL REFERENCES organizations(id),
  terms TEXT REFERENCES academic_sessions(id),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE enrollments (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  "class" TEXT NOT NULL REFERENCES classes(id),
  "user" TEXT NOT NULL REFERENCES people(id),
  school TEXT NOT NULL REFERENCES organizations(id),
  role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'administrator', 'aide')),
  begin_date TEXT,
  end_date TEXT,
  "primary" TEXT CHECK ("primary" IN ('true', 'false')),
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE line_items (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  "class" TEXT NOT NULL REFERENCES classes(id),
  category TEXT CHECK (category IN ('assignment', 'quiz', 'test', 'participation')),
  assign_date TEXT,
  due_date TEXT,
  result_value_min REAL,
  result_value_max REAL,
  case_target_uri TEXT,
  status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'tobedeleted')),
  date_last_modified TEXT NOT NULL
);

CREATE TABLE results (
  id TEXT PRIMARY KEY,
  sourced_id TEXT NOT NULL UNIQUE,
  line_item TEXT NOT NULL REFERENCES line_items(id),
  student TEXT NOT NULL REFERENCES people(id),
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
JOIN classes c ON c.id = e."class"
JOIN people p ON p.id = e."user"
JOIN organizations o ON o.id = e.school;

CREATE VIEW gradebook_results AS
SELECT
  r.id AS result_id,
  li.title AS line_item_title,
  c.title AS class_title,
  p.display_name AS learner_name,
  r.score_status,
  r.score,
  li.result_value_max,
  li.case_target_uri,
  r.comment,
  r.score_date
FROM results r
JOIN line_items li ON li.id = r.line_item
JOIN classes c ON c.id = li."class"
JOIN people p ON p.id = r.student;
