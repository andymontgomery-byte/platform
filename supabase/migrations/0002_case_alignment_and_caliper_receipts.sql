-- decision_id: DEC-006-standards-alignment, DEC-016-dictionary-canonical, DEC-019-closed-privacy-classes
-- Adds the smallest schema shape needed to:
--   1. Link a OneRoster line item to a CASE framework item URI (assignment alignment).
--   2. Persist a tenant-scoped Caliper event receipt for the activity feed read path.
-- Both are idempotent so the migration is safe to re-run.

begin;

-- 1. CASE alignment on line items.
alter table public.line_items
  add column if not exists case_framework_item_uri text,
  add column if not exists case_framework_item_human_coding text;

comment on column public.line_items.case_framework_item_uri is
  'CASE 1.1 CFItem.uri the line item is aligned to. Public per DEC-019. Resolves to docs/generated/case-core-dictionary.md#case-framework-item.';
comment on column public.line_items.case_framework_item_human_coding is
  'CASE 1.1 CFItem.humanCodingScheme shown to teachers (e.g. CCSS.MATH.CONTENT.6.EE.A.2). Public per DEC-019.';

-- 2. Caliper event receipts (tenant-scoped, RLS-enforced).
create table if not exists public.caliper_event_receipts (
  tenant_id uuid not null,
  id text primary key,
  envelope_sensor text not null,
  event_id text not null,
  event_type text not null,
  action text,
  actor_id text,
  object_id text,
  event_time timestamptz,
  received_at timestamptz not null default now(),
  raw_event jsonb not null
);

create index if not exists caliper_event_receipts_tenant_time_idx
  on public.caliper_event_receipts (tenant_id, received_at desc);

create index if not exists caliper_event_receipts_actor_idx
  on public.caliper_event_receipts (tenant_id, actor_id);

alter table public.caliper_event_receipts enable row level security;

drop policy if exists caliper_event_receipts_select_tenant on public.caliper_event_receipts;
create policy caliper_event_receipts_select_tenant
  on public.caliper_event_receipts
  for select
  using (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
      or tenant_id = ((auth.jwt() -> 'app_metadata') ->> 'tenant_id')::uuid);

drop policy if exists caliper_event_receipts_insert_tenant on public.caliper_event_receipts;
create policy caliper_event_receipts_insert_tenant
  on public.caliper_event_receipts
  for insert
  with check (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
           or tenant_id = ((auth.jwt() -> 'app_metadata') ->> 'tenant_id')::uuid);

comment on table public.caliper_event_receipts is
  'Tenant-scoped Caliper 1.2 event receipts written by the caliper-event-ingestion Edge Function. Resolves to docs/generated/caliper-core-dictionary.md#caliper-event.';

commit;
