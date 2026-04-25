begin;

drop view if exists public.gradebook_results;
drop view if exists public.class_roster;
drop table if exists public.source_identifiers cascade;
drop table if exists public.results cascade;
drop table if exists public.line_items cascade;
drop table if exists public.enrollments cascade;
drop table if exists public.classes cascade;
drop table if exists public.courses cascade;
drop table if exists public.academic_sessions cascade;
drop table if exists public.people cascade;
drop table if exists public.organizations cascade;

create table public.organizations (
  id text primary key,
  sourced_id text not null unique,
  name text not null,
  organization_type text not null check (organization_type in ('district', 'school', 'department', 'program')),
  parent_organization_id text references public.organizations(id) on delete set null,
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.people (
  id text primary key,
  sourced_id text not null unique,
  display_name text not null,
  given_name text,
  family_name text,
  email text,
  primary_role text not null check (primary_role in ('student', 'teacher', 'administrator', 'guardian')),
  enabled_user text not null check (enabled_user in ('true', 'false')),
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.academic_sessions (
  id text primary key,
  sourced_id text not null unique,
  title text not null,
  session_type text not null check (session_type in ('schoolYear', 'term', 'semester', 'quarter', 'gradingPeriod')),
  start_date date not null,
  end_date date not null,
  school_year integer,
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.courses (
  id text primary key,
  sourced_id text not null unique,
  title text not null,
  course_code text,
  org_id text not null references public.organizations(id),
  school_year_id text references public.academic_sessions(id),
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.classes (
  id text primary key,
  sourced_id text not null unique,
  title text not null,
  class_type text not null check (class_type in ('scheduled', 'homeroom')),
  class_code text,
  course_id text not null references public.courses(id),
  school_id text not null references public.organizations(id),
  term_id text references public.academic_sessions(id),
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.enrollments (
  id text primary key,
  sourced_id text not null unique,
  class_id text not null references public.classes(id),
  person_id text not null references public.people(id),
  school_id text not null references public.organizations(id),
  role text not null check (role in ('student', 'teacher', 'administrator', 'aide')),
  begin_date date,
  end_date date,
  primary_flag text check (primary_flag in ('true', 'false')),
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.line_items (
  id text primary key,
  sourced_id text not null unique,
  title text not null,
  class_id text not null references public.classes(id),
  category text check (category in ('assignment', 'quiz', 'test', 'participation')),
  assign_date date,
  due_date date,
  result_value_min double precision,
  result_value_max double precision,
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.results (
  id text primary key,
  sourced_id text not null unique,
  line_item_id text not null references public.line_items(id),
  person_id text not null references public.people(id),
  score_status text not null check (score_status in ('notSubmitted', 'submitted', 'partiallyGraded', 'fullyGraded')),
  score double precision,
  score_date timestamptz,
  comment text,
  status text not null check (status in ('active', 'inactive', 'tobedeleted')),
  date_last_modified timestamptz not null
);

create table public.source_identifiers (
  id text primary key,
  object_type text not null,
  object_id text not null,
  source_system text not null,
  external_id text not null,
  identifier_type text not null check (identifier_type in ('oneRosterSourcedId', 'sisSourcedId', 'ltiContextId', 'ltiUserId', 'emailAddress')),
  status text not null check (status in ('active', 'inactive', 'tobedeleted'))
);

create index organizations_parent_idx on public.organizations(parent_organization_id);
create index courses_org_idx on public.courses(org_id);
create index courses_school_year_idx on public.courses(school_year_id);
create index classes_course_idx on public.classes(course_id);
create index classes_school_idx on public.classes(school_id);
create index classes_term_idx on public.classes(term_id);
create index enrollments_class_idx on public.enrollments(class_id);
create index enrollments_person_idx on public.enrollments(person_id);
create index enrollments_school_idx on public.enrollments(school_id);
create index line_items_class_idx on public.line_items(class_id);
create index results_line_item_idx on public.results(line_item_id);
create index results_person_idx on public.results(person_id);
create index source_identifiers_lookup_idx on public.source_identifiers(object_type, object_id);

create view public.class_roster
with (security_invoker = true) as
select
  e.id as enrollment_id,
  c.id as class_id,
  c.title as class_title,
  p.id as person_id,
  p.display_name,
  p.primary_role,
  e.role as class_role,
  o.name as school_name,
  e.status
from public.enrollments e
join public.classes c on c.id = e.class_id
join public.people p on p.id = e.person_id
join public.organizations o on o.id = e.school_id;

create view public.gradebook_results
with (security_invoker = true) as
select
  r.id as result_id,
  li.title as line_item_title,
  c.title as class_title,
  p.display_name as learner_name,
  r.score_status,
  r.score,
  li.result_value_max,
  r.comment,
  r.score_date
from public.results r
join public.line_items li on li.id = r.line_item_id
join public.classes c on c.id = li.class_id
join public.people p on p.id = r.person_id;

alter table public.organizations enable row level security;
alter table public.people enable row level security;
alter table public.academic_sessions enable row level security;
alter table public.courses enable row level security;
alter table public.classes enable row level security;
alter table public.enrollments enable row level security;
alter table public.line_items enable row level security;
alter table public.results enable row level security;
alter table public.source_identifiers enable row level security;

create policy demo_read_organizations on public.organizations for select to anon, authenticated using (true);
create policy demo_read_people on public.people for select to anon, authenticated using (true);
create policy demo_read_academic_sessions on public.academic_sessions for select to anon, authenticated using (true);
create policy demo_read_courses on public.courses for select to anon, authenticated using (true);
create policy demo_read_classes on public.classes for select to anon, authenticated using (true);
create policy demo_read_enrollments on public.enrollments for select to anon, authenticated using (true);
create policy demo_read_line_items on public.line_items for select to anon, authenticated using (true);
create policy demo_read_results on public.results for select to anon, authenticated using (true);
create policy demo_read_source_identifiers on public.source_identifiers for select to anon, authenticated using (true);

grant usage on schema public to anon, authenticated;
grant select on
  public.organizations,
  public.people,
  public.academic_sessions,
  public.courses,
  public.classes,
  public.enrollments,
  public.line_items,
  public.results,
  public.source_identifiers,
  public.class_roster,
  public.gradebook_results
to anon, authenticated;

commit;
