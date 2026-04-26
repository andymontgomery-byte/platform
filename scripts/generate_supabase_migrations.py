#!/usr/bin/env python3
"""Generate Supabase migrations from the shared dictionary relational graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "data-dictionary.seed.json"

SQL_TYPE_MAP = {
    "text": "text",
    "enum": "text",
    "datetime": "timestamptz",
    "date": "date",
    "integer": "integer",
    "number": "double precision",
}


def main() -> int:
    args = parse_args()
    seed = json.loads(SEED.read_text())
    config = seed.get("migration_generation", {})
    migration_path = ROOT / config.get(
        "migration_path",
        "supabase/migrations/0001_oneroster_core_demo.sql",
    )
    objects = runtime_objects(seed)
    errors = validate_graph(objects, config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    rendered = render_migration(seed, objects, config)
    if args.check:
        if not migration_path.exists():
            print(f"ERROR: missing generated migration: {migration_path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        actual = migration_path.read_text()
        if actual != rendered:
            print(
                "ERROR: supabase/migrations/0001_oneroster_core_demo.sql differs from "
                "data/data-dictionary.seed.json; run `python3 scripts/generate_supabase_migrations.py`",
                file=sys.stderr,
            )
            return 1
        print(f"supabase-migrations-ok migrations=1 tables={len(objects) + 1} relationships={count_relationships(objects)}")
        return 0

    migration_path.parent.mkdir(parents=True, exist_ok=True)
    migration_path.write_text(rendered)
    print(f"generated {migration_path.relative_to(ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated Supabase migrations differ from committed SQL.",
    )
    return parser.parse_args()


def runtime_objects(seed: dict) -> list[dict]:
    config = seed.get("migration_generation", {})
    runtime_keys = config.get("runtime_object_keys", [])
    if runtime_keys:
        objects_by_key = {obj["object_key"]: obj for obj in seed.get("objects", []) if obj.get("object_key")}
        missing = [key for key in runtime_keys if key not in objects_by_key]
        if missing:
            raise SystemExit(f"migration_generation.runtime_object_keys has unknown object keys: {', '.join(missing)}")
        objects = [objects_by_key[key] for key in runtime_keys]
    else:
        spec_key = config.get("source_spec_key", "oneroster-core")
        objects = [obj for obj in seed.get("objects", []) if obj.get("spec_key") == spec_key]
    order = config.get("table_order", [])
    if order:
        by_key = {obj["object_key"]: obj for obj in objects}
        return [by_key[key] for key in order if key in by_key]
    return objects


def validate_graph(objects: list[dict], config: dict) -> list[str]:
    errors: list[str] = []
    if config.get("decision_id") != "DEC-020-relational-graph-migrations":
        errors.append("migration_generation must cite DEC-020-relational-graph-migrations")
    if config.get("generator") != "scripts/generate_supabase_migrations.py":
        errors.append("migration_generation.generator must be scripts/generate_supabase_migrations.py")
    object_by_key = {obj.get("object_key"): obj for obj in objects}
    if len(object_by_key) != len(objects):
        errors.append("runtime objects have duplicate object_key values")

    relationship_keys: set[str] = set()
    for obj in objects:
        fields_by_key = {field.get("field_key"): field for field in obj.get("fields", [])}
        for rel in obj.get("relationships", []):
            rel_key = rel.get("relationship_key")
            if not rel_key:
                errors.append(f"{obj.get('object_key')} relationship missing relationship_key")
                continue
            if rel_key in relationship_keys:
                errors.append(f"duplicate relationship_key: {rel_key}")
            relationship_keys.add(rel_key)
            for key in [
                "from_object",
                "source_field",
                "target_field",
                "relationship_type",
                "cardinality",
                "ownership",
                "delete_behavior",
                "required",
                "index_name",
                "decision_id",
            ]:
                if key not in rel or rel[key] in (None, "", []):
                    errors.append(f"{rel_key} missing {key}")
            if rel.get("from_object") != obj.get("object_key"):
                errors.append(f"{rel_key} from_object does not match containing object")
            source_field = rel.get("source_field")
            if source_field not in fields_by_key:
                errors.append(f"{rel_key} source_field {source_field} is not on {obj.get('object_key')}")
            elif bool(fields_by_key[source_field]["spec_field"].get("required")) != bool(rel.get("required")):
                errors.append(f"{rel_key} required flag does not match {obj.get('object_key')}.{source_field}")
            if rel.get("decision_id") != "DEC-020-relational-graph-migrations":
                errors.append(f"{rel_key} must cite DEC-020-relational-graph-migrations")
            if rel.get("relationship_type") == "foreign_key":
                target = object_by_key.get(rel.get("to_object"))
                if not target:
                    errors.append(f"{rel_key} targets unknown object {rel.get('to_object')}")
                    continue
                target_fields = {field.get("field_key") for field in target.get("fields", [])}
                if rel.get("target_field") not in target_fields:
                    errors.append(f"{rel_key} target_field {rel.get('target_field')} is not on {target.get('object_key')}")
            elif rel.get("relationship_type") == "polymorphic_reference":
                for target_key in rel.get("target_objects", []):
                    if target_key not in object_by_key:
                        errors.append(f"{rel_key} target_objects includes unknown object {target_key}")
            else:
                errors.append(f"{rel_key} has unsupported relationship_type {rel.get('relationship_type')}")

    expected = set(config.get("relationship_keys", []))
    if expected and expected != relationship_keys:
        errors.append(
            "migration_generation.relationship_keys does not match objects[].relationships: "
            f"missing={sorted(expected - relationship_keys)} extra={sorted(relationship_keys - expected)}"
        )
    return errors


def render_migration(seed: dict, objects: list[dict], config: dict) -> str:
    shared_allowed_values_by_spec = shared_values_by_spec(seed)
    runtime_tables = [obj["spec_object"]["table_name"] for obj in objects]
    object_by_key = {obj["object_key"]: obj for obj in objects}
    lines: list[str] = [
        "-- Generated by scripts/generate_supabase_migrations.py.",
        "-- Source: data/data-dictionary.seed.json migration_generation and objects[].relationships.",
        "-- Decision: DEC-020-relational-graph-migrations.",
        "",
        "begin;",
        "",
        "drop view if exists public.class_activity_feed;",
        "drop view if exists public.gradebook_results;",
        "drop view if exists public.class_roster;",
        "drop function if exists public.read_people_sensitive_audited(text, text, text, text, text, text);",
    ]

    for table in ["audit_log", *reversed(runtime_tables)]:
        lines.append(f"drop table if exists public.{table} cascade;")
    lines.append("")

    for obj in objects:
        lines.extend(render_table(obj, object_by_key, shared_allowed_values_by_spec.get(obj.get("spec_key"), {})))
        lines.append("")

    lines.extend(render_audit_table())
    lines.append("")
    lines.extend(render_indexes(objects))
    lines.append("")
    lines.extend(render_views())
    lines.append("")
    lines.extend(render_rls(objects))
    lines.append("")
    lines.extend(render_read_policies(objects))
    lines.extend(render_write_policies(objects))
    lines.extend(render_source_identifier_policy())
    lines.extend(render_audit_policies())
    lines.append("")
    lines.extend(render_audited_read_function())
    lines.append("")
    lines.extend(render_grants(objects))
    lines.append("")
    lines.append("notify pgrst, 'reload schema';")
    lines.append("")
    lines.append("commit;")
    lines.append("")
    return "\n".join(lines)


def render_table(obj: dict, object_by_key: dict[str, dict], shared_allowed_values: dict[str, list[dict]]) -> list[str]:
    table = obj["spec_object"]["table_name"]
    relationships = {
        rel["source_field"]: rel
        for rel in obj.get("relationships", [])
        if rel.get("relationship_type") == "foreign_key"
    }
    column_defs = [
        "  tenant_id uuid not null default coalesce("
        "nullif(auth.jwt() ->> 'tenant_id', '')::uuid, "
        "nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid)"
    ]
    for field in obj["fields"]:
        column_defs.append(
            "  " + render_column(field, relationships.get(field["field_key"]), object_by_key, shared_allowed_values)
        )
    return [
        f"create table public.{table} (",
        *[line + ("," if index < len(column_defs) - 1 else "") for index, line in enumerate(column_defs)],
        ");",
    ]


def render_column(
    field: dict,
    relationship: dict | None,
    object_by_key: dict[str, dict],
    shared_allowed_values: dict[str, list[dict]],
) -> str:
    spec = field["spec_field"]
    column = spec["column_name"]
    sql_type = SQL_TYPE_MAP.get(spec["data_type"])
    if not sql_type:
        raise ValueError(f"unsupported SQL data type {spec['data_type']} for {column}")
    if column == "id":
        return "id text primary key"

    parts = [column, sql_type]
    if spec.get("required"):
        parts.append("not null")
    if column == "sourced_id":
        parts.append("unique")
    if relationship:
        target = object_by_key[relationship["to_object"]]
        target_table = target["spec_object"]["table_name"]
        target_column = column_for_field(target, relationship["target_field"])
        parts.append(f"references public.{target_table}({target_column})")
        if relationship.get("delete_behavior") == "set_null":
            parts.append("on delete set null")
    values = allowed_values(spec, shared_allowed_values)
    if values:
        value_list = ", ".join(sql_quote(value["value"]) for value in values)
        parts.append(f"check ({column} in ({value_list}))")
    return " ".join(parts)


def render_audit_table() -> list[str]:
    return [
        "create table public.audit_log (",
        "  tenant_id uuid not null,",
        "  id bigint generated by default as identity primary key,",
        "  client_id text not null,",
        "  scope text not null,",
        "  purpose text not null,",
        "  field_accessed text not null,",
        "  subject_table text not null,",
        "  subject_id text,",
        "  actor_user_id uuid,",
        "  request_path text,",
        "  request_id text,",
        "  timestamp timestamptz not null default now()",
        ");",
    ]


def render_indexes(objects: list[dict]) -> list[str]:
    lines: list[str] = []
    for obj in objects:
        table = obj["spec_object"]["table_name"]
        lines.append(f"create index {table}_tenant_idx on public.{table}(tenant_id);")
        for rel in obj.get("relationships", []):
            if rel.get("relationship_type") != "foreign_key":
                continue
            source_column = column_for_field(obj, rel["source_field"])
            lines.append(f"create index {rel['index_name']} on public.{table}({source_column});")
        if obj["object_key"] == "source_identifier":
            lines.append("create index source_identifiers_lookup_idx on public.source_identifiers(object_type, object_id);")
    lines.extend(
        [
            "create index audit_log_tenant_timestamp_idx on public.audit_log(tenant_id, timestamp desc);",
            "create index audit_log_field_idx on public.audit_log(field_accessed);",
        ]
    )
    return lines


def render_views() -> list[str]:
    return [
        "create view public.class_roster",
        "with (security_invoker = true) as",
        "select",
        "  e.id as enrollment_id,",
        "  c.id as class_id,",
        "  c.title as class_title,",
        "  p.id as person_id,",
        "  p.display_name,",
        "  p.primary_role,",
        "  e.role as class_role,",
        "  o.name as school_name,",
        "  e.status",
        "from public.enrollments e",
        "join public.classes c on c.id = e.class_id",
        "join public.people p on p.id = e.person_id",
        "join public.organizations o on o.id = e.school_id;",
        "",
        "create view public.gradebook_results",
        "with (security_invoker = true) as",
        "select",
        "  r.id as result_id,",
        "  li.title as line_item_title,",
        "  c.title as class_title,",
        "  p.display_name as learner_name,",
        "  r.score_status,",
        "  r.score,",
        "  li.result_value_max,",
        "  li.case_target_uri,",
        "  r.comment,",
        "  r.score_date",
        "from public.results r",
        "join public.line_items li on li.id = r.line_item_id",
        "join public.classes c on c.id = li.class_id",
        "join public.people p on p.id = r.person_id;",
        "",
        "create view public.class_activity_feed",
        "with (security_invoker = true) as",
        "select",
        "  e.id as event_id,",
        "  e.tenant_id,",
        "  e.group_id as class_id,",
        "  e.event_time,",
        "  e.event_type,",
        "  e.action,",
        "  e.profile,",
        "  jsonb_build_object(",
        "    '@context', 'http://purl.imsglobal.org/ctx/caliper/v1p2',",
        "    'id', e.event_iri,",
        "    'type', e.event_type,",
        "    'action', e.action,",
        "    'profile', e.profile,",
        "    'eventTime', e.event_time,",
        "    'actor', jsonb_build_object(",
        "      'id', e.actor_id,",
        "      'type', 'Person',",
        "      'name', actor.display_name",
        "    ),",
        "    'group', jsonb_build_object(",
        "      'id', c.id,",
        "      'type', 'CourseSection',",
        "      'name', c.title",
        "    ),",
        "    'object', jsonb_build_object(",
        "      'id', li.id,",
        "      'type', 'AssignableDigitalResource',",
        "      'name', li.title,",
        "      'caseItemUri', li.case_target_uri",
        "    ),",
        "    'generated', jsonb_build_object(",
        "      'id', r.id,",
        "      'type', 'Result',",
        "      'score', r.score,",
        "      'maxScore', li.result_value_max",
        "    )",
        "  ) as event",
        "from public.caliper_events e",
        "join public.classes c on c.id = e.group_id",
        "left join public.people actor on actor.id = e.actor_id",
        "left join public.line_items li on li.id = e.object_id",
        "left join public.results r on r.id = e.generated_id;",
    ]


def render_rls(objects: list[dict]) -> list[str]:
    lines: list[str] = []
    for table in [obj["spec_object"]["table_name"] for obj in objects] + ["audit_log"]:
        lines.append(f"alter table public.{table} enable row level security;")
        lines.append(f"alter table public.{table} force row level security;")
    return lines


def render_read_policies(objects: list[dict]) -> list[str]:
    lines: list[str] = []
    for table in [obj["spec_object"]["table_name"] for obj in objects if obj["object_key"] != "source_identifier"]:
        lines.extend(render_tenant_read_policy(table))
    return lines


def render_tenant_read_policy(table: str) -> list[str]:
    return [
        "-- decision_id: DEC-010-tenancy-reference-data; tenant-claim RLS for runtime records.",
        f"create policy demo_read_{table} on public.{table} for select to anon, authenticated using (",
        "  tenant_id = coalesce(",
        "    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
        "    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid,",
        "    case when auth.role() = 'anon' then '11111111-1111-1111-1111-111111111111'::uuid end",
        "  )",
        ");",
    ]


def render_write_policies(objects: list[dict]) -> list[str]:
    lines: list[str] = []
    object_by_key = {obj["object_key"]: obj for obj in objects}
    for obj in objects:
        if obj["object_key"] == "source_identifier":
            continue
        table = obj["spec_object"]["table_name"]
        body = tenant_write_body(obj, object_by_key)
        lines.extend(
            [
                f"-- decision_id: DEC-010-tenancy-reference-data; tenant-claim RLS for {table} writes.",
                f"create policy demo_insert_{table} on public.{table} for insert to authenticated with check (",
                *body,
                ");",
                f"-- decision_id: DEC-010-tenancy-reference-data; tenant-claim RLS for {table} writes.",
                f"create policy demo_update_{table} on public.{table} for update to authenticated using (",
                *tenant_claim_body(),
                ") with check (",
                *body,
                ");",
            ]
        )
    return lines


def tenant_write_body(obj: dict, object_by_key: dict[str, dict]) -> list[str]:
    lines = tenant_claim_body()
    for rel in obj.get("relationships", []):
        if rel.get("relationship_type") != "foreign_key":
            continue
        if rel.get("to_object") == obj.get("object_key"):
            continue
        source_column = column_for_field(obj, rel["source_field"])
        target_obj = object_by_key[rel["to_object"]]
        target_table = target_obj["spec_object"]["table_name"]
        target_column = column_for_field(target_obj, rel["target_field"])
        target_alias = target_table[:1]
        required = bool(rel.get("required"))
        first_line = (
            "  and exists ("
            if required
            else f"  and ({source_column} is null or exists ("
        )
        relation_lines = [
            first_line,
            "    select 1",
            f"    from public.{target_table} {target_alias}",
            f"    where {target_alias}.{target_column} = {source_column}",
            f"      and {target_alias}.tenant_id = coalesce(",
            "        nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
            "        nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid",
            "      )",
            "  )" + (")" if not required else ""),
        ]
        lines.extend(relation_lines)
    return lines


def tenant_claim_body() -> list[str]:
    return [
        "  tenant_id = coalesce(",
        "    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
        "    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid",
        "  )",
    ]


def render_source_identifier_policy() -> list[str]:
    return [
        "-- decision_id: DEC-010-tenancy-reference-data; tenant-claim RLS for identifier crosswalks.",
        "create policy demo_read_source_identifiers on public.source_identifiers for select to anon, authenticated using (",
        "  tenant_id = coalesce(",
        "    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
        "    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid,",
        "    case when auth.role() = 'anon' then '11111111-1111-1111-1111-111111111111'::uuid end",
        "  )",
        ");",
    ]


def render_audit_policies() -> list[str]:
    return [
        "-- decision_id: DEC-013-audit-response-truth; audit writes remain tenant-scoped.",
        "create policy demo_insert_audit_log on public.audit_log for insert to authenticated with check (",
        "  tenant_id = coalesce(",
        "    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
        "    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid",
        "  )",
        "  and client_id <> ''",
        "  and scope <> ''",
        "  and purpose <> ''",
        "  and field_accessed <> ''",
        ");",
        "-- decision_id: DEC-013-audit-response-truth; audited responses read back tenant-scoped rows.",
        "create policy demo_read_audit_log on public.audit_log for select to authenticated using (",
        "  tenant_id = coalesce(",
        "    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
        "    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid",
        "  )",
        ");",
    ]


def render_audited_read_function() -> list[str]:
    return [
        "-- decision_id: DEC-013-audit-response-truth; sensitive reads write audit_log rows before returning data.",
        "create function public.read_people_sensitive_audited(",
        "  person_id text,",
        "  client_id text,",
        "  scope text,",
        "  purpose text,",
        "  request_path text default null,",
        "  request_id text default null",
        ")",
        "returns table (",
        "  id text,",
        "  sourced_id text,",
        "  display_name text,",
        "  given_name text,",
        "  family_name text,",
        "  email text,",
        "  primary_role text",
        ")",
        "language plpgsql",
        "security definer",
        "set search_path = public",
        "as $$",
        "declare",
        "  caller_tenant uuid;",
        "  safe_client_id text := nullif(btrim(client_id), '');",
        "  safe_scope text := nullif(btrim(scope), '');",
        "  safe_purpose text := nullif(btrim(purpose), '');",
        "  person_row public.people%rowtype;",
        "begin",
        "  caller_tenant := coalesce(",
        "    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,",
        "    nullif(auth.jwt() -> 'app_metadata' ->> 'tenant_id', '')::uuid",
        "  );",
        "",
        "  if caller_tenant is null then",
        "    raise exception 'tenant_id claim is required for audited sensitive reads'",
        "      using errcode = '28000';",
        "  end if;",
        "",
        "  if safe_client_id is null or safe_scope is null or safe_purpose is null then",
        "    raise exception 'client_id, scope, and purpose are required for audited sensitive reads'",
        "      using errcode = '22023';",
        "  end if;",
        "",
        "  select *",
        "    into person_row",
        "    from public.people p",
        "   where p.id = person_id",
        "     and p.tenant_id = caller_tenant;",
        "",
        "  if not found then",
        "    return;",
        "  end if;",
        "",
        "  insert into public.audit_log (",
        "    tenant_id,",
        "    client_id,",
        "    scope,",
        "    purpose,",
        "    field_accessed,",
        "    subject_table,",
        "    subject_id,",
        "    actor_user_id,",
        "    request_path,",
        "    request_id",
        "  )",
        "  select",
        "    caller_tenant,",
        "    safe_client_id,",
        "    safe_scope,",
        "    safe_purpose,",
        "    field_name,",
        "    'people',",
        "    person_row.id,",
        "    auth.uid(),",
        "    nullif(btrim(request_path), ''),",
        "    nullif(btrim(request_id), '')",
        "  from unnest(array[",
        "    'people.display_name',",
        "    'people.given_name',",
        "    'people.family_name',",
        "    'people.email',",
        "    'people.primary_role'",
        "  ]) as audited(field_name);",
        "",
        "  return query",
        "  select",
        "    person_row.id,",
        "    person_row.sourced_id,",
        "    person_row.display_name,",
        "    person_row.given_name,",
        "    person_row.family_name,",
        "    person_row.email,",
        "    person_row.primary_role;",
        "end;",
        "$$;",
    ]


def render_grants(objects: list[dict]) -> list[str]:
    runtime_tables = [obj["spec_object"]["table_name"] for obj in objects]
    select_tables = [
        table
        for table in runtime_tables
        if table not in {"people"}
    ]
    write_tables = [
        table
        for obj in objects
        for table in [obj["spec_object"]["table_name"]]
        if obj["object_key"] != "source_identifier"
    ]
    return [
        "grant usage on schema public to anon, authenticated;",
        "revoke all privileges on",
        *format_table_list([*runtime_tables, "audit_log"]),
        "from anon, authenticated;",
        "revoke all on function public.read_people_sensitive_audited(text, text, text, text, text, text) from public;",
        "",
        "grant select on",
        *format_table_list([*select_tables, "class_roster", "gradebook_results", "class_activity_feed"]),
        "to anon, authenticated;",
        "",
        "grant select (",
        "  tenant_id,",
        "  id,",
        "  sourced_id,",
        "  display_name,",
        "  primary_role,",
        "  status,",
        "  date_last_modified",
        ") on public.people to anon, authenticated;",
        "",
        "grant insert, update on",
        *format_table_list(write_tables),
        "to authenticated;",
        "grant select, insert on public.audit_log to authenticated;",
        "grant execute on function public.read_people_sensitive_audited(text, text, text, text, text, text) to authenticated;",
    ]


def format_table_list(tables: list[str]) -> list[str]:
    return [
        f"  public.{table}" + ("," if index < len(tables) - 1 else "")
        for index, table in enumerate(tables)
    ]


def shared_values_by_spec(seed: dict) -> dict[str, dict[str, list[dict]]]:
    values: dict[str, dict[str, list[dict]]] = {}
    for projection in seed.get("spec_dictionary_projections", []):
        spec_key = projection.get("spec_key")
        if spec_key:
            values[spec_key] = projection.get("dictionary_header", {}).get("shared_allowed_values", {})
    return values


def allowed_values(spec_field: dict, shared_allowed_values: dict[str, list[dict]]) -> list[dict]:
    if "allowed_values" in spec_field:
        return spec_field["allowed_values"]
    ref = spec_field.get("allowed_values_ref")
    if ref:
        return shared_allowed_values.get(ref, [])
    return []


def column_for_field(obj: dict, field_key: str) -> str:
    for field in obj.get("fields", []):
        if field.get("field_key") == field_key:
            return field["spec_field"]["column_name"]
    raise KeyError(f"{obj.get('object_key')} has no field {field_key}")


def count_relationships(objects: list[dict]) -> int:
    return sum(len(obj.get("relationships", [])) for obj in objects)


def sql_quote(value: object) -> str:
    return "'" + str(value).replace("'", "''") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
