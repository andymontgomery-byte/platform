#!/usr/bin/env python3
"""Smoke-test public read access to the Supabase demo REST API."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://qzxlgrerjoiamxvnkklq.supabase.co"


def main() -> int:
    env = load_env()
    supabase_url = first(env, "SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL") or DEFAULT_URL
    publishable_key = first(
        env,
        "SUPABASE_PUBLISHABLE_KEY",
        "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_ANON_KEY",
    )

    if not publishable_key:
        print("Missing SUPABASE_PUBLISHABLE_KEY or NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY.", file=sys.stderr)
        return 2

    checks = [
        ("people", "/rest/v1/people", {"select": "id,display_name", "order": "id.asc", "limit": "1"}),
        (
            "class_roster",
            "/rest/v1/class_roster",
            {"select": "class_title,display_name,class_role", "order": "class_title.asc,display_name.asc", "limit": "1"},
        ),
        (
            "gradebook_results",
            "/rest/v1/gradebook_results",
            {"select": "class_title,line_item_title,learner_name,score_status,score", "limit": "1"},
        ),
    ]
    results = {}
    for name, path, query in checks:
        results[name] = fetch_json(supabase_url, publishable_key, path, query)

    print(json.dumps({"ok": True, "supabaseUrl": supabase_url, "checks": results}, indent=2))
    return 0


def load_env() -> dict[str, str]:
    values = dict(os.environ)
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


def fetch_json(base_url: str, publishable_key: str, path: str, query: dict[str, str]) -> object:
    encoded = urllib.parse.urlencode(query, safe=",.")
    url = base_url.rstrip("/") + path + "?" + encoded
    request = urllib.request.Request(
        url,
        headers={
            "apikey": publishable_key,
            "authorization": f"Bearer {publishable_key}",
            "accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{path} returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"{path} failed: {error.reason}") from error


if __name__ == "__main__":
    raise SystemExit(main())
