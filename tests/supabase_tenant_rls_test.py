#!/usr/bin/env python3
"""Verify live Supabase RLS isolates OneRoster rows by tenant JWT claim."""

from __future__ import annotations

import base64
import json
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TENANT_A = "11111111-1111-1111-1111-111111111111"
TENANT_B = "22222222-2222-2222-2222-222222222222"
TENANT_A_ROW = "person_ada"
TENANT_B_ROW = "person_tenant_b_student"


def main() -> int:
    env = load_env()
    supabase_url = first(env, "SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
    publishable_key = first(
        env,
        "SUPABASE_PUBLISHABLE_KEY",
        "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_ANON_KEY",
    )
    # Admin operation: tenant_rls_test_auth_fixture_setup.
    service_role_key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    missing = [
        name
        for name, value in [
            ("SUPABASE_URL", supabase_url),
            ("SUPABASE_PUBLISHABLE_KEY or SUPABASE_ANON_KEY", publishable_key),
            ("SUPABASE_SERVICE_ROLE_KEY", service_role_key),
        ]
        if not value
    ]
    if missing:
        print(f"Missing required environment values: {', '.join(missing)}", file=sys.stderr)
        return 2

    users: list[str] = []
    try:
        token_a, user_a = create_tenant_user(supabase_url, service_role_key, publishable_key, TENANT_A, "a")
        users.append(user_a)
        token_b, user_b = create_tenant_user(supabase_url, service_role_key, publishable_key, TENANT_B, "b")
        users.append(user_b)

        assert_token_tenant(token_a, TENANT_A)
        assert_token_tenant(token_b, TENANT_B)

        tenant_a_people = fetch_people(supabase_url, publishable_key, token_a)
        tenant_b_people = fetch_people(supabase_url, publishable_key, token_b)

        tenant_a_ids = {row["id"] for row in tenant_a_people}
        tenant_b_ids = {row["id"] for row in tenant_b_people}

        require(TENANT_A_ROW in tenant_a_ids, f"tenant A token could not read {TENANT_A_ROW}")
        require(TENANT_B_ROW not in tenant_a_ids, "tenant A token read tenant B person row")
        require(TENANT_B_ROW in tenant_b_ids, f"tenant B token could not read {TENANT_B_ROW}")
        require(TENANT_A_ROW not in tenant_b_ids, "tenant B token read tenant A person row")

        print(
            json.dumps(
                {
                    "ok": True,
                    "check": "supabase_tenant_rls",
                    "tenantAVisibleRows": len(tenant_a_people),
                    "tenantBVisibleRows": len(tenant_b_people),
                    "tenantACannotReadTenantB": True,
                    "tenantBCannotReadTenantA": True,
                },
                indent=2,
            )
        )
        return 0
    finally:
        for user_id in users:
            delete_user(supabase_url, service_role_key, user_id)


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for name in [".env.local", ".env", ".env.example"]:
        path = ROOT / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            clean = line.strip()
            if not clean or clean.startswith("#") or "=" not in clean:
                continue
            key, value = clean.split("=", 1)
            values.setdefault(key.strip(), value.strip().strip("'\""))
    return values


def first(values: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = values.get(key)
        if value:
            return value
    return None


def create_tenant_user(
    supabase_url: str,
    service_role_key: str,
    publishable_key: str,
    tenant_id: str,
    label: str,
) -> tuple[str, str]:
    email = f"tenant-rls-{label}-{secrets.token_hex(8)}@example.invalid"
    password = "Tenant-RLS-" + secrets.token_urlsafe(18)
    user = request_json(
        "POST",
        f"{supabase_url.rstrip('/')}/auth/v1/admin/users",
        service_role_key,
        {
            "email": email,
            "password": password,
            "email_confirm": True,
            "app_metadata": {
                "tenant_id": tenant_id,
                "test_owner": "platform_tenant_rls",
            },
        },
    )
    user_id = user.get("id")
    require(isinstance(user_id, str) and user_id, "admin user creation did not return an id")

    token_payload = request_json(
        "POST",
        f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password",
        publishable_key,
        {
            "email": email,
            "password": password,
        },
    )
    access_token = token_payload.get("access_token")
    require(isinstance(access_token, str) and access_token, "password grant did not return access_token")
    return access_token, user_id


def delete_user(supabase_url: str, service_role_key: str | None, user_id: str) -> None:
    if not service_role_key:
        return
    try:
        request_json(
            "DELETE",
            f"{supabase_url.rstrip('/')}/auth/v1/admin/users/{urllib.parse.quote(user_id)}",
            service_role_key,
            None,
        )
    except RuntimeError as exc:
        print(f"warning: could not delete temporary auth user {user_id}: {exc}", file=sys.stderr)


def fetch_people(supabase_url: str, publishable_key: str, access_token: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "select": "id,sourced_id,display_name,tenant_id",
            "order": "id.asc",
        },
        safe=",",
    )
    data = request_json(
        "GET",
        f"{supabase_url.rstrip('/')}/rest/v1/people?{query}",
        publishable_key,
        None,
        bearer=access_token,
    )
    require(isinstance(data, list), "people REST response was not a JSON array")
    return data


def request_json(
    method: str,
    url: str,
    api_key: str,
    body: object | None,
    *,
    bearer: str | None = None,
) -> object:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        method=method,
        data=data,
        headers={
            "apikey": api_key,
            "authorization": f"Bearer {bearer or api_key}",
            "content-type": "application/json",
            "accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"{method} {url} failed: {error.reason}") from error


def assert_token_tenant(access_token: str, tenant_id: str) -> None:
    parts = access_token.split(".")
    require(len(parts) >= 2, "access token was not a JWT")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")).decode("utf-8"))
    actual = claims.get("tenant_id") or claims.get("app_metadata", {}).get("tenant_id")
    require(actual == tenant_id, f"access token tenant claim was {actual!r}, expected {tenant_id!r}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


if __name__ == "__main__":
    raise SystemExit(main())
