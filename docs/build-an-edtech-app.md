# Build An Edtech App

This guide builds one teaching-app slice against the live Supabase runtime using `curl` and PostgREST. It creates a tenant-scoped API token, writes roster and gradebook rows through platform tables, attaches a CASE standard URI to the assignment, and reads a Caliper-style class activity feed from the platform's Caliper event projection.

## Choose A Runtime

Start with the self-hosted sandbox unless you already have dashboard access to the platform team's hosted Supabase project. Both runtimes use the same migration, table names, row-level security policies, and `curl` requests; only the project URL and keys differ.

| Runtime | Use when | Values used in Step 0 |
| --- | --- | --- |
| Self-hosted sandbox | You are a new developer without platform-admin access. | Your own Supabase Project URL, publishable or `anon` key, and legacy `service_role` key. |
| Hosted platform sandbox | You are a platform maintainer or invited reviewer with dashboard access to `qzxlgrerjoiamxvnkklq`. | Hosted Project URL, hosted publishable key, and hosted legacy `service_role` key. |

### Self-Hosted Supabase Sandbox

Do this once before Step 0:

1. Open `https://supabase.com/dashboard` and sign in or create an account.
2. Click **New project**.
3. Choose or create an organization.
4. Set **Name** to `platform-build-guide`.
5. Generate a strong **Database Password** and store it in a password manager. This is the Postgres password used in the connection string below; Supabase will not show it again.
6. Choose the region closest to you. The examples work in any region because the dashboard supplies the correct pooler host.
7. Click **Create new project** and wait until the project dashboard opens with the project marked active. Do not continue while provisioning is still running.
8. In the project dashboard, click **Connect** in the top bar, choose a Postgres connection string that works from your machine, and copy the **Transaction pooler** or **Session pooler** URI. If the URI contains `[YOUR-PASSWORD]`, keep that placeholder for the command below.
9. In **Project Settings -> API**, copy:
   - **Project URL**, which becomes `SUPABASE_URL`.
   - A **Publishable key**. If your project only shows legacy keys, copy the legacy `anon` key into `SUPABASE_PUBLISHABLE_KEY`.
   - The legacy **service_role** key. Use the JWT-looking legacy `service_role` key for this guide, not an `sb_secret_...` key, because the Auth Admin request in Step 0 sends it as a bearer token from your trusted shell.

Now load the platform schema into your project from the repository root:

```sh
export SUPABASE_DB_PASSWORD='<database-password-from-project-creation>'
export SUPABASE_DB_URL_TEMPLATE='<paste-the-pooler-uri-from-the-Connect-dialog>'
export SUPABASE_DB_URL="$(
  python3 - <<'PY'
import os
import urllib.parse

template = os.environ["SUPABASE_DB_URL_TEMPLATE"]
password = urllib.parse.quote(os.environ["SUPABASE_DB_PASSWORD"], safe="")
print(
    template
    .replace("[YOUR-PASSWORD]", password)
    .replace("<password>", password)
    .replace("<PASSWORD>", password)
)
PY
)"

psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 \
  -f supabase/migrations/0001_oneroster_core_demo.sql
```

Use the Project URL, publishable or `anon` key, and legacy `service_role` key you copied above in Step 0. The synthetic `PLATFORM_TENANT_ID` and all row IDs in this guide can stay unchanged because they are just sandbox data inside your project. See [New Developer Onboarding](supabase-hosted-database.html#new-developer-onboarding-without-platform-admin-access) for the same setup checklist in the hosted database notes.

Invited hosted reviewers can skip the self-hosted project creation and use `https://qzxlgrerjoiamxvnkklq.supabase.co` plus the hosted keys from the platform Supabase dashboard.

## 0. Get An API Token

The REST endpoint is the Supabase project you chose above. The examples use a synthetic build-guide tenant.

The `SUPABASE_SERVICE_ROLE_KEY` value comes from your chosen Supabase dashboard: [Project Settings -> API -> legacy service_role](supabase-hosted-database.html#where-to-find-the-service-role-key). Use the hosted platform key only if you have been granted platform dashboard access; otherwise use your self-hosted project's legacy `service_role` key. This key is used once to create a temporary Auth user with a tenant claim; every platform table write after that uses the tenant-scoped user JWT, per [DEC-015](decisions-standards-overlap-decisions.html#DEC-015-service-role-policy).

```sh
# Self-hosted sandbox values from the setup above.
# Invited hosted reviewers may use https://qzxlgrerjoiamxvnkklq.supabase.co
# and the hosted dashboard keys instead.
export SUPABASE_URL='https://<your-project-ref>.supabase.co'
export SUPABASE_PUBLISHABLE_KEY='<paste-publishable-or-anon-key>'
export SUPABASE_SERVICE_ROLE_KEY='<paste-legacy-service-role-key>'
export PLATFORM_TENANT_ID='33333333-3333-3333-3333-333333333333'
export BUILD_GUIDE_EMAIL="build-guide-$(date +%s)@example.invalid"
export BUILD_GUIDE_PASSWORD="Build-guide-$(date +%s)"

curl -sS -X POST "$SUPABASE_URL/auth/v1/admin/users" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "content-type: application/json" \
  --data "{
    \"email\": \"$BUILD_GUIDE_EMAIL\",
    \"password\": \"$BUILD_GUIDE_PASSWORD\",
    \"email_confirm\": true,
    \"app_metadata\": {
      \"tenant_id\": \"$PLATFORM_TENANT_ID\",
      \"test_owner\": \"platform_buildability_guide\"
    }
  }"

curl -sS -X POST "$SUPABASE_URL/auth/v1/token?grant_type=password" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "content-type: application/json" \
  --data "{
    \"email\": \"$BUILD_GUIDE_EMAIL\",
    \"password\": \"$BUILD_GUIDE_PASSWORD\"
  }" >/tmp/platform-build-guide-token.json

export PLATFORM_ACCESS_TOKEN="$(
  python3 -c 'import json; print(json.load(open("/tmp/platform-build-guide-token.json"))["access_token"])'
)"

export REST_AUTH_HEADERS=(
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY"
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"
  -H "content-type: application/json"
)
```

The runtime `tenant_id` column is filled from the JWT claim and checked by row-level security, per [DEC-010](decisions-standards-overlap-decisions.html#DEC-010-tenancy-reference-data). The request bodies below intentionally omit `tenant_id`.

## 1. Create A School, Teacher, And Ten Students

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `organizations.id` | [organization.id](oneroster-core-dictionary.html#organization.id) |
| `organizations.sourced_id` | [organization.sourced_id](oneroster-core-dictionary.html#organization.sourced_id) |
| `organizations.name` | [organization.name](oneroster-core-dictionary.html#organization.name) |
| `organizations.type` | [organization.type](oneroster-core-dictionary.html#organization.type) |
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
curl -sS -X POST "$SUPABASE_URL/rest/v1/organizations?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "org_build_school",
    "sourced_id": "BUILD-SCHOOL-001",
    "name": "Build Guide Middle School",
    "type": "school",
    "parent": null,
    "status": "active",
    "date_last_modified": "2026-09-01T12:00:00Z"
  }]'

curl -sS -X POST "$SUPABASE_URL/rest/v1/people?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[
    {"id":"person_build_teacher","sourced_id":"BUILD-TEACHER-001","display_name":"Nora Teacher","given_name":"Nora","family_name":"Teacher","email":"nora.teacher@build-guide.test","primary_role":"teacher","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_01","sourced_id":"BUILD-STUDENT-001","display_name":"Student 01","given_name":"Student","family_name":"01","email":"student01@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_02","sourced_id":"BUILD-STUDENT-002","display_name":"Student 02","given_name":"Student","family_name":"02","email":"student02@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_03","sourced_id":"BUILD-STUDENT-003","display_name":"Student 03","given_name":"Student","family_name":"03","email":"student03@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_04","sourced_id":"BUILD-STUDENT-004","display_name":"Student 04","given_name":"Student","family_name":"04","email":"student04@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_05","sourced_id":"BUILD-STUDENT-005","display_name":"Student 05","given_name":"Student","family_name":"05","email":"student05@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_06","sourced_id":"BUILD-STUDENT-006","display_name":"Student 06","given_name":"Student","family_name":"06","email":"student06@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_07","sourced_id":"BUILD-STUDENT-007","display_name":"Student 07","given_name":"Student","family_name":"07","email":"student07@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_08","sourced_id":"BUILD-STUDENT-008","display_name":"Student 08","given_name":"Student","family_name":"08","email":"student08@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_09","sourced_id":"BUILD-STUDENT-009","display_name":"Student 09","given_name":"Student","family_name":"09","email":"student09@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"person_build_student_10","sourced_id":"BUILD-STUDENT-010","display_name":"Student 10","given_name":"Student","family_name":"10","email":"student10@build-guide.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"}
  ]'

curl -sS "$SUPABASE_URL/rest/v1/organizations?select=id,name,type&id=eq.org_build_school" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"

curl -sS "$SUPABASE_URL/rest/v1/people?select=id,display_name,primary_role&id=like.person_build_%25&order=id.asc" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"
```

## 2. Create A Class And Enroll Everyone

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `academic_sessions.id` | [academic_session.id](oneroster-core-dictionary.html#academic_session.id) |
| `academic_sessions.type` | [academic_session.type](oneroster-core-dictionary.html#academic_session.type) |
| `term` | [global enum academic_session_type.term](oneroster-core-dictionary.html#enum.academic_session_type.term) |
| `courses.id` | [course.id](oneroster-core-dictionary.html#course.id) |
| `courses.org` | [course.org](oneroster-core-dictionary.html#course.org) |
| `classes.id` | [class.id](oneroster-core-dictionary.html#class.id) |
| `classes.class_type` | [class.class_type](oneroster-core-dictionary.html#class.class_type) |
| `scheduled` | [global enum class_type.scheduled](oneroster-core-dictionary.html#enum.class_type.scheduled) |
| `classes.course` | [class.course](oneroster-core-dictionary.html#class.course) |
| `classes.school` | [class.school](oneroster-core-dictionary.html#class.school) |
| `classes.terms` | [class.terms](oneroster-core-dictionary.html#class.terms) |
| `enrollments.id` | [enrollment.id](oneroster-core-dictionary.html#enrollment.id) |
| `enrollments.class` | [enrollment.class](oneroster-core-dictionary.html#enrollment.class) |
| `enrollments.user` | [enrollment.user](oneroster-core-dictionary.html#enrollment.user) |
| `enrollments.role` | [enrollment.role](oneroster-core-dictionary.html#enrollment.role) |
| `enrollments.primary` | [enrollment.primary](oneroster-core-dictionary.html#enrollment.primary) |

```sh
curl -sS -X POST "$SUPABASE_URL/rest/v1/academic_sessions?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "session_build_fall_2026",
    "sourced_id": "BUILD-TERM-FALL-2026",
    "title": "Build Guide Fall 2026",
    "type": "term",
    "start_date": "2026-08-24",
    "end_date": "2026-12-18",
    "school_year": 2026,
    "status": "active",
    "date_last_modified": "2026-09-01T12:00:00Z"
  }]'

curl -sS -X POST "$SUPABASE_URL/rest/v1/courses?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "course_build_math_6",
    "sourced_id": "BUILD-COURSE-MATH-6",
    "title": "Build Guide Grade 6 Mathematics",
    "course_code": "BUILD-MATH-06",
    "org": "org_build_school",
    "school_year": "session_build_fall_2026",
    "status": "active",
    "date_last_modified": "2026-09-01T12:00:00Z"
  }]'

curl -sS -X POST "$SUPABASE_URL/rest/v1/classes?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "class_build_math_6a",
    "sourced_id": "BUILD-CLASS-MATH-6A",
    "title": "Build Guide Math 6A",
    "class_type": "scheduled",
    "class_code": "BUILD-P1-MATH6",
    "course": "course_build_math_6",
    "school": "org_build_school",
    "terms": "session_build_fall_2026",
    "status": "active",
    "date_last_modified": "2026-09-01T12:00:00Z"
  }]'

curl -sS -X POST "$SUPABASE_URL/rest/v1/enrollments?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[
    {"id":"enr_build_teacher","sourced_id":"BUILD-ENR-TEACHER","class":"class_build_math_6a","user":"person_build_teacher","school":"org_build_school","role":"teacher","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"true","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_01","sourced_id":"BUILD-ENR-STUDENT-001","class":"class_build_math_6a","user":"person_build_student_01","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_02","sourced_id":"BUILD-ENR-STUDENT-002","class":"class_build_math_6a","user":"person_build_student_02","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_03","sourced_id":"BUILD-ENR-STUDENT-003","class":"class_build_math_6a","user":"person_build_student_03","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_04","sourced_id":"BUILD-ENR-STUDENT-004","class":"class_build_math_6a","user":"person_build_student_04","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_05","sourced_id":"BUILD-ENR-STUDENT-005","class":"class_build_math_6a","user":"person_build_student_05","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_06","sourced_id":"BUILD-ENR-STUDENT-006","class":"class_build_math_6a","user":"person_build_student_06","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_07","sourced_id":"BUILD-ENR-STUDENT-007","class":"class_build_math_6a","user":"person_build_student_07","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_08","sourced_id":"BUILD-ENR-STUDENT-008","class":"class_build_math_6a","user":"person_build_student_08","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_09","sourced_id":"BUILD-ENR-STUDENT-009","class":"class_build_math_6a","user":"person_build_student_09","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"},
    {"id":"enr_build_student_10","sourced_id":"BUILD-ENR-STUDENT-010","class":"class_build_math_6a","user":"person_build_student_10","school":"org_build_school","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary":"false","status":"active","date_last_modified":"2026-09-01T12:00:00Z"}
  ]'

curl -sS "$SUPABASE_URL/rest/v1/class_roster?select=class_id,class_title,person_id,display_name,class_role&class_id=eq.class_build_math_6a&order=person_id.asc" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"
```

## 3. Post A Numeric Grade

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `line_items.id` | [line_item.id](oneroster-core-dictionary.html#line_item.id) |
| `line_items.title` | [line_item.title](oneroster-core-dictionary.html#line_item.title) |
| `line_items.class` | [line_item.class](oneroster-core-dictionary.html#line_item.class) |
| `line_items.category` | [line_item.category](oneroster-core-dictionary.html#line_item.category) |
| `assignment` | [global enum gradebook_category.assignment](oneroster-core-dictionary.html#enum.gradebook_category.assignment) |
| `line_items.result_value_max` | [line_item.result_value_max](oneroster-core-dictionary.html#line_item.result_value_max) |
| `results.id` | [result.id](oneroster-core-dictionary.html#result.id) |
| `results.line_item` | [result.line_item](oneroster-core-dictionary.html#result.line_item) |
| `results.student` | [result.student](oneroster-core-dictionary.html#result.student) |
| `results.score_status` | [result.score_status](oneroster-core-dictionary.html#result.score_status) |
| `fullyGraded` | [global enum grading_progress.fullyGraded](oneroster-core-dictionary.html#enum.grading_progress.fullyGraded) |
| `results.score` | [result.score](oneroster-core-dictionary.html#result.score) |

```sh
curl -sS -X POST "$SUPABASE_URL/rest/v1/line_items?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "li_build_fractions_exit_ticket",
    "sourced_id": "BUILD-LINEITEM-FRACTIONS-EXIT",
    "title": "Fractions Exit Ticket",
    "class": "class_build_math_6a",
    "category": "assignment",
    "assign_date": "2026-09-08",
    "due_date": "2026-09-08",
    "result_value_min": 0,
    "result_value_max": 10,
    "status": "active",
    "date_last_modified": "2026-09-08T15:00:00Z"
  }]'

curl -sS -X POST "$SUPABASE_URL/rest/v1/results?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "res_build_student_01_exit_ticket",
    "sourced_id": "BUILD-RESULT-STUDENT-001",
    "line_item": "li_build_fractions_exit_ticket",
    "student": "person_build_student_01",
    "score_status": "fullyGraded",
    "score": 9,
    "score_date": "2026-09-08T15:30:00Z",
    "comment": "Accurate fraction model.",
    "status": "active",
    "date_last_modified": "2026-09-08T15:30:00Z"
  }]'

curl -sS "$SUPABASE_URL/rest/v1/gradebook_results?select=result_id,line_item_title,learner_name,score,result_value_max,score_status&result_id=eq.res_build_student_01_exit_ticket" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"
```

## 4. Link The Assignment To A CASE Standard URI

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `line_items.id` | [line_item.id](oneroster-core-dictionary.html#line_item.id) |
| `line_items.case_target_uri` | [line_item.case_target_uri](oneroster-core-dictionary.html#line_item.case_target_uri) |
| `case_item.uri` | [case_item.uri](case-core-dictionary.html#case_item.uri) |
| `case_item.item_type` | [case_item.item_type](case-core-dictionary.html#case_item.item_type) |
| `standard` | [global enum item_type.standard](case-core-dictionary.html#enum.item_type.standard) |

CASE framework import is deferred (see DEC-012 and PEND-001); the runtime stores the URI as an opaque reference, so any well-formed URI is accepted in the current sandbox.

```sh
curl -sS -X PATCH "$SUPABASE_URL/rest/v1/line_items?id=eq.li_build_fractions_exit_ticket" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: return=minimal" \
  --data '{
    "case_target_uri": "https://standards.example.test/math/2026/6.NS.A.1",
    "date_last_modified": "2026-09-08T15:35:00Z"
  }'

curl -sS "$SUPABASE_URL/rest/v1/line_items?select=id,title,case_target_uri&id=eq.li_build_fractions_exit_ticket" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"
```

## 5. Read A Caliper-Style Activity Feed For The Class

Dictionary fields and values used by this step:

| Runtime field or value | Dictionary link |
| --- | --- |
| `caliper_events.id` | [caliper_event.id](caliper-core-dictionary.html#caliper_event.id) |
| `caliper_events.event_iri` | [caliper_event.event_iri](caliper-core-dictionary.html#caliper_event.event_iri) |
| `caliper_events.event_type` | [caliper_event.event_type](caliper-core-dictionary.html#caliper_event.event_type) |
| `GradeEvent` | [global enum event_type.GradeEvent](caliper-core-dictionary.html#enum.event_type.GradeEvent) |
| `caliper_events.action` | [caliper_event.action](caliper-core-dictionary.html#caliper_event.action) |
| `Graded` | [global enum action.Graded](caliper-core-dictionary.html#enum.action.Graded) |
| `caliper_events.profile` | [caliper_event.profile](caliper-core-dictionary.html#caliper_event.profile) |
| `GradingProfile` | [global enum profile.GradingProfile](caliper-core-dictionary.html#enum.profile.GradingProfile) |
| `caliper_events.event_time` | [caliper_event.event_time](caliper-core-dictionary.html#caliper_event.event_time) |
| `caliper_events.actor_id` | [caliper_event.actor_id](caliper-core-dictionary.html#caliper_event.actor_id) |
| `caliper_events.group_id` | [caliper_event.group_id](caliper-core-dictionary.html#caliper_event.group_id) |
| `caliper_events.object_id` | [caliper_event.object_id](caliper-core-dictionary.html#caliper_event.object_id) |
| `caliper_events.generated_id` | [caliper_event.generated_id](caliper-core-dictionary.html#caliper_event.generated_id) |
| `caliper_events.raw_event` | [caliper_event.raw_event](caliper-core-dictionary.html#caliper_event.raw_event) |

```sh
curl -sS -X POST "$SUPABASE_URL/rest/v1/caliper_events?on_conflict=id" \
  "${REST_AUTH_HEADERS[@]}" \
  -H "prefer: resolution=merge-duplicates,return=minimal" \
  --data '[{
    "id": "caliper_build_grade_event_1",
    "envelope_id": "caliper_env_build_1",
    "event_iri": "urn:uuid:build-guide-grade-event-1",
    "event_type": "GradeEvent",
    "profile": "GradingProfile",
    "action": "Graded",
    "actor_id": "person_build_teacher",
    "object_id": "li_build_fractions_exit_ticket",
    "event_time": "2026-09-08T15:31:00Z",
    "generated_id": "res_build_student_01_exit_ticket",
    "group_id": "class_build_math_6a",
    "raw_event": "{\"type\":\"GradeEvent\",\"action\":\"Graded\",\"object\":\"li_build_fractions_exit_ticket\",\"generated\":\"res_build_student_01_exit_ticket\"}"
  }]'

curl -sS "$SUPABASE_URL/rest/v1/class_activity_feed?select=event&class_id=eq.class_build_math_6a&order=event_time.asc" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $PLATFORM_ACCESS_TOKEN"
```

## What The App Has Now

The app has a school, one teacher, ten students, one scheduled class, one assignment, one numeric result, a CASE standard URI attached to that assignment through `line_items.case_target_uri`, and a Caliper-style class feed item read from `class_activity_feed`.
