#!/usr/bin/env python3
"""Verify live Supabase sensitive reads create tenant-scoped audit rows."""

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
PERSON_ID = "person_ada"
AUDIT_SCOPE = "platform.roster.users.directory:read"
AUDIT_PURPOSE = "directory-review-test"
REQUIRED_FIELDS = {
    "people.display_name",
    "people.given_name",
    "people.family_name",
    "people.email",
    "people.primary_role",
}


def main() -> int:
    env = load_env()
    supabase_url = first(env, "SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
    publishable_key = first(
        env,
        "SUPABASE_PUBLISHABLE_KEY",
        "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_ANON_KEY",
    )
    # Admin operation: audit_log_test_auth_fixture_setup.
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

    client_id = f"audit-test-client-{secrets.token_hex(6)}"
    user_id: str | None = None
    try:
        access_token, user_id = create_audit_user(
            supabase_url,
            service_role_key,
            publishable_key,
            client_id,
        )
        assert_token_claims(access_token, client_id)
        assert_direct_restricted_rest_blocked(supabase_url, publishable_key, access_token)

        request_id = f"audit-test-{secrets.token_hex(6)}"
        function_payload = call_audited_read(
            supabase_url,
            publishable_key,
            access_token,
            client_id,
            request_id,
        )
        person = function_payload.get("person")
        require(isinstance(person, dict), "audited read did not return a person object")
        require(person.get("id") == PERSON_ID, f"audited read returned {person.get('id')!r}")
        require(person.get("email"), "audited read did not return a restricted email field")

        audit_rows = fetch_audit_rows(supabase_url, publishable_key, access_token, client_id, request_id)
        fields_seen = {row.get("field_accessed") for row in audit_rows}
        missing_fields = sorted(REQUIRED_FIELDS - fields_seen)
        require(not missing_fields, f"audit rows missing fields: {', '.join(missing_fields)}")
        assert_response_audit_matches_rows(function_payload.get("audit"), audit_rows, client_id, request_id)

        for row in audit_rows:
            require(row.get("client_id") == client_id, "audit row client_id did not match")
            require(row.get("scope") == AUDIT_SCOPE, "audit row scope did not match")
            require(row.get("purpose") == AUDIT_PURPOSE, "audit row purpose did not match")
            require(row.get("tenant_id") == TENANT_A, "audit row tenant_id did not match")
            require(row.get("request_id") == request_id, "audit row request_id did not match")
            require(row.get("timestamp"), "audit row timestamp was empty")

        print(
            json.dumps(
                {
                    "ok": True,
                    "check": "supabase_audit_log",
                    "clientId": client_id,
                    "auditedPerson": PERSON_ID,
                    "directRestrictedRestBlocked": True,
                    "auditRows": len(audit_rows),
                    "fieldsSeen": sorted(fields_seen),
                },
                indent=2,
            )
        )
        return 0
    finally:
        if user_id:
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


def create_audit_user(
    supabase_url: str,
    service_role_key: str,
    publishable_key: str,
    client_id: str,
) -> tuple[str, str]:
    email = f"audit-log-{secrets.token_hex(8)}@example.invalid"
    password = "Audit-Log-" + secrets.token_urlsafe(18)
    user = request_json(
        "POST",
        f"{supabase_url.rstrip('/')}/auth/v1/admin/users",
        service_role_key,
        {
            "email": email,
            "password": password,
            "email_confirm": True,
            "app_metadata": {
                "tenant_id": TENANT_A,
                "client_id": client_id,
                "scope": AUDIT_SCOPE,
                "purpose": AUDIT_PURPOSE,
                "test_owner": "platform_audit_log",
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


def call_audited_read(
    supabase_url: str,
    publishable_key: str,
    access_token: str,
    client_id: str,
    request_id: str,
) -> dict:
    functions_url = supabase_url.rstrip("/").replace(".supabase.co", ".functions.supabase.co")
    payload = request_json(
        "GET",
        f"{functions_url}/audited-roster-read?personId={urllib.parse.quote(PERSON_ID)}",
        publishable_key,
        None,
        bearer=access_token,
        extra_headers={
            "x-platform-client-id": client_id,
            "x-platform-scope": AUDIT_SCOPE,
            "x-platform-purpose": AUDIT_PURPOSE,
            "x-request-id": request_id,
        },
    )
    require(isinstance(payload, dict), "audited Edge Function response was not a JSON object")
    return payload


def assert_direct_restricted_rest_blocked(
    supabase_url: str,
    publishable_key: str,
    access_token: str,
) -> None:
    query = urllib.parse.urlencode(
        {
            "select": "id,email",
            "id": f"eq.{PERSON_ID}",
            "limit": "1",
        },
        safe=",.",
    )
    url = f"{supabase_url.rstrip('/')}/rest/v1/people?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "apikey": publishable_key,
            "authorization": f"Bearer {access_token}",
            "accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"direct restricted REST read unexpectedly returned HTTP {response.status}: {body}")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        require(error.code in (401, 403), f"direct restricted REST read returned HTTP {error.code}: {body}")
        require("permission denied" in body.lower(), f"direct restricted REST error was unexpected: {body}")
    except urllib.error.URLError as error:
        raise RuntimeError(f"direct restricted REST read failed unexpectedly: {error.reason}") from error


def fetch_audit_rows(
    supabase_url: str,
    publishable_key: str,
    access_token: str,
    client_id: str,
    request_id: str,
) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "select": "id,client_id,scope,purpose,field_accessed,tenant_id,timestamp,subject_id,request_id",
            "client_id": f"eq.{client_id}",
            "subject_id": f"eq.{PERSON_ID}",
            "request_id": f"eq.{request_id}",
            "order": "id.asc",
            "limit": "20",
        },
        safe=",.",
    )
    data = request_json(
        "GET",
        f"{supabase_url.rstrip('/')}/rest/v1/audit_log?{query}",
        publishable_key,
        None,
        bearer=access_token,
    )
    require(isinstance(data, list), "audit_log REST response was not a JSON array")
    return data


def assert_response_audit_matches_rows(
    audit: object,
    audit_rows: list[dict],
    client_id: str,
    request_id: str,
) -> None:
    require(isinstance(audit, dict), "audited Edge Function response did not include an audit object")
    fields_from_rows = [row.get("field_accessed") for row in audit_rows]
    require(audit.get("logged") == len(audit_rows), "response audit logged count did not match audit_log rows")
    require(audit.get("fields") == fields_from_rows, "response audit fields did not match audit_log rows")
    require(audit.get("clientId") == client_id, "response audit clientId did not match")
    require(audit.get("scope") == AUDIT_SCOPE, "response audit scope did not match")
    require(audit.get("purpose") == AUDIT_PURPOSE, "response audit purpose did not match")
    require(audit.get("tenantId") == TENANT_A, "response audit tenantId did not match")
    require(audit.get("requestId") == request_id, "response audit requestId did not match")


def request_json(
    method: str,
    url: str,
    api_key: str,
    body: object | None,
    *,
    bearer: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> object:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "apikey": api_key,
        "authorization": f"Bearer {bearer or api_key}",
        "content-type": "application/json",
        "accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"{method} {url} failed: {error.reason}") from error


def assert_token_claims(access_token: str, client_id: str) -> None:
    parts = access_token.split(".")
    require(len(parts) >= 2, "access token was not a JWT")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")).decode("utf-8"))
    app_metadata = claims.get("app_metadata", {})
    actual_tenant = claims.get("tenant_id") or app_metadata.get("tenant_id")
    actual_client = claims.get("client_id") or app_metadata.get("client_id")
    actual_scope = claims.get("scope") or app_metadata.get("scope")
    actual_purpose = claims.get("purpose") or app_metadata.get("purpose")
    require(actual_tenant == TENANT_A, f"access token tenant claim was {actual_tenant!r}")
    require(actual_client == client_id, f"access token client_id claim was {actual_client!r}")
    require(actual_scope == AUDIT_SCOPE, f"access token scope claim was {actual_scope!r}")
    require(actual_purpose == AUDIT_PURPOSE, f"access token purpose claim was {actual_purpose!r}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


if __name__ == "__main__":
    raise SystemExit(main())
