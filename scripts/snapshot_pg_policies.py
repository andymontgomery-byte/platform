#!/usr/bin/env python3
"""Snapshot PostgreSQL RLS and policy metadata from the live Supabase project."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "supabase" / "policies" / "pg_policies.snapshot.json"
DEFAULT_ENV_FILE = ROOT / ".env.local"
PSQL_CANDIDATES = [
    "psql",
    "/opt/homebrew/opt/libpq/bin/psql",
    "/usr/local/opt/libpq/bin/psql",
]

SNAPSHOT_SQL_TEMPLATE = r"""
with user_tables as (
  select
    n.nspname as schema_name,
    c.relname as table_name,
    c.relrowsecurity as rowsecurity,
    c.relforcerowsecurity as force_rowsecurity
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where c.relkind = 'r'
    and n.nspname not in ('information_schema', 'pg_catalog')
    and n.nspname not like 'pg_toast%'
    and n.nspname not like 'pg_temp_%'
    and n.nspname in ({schema_list})
)
select jsonb_pretty(
  jsonb_build_object(
    'source', jsonb_build_object(
      'provider', 'Supabase',
      'projectUrl', 'https://qzxlgrerjoiamxvnkklq.supabase.co',
      'schemas', jsonb_build_array({schema_list})
    ),
    'generatedAt', to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
    'tables', coalesce(
      jsonb_agg(
        jsonb_build_object(
          'schema', t.schema_name,
          'table', t.table_name,
          'qualifiedName', t.schema_name || '.' || t.table_name,
          'rowsecurity', t.rowsecurity,
          'forceRowSecurity', t.force_rowsecurity,
          'policies', coalesce(
            (
              select jsonb_agg(
                jsonb_build_object(
                  'decision_id',
                  case
                    when p.policyname in ('demo_insert_audit_log', 'demo_read_audit_log') then 'DEC-013-audit-response-truth'
                    else 'DEC-010-tenancy-reference-data'
                  end,
                  'policyName', p.policyname,
                  'permissive', p.permissive,
                  'roles', p.roles,
                  'command', p.cmd,
                  'using', p.qual,
                  'withCheck', p.with_check
                )
                order by p.policyname
              )
              from pg_policies p
              where p.schemaname = t.schema_name
                and p.tablename = t.table_name
            ),
            '[]'::jsonb
          )
        )
        order by t.schema_name, t.table_name
      ),
      '[]'::jsonb
    )
  )
) as snapshot
from user_tables t;
"""


def main() -> int:
    args = parse_args()
    env = load_env(Path(args.env_file))
    db_url = args.db_url or env.get("SUPABASE_DB_URL")
    if not db_url:
        print("Missing SUPABASE_DB_URL. Put it in .env.local or pass --db-url.", file=sys.stderr)
        return 2

    psql = find_psql()
    if not psql:
        print("psql not found. Install PostgreSQL client tools or Homebrew libpq.", file=sys.stderr)
        return 2

    snapshot = run_snapshot(psql, db_url, args.schema)
    parsed = json.loads(snapshot)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n")
    try:
        display_path = output.relative_to(ROOT)
    except ValueError:
        display_path = output
    print(f"wrote {display_path} tables={len(parsed.get('tables', []))}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Snapshot output JSON path.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Env file containing SUPABASE_DB_URL.")
    parser.add_argument("--db-url", help="PostgreSQL connection URI. Prefer .env.local for secrets.")
    parser.add_argument(
        "--schema",
        action="append",
        default=["public"],
        help="Schema to include. Repeat for multiple schemas. Default: public.",
    )
    return parser.parse_args()


def load_env(path: Path) -> dict[str, str]:
    values = dict(os.environ)
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        key, value = clean.split("=", 1)
        values.setdefault(key.strip(), value.strip().strip("'\""))
    return values


def find_psql() -> str | None:
    for candidate in PSQL_CANDIDATES:
        found = shutil.which(candidate) if candidate == "psql" else candidate
        if found and Path(found).exists():
            return found
    return None


def run_snapshot(psql: str, db_url: str, schemas: list[str]) -> str:
    schema_list = ", ".join(sql_literal(schema) for schema in schemas)
    query = SNAPSHOT_SQL_TEMPLATE.format(schema_list=schema_list)
    command = [
        psql,
        db_url,
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "--tuples-only",
        "--no-align",
        "-c",
        query,
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
