-- decision_id: DEC-010-tenancy-reference-data, DEC-011-privacy-surfaces, DEC-013-runtime-coverage
-- Tenant-scoped INSERT/UPDATE RLS policies for the OneRoster core CRUD tables that
-- docs/build-an-edtech-app.md teaches a layperson to write to via PostgREST.
--
-- Without these policies the buildability guide's curls would fail with RLS errors
-- on workflows 1, 2, and the line-item creation in workflow 3. With them, an
-- authenticated user JWT carrying app_metadata.tenant_id can insert/update only
-- rows whose tenant_id matches its claim. Pattern mirrors demo_insert_results /
-- demo_update_results in 0001_oneroster_core_demo.sql.
--
-- Idempotent: drop policy if exists guards every create.

begin;

-- organizations
drop policy if exists demo_insert_organizations on public.organizations;
create policy demo_insert_organizations on public.organizations for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);
drop policy if exists demo_update_organizations on public.organizations;
create policy demo_update_organizations on public.organizations for update to authenticated using (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
) with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- people
drop policy if exists demo_insert_people on public.people;
create policy demo_insert_people on public.people for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);
drop policy if exists demo_update_people on public.people;
create policy demo_update_people on public.people for update to authenticated using (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
) with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- academic_sessions
drop policy if exists demo_insert_academic_sessions on public.academic_sessions;
create policy demo_insert_academic_sessions on public.academic_sessions for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- courses
drop policy if exists demo_insert_courses on public.courses;
create policy demo_insert_courses on public.courses for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- classes
drop policy if exists demo_insert_classes on public.classes;
create policy demo_insert_classes on public.classes for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);
drop policy if exists demo_update_classes on public.classes;
create policy demo_update_classes on public.classes for update to authenticated using (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
) with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- enrollments
drop policy if exists demo_insert_enrollments on public.enrollments;
create policy demo_insert_enrollments on public.enrollments for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- line_items (insert + update for the CASE-alignment PATCH in workflow 4)
drop policy if exists demo_insert_line_items on public.line_items;
create policy demo_insert_line_items on public.line_items for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);
drop policy if exists demo_update_line_items on public.line_items;
create policy demo_update_line_items on public.line_items for update to authenticated using (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
) with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

-- source_identifiers (used by source-system crosswalks the guide may extend)
drop policy if exists demo_insert_source_identifiers on public.source_identifiers;
create policy demo_insert_source_identifiers on public.source_identifiers for insert to authenticated with check (
  tenant_id = coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid
  )
);

commit;
