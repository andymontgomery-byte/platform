# Build an EdTech App on This Platform

decision_ids: `DEC-001-person-agent-subject`, `DEC-006-standards-alignment`, `DEC-007-identifier-crosswalk`, `DEC-008-time-session`, `DEC-011-privacy-surfaces`, `DEC-013-runtime-coverage`, `DEC-015-service-role-policy`, `DEC-016-dictionary-canonical`, `DEC-017-canonical-fields`, `DEC-018-global-enums`, `DEC-019-closed-privacy-classes`.

This guide is the apex buildability artifact. Reading only files under `docs/`, a person who has never seen this codebase before can produce executable curl/SQL for the five workflows below, run them against the live hosted runtime, and observe the expected results. Every field in every payload links to the dictionary entry that defines it. Every enum value links to the global enum. There are no "for more details, see..." gaps.

If a step fails, the gap is in this guide; file an issue against `docs/build-an-edtech-app.md`.

## Live Runtime

You write against the live hosted Supabase project. No local install. No Docker. No build step.

| What | Value |
| --- | --- |
| Project URL | `https://qzxlgrerjoiamxvnkklq.supabase.co` |
| REST base | `https://qzxlgrerjoiamxvnkklq.supabase.co/rest/v1/` |
| Edge Functions base | `https://qzxlgrerjoiamxvnkklq.functions.supabase.co/` |
| Publishable (anon) key | `sb_publishable_DaJsnILCWdUIjl4cCaL3Jw_qLy8BPXK` |
| Tenant A (North Valley) | `11111111-1111-1111-1111-111111111111` |
| Tenant B (South Ridge, RLS test only) | `22222222-2222-2222-2222-222222222222` |

These values are also published in [`.env.example`](../.env.example) and [`docs/supabase-hosted-database.md`](./supabase-hosted-database.md).

Set them as shell variables once:

```sh
export SUPABASE_URL='https://qzxlgrerjoiamxvnkklq.supabase.co'
export SUPABASE_FUNCTIONS_URL='https://qzxlgrerjoiamxvnkklq.functions.supabase.co'
export SUPABASE_PUBLISHABLE_KEY='sb_publishable_DaJsnILCWdUIjl4cCaL3Jw_qLy8BPXK'
export TENANT_A='11111111-1111-1111-1111-111111111111'
```

## Two Auth Modes You Will Use

The platform never accepts the publishable key in place of a user JWT for writes. Per [`DEC-015-service-role-policy`](./decisions.md#dec-015-service-role-policy) and [`DEC-011-privacy-surfaces`](./decisions.md#dec-011-privacy-surfaces):

1. **Anonymous read mode.** Send only the publishable key. RLS limits you to the synthetic North Valley demo rows that are explicitly marked public. Use this to confirm the project is reachable and to read non-restricted fields. No grades, no restricted PII, no Edge Function writes.

2. **Tenant-scoped user JWT mode.** Required for every workflow below that writes data, calls an Edge Function, or reads restricted PII (`person.given_name`, `person.family_name`, `person.email`). Get one by running the helper script in [Step 0](#step-0-obtain-a-tenant-scoped-user-jwt). The script uses `SUPABASE_SERVICE_ROLE_KEY` only to mint the test user; that one operation is allowlisted in [`docs/admin-operations.md`](./admin-operations.md) under `tenant_rls_test_auth_fixture_setup`.

You will never paste the service role key into a curl. You will never see it in a request header in this guide. Production apps mint user JWTs through your own identity provider; for local exploration the helper script is the supported path.

---

## Step 0: Obtain a Tenant-Scoped User JWT

Prereq: copy `.env.example` to `.env.local` and fill in `SUPABASE_SERVICE_ROLE_KEY` from the Supabase dashboard. The service role key is required only for this minting step and never leaves your machine.

```sh
python3 - <<'PY'
import json, os, secrets, urllib.request, urllib.parse, pathlib
env = {}
for line in pathlib.Path('.env.local').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")
url = env['SUPABASE_URL']
service = env['SUPABASE_SERVICE_ROLE_KEY']
publishable = env['SUPABASE_PUBLISHABLE_KEY']
tenant = '11111111-1111-1111-1111-111111111111'
email = f'demo-{secrets.token_hex(4)}@northview.k12.test'
password = secrets.token_urlsafe(24)

# 1. Create user with tenant claim (admin operation: tenant_rls_test_auth_fixture_setup).
req = urllib.request.Request(
    f'{url}/auth/v1/admin/users',
    data=json.dumps({
        'email': email, 'password': password, 'email_confirm': True,
        'app_metadata': {'tenant_id': tenant},
    }).encode(),
    headers={'apikey': service, 'authorization': f'Bearer {service}', 'content-type': 'application/json'},
)
urllib.request.urlopen(req).read()

# 2. Sign in to receive a JWT carrying the tenant_id app_metadata claim.
req = urllib.request.Request(
    f'{url}/auth/v1/token?grant_type=password',
    data=json.dumps({'email': email, 'password': password}).encode(),
    headers={'apikey': publishable, 'content-type': 'application/json'},
)
tok = json.loads(urllib.request.urlopen(req).read())
print(f"export SUPABASE_USER_JWT='{tok['access_token']}'")
PY
```

Run the printed `export` line in your shell. The JWT is good for one hour. Re-run this step to get a fresh one.

Verify the JWT carries the tenant claim:

```sh
echo "$SUPABASE_USER_JWT" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool | grep -E 'tenant_id|app_metadata'
```

Expected output includes `"tenant_id": "11111111-1111-1111-1111-111111111111"` inside `app_metadata`.

---

## Workflow 1: Create a School with One Teacher and Ten Students

Goal: insert one [organization](./generated/oneroster-core-dictionary.md#organization) of type [`school`](./generated/oneroster-core-dictionary.md#organization), one [person](./generated/oneroster-core-dictionary.md#person) with role [`teacher`](./generated/oneroster-core-dictionary.md#person), and ten people with role [`student`](./generated/oneroster-core-dictionary.md#person). All rows are tenant-scoped to North Valley by RLS per [`DEC-011`](./decisions.md#dec-011-privacy-surfaces).

PostgREST writes apply RLS as the JWT's tenant. The publishable key reads but never writes; you must send `SUPABASE_USER_JWT`.

```sh
curl "$SUPABASE_URL/rest/v1/organizations" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  -H 'prefer: return=representation' \
  --data '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "id": "org_school_madison",
    "sourced_id": "SCHOOL-MADISON",
    "name": "Madison Middle School",
    "organization_type": "school",
    "parent_organization_id": "org_district_north",
    "status": "active",
    "date_last_modified": "2026-04-26T15:00:00Z"
  }'
```

Field anchors: [`tenant_id`](./generated/integration-governance-core-dictionary.md#tenancy), [`id`](./generated/oneroster-core-dictionary.md#organization), [`sourced_id`](./generated/oneroster-core-dictionary.md#organization), [`name`](./generated/oneroster-core-dictionary.md#organization), [`organization_type`](./generated/oneroster-core-dictionary.md#organization), [`parent_organization_id`](./generated/oneroster-core-dictionary.md#organization), [`status`](./generated/oneroster-core-dictionary.md#organization), [`date_last_modified`](./generated/oneroster-core-dictionary.md#academic-session). Enum values: `organization_type=school` and `status=active` are listed under "Controlled Values" of each object. Status values are the global [`base_status`](./generated/oneroster-core-dictionary.md#person) enum (`active`, `inactive`, `tobedeleted`) per [`DEC-018-global-enums`](./decisions.md#dec-018-global-enums).

Insert one teacher:

```sh
curl "$SUPABASE_URL/rest/v1/people" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  -H 'prefer: return=representation' \
  --data '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "id": "person_ms_torres",
    "sourced_id": "USER-TORRES",
    "display_name": "Maria Torres",
    "given_name": "Maria",
    "family_name": "Torres",
    "email": "maria.torres@northview.k12.test",
    "primary_role": "teacher",
    "enabled_user": "true",
    "status": "active",
    "date_last_modified": "2026-04-26T15:01:00Z"
  }'
```

Field anchors: [`display_name`, `given_name`, `family_name`, `email`, `primary_role`, `enabled_user`, `status`](./generated/oneroster-core-dictionary.md#person). The fields `given_name`, `family_name`, and `email` are privacy class [`directory`](./decisions.md#dec-019-closed-privacy-classes); reading them through PostgREST returns null. Read them via the [audited roster Edge Function](#how-to-read-restricted-pii) — covered below.

Insert ten students with one batch request:

```sh
curl "$SUPABASE_URL/rest/v1/people" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  -H 'prefer: return=representation' \
  --data '[
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s01","sourced_id":"USER-MAD-S01","display_name":"Avery Kim","given_name":"Avery","family_name":"Kim","email":"avery.kim@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:00Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s02","sourced_id":"USER-MAD-S02","display_name":"Bailey Cruz","given_name":"Bailey","family_name":"Cruz","email":"bailey.cruz@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:01Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s03","sourced_id":"USER-MAD-S03","display_name":"Casey Diaz","given_name":"Casey","family_name":"Diaz","email":"casey.diaz@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:02Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s04","sourced_id":"USER-MAD-S04","display_name":"Drew Evans","given_name":"Drew","family_name":"Evans","email":"drew.evans@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:03Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s05","sourced_id":"USER-MAD-S05","display_name":"Emery Frost","given_name":"Emery","family_name":"Frost","email":"emery.frost@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:04Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s06","sourced_id":"USER-MAD-S06","display_name":"Finley Gray","given_name":"Finley","family_name":"Gray","email":"finley.gray@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:05Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s07","sourced_id":"USER-MAD-S07","display_name":"Harper Iqbal","given_name":"Harper","family_name":"Iqbal","email":"harper.iqbal@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:06Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s08","sourced_id":"USER-MAD-S08","display_name":"Indigo Jones","given_name":"Indigo","family_name":"Jones","email":"indigo.jones@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:07Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s09","sourced_id":"USER-MAD-S09","display_name":"Juno Khan","given_name":"Juno","family_name":"Khan","email":"juno.khan@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:08Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"person_madison_s10","sourced_id":"USER-MAD-S10","display_name":"Kai Lopez","given_name":"Kai","family_name":"Lopez","email":"kai.lopez@northview.k12.test","primary_role":"student","enabled_user":"true","status":"active","date_last_modified":"2026-04-26T15:02:09Z"}
  ]'
```

Confirm the inserts:

```sh
curl "$SUPABASE_URL/rest/v1/people?select=id,display_name,primary_role&id=like.person_madison_*&order=id.asc" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT"
```

Expected: ten rows, all `primary_role=student`. The teacher row reads from `id=eq.person_ms_torres`.

---

## Workflow 2: Create a Class and Enroll the Roster

Insert a [course](./generated/oneroster-core-dictionary.md#course), a [class](./generated/oneroster-core-dictionary.md#class) for that course at Madison, and one [enrollment](./generated/oneroster-core-dictionary.md#enrollment) per person. Reuse existing [`session_2026_fall`](./generated/oneroster-core-dictionary.md#academic-session) (Aug 24 – Dec 18, 2026) so we don't have to mint a session.

```sh
curl "$SUPABASE_URL/rest/v1/courses" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' -H 'prefer: return=representation' \
  --data '{"tenant_id":"11111111-1111-1111-1111-111111111111","id":"course_sci_6","sourced_id":"COURSE-SCI-6","title":"Grade 6 Science","course_code":"SCI-06","org_id":"org_district_north","school_year_id":"session_2026","status":"active","date_last_modified":"2026-04-26T15:10:00Z"}'

curl "$SUPABASE_URL/rest/v1/classes" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' -H 'prefer: return=representation' \
  --data '{"tenant_id":"11111111-1111-1111-1111-111111111111","id":"class_sci_6_a","sourced_id":"CLASS-SCI-6A","title":"Science 6 - Period 4","class_type":"scheduled","class_code":"P4-SCI6","course_id":"course_sci_6","school_id":"org_school_madison","term_id":"session_2026_fall","status":"active","date_last_modified":"2026-04-26T15:11:00Z"}'
```

Field anchors for [Class](./generated/oneroster-core-dictionary.md#class): `class_type` (global enum [`class_type`](./generated/oneroster-core-dictionary.md#class) — `scheduled`, `homeroom`, `tutorial`), `course_id`, `school_id`, `term_id`, `status`. The `school_id` must reference an `organizations.id` with `organization_type='school'`; here that's `org_school_madison` from Workflow 1.

Insert all eleven enrollments in one batch (one teacher + ten students). The `role` field uses the global [`enrollment_role`](./generated/oneroster-core-dictionary.md#enrollment) enum.

```sh
curl "$SUPABASE_URL/rest/v1/enrollments" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' -H 'prefer: return=representation' \
  --data '[
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_torres_sci_6_a","sourced_id":"ENR-20000","class_id":"class_sci_6_a","person_id":"person_ms_torres","school_id":"org_school_madison","role":"teacher","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"true","status":"active","date_last_modified":"2026-04-26T15:12:00Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s01_sci_6_a","sourced_id":"ENR-20001","class_id":"class_sci_6_a","person_id":"person_madison_s01","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:01Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s02_sci_6_a","sourced_id":"ENR-20002","class_id":"class_sci_6_a","person_id":"person_madison_s02","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:02Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s03_sci_6_a","sourced_id":"ENR-20003","class_id":"class_sci_6_a","person_id":"person_madison_s03","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:03Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s04_sci_6_a","sourced_id":"ENR-20004","class_id":"class_sci_6_a","person_id":"person_madison_s04","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:04Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s05_sci_6_a","sourced_id":"ENR-20005","class_id":"class_sci_6_a","person_id":"person_madison_s05","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:05Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s06_sci_6_a","sourced_id":"ENR-20006","class_id":"class_sci_6_a","person_id":"person_madison_s06","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:06Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s07_sci_6_a","sourced_id":"ENR-20007","class_id":"class_sci_6_a","person_id":"person_madison_s07","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:07Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s08_sci_6_a","sourced_id":"ENR-20008","class_id":"class_sci_6_a","person_id":"person_madison_s08","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:08Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s09_sci_6_a","sourced_id":"ENR-20009","class_id":"class_sci_6_a","person_id":"person_madison_s09","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:09Z"},
    {"tenant_id":"11111111-1111-1111-1111-111111111111","id":"enr_s10_sci_6_a","sourced_id":"ENR-20010","class_id":"class_sci_6_a","person_id":"person_madison_s10","school_id":"org_school_madison","role":"student","begin_date":"2026-08-24","end_date":"2026-12-18","primary_flag":"false","status":"active","date_last_modified":"2026-04-26T15:12:10Z"}
  ]'
```

Roster check:

```sh
curl "$SUPABASE_URL/rest/v1/enrollments?select=id,role,person_id&class_id=eq.class_sci_6_a&order=role.asc,id.asc" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT"
```

Expected: 11 rows — one with `role=teacher`, ten with `role=student`. Per [`DEC-019`](./decisions.md#dec-019-closed-privacy-classes), `display_name` here is privacy class [`directory`](./generated/oneroster-core-dictionary.md#person), so anonymous reads will not include it. With your user JWT it does.

---

## Workflow 3: Post a Numeric Grade

Goal: create a [line item](./generated/oneroster-core-dictionary.md#line-item) and post a [result](./generated/oneroster-core-dictionary.md#result) for a student.

This workflow uses the [`gradebook-bulk-submit`](./supabase-hosted-database.md#edge-function-gradebook-bulk-submit) Edge Function rather than direct PostgREST inserts. Per [`DEC-013-runtime-coverage`](./decisions.md#dec-013-runtime-coverage), every non-CRUD action lives behind an Edge Function so the JWT is freshly verified and the RLS policy applies on the same DB connection. The Edge Function also propagates your bearer token to PostgREST per [`DEC-015-service-role-policy`](./decisions.md#dec-015-service-role-policy) — it never escalates to the service role.

First create the line item via PostgREST (line items are CRUD-shaped, so no Edge Function needed):

```sh
curl "$SUPABASE_URL/rest/v1/line_items" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' -H 'prefer: return=representation' \
  --data '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "id": "li_sci_lab_1",
    "sourced_id": "LINEITEM-SCI-LAB1",
    "title": "Lab 1: Density Measurements",
    "class_id": "class_sci_6_a",
    "category": "assignment",
    "assign_date": "2026-09-08",
    "due_date": "2026-09-15",
    "result_value_min": 0,
    "result_value_max": 20,
    "status": "active",
    "date_last_modified": "2026-04-26T15:20:00Z"
  }'
```

Field anchors: [`category`](./generated/oneroster-core-dictionary.md#line-item) uses global enum [`line_item_category`](./generated/oneroster-core-dictionary.md#line-item) — `assignment`, `quiz`, `test`, `participation`. [`result_value_min`/`result_value_max`](./generated/oneroster-core-dictionary.md#line-item) define the legal score range. [`assign_date`/`due_date`](./generated/oneroster-core-dictionary.md#line-item) are calendar dates per [`DEC-008-time-session`](./decisions.md#dec-008-time-session).

Now post the grade:

```sh
curl "$SUPABASE_FUNCTIONS_URL/gradebook-bulk-submit" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  --data '{
    "submissions": [
      {
        "id": "res_avery_lab_1",
        "sourcedId": "RESULT-30001",
        "lineItemId": "li_sci_lab_1",
        "personId": "person_madison_s01",
        "scoreStatus": "fullyGraded",
        "score": 18,
        "scoreDate": "2026-09-15T14:00:00Z",
        "comment": "Strong technique; double-check unit conversions on Q3."
      }
    ]
  }'
```

Field anchors for the [Result](./generated/oneroster-core-dictionary.md#result): [`scoreStatus`](./generated/oneroster-core-dictionary.md#result) is global enum [`score_status`](./generated/oneroster-core-dictionary.md#result) — `notSubmitted`, `submitted`, `partial`, `fullyGraded`, `exempt`. [`score`](./generated/oneroster-core-dictionary.md#result) must be within `[result_value_min, result_value_max]` of the line item — here `0..20`. [`scoreDate`](./generated/oneroster-core-dictionary.md#result) is an ISO-8601 instant.

Confirm:

```sh
curl "$SUPABASE_URL/rest/v1/results?select=id,score,score_status,score_date&line_item_id=eq.li_sci_lab_1" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT"
```

Expected: one row, `score=18`, `score_status=fullyGraded`. RLS guarantees a tenant B JWT cannot see this row — verified live by [`tests/supabase_tenant_rls_test.py`](../tests/supabase_tenant_rls_test.py).

---

## Workflow 4: Link the Assignment to a CASE Standard URI

Goal: align `li_sci_lab_1` to a published [CASE Framework Item](./generated/case-core-dictionary.md#case-framework-item). The shape used here is the canonical [`uri`](./generated/case-core-dictionary.md#case-framework-item) of the framework item plus the [`humanCodingScheme`](./generated/case-core-dictionary.md#case-framework-item) shown to teachers, per [`DEC-006-standards-alignment`](./decisions.md#dec-006-standards-alignment).

The current OneRoster slice carries alignment as two columns on `line_items` (added in migration `0002_case_alignment_and_caliper_receipts.sql`): `case_framework_item_uri` and `case_framework_item_human_coding`. A future migration replaces these with a full association table per the CASE 1.1 graph; both shapes resolve back to the same dictionary entry.

```sh
curl -X PATCH "$SUPABASE_URL/rest/v1/line_items?id=eq.li_sci_lab_1" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  -H 'prefer: return=representation' \
  --data '{
    "case_framework_item_uri": "https://commonstandardsproject.com/api/v1/standards/A4DD5BFB91B4445C8A0D3F4B6B1A6F3D",
    "case_framework_item_human_coding": "CCSS.MATH.CONTENT.6.RP.A.3"
  }'
```

Field anchors: [`case_framework_item_uri`](./generated/case-core-dictionary.md#case-framework-item) (privacy class [`public`](./decisions.md#dec-019-closed-privacy-classes)), [`case_framework_item_human_coding`](./generated/case-core-dictionary.md#case-framework-item). The URI is a CASE 1.1 CFItem identifier; any tool that resolves CASE URIs (Common Standards Project, the publishing state's hosted framework, an internal mirror) will return the canonical item.

Read it back:

```sh
curl "$SUPABASE_URL/rest/v1/line_items?select=id,title,case_framework_item_uri,case_framework_item_human_coding&id=eq.li_sci_lab_1" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT"
```

Expected: one row showing the URI and the human coding scheme.

---

## Workflow 5: Read a Caliper Activity Feed

Goal: ingest a [Caliper 1.2 envelope](./generated/caliper-core-dictionary.md#caliper-envelope) describing one [GradeEvent](./generated/caliper-core-dictionary.md#caliper-event), then read it back as the activity feed for the class.

Ingestion goes through the [`caliper-event-ingestion`](./supabase-hosted-database.md#edge-function-caliper-event-ingestion) Edge Function, which propagates your JWT into PostgREST per [`DEC-015`](./decisions.md#dec-015-service-role-policy). Each accepted event writes one row into [`caliper_event_receipts`](./generated/caliper-core-dictionary.md#caliper-event), which is tenant-scoped via RLS.

```sh
curl "$SUPABASE_FUNCTIONS_URL/caliper-event-ingestion" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'content-type: application/json' \
  --data '{
    "sensor": "https://platform.example/sensors/madison-sci",
    "data": [
      {
        "id": "urn:uuid:7b39c3c4-1d2a-4f67-9e1b-2c5a9c7b1234",
        "type": "GradeEvent",
        "action": "Graded",
        "actor": {"id": "person_ms_torres", "type": "Person"},
        "object": {"id": "li_sci_lab_1", "type": "Assessment"},
        "generated": {"id": "res_avery_lab_1", "type": "Score", "scoreGiven": 18, "maxScore": 20},
        "eventTime": "2026-09-15T14:00:00.000Z"
      }
    ]
  }'
```

Field anchors: [`sensor`](./generated/caliper-core-dictionary.md#caliper-envelope), [`data[].id`](./generated/caliper-core-dictionary.md#caliper-event), [`type`](./generated/caliper-core-dictionary.md#caliper-event) global enum [`caliper_event_type`](./generated/caliper-core-dictionary.md#caliper-event) — `GradeEvent`, `AssessmentEvent`, `NavigationEvent`, etc. [`action`](./generated/caliper-core-dictionary.md#caliper-event) global enum [`caliper_action`](./generated/caliper-core-dictionary.md#caliper-event). [`actor`](./generated/caliper-core-dictionary.md#caliper-actor), [`object`](./generated/caliper-core-dictionary.md#caliper-entity), [`eventTime`](./generated/caliper-core-dictionary.md#caliper-event) (ISO-8601, [`DEC-008`](./decisions.md#dec-008-time-session)).

Read the activity feed back. The receipt rows are queryable directly:

```sh
curl "$SUPABASE_URL/rest/v1/caliper_event_receipts?select=id,event_type,action,actor_id,object_id,event_time,received_at&order=received_at.desc&limit=20" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT"
```

Expected: at least one row with `event_type=GradeEvent`, `action=Graded`, `actor_id=person_ms_torres`, `object_id=li_sci_lab_1`. RLS prevents tenant B from seeing this row even with the same query.

To filter the feed by an actor (a teacher's view of their own gradings):

```sh
curl "$SUPABASE_URL/rest/v1/caliper_event_receipts?select=id,event_type,action,event_time&actor_id=eq.person_ms_torres&order=event_time.desc" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT"
```

---

## How to Read Restricted PII

`person.given_name`, `person.family_name`, and `person.email` are privacy class [`directory`](./decisions.md#dec-019-closed-privacy-classes). PostgREST returns them as null. To read them, call the [`audited-roster-read`](./supabase-hosted-database.md#edge-function-audited-roster-read) Edge Function, which writes one [`audit_log`](./generated/integration-governance-core-dictionary.md#audit-log) row per field accessed before returning the data. Per [`DEC-011-privacy-surfaces`](./decisions.md#dec-011-privacy-surfaces), there is no "back door" path that bypasses the audit log.

```sh
curl "$SUPABASE_FUNCTIONS_URL/audited-roster-read?personId=person_madison_s01" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "authorization: Bearer $SUPABASE_USER_JWT" \
  -H 'x-platform-client-id: my-edtech-app' \
  -H 'x-platform-scope: platform.roster.users.directory:read' \
  -H 'x-platform-purpose: gradebook-roster-display'
```

Field anchors: [`x-platform-client-id`](./generated/integration-governance-core-dictionary.md#audit-log), [`x-platform-scope`](./generated/integration-governance-core-dictionary.md#audit-log), [`x-platform-purpose`](./generated/integration-governance-core-dictionary.md#audit-log). All three are required; without them the function refuses the read.

Verify the audit log captured the access:

```sh
curl "$SUPABASE_URL/rest/v1/audit_log?select=field_accessed,client_id,scope,purpose,occurred_at&order=occurred_at.desc&limit=4" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" -H "authorization: Bearer $SUPABASE_USER_JWT"
```

---

## What to Do When a Step Fails

| Symptom | Most likely cause | Fix |
| --- | --- | --- |
| `401 Invalid JWT` | `SUPABASE_USER_JWT` expired (1-hour lifetime). | Re-run [Step 0](#step-0-obtain-a-tenant-scoped-user-jwt). |
| `400` with `missing_tenant` from Edge Function | JWT does not carry `app_metadata.tenant_id`. | Make sure the helper script set `app_metadata` on the user record. |
| `403` on insert with no rows returned | Your JWT's tenant differs from `tenant_id` in the row. | Match `tenant_id` in the body to the JWT's claim. |
| `null` returned for `given_name`/`family_name`/`email` | Reading restricted PII through PostgREST. | Use the [audited roster Edge Function](#how-to-read-restricted-pii). |
| `409 duplicate key` on insert | The seed already contains that `id`. | Pick a fresh `id`; existing seed IDs are listed in [`supabase/seed.sql`](../supabase/seed.sql). |

---

## What This Guide Does Not Cover

- Production OAuth client registration. The [`oauth-token-exchange`](./supabase-hosted-database.md#edge-function-oauth-token-exchange) function emits sandbox bearer contexts; it is not a full authorization server.
- Full LTI Advantage callbacks. The [`lti-launch-handler`](./supabase-hosted-database.md#edge-function-lti-launch-handler) function records launches but does not implement the full Names and Role Provisioning Services or Assignment and Grade Services round-trip.
- QTI delivery. The QTI dictionary is in [`docs/generated/qti-core-dictionary.md`](./generated/qti-core-dictionary.md); a delivery runtime is not yet hosted.
- Multi-tenant signup. The helper in [Step 0](#step-0-obtain-a-tenant-scoped-user-jwt) creates a user under tenant A. Tenant provisioning is a future migration tracked in [`docs/spec-gap-backlog.md`](./spec-gap-backlog.md).

These gaps are deliberate per [`DEC-013-runtime-coverage`](./decisions.md#dec-013-runtime-coverage) — the platform ships the smallest end-to-end slice that still proves OneRoster + CASE alignment + Caliper + tenant-scoped privacy.
