# Build An Edtech App

This guide builds one teaching-app slice against the live Supabase runtime. It uses SQL because the current runtime already exposes the OneRoster core tables and the required CASE and Caliper read/write app workflow can be proven today without waiting for a broader product API server.

Run each block from a shell that has the hosted database URL:

```sh
export SUPABASE_DB_URL='postgresql://...'
```

Use the Supabase pooler/database URL for the live project `https://qzxlgrerjoiamxvnkklq.supabase.co`. The SQL below is idempotent: rerunning it updates the same build-guide rows.

## 1. Create A School, Teacher, And Ten Students

Dictionary fields used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `organizations.id` | [organization.id](oneroster-core-dictionary.html#organization.id) |
| `organizations.sourced_id` | [organization.sourced_id](oneroster-core-dictionary.html#organization.sourced_id) |
| `organizations.name` | [organization.name](oneroster-core-dictionary.html#organization.name) |
| `organizations.organization_type` | [organization.organization_type](oneroster-core-dictionary.html#organization.organization_type) |
| `school` | [global enum organization_type.school](oneroster-core-dictionary.html#enum.organization_type.school) |
| `organizations.status` | [organization.status](oneroster-core-dictionary.html#organization.status) |
| `active` | [global enum record_status.active](oneroster-core-dictionary.html#enum.record_status.active) |
| `people.id` | [person.id](oneroster-core-dictionary.html#person.id) |
| `people.sourced_id` | [person.sourced_id](oneroster-core-dictionary.html#person.sourced_id) |
| `people.display_name` | [person.display_name](oneroster-core-dictionary.html#person.display_name) |
| `people.given_name` | [person.given_name](oneroster-core-dictionary.html#person.given_name) |
| `people.family_name` | [person.family_name](oneroster-core-dictionary.html#person.family_name) |
| `people.email` | [person.email](oneroster-core-dictionary.html#person.email) |
| `people.primary_role` | [person.primary_role](oneroster-core-dictionary.html#person.primary_role) |
| `teacher` | [global enum role_family.teacher](oneroster-core-dictionary.html#enum.role_family.teacher) |
| `student` | [global enum role_family.student](oneroster-core-dictionary.html#enum.role_family.student) |
| `people.enabled_user` | [person.enabled_user](oneroster-core-dictionary.html#person.enabled_user) |
| `true` | [global enum enabled_user_state.true](oneroster-core-dictionary.html#enum.enabled_user_state.true) |

```sh
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
insert into public.organizations (
  tenant_id, id, sourced_id, name, organization_type, parent_organization_id, status, date_last_modified
) values (
  '33333333-3333-3333-3333-333333333333',
  'org_build_school',
  'BUILD-SCHOOL-001',
  'Build Guide Middle School',
  'school',
  null,
  'active',
  now()
)
on conflict (id) do update set
  name = excluded.name,
  organization_type = excluded.organization_type,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

with people_rows(id, sourced_id, display_name, given_name, family_name, email, primary_role) as (
  values
    ('person_build_teacher', 'BUILD-TEACHER-001', 'Nora Teacher', 'Nora', 'Teacher', 'nora.teacher@build-guide.test', 'teacher'),
    ('person_build_student_01', 'BUILD-STUDENT-001', 'Student 01', 'Student', '01', 'student01@build-guide.test', 'student'),
    ('person_build_student_02', 'BUILD-STUDENT-002', 'Student 02', 'Student', '02', 'student02@build-guide.test', 'student'),
    ('person_build_student_03', 'BUILD-STUDENT-003', 'Student 03', 'Student', '03', 'student03@build-guide.test', 'student'),
    ('person_build_student_04', 'BUILD-STUDENT-004', 'Student 04', 'Student', '04', 'student04@build-guide.test', 'student'),
    ('person_build_student_05', 'BUILD-STUDENT-005', 'Student 05', 'Student', '05', 'student05@build-guide.test', 'student'),
    ('person_build_student_06', 'BUILD-STUDENT-006', 'Student 06', 'Student', '06', 'student06@build-guide.test', 'student'),
    ('person_build_student_07', 'BUILD-STUDENT-007', 'Student 07', 'Student', '07', 'student07@build-guide.test', 'student'),
    ('person_build_student_08', 'BUILD-STUDENT-008', 'Student 08', 'Student', '08', 'student08@build-guide.test', 'student'),
    ('person_build_student_09', 'BUILD-STUDENT-009', 'Student 09', 'Student', '09', 'student09@build-guide.test', 'student'),
    ('person_build_student_10', 'BUILD-STUDENT-010', 'Student 10', 'Student', '10', 'student10@build-guide.test', 'student')
)
insert into public.people (
  tenant_id, id, sourced_id, display_name, given_name, family_name, email, primary_role, enabled_user, status, date_last_modified
)
select
  '33333333-3333-3333-3333-333333333333',
  id,
  sourced_id,
  display_name,
  given_name,
  family_name,
  email,
  primary_role,
  'true',
  'active',
  now()
from people_rows
on conflict (id) do update set
  display_name = excluded.display_name,
  given_name = excluded.given_name,
  family_name = excluded.family_name,
  email = excluded.email,
  primary_role = excluded.primary_role,
  enabled_user = excluded.enabled_user,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

select id, name, organization_type from public.organizations where id = 'org_build_school';
select id, display_name, primary_role from public.people where id like 'person_build_%' order by id;
SQL
```

## 2. Create A Class And Enroll Everyone

Dictionary fields used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `academic_sessions.id` | [academic_session.id](oneroster-core-dictionary.html#academic_session.id) |
| `academic_sessions.session_type` | [academic_session.session_type](oneroster-core-dictionary.html#academic_session.session_type) |
| `term` | [global enum academic_session_type.term](oneroster-core-dictionary.html#enum.academic_session_type.term) |
| `courses.id` | [course.id](oneroster-core-dictionary.html#course.id) |
| `courses.org_id` | [course.org_id](oneroster-core-dictionary.html#course.org_id) |
| `classes.id` | [class.id](oneroster-core-dictionary.html#class.id) |
| `classes.class_type` | [class.class_type](oneroster-core-dictionary.html#class.class_type) |
| `scheduled` | [global enum class_type.scheduled](oneroster-core-dictionary.html#enum.class_type.scheduled) |
| `classes.course_id` | [class.course_id](oneroster-core-dictionary.html#class.course_id) |
| `classes.school_id` | [class.school_id](oneroster-core-dictionary.html#class.school_id) |
| `classes.term_id` | [class.term_id](oneroster-core-dictionary.html#class.term_id) |
| `enrollments.id` | [enrollment.id](oneroster-core-dictionary.html#enrollment.id) |
| `enrollments.class_id` | [enrollment.class_id](oneroster-core-dictionary.html#enrollment.class_id) |
| `enrollments.person_id` | [enrollment.person_id](oneroster-core-dictionary.html#enrollment.person_id) |
| `enrollments.role` | [enrollment.role](oneroster-core-dictionary.html#enrollment.role) |
| `enrollments.primary_flag` | [enrollment.primary_flag](oneroster-core-dictionary.html#enrollment.primary_flag) |

```sh
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
insert into public.academic_sessions (
  tenant_id, id, sourced_id, title, session_type, start_date, end_date, school_year, status, date_last_modified
) values (
  '33333333-3333-3333-3333-333333333333',
  'session_build_fall_2026',
  'BUILD-TERM-FALL-2026',
  'Build Guide Fall 2026',
  'term',
  '2026-08-24',
  '2026-12-18',
  2026,
  'active',
  now()
)
on conflict (id) do update set
  title = excluded.title,
  session_type = excluded.session_type,
  start_date = excluded.start_date,
  end_date = excluded.end_date,
  school_year = excluded.school_year,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

insert into public.courses (
  tenant_id, id, sourced_id, title, course_code, org_id, school_year_id, status, date_last_modified
) values (
  '33333333-3333-3333-3333-333333333333',
  'course_build_math_6',
  'BUILD-COURSE-MATH-6',
  'Build Guide Grade 6 Mathematics',
  'BUILD-MATH-06',
  'org_build_school',
  'session_build_fall_2026',
  'active',
  now()
)
on conflict (id) do update set
  title = excluded.title,
  course_code = excluded.course_code,
  org_id = excluded.org_id,
  school_year_id = excluded.school_year_id,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

insert into public.classes (
  tenant_id, id, sourced_id, title, class_type, class_code, course_id, school_id, term_id, status, date_last_modified
) values (
  '33333333-3333-3333-3333-333333333333',
  'class_build_math_6a',
  'BUILD-CLASS-MATH-6A',
  'Build Guide Math 6A',
  'scheduled',
  'BUILD-P1-MATH6',
  'course_build_math_6',
  'org_build_school',
  'session_build_fall_2026',
  'active',
  now()
)
on conflict (id) do update set
  title = excluded.title,
  class_type = excluded.class_type,
  class_code = excluded.class_code,
  course_id = excluded.course_id,
  school_id = excluded.school_id,
  term_id = excluded.term_id,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

with enrollments_to_write(id, sourced_id, person_id, role, primary_flag) as (
  values
    ('enr_build_teacher', 'BUILD-ENR-TEACHER', 'person_build_teacher', 'teacher', 'true'),
    ('enr_build_student_01', 'BUILD-ENR-STUDENT-001', 'person_build_student_01', 'student', 'false'),
    ('enr_build_student_02', 'BUILD-ENR-STUDENT-002', 'person_build_student_02', 'student', 'false'),
    ('enr_build_student_03', 'BUILD-ENR-STUDENT-003', 'person_build_student_03', 'student', 'false'),
    ('enr_build_student_04', 'BUILD-ENR-STUDENT-004', 'person_build_student_04', 'student', 'false'),
    ('enr_build_student_05', 'BUILD-ENR-STUDENT-005', 'person_build_student_05', 'student', 'false'),
    ('enr_build_student_06', 'BUILD-ENR-STUDENT-006', 'person_build_student_06', 'student', 'false'),
    ('enr_build_student_07', 'BUILD-ENR-STUDENT-007', 'person_build_student_07', 'student', 'false'),
    ('enr_build_student_08', 'BUILD-ENR-STUDENT-008', 'person_build_student_08', 'student', 'false'),
    ('enr_build_student_09', 'BUILD-ENR-STUDENT-009', 'person_build_student_09', 'student', 'false'),
    ('enr_build_student_10', 'BUILD-ENR-STUDENT-010', 'person_build_student_10', 'student', 'false')
)
insert into public.enrollments (
  tenant_id, id, sourced_id, class_id, person_id, school_id, role, begin_date, end_date, primary_flag, status, date_last_modified
)
select
  '33333333-3333-3333-3333-333333333333',
  id,
  sourced_id,
  'class_build_math_6a',
  person_id,
  'org_build_school',
  role,
  '2026-08-24',
  '2026-12-18',
  primary_flag,
  'active',
  now()
from enrollments_to_write
on conflict (id) do update set
  class_id = excluded.class_id,
  person_id = excluded.person_id,
  school_id = excluded.school_id,
  role = excluded.role,
  begin_date = excluded.begin_date,
  end_date = excluded.end_date,
  primary_flag = excluded.primary_flag,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

select class_id, class_title, person_id, display_name, class_role
from public.class_roster
where class_id = 'class_build_math_6a'
order by class_role desc, person_id;
SQL
```

## 3. Post A Numeric Grade

Dictionary fields used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `line_items.id` | [line_item.id](oneroster-core-dictionary.html#line_item.id) |
| `line_items.title` | [line_item.title](oneroster-core-dictionary.html#line_item.title) |
| `line_items.class_id` | [line_item.class_id](oneroster-core-dictionary.html#line_item.class_id) |
| `line_items.category` | [line_item.category](oneroster-core-dictionary.html#line_item.category) |
| `assignment` | [global enum gradebook_category.assignment](oneroster-core-dictionary.html#enum.gradebook_category.assignment) |
| `line_items.result_value_max` | [line_item.result_value_max](oneroster-core-dictionary.html#line_item.result_value_max) |
| `results.id` | [result.id](oneroster-core-dictionary.html#result.id) |
| `results.line_item_id` | [result.line_item_id](oneroster-core-dictionary.html#result.line_item_id) |
| `results.person_id` | [result.person_id](oneroster-core-dictionary.html#result.person_id) |
| `results.score_status` | [result.score_status](oneroster-core-dictionary.html#result.score_status) |
| `fullyGraded` | [global enum grading_progress.fullyGraded](oneroster-core-dictionary.html#enum.grading_progress.fullyGraded) |
| `results.score` | [result.score](oneroster-core-dictionary.html#result.score) |

```sh
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
insert into public.line_items (
  tenant_id, id, sourced_id, title, class_id, category, assign_date, due_date, result_value_min, result_value_max, status, date_last_modified
) values (
  '33333333-3333-3333-3333-333333333333',
  'li_build_fractions_exit_ticket',
  'BUILD-LINEITEM-FRACTIONS-EXIT',
  'Fractions Exit Ticket',
  'class_build_math_6a',
  'assignment',
  '2026-09-08',
  '2026-09-08',
  0,
  10,
  'active',
  now()
)
on conflict (id) do update set
  title = excluded.title,
  class_id = excluded.class_id,
  category = excluded.category,
  assign_date = excluded.assign_date,
  due_date = excluded.due_date,
  result_value_min = excluded.result_value_min,
  result_value_max = excluded.result_value_max,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

insert into public.results (
  tenant_id, id, sourced_id, line_item_id, person_id, score_status, score, score_date, comment, status, date_last_modified
) values (
  '33333333-3333-3333-3333-333333333333',
  'res_build_student_01_exit_ticket',
  'BUILD-RESULT-STUDENT-001',
  'li_build_fractions_exit_ticket',
  'person_build_student_01',
  'fullyGraded',
  9,
  '2026-09-08T15:30:00Z',
  'Accurate fraction model.',
  'active',
  now()
)
on conflict (id) do update set
  line_item_id = excluded.line_item_id,
  person_id = excluded.person_id,
  score_status = excluded.score_status,
  score = excluded.score,
  score_date = excluded.score_date,
  comment = excluded.comment,
  status = excluded.status,
  date_last_modified = excluded.date_last_modified;

select result_id, line_item_title, learner_name, score, result_value_max, score_status
from public.gradebook_results
where result_id = 'res_build_student_01_exit_ticket';
SQL
```

## 4. Link The Assignment To A CASE Standard URI

The current live runtime has generated CASE dictionary coverage but no full CASE import/search service. This step creates the small app-owned alignment table that a teaching app needs today, while using the platform's [line_item.id](oneroster-core-dictionary.html#line_item.id) and CASE [case_item.uri](case-core-dictionary.html#case_item.uri) contracts.

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `line_item_id` | [line_item.id](oneroster-core-dictionary.html#line_item.id) |
| `case_item_uri` | [case_item.uri](case-core-dictionary.html#case_item.uri) |
| `case_item_identifier` | [case_item.identifier](case-core-dictionary.html#case_item.identifier) |
| `case_item.item_type` | [case_item.item_type](case-core-dictionary.html#case_item.item_type) |
| `standard` | [global enum item_type.standard](case-core-dictionary.html#enum.item_type.standard) |

```sh
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
create table if not exists public.build_app_assignment_case_links (
  tenant_id uuid not null,
  line_item_id text not null references public.line_items(id),
  case_item_uri text not null,
  case_item_identifier text not null,
  created_at timestamptz not null default now(),
  primary key (tenant_id, line_item_id, case_item_uri)
);

insert into public.build_app_assignment_case_links (
  tenant_id, line_item_id, case_item_uri, case_item_identifier
) values (
  '33333333-3333-3333-3333-333333333333',
  'li_build_fractions_exit_ticket',
  'https://standards.example.test/math/2026/6.NS.A.1',
  '6.NS.A.1'
)
on conflict (tenant_id, line_item_id, case_item_uri) do update set
  case_item_identifier = excluded.case_item_identifier,
  created_at = now();

select li.title as assignment_title, l.case_item_identifier, l.case_item_uri
from public.build_app_assignment_case_links l
join public.line_items li on li.id = l.line_item_id
where l.tenant_id = '33333333-3333-3333-3333-333333333333'
  and l.line_item_id = 'li_build_fractions_exit_ticket';
SQL
```

## 5. Read A Caliper-Style Activity Feed For The Class

The live `caliper-event-ingestion` function records tenant-scoped Caliper receipts in `audit_log`. This SQL creates the same receipt for the grade event and reads it back as a Caliper-style class feed.

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `caliper_event.event_type` | [caliper_event.event_type](caliper-core-dictionary.html#caliper_event.event_type) |
| `GradeEvent` | [global enum event_type.GradeEvent](caliper-core-dictionary.html#enum.event_type.GradeEvent) |
| `caliper_event.action` | [caliper_event.action](caliper-core-dictionary.html#caliper_event.action) |
| `Graded` | [global enum action.Graded](caliper-core-dictionary.html#enum.action.Graded) |
| `caliper_event.profile` | [caliper_event.profile](caliper-core-dictionary.html#caliper_event.profile) |
| `GradingProfile` | [global enum profile.GradingProfile](caliper-core-dictionary.html#enum.profile.GradingProfile) |
| `caliper_event.event_time` | [caliper_event.event_time](caliper-core-dictionary.html#caliper_event.event_time) |
| `caliper_event.actor_id` | [caliper_event.actor_id](caliper-core-dictionary.html#caliper_event.actor_id) |
| `caliper_event.group_id` | [caliper_event.group_id](caliper-core-dictionary.html#caliper_event.group_id) |
| `caliper_event.object_id` | [caliper_event.object_id](caliper-core-dictionary.html#caliper_event.object_id) |
| `caliper_event.generated_id` | [caliper_event.generated_id](caliper-core-dictionary.html#caliper_event.generated_id) |

```sh
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
delete from public.audit_log
where tenant_id = '33333333-3333-3333-3333-333333333333'
  and request_id = 'build-guide-class-feed';

insert into public.audit_log (
  tenant_id,
  client_id,
  scope,
  purpose,
  field_accessed,
  subject_table,
  subject_id,
  request_path,
  request_id
) values (
  '33333333-3333-3333-3333-333333333333',
  'build-guide-teaching-app',
  'platform.caliper.events:write',
  'learning-analytics',
  'caliper.event.GradeEvent',
  'caliper_event',
  'urn:uuid:build-guide-grade-event-1',
  '/caliper-event-ingestion',
  'build-guide-class-feed'
);

select jsonb_pretty(jsonb_agg(feed.event order by feed.event ->> 'eventTime')) as caliper_style_activity_feed
from (
  select jsonb_build_object(
    '@context', 'http://purl.imsglobal.org/ctx/caliper/v1p2',
    'id', a.subject_id,
    'type', 'GradeEvent',
    'action', 'Graded',
    'profile', 'GradingProfile',
    'eventTime', a.timestamp,
    'actor', jsonb_build_object(
      'id', 'person_build_teacher',
      'type', 'Person',
      'name', 'Nora Teacher'
    ),
    'group', jsonb_build_object(
      'id', c.id,
      'type', 'CourseSection',
      'name', c.title
    ),
    'object', jsonb_build_object(
      'id', li.id,
      'type', 'AssignableDigitalResource',
      'name', li.title
    ),
    'generated', jsonb_build_object(
      'id', r.id,
      'type', 'Result',
      'score', r.score,
      'maxScore', li.result_value_max,
      'caseItemUri', l.case_item_uri
    )
  ) as event
  from public.audit_log a
  join public.classes c on c.id = 'class_build_math_6a'
  join public.line_items li on li.id = 'li_build_fractions_exit_ticket' and li.class_id = c.id
  join public.results r on r.line_item_id = li.id and r.person_id = 'person_build_student_01'
  join public.build_app_assignment_case_links l on l.line_item_id = li.id
  where a.tenant_id = '33333333-3333-3333-3333-333333333333'
    and a.request_id = 'build-guide-class-feed'
) feed;
SQL
```

## What The App Has Now

The app has a school, one teacher, ten students, one scheduled class, one assignment, one numeric result, a CASE standard URI attached to that assignment, and a Caliper-style feed item tying the score activity back to the class and standard.
