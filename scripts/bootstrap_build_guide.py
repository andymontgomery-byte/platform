#!/usr/bin/env python3
"""Bootstrap the buildability guide sandbox.

Loads the platform migration into a Supabase project, creates one temporary
tenant-scoped Auth user, exchanges it for a user JWT, and writes shell exports
for the remaining build-guide curls.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MIGRATION = ROOT / "supabase" / "migrations" / "0001_oneroster_core_demo.sql"
DEFAULT_ENV_OUT = Path("/tmp/platform-build-guide.env")
DEFAULT_TENANT_ID = "33333333-3333-3333-3333-333333333333"


def main() -> int:
    args = parse_args()
    supabase_url = required_value(args.supabase_url, "SUPABASE_URL")
    publishable_key = required_value(args.publishable_key, "SUPABASE_PUBLISHABLE_KEY")
    service_role_key = secret_value(args.service_role_key, "SUPABASE_SERVICE_ROLE_KEY")
    db_url = required_value(args.db_url, "SUPABASE_DB_URL")
    db_password = args.db_password or os.environ.get("SUPABASE_DB_PASSWORD")
    tenant_id = args.tenant_id

    run_migration(db_url=db_url, db_password=db_password, migration=args.migration)

    stamp = int(time.time())
    email = args.email or f"build-guide-{stamp}@example.invalid"
    password = args.password or f"Build-guide-{stamp}"
    create_auth_user(
        supabase_url=supabase_url,
        service_role_key=service_role_key,
        email=email,
        password=password,
        tenant_id=tenant_id,
    )
    access_token = fetch_access_token(
        supabase_url=supabase_url,
        publishable_key=publishable_key,
        email=email,
        password=password,
    )
    write_env(
        path=args.env_out,
        values={
            "SUPABASE_URL": supabase_url,
            "SUPABASE_PUBLISHABLE_KEY": publishable_key,
            "PLATFORM_TENANT_ID": tenant_id,
            "PLATFORM_ACCESS_TOKEN": access_token,
            "BUILD_GUIDE_EMAIL": email,
        },
    )
    print(f"build-guide-bootstrap-ok env={args.env_out}")
    print(f"Run: source {shlex.quote(str(args.env_out))}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supabase-url", default=os.environ.get("SUPABASE_URL"))
    parser.add_argument("--publishable-key", default=os.environ.get("SUPABASE_PUBLISHABLE_KEY"))
    parser.add_argument("--service-role-key", default=os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
    parser.add_argument("--db-url", default=os.environ.get("SUPABASE_DB_URL"))
    parser.add_argument("--db-password", default=os.environ.get("SUPABASE_DB_PASSWORD"))
    parser.add_argument("--tenant-id", default=os.environ.get("PLATFORM_TENANT_ID", DEFAULT_TENANT_ID))
    parser.add_argument("--email", default=os.environ.get("BUILD_GUIDE_EMAIL"))
    parser.add_argument("--password", default=os.environ.get("BUILD_GUIDE_PASSWORD"))
    parser.add_argument("--env-out", type=Path, default=DEFAULT_ENV_OUT)
    parser.add_argument("--migration", type=Path, default=DEFAULT_MIGRATION)
    return parser.parse_args()


def required_value(value: str | None, name: str) -> str:
    if value:
        return value
    print(f"Missing {name}; pass the matching flag or export {name}.", file=sys.stderr)
    raise SystemExit(2)


def secret_value(value: str | None, name: str) -> str:
    if value:
        return value
    entered = getpass.getpass(f"{name}: ")
    if not entered:
        print(f"Missing {name}.", file=sys.stderr)
        raise SystemExit(2)
    return entered


def run_migration(*, db_url: str, db_password: str | None, migration: Path) -> None:
    if shutil.which("psql") is None:
        print("Missing psql. Install PostgreSQL client tools and rerun this command.", file=sys.stderr)
        raise SystemExit(2)
    if not migration.exists():
        print(f"Migration not found: {migration}", file=sys.stderr)
        raise SystemExit(2)
    env = os.environ.copy()
    if db_password:
        env["PGPASSWORD"] = db_password
    subprocess.run(
        ["psql", db_url, "-v", "ON_ERROR_STOP=1", "-f", str(migration)],
        check=True,
        env=env,
    )


def create_auth_user(
    *,
    supabase_url: str,
    service_role_key: str,
    email: str,
    password: str,
    tenant_id: str,
) -> None:
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "app_metadata": {
            "tenant_id": tenant_id,
            "test_owner": "platform_buildability_guide",
        },
    }
    request_json(
        f"{supabase_url.rstrip('/')}/auth/v1/admin/users",
        method="POST",
        headers={
            "apikey": service_role_key,
            "authorization": f"Bearer {service_role_key}",
            "content-type": "application/json",
        },
        payload=payload,
    )


def fetch_access_token(
    *,
    supabase_url: str,
    publishable_key: str,
    email: str,
    password: str,
) -> str:
    response = request_json(
        f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password",
        method="POST",
        headers={
            "apikey": publishable_key,
            "content-type": "application/json",
        },
        payload={"email": email, "password": password},
    )
    token = response.get("access_token")
    if not token:
        print("Supabase token response did not include access_token.", file=sys.stderr)
        raise SystemExit(2)
    return str(token)


def request_json(url: str, *, method: str, headers: dict[str, str], payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            body = res.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code} from {url}: {detail}", file=sys.stderr)
        raise SystemExit(2) from exc
    except urllib.error.URLError as exc:
        print(f"Request failed for {url}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    return json.loads(body) if body else {}


def write_env(*, path: Path, values: dict[str, str]) -> None:
    lines = [f"export {key}={shlex.quote(value)}" for key, value in values.items()]
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
