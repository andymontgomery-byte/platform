#!/usr/bin/env python3
"""Check that structured dictionaries are represented in generated artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONFIGS = [
    {
        "name": "OneRoster core",
        "source": ROOT / "dictionary" / "oneroster-core.v1.json",
        "sql_schema": "demo",
        "sql": ROOT / "schema" / "generated" / "oneroster_core_comments.sql",
        "openapi": ROOT / "openapi" / "generated" / "oneroster-core.v0.json",
        "markdown": ROOT / "docs" / "generated" / "oneroster-core-dictionary.md",
        "html": ROOT / "site" / "docs" / "oneroster-core-dictionary.html",
    },
    {
        "name": "QTI core",
        "source": ROOT / "dictionary" / "qti-core.v1.json",
        "sql_schema": "assessment",
        "sql": ROOT / "schema" / "generated" / "qti_core_comments.sql",
        "openapi": ROOT / "openapi" / "generated" / "qti-core.v0.json",
        "markdown": ROOT / "docs" / "generated" / "qti-core-dictionary.md",
        "html": ROOT / "site" / "docs" / "qti-core-dictionary.html",
    },
    {
        "name": "CASE core",
        "source": ROOT / "dictionary" / "case-core.v1.json",
        "sql_schema": "standards",
        "sql": ROOT / "schema" / "generated" / "case_core_comments.sql",
        "openapi": ROOT / "openapi" / "generated" / "case-core.v0.json",
        "markdown": ROOT / "docs" / "generated" / "case-core-dictionary.md",
        "html": ROOT / "site" / "docs" / "case-core-dictionary.html",
    },
    {
        "name": "Caliper core",
        "source": ROOT / "dictionary" / "caliper-core.v1.json",
        "sql_schema": "analytics",
        "sql": ROOT / "schema" / "generated" / "caliper_core_comments.sql",
        "openapi": ROOT / "openapi" / "generated" / "caliper-core.v0.json",
        "markdown": ROOT / "docs" / "generated" / "caliper-core-dictionary.md",
        "html": ROOT / "site" / "docs" / "caliper-core-dictionary.html",
    },
]

REQUIRED_OBJECT_KEYS = {
    "object_key",
    "table_name",
    "api_path",
    "name",
    "plain_description",
    "why_it_exists",
    "privacy_class",
    "fields",
}

REQUIRED_FIELD_KEYS = {
    "field_key",
    "column_name",
    "json_name",
    "data_type",
    "required",
    "plain_description",
    "school_example",
    "privacy_class",
}


def main() -> None:
    errors: list[str] = []
    total_objects = 0
    total_fields = 0
    total_values = 0
    for config in CONFIGS:
        data = json.loads(config["source"].read_text())
        openapi = json.loads(config["openapi"].read_text())
        sql = config["sql"].read_text()
        markdown = config["markdown"].read_text()
        html_doc = config["html"].read_text()
        errors.extend(check_dictionary_shape(config, data))
        errors.extend(check_artifacts(config, data, openapi, sql, markdown, html_doc))
        total_objects += len(data["objects"])
        for obj in data["objects"]:
            total_fields += len(obj["fields"])
            for field in obj["fields"]:
                total_values += len(allowed_values(field, data))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(
        "dictionary-artifacts-ok "
        f"configs={len(CONFIGS)} objects={total_objects} fields={total_fields} values={total_values}"
    )


def check_dictionary_shape(config: dict, data: dict) -> list[str]:
    errors = []
    seen_objects = set()
    seen_tables = set()
    seen_paths = set()
    allowed_refs = set(data.get("shared_allowed_values", {}))
    for obj in data.get("objects", []):
        missing = REQUIRED_OBJECT_KEYS - set(obj)
        if missing:
            errors.append(f"{config['name']} object missing keys {sorted(missing)}: {obj.get('object_key')}")
        for key, seen in [
            ("object_key", seen_objects),
            ("table_name", seen_tables),
            ("api_path", seen_paths),
        ]:
            value = obj.get(key)
            if value in seen:
                errors.append(f"{config['name']} duplicate {key}: {value}")
            seen.add(value)
        seen_fields = set()
        seen_columns = set()
        seen_json = set()
        for field in obj.get("fields", []):
            missing = REQUIRED_FIELD_KEYS - set(field)
            if missing:
                errors.append(
                    f"{config['name']} {obj.get('object_key')} field missing keys "
                    f"{sorted(missing)}: {field.get('field_key')}"
                )
            for key, seen in [
                ("field_key", seen_fields),
                ("column_name", seen_columns),
                ("json_name", seen_json),
            ]:
                value = field.get(key)
                if value in seen:
                    errors.append(f"{config['name']} {obj.get('object_key')} duplicate {key}: {value}")
                seen.add(value)
            ref = field.get("allowed_values_ref")
            if ref and ref not in allowed_refs:
                errors.append(f"{config['name']} {field.get('field_key')} references missing values: {ref}")
            for value in allowed_values(field, data):
                for key in ["value", "label", "plain_description"]:
                    if key not in value or not str(value[key]).strip():
                        errors.append(
                            f"{config['name']} {field.get('field_key')} value missing {key}: {value}"
                        )
    return errors


def check_artifacts(
    config: dict,
    data: dict,
    openapi: dict,
    sql: str,
    markdown: str,
    html_doc: str,
) -> list[str]:
    errors = []
    schemas = openapi.get("components", {}).get("schemas", {})
    for obj in data["objects"]:
        schema_name = pascal(obj["object_key"])
        schema = schemas.get(schema_name)
        if not schema:
            errors.append(f"{config['name']} OpenAPI missing schema {schema_name}")
            continue
        if obj["api_path"] not in openapi.get("paths", {}):
            errors.append(f"{config['name']} OpenAPI missing path {obj['api_path']}")
        table_comment = f"COMMENT ON TABLE {config['sql_schema']}.{obj['table_name']} IS "
        if table_comment not in sql:
            errors.append(f"{config['name']} SQL missing table comment for {obj['table_name']}")
        if f"### {obj['name']}" not in markdown:
            errors.append(f"{config['name']} Markdown missing object heading {obj['name']}")
        if html_escape(obj["plain_description"]) not in html_doc:
            errors.append(f"{config['name']} HTML missing object description {obj['object_key']}")
        properties = schema.get("properties", {})
        for field in obj["fields"]:
            column_comment = (
                f"COMMENT ON COLUMN {config['sql_schema']}.{obj['table_name']}."
                f"{field['column_name']} IS "
            )
            if column_comment not in sql:
                errors.append(
                    f"{config['name']} SQL missing column comment "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            prop = properties.get(field["json_name"])
            if not prop:
                errors.append(
                    f"{config['name']} OpenAPI missing property "
                    f"{schema_name}.{field['json_name']}"
                )
                continue
            if prop.get("description") != field["plain_description"]:
                errors.append(
                    f"{config['name']} OpenAPI description mismatch "
                    f"{schema_name}.{field['json_name']}"
                )
            if f"`{field['column_name']}`" not in markdown:
                errors.append(
                    f"{config['name']} Markdown missing field {obj['table_name']}.{field['column_name']}"
                )
            if html_escape(field["plain_description"]) not in html_doc:
                errors.append(
                    f"{config['name']} HTML missing field description "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            values = allowed_values(field, data)
            if values:
                expected_enum = [item["value"] for item in values]
                if prop.get("enum") != expected_enum:
                    errors.append(
                        f"{config['name']} OpenAPI enum mismatch {schema_name}.{field['json_name']}"
                    )
    return errors


def allowed_values(field: dict, data: dict) -> list[dict]:
    if "allowed_values" in field:
        return field["allowed_values"]
    ref = field.get("allowed_values_ref")
    if ref:
        return data.get("shared_allowed_values", {}).get(ref, [])
    return []


def pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.split("_"))


def html_escape(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


if __name__ == "__main__":
    main()
