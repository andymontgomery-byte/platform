#!/usr/bin/env python3
"""Build GitHub Pages JSON endpoints from the demo SQLite schema and seed data."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DICTIONARY = ROOT / "dictionary" / "oneroster-core.v1.json"
SCHEMA = ROOT / "demo" / "schema.sql"
SEED = ROOT / "demo" / "seed.sql"
OUT = ROOT / "site" / "api"
SUPABASE_URL = "https://qzxlgrerjoiamxvnkklq.supabase.co"
STATIC_MIRROR_DECISION_ID = "DEC-014-static-mirror-policy"
STATIC_PRIVACY_DECISION_ID = "DEC-011-privacy-surfaces"


def main() -> None:
    dictionary = json.loads(DICTIONARY.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA.read_text())
    db.executescript(SEED.read_text())

    endpoints = []
    write_json(
        OUT / "health.json",
        {
            "ok": True,
            "name": "Platform OneRoster Core Static JSON API",
            "hosting": "GitHub Pages",
            "dictionaryVersion": dictionary["dictionary_version"],
            "decision_id": STATIC_MIRROR_DECISION_ID,
        },
    )
    endpoints.append(["health", "api/health.json"])

    for obj in dictionary["objects"]:
        rows = db.execute(f"select * from {obj['table_name']} order by id").fetchall()
        payload = {
            "items": [row_to_json(obj, row) for row in rows],
            "count": len(rows),
            "decision_id": STATIC_MIRROR_DECISION_ID,
            "source": {
                "objectKey": obj["object_key"],
                "tableName": obj["table_name"],
                "dictionary": "dictionary/oneroster-core.v1.json",
                "decision_id": STATIC_MIRROR_DECISION_ID,
                "decision_ids": source_decision_ids(obj),
                "fieldDecisionIds": field_decision_ids(obj),
            },
        }
        file_name = api_file_name(obj["api_path"])
        write_json(OUT / file_name, payload)
        endpoints.append([obj["api_path"], f"api/{file_name}"])

    view_specs = [
        ("class-roster", "select * from class_roster order by class_title, class_role, display_name"),
        (
            "gradebook-results",
            "select * from gradebook_results order by class_title, line_item_title, learner_name",
        ),
    ]
    views_dir = OUT / "views"
    views_dir.mkdir(exist_ok=True)
    for name, sql in view_specs:
        rows = [dict(row) for row in db.execute(sql).fetchall()]
        write_json(
            views_dir / f"{name}.json",
            {
                "items": rows,
                "count": len(rows),
                "decision_id": STATIC_MIRROR_DECISION_ID,
                "source": view_source(name),
            },
        )
        endpoints.append([f"/views/{name}", f"api/views/{name}.json"])

    write_json(
        OUT / "index.json",
        {
            "description": "Static JSON endpoints for the GitHub Pages OneRoster core demo.",
            "note": "GitHub Pages has no server runtime. These are live hosted JSON resources; use the in-browser SQL console for ad hoc SQL.",
            "decision_id": STATIC_MIRROR_DECISION_ID,
            "hostedDatabase": {
                "provider": "Supabase",
                "projectUrl": SUPABASE_URL,
                "restBaseUrl": f"{SUPABASE_URL}/rest/v1",
                "status": "Live for the current OneRoster core demo slice. Supabase Postgres is loaded with seeded demo data, read-only RLS policies, SQL smoke checks, and public REST smoke verification.",
                "publishableKeyEnv": "SUPABASE_PUBLISHABLE_KEY",
            },
            "endpoints": [
                {
                    "name": name,
                    "url": f"https://andymontgomery-byte.github.io/platform/site/{url}",
                    "relativeUrl": url,
                }
                for name, url in endpoints
            ],
        },
    )
    db.close()
    print(f"generated {OUT.relative_to(ROOT)}")


def row_to_json(obj: dict, row: sqlite3.Row) -> dict:
    return {field["json_name"]: row[field["column_name"]] for field in obj["fields"]}


def field_decision_ids(obj: dict) -> dict[str, str]:
    return {
        field["json_name"]: field["decision_id"]
        for field in obj["fields"]
        if field.get("decision_id")
    }


def source_decision_ids(obj: dict) -> list[str]:
    decision_ids = {
        STATIC_MIRROR_DECISION_ID,
        STATIC_PRIVACY_DECISION_ID,
        *field_decision_ids(obj).values(),
    }
    return sorted(decision_ids)


def view_source(name: str) -> dict[str, object]:
    view_decisions = {
        "class-roster": [
            "DEC-002-learning-context",
            "DEC-003-role-vocabulary",
            "DEC-004-enrollment-membership",
            "DEC-010-tenancy-reference-data",
        ],
        "gradebook-results": [
            "DEC-005-results-scores",
            "DEC-010-tenancy-reference-data",
            STATIC_PRIVACY_DECISION_ID,
        ],
    }
    return {
        "view": name.replace("-", "_"),
        "dictionary": "dictionary/oneroster-core.v1.json",
        "decision_id": STATIC_MIRROR_DECISION_ID,
        "decision_ids": sorted({STATIC_MIRROR_DECISION_ID, *view_decisions.get(name, [])}),
    }


def api_file_name(api_path: str) -> str:
    clean = api_path.strip("/").replace("/", "-")
    return f"{clean}.json"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


if __name__ == "__main__":
    main()
