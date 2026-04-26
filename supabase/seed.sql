begin;

truncate
  public.source_identifiers,
  public.results,
  public.line_items,
  public.enrollments,
  public.classes,
  public.courses,
  public.academic_sessions,
  public.people,
  public.organizations
restart identity cascade;

insert into public.organizations (
  tenant_id, id, sourced_id, name, organization_type, parent_organization_id, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'org_district_north', 'DISTRICT-NORTH', 'North Valley School District', 'district', null, 'active', '2026-04-24T09:00:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'org_school_lincoln', 'SCHOOL-LINCOLN', 'Lincoln Middle School', 'school', 'org_district_north', 'active', '2026-04-24T09:01:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'org_school_roosevelt', 'SCHOOL-ROOSEVELT', 'Roosevelt Elementary School', 'school', 'org_district_north', 'active', '2026-04-24T09:02:00Z'),
  ('22222222-2222-2222-2222-222222222222', 'org_district_south', 'DISTRICT-SOUTH', 'South Ridge Test District', 'district', null, 'active', '2026-04-24T10:00:00Z');

insert into public.people (
  tenant_id, id, sourced_id, display_name, given_name, family_name, email, primary_role, enabled_user, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'person_ada', 'USER-ADA', 'Ada Johnson', 'Ada', 'Johnson', 'ada.johnson@northview.k12.test', 'student', 'true', 'active', '2026-04-24T09:10:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'person_miguel', 'USER-MIGUEL', 'Miguel Santos', 'Miguel', 'Santos', 'miguel.santos@northview.k12.test', 'student', 'true', 'active', '2026-04-24T09:11:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'person_sam', 'USER-SAM', 'Sam Patel', 'Sam', 'Patel', 'sam.patel@northview.k12.test', 'student', 'true', 'active', '2026-04-24T09:12:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'person_ms_rivera', 'USER-RIVERA', 'Elena Rivera', 'Elena', 'Rivera', 'elena.rivera@northview.k12.test', 'teacher', 'true', 'active', '2026-04-24T09:13:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'person_mr_chen', 'USER-CHEN', 'David Chen', 'David', 'Chen', 'david.chen@northview.k12.test', 'teacher', 'true', 'active', '2026-04-24T09:14:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'person_admin_lee', 'USER-LEE', 'Principal Lee', 'Jordan', 'Lee', 'principal.lee@northview.k12.test', 'administrator', 'true', 'active', '2026-04-24T09:15:00Z'),
  ('22222222-2222-2222-2222-222222222222', 'person_tenant_b_student', 'USER-TENANT-B', 'Blake South', 'Blake', 'South', 'blake.south@southridge.k12.test', 'student', 'true', 'active', '2026-04-24T10:10:00Z');

insert into public.academic_sessions (
  tenant_id, id, sourced_id, title, session_type, start_date, end_date, school_year, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'session_2026', 'SY-2026', '2026 School Year', 'schoolYear', '2026-08-24', '2027-06-04', 2026, 'active', '2026-04-24T09:20:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'session_2026_fall', 'TERM-FALL-2026', 'Fall 2026', 'term', '2026-08-24', '2026-12-18', 2026, 'active', '2026-04-24T09:21:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'session_2026_q1', 'GP-Q1-2026', 'Quarter 1 2026', 'gradingPeriod', '2026-08-24', '2026-10-16', 2026, 'active', '2026-04-24T09:22:00Z');

insert into public.courses (
  tenant_id, id, sourced_id, title, course_code, org_id, school_year_id, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'course_math_6', 'COURSE-MATH-6', 'Grade 6 Mathematics', 'MATH-06', 'org_district_north', 'session_2026', 'active', '2026-04-24T09:25:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'course_ela_6', 'COURSE-ELA-6', 'Grade 6 English Language Arts', 'ELA-06', 'org_district_north', 'session_2026', 'active', '2026-04-24T09:26:00Z');

insert into public.classes (
  tenant_id, id, sourced_id, title, class_type, class_code, course_id, school_id, term_id, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'class_math_6_a', 'CLASS-MATH-6A', 'Math 6 - Period 1', 'scheduled', 'P1-MATH6', 'course_math_6', 'org_school_lincoln', 'session_2026_fall', 'active', '2026-04-24T09:30:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'class_math_6_b', 'CLASS-MATH-6B', 'Math 6 - Period 3', 'scheduled', 'P3-MATH6', 'course_math_6', 'org_school_lincoln', 'session_2026_fall', 'active', '2026-04-24T09:31:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'class_ela_6_a', 'CLASS-ELA-6A', 'ELA 6 - Period 2', 'scheduled', 'P2-ELA6', 'course_ela_6', 'org_school_lincoln', 'session_2026_fall', 'active', '2026-04-24T09:32:00Z');

insert into public.enrollments (
  tenant_id, id, sourced_id, class_id, person_id, school_id, role, begin_date, end_date, primary_flag, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'enr_rivera_math_6_a', 'ENR-10000', 'class_math_6_a', 'person_ms_rivera', 'org_school_lincoln', 'teacher', '2026-08-24', '2026-12-18', 'true', 'active', '2026-04-24T09:35:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'enr_ada_math_6_a', 'ENR-10001', 'class_math_6_a', 'person_ada', 'org_school_lincoln', 'student', '2026-08-24', '2026-12-18', 'false', 'active', '2026-04-24T09:36:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'enr_miguel_math_6_a', 'ENR-10002', 'class_math_6_a', 'person_miguel', 'org_school_lincoln', 'student', '2026-08-24', '2026-12-18', 'false', 'active', '2026-04-24T09:37:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'enr_chen_ela_6_a', 'ENR-10003', 'class_ela_6_a', 'person_mr_chen', 'org_school_lincoln', 'teacher', '2026-08-24', '2026-12-18', 'true', 'active', '2026-04-24T09:38:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'enr_sam_ela_6_a', 'ENR-10004', 'class_ela_6_a', 'person_sam', 'org_school_lincoln', 'student', '2026-08-24', '2026-12-18', 'false', 'active', '2026-04-24T09:39:00Z');

insert into public.line_items (
  tenant_id, id, sourced_id, title, class_id, category, assign_date, due_date, result_value_min, result_value_max, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'li_math_quiz_1', 'LINEITEM-MATH-Q1', 'Unit 1 Quiz', 'class_math_6_a', 'quiz', '2026-09-08', '2026-09-15', 0, 100, 'active', '2026-04-24T09:40:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'li_math_homework_1', 'LINEITEM-MATH-HW1', 'Expressions Practice', 'class_math_6_a', 'assignment', '2026-09-01', '2026-09-05', 0, 10, 'active', '2026-04-24T09:41:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'li_ela_essay_1', 'LINEITEM-ELA-E1', 'Personal Narrative Draft', 'class_ela_6_a', 'assignment', '2026-09-03', '2026-09-17', 0, 4, 'active', '2026-04-24T09:42:00Z');

insert into public.results (
  tenant_id, id, sourced_id, line_item_id, person_id, score_status, score, score_date, comment, status, date_last_modified
) values
  ('11111111-1111-1111-1111-111111111111', 'res_ada_quiz_1', 'RESULT-9001', 'li_math_quiz_1', 'person_ada', 'fullyGraded', 87, '2026-09-16T14:30:00Z', 'Strong strategy; check question 4.', 'active', '2026-04-24T09:45:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'res_miguel_quiz_1', 'RESULT-9002', 'li_math_quiz_1', 'person_miguel', 'fullyGraded', 93, '2026-09-16T14:35:00Z', 'Clear explanations.', 'active', '2026-04-24T09:46:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'res_ada_homework_1', 'RESULT-9003', 'li_math_homework_1', 'person_ada', 'fullyGraded', 9, '2026-09-06T10:00:00Z', 'Complete.', 'active', '2026-04-24T09:47:00Z'),
  ('11111111-1111-1111-1111-111111111111', 'res_sam_essay_1', 'RESULT-9004', 'li_ela_essay_1', 'person_sam', 'submitted', null, '2026-09-17T09:15:00Z', 'Submitted; awaiting rubric scoring.', 'active', '2026-04-24T09:48:00Z');

insert into public.source_identifiers (
  tenant_id, id, object_type, object_id, source_system, external_id, identifier_type, status
) values
  ('11111111-1111-1111-1111-111111111111', 'sid_1', 'person', 'person_ada', 'North SIS', 'USER-ADA', 'oneRosterSourcedId', 'active'),
  ('11111111-1111-1111-1111-111111111111', 'sid_2', 'person', 'person_ada', 'North SIS', 'SIS-41001', 'sisSourcedId', 'active'),
  ('11111111-1111-1111-1111-111111111111', 'sid_3', 'class', 'class_math_6_a', 'North LMS', 'LTI-CONTEXT-MATH-6A', 'ltiContextId', 'active'),
  ('11111111-1111-1111-1111-111111111111', 'sid_4', 'organization', 'org_school_lincoln', 'North SIS', 'SCHOOL-LINCOLN', 'oneRosterSourcedId', 'active'),
  ('22222222-2222-2222-2222-222222222222', 'sid_5', 'person', 'person_tenant_b_student', 'South SIS', 'USER-TENANT-B', 'oneRosterSourcedId', 'active');

commit;
