INSERT INTO organizations VALUES
  ('org_district_north', 'DISTRICT-NORTH', 'North Valley School District', 'district', NULL, 'active', '2026-04-24T09:00:00Z'),
  ('org_school_lincoln', 'SCHOOL-LINCOLN', 'Lincoln Middle School', 'school', 'org_district_north', 'active', '2026-04-24T09:01:00Z'),
  ('org_school_roosevelt', 'SCHOOL-ROOSEVELT', 'Roosevelt Elementary School', 'school', 'org_district_north', 'active', '2026-04-24T09:02:00Z');

INSERT INTO people VALUES
  ('person_ada', 'USER-ADA', 'Ada Johnson', 'Ada', 'Johnson', 'ada.johnson@example.edu', 'student', 'true', 'active', '2026-04-24T09:10:00Z'),
  ('person_miguel', 'USER-MIGUEL', 'Miguel Santos', 'Miguel', 'Santos', 'miguel.santos@example.edu', 'student', 'true', 'active', '2026-04-24T09:11:00Z'),
  ('person_sam', 'USER-SAM', 'Sam Patel', 'Sam', 'Patel', 'sam.patel@example.edu', 'student', 'true', 'active', '2026-04-24T09:12:00Z'),
  ('person_ms_rivera', 'USER-RIVERA', 'Elena Rivera', 'Elena', 'Rivera', 'elena.rivera@example.edu', 'teacher', 'true', 'active', '2026-04-24T09:13:00Z'),
  ('person_mr_chen', 'USER-CHEN', 'David Chen', 'David', 'Chen', 'david.chen@example.edu', 'teacher', 'true', 'active', '2026-04-24T09:14:00Z'),
  ('person_admin_lee', 'USER-LEE', 'Principal Lee', 'Jordan', 'Lee', 'principal.lee@example.edu', 'administrator', 'true', 'active', '2026-04-24T09:15:00Z');

INSERT INTO academic_sessions VALUES
  ('session_2026', 'SY-2026', '2026 School Year', 'schoolYear', '2026-08-24', '2027-06-04', 2026, 'active', '2026-04-24T09:20:00Z'),
  ('session_2026_fall', 'TERM-FALL-2026', 'Fall 2026', 'term', '2026-08-24', '2026-12-18', 2026, 'active', '2026-04-24T09:21:00Z'),
  ('session_2026_q1', 'GP-Q1-2026', 'Quarter 1 2026', 'gradingPeriod', '2026-08-24', '2026-10-16', 2026, 'active', '2026-04-24T09:22:00Z');

INSERT INTO courses VALUES
  ('course_math_6', 'COURSE-MATH-6', 'Grade 6 Mathematics', 'MATH-06', 'org_district_north', 'session_2026', 'active', '2026-04-24T09:25:00Z'),
  ('course_ela_6', 'COURSE-ELA-6', 'Grade 6 English Language Arts', 'ELA-06', 'org_district_north', 'session_2026', 'active', '2026-04-24T09:26:00Z');

INSERT INTO classes VALUES
  ('class_math_6_a', 'CLASS-MATH-6A', 'Math 6 - Period 1', 'scheduled', 'P1-MATH6', 'course_math_6', 'org_school_lincoln', 'session_2026_fall', 'active', '2026-04-24T09:30:00Z'),
  ('class_math_6_b', 'CLASS-MATH-6B', 'Math 6 - Period 3', 'scheduled', 'P3-MATH6', 'course_math_6', 'org_school_lincoln', 'session_2026_fall', 'active', '2026-04-24T09:31:00Z'),
  ('class_ela_6_a', 'CLASS-ELA-6A', 'ELA 6 - Period 2', 'scheduled', 'P2-ELA6', 'course_ela_6', 'org_school_lincoln', 'session_2026_fall', 'active', '2026-04-24T09:32:00Z');

INSERT INTO enrollments VALUES
  ('enr_rivera_math_6_a', 'ENR-10000', 'class_math_6_a', 'person_ms_rivera', 'org_school_lincoln', 'teacher', '2026-08-24', '2026-12-18', 'true', 'active', '2026-04-24T09:35:00Z'),
  ('enr_ada_math_6_a', 'ENR-10001', 'class_math_6_a', 'person_ada', 'org_school_lincoln', 'student', '2026-08-24', '2026-12-18', 'false', 'active', '2026-04-24T09:36:00Z'),
  ('enr_miguel_math_6_a', 'ENR-10002', 'class_math_6_a', 'person_miguel', 'org_school_lincoln', 'student', '2026-08-24', '2026-12-18', 'false', 'active', '2026-04-24T09:37:00Z'),
  ('enr_chen_ela_6_a', 'ENR-10003', 'class_ela_6_a', 'person_mr_chen', 'org_school_lincoln', 'teacher', '2026-08-24', '2026-12-18', 'true', 'active', '2026-04-24T09:38:00Z'),
  ('enr_sam_ela_6_a', 'ENR-10004', 'class_ela_6_a', 'person_sam', 'org_school_lincoln', 'student', '2026-08-24', '2026-12-18', 'false', 'active', '2026-04-24T09:39:00Z');

INSERT INTO line_items VALUES
  ('li_math_quiz_1', 'LINEITEM-MATH-Q1', 'Unit 1 Quiz', 'class_math_6_a', 'quiz', '2026-09-08', '2026-09-15', 0, 100, 'active', '2026-04-24T09:40:00Z'),
  ('li_math_homework_1', 'LINEITEM-MATH-HW1', 'Expressions Practice', 'class_math_6_a', 'assignment', '2026-09-01', '2026-09-05', 0, 10, 'active', '2026-04-24T09:41:00Z'),
  ('li_ela_essay_1', 'LINEITEM-ELA-E1', 'Personal Narrative Draft', 'class_ela_6_a', 'assignment', '2026-09-03', '2026-09-17', 0, 4, 'active', '2026-04-24T09:42:00Z');

INSERT INTO results VALUES
  ('res_ada_quiz_1', 'RESULT-9001', 'li_math_quiz_1', 'person_ada', 'fullyGraded', 87, '2026-09-16T14:30:00Z', 'Strong strategy; check question 4.', 'active', '2026-04-24T09:45:00Z'),
  ('res_miguel_quiz_1', 'RESULT-9002', 'li_math_quiz_1', 'person_miguel', 'fullyGraded', 93, '2026-09-16T14:35:00Z', 'Clear explanations.', 'active', '2026-04-24T09:46:00Z'),
  ('res_ada_homework_1', 'RESULT-9003', 'li_math_homework_1', 'person_ada', 'fullyGraded', 9, '2026-09-06T10:00:00Z', 'Complete.', 'active', '2026-04-24T09:47:00Z'),
  ('res_sam_essay_1', 'RESULT-9004', 'li_ela_essay_1', 'person_sam', 'submitted', NULL, '2026-09-17T09:15:00Z', 'Submitted; awaiting rubric scoring.', 'active', '2026-04-24T09:48:00Z');

INSERT INTO source_identifiers VALUES
  ('sid_1', 'person', 'person_ada', 'North SIS', 'USER-ADA', 'oneRosterSourcedId', 'active'),
  ('sid_2', 'person', 'person_ada', 'North SIS', 'SIS-41001', 'sisSourcedId', 'active'),
  ('sid_3', 'class', 'class_math_6_a', 'North LMS', 'LTI-CONTEXT-MATH-6A', 'ltiContextId', 'active'),
  ('sid_4', 'organization', 'org_school_lincoln', 'North SIS', 'SCHOOL-LINCOLN', 'oneRosterSourcedId', 'active');
