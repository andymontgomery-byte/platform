#!/usr/bin/env python3
"""Check that structured dictionaries are represented in generated artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_TRACE_DOC = ROOT / "docs" / "decisions" / "standards-overlap-decisions.md"
DECISION_TRACE_START = "<!-- decision-trace:start -->"
DECISION_TRACE_END = "<!-- decision-trace:end -->"

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
    {
        "name": "Integration and governance core",
        "source": ROOT / "dictionary" / "integration-governance-core.v1.json",
        "sql_schema": "integration",
        "sql": ROOT / "schema" / "generated" / "integration_governance_core_comments.sql",
        "openapi": ROOT / "openapi" / "generated" / "integration-governance-core.v0.json",
        "markdown": ROOT / "docs" / "generated" / "integration-governance-core-dictionary.md",
        "html": ROOT / "site" / "docs" / "integration-governance-core-dictionary.html",
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
    "sourceStandard",
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
    "decision_id",
    "sourceStandard",
}

REQUIRED_UNSUPPORTED_KEYS = {
    "area",
    "reason",
    "sourceStandard",
    "sourceFieldsOrValues",
}


def main() -> None:
    errors: list[str] = []
    decision_trace, trace_errors = load_decision_trace()
    errors.extend(trace_errors)
    known_field_refs: set[str] = set()
    total_objects = 0
    total_fields = 0
    total_values = 0
    for config in CONFIGS:
        data = json.loads(config["source"].read_text())
        openapi = json.loads(config["openapi"].read_text())
        sql = config["sql"].read_text()
        markdown = config["markdown"].read_text()
        html_doc = config["html"].read_text()
        known_field_refs.update(dictionary_field_refs(config, data))
        errors.extend(check_dictionary_shape(config, data, decision_trace))
        errors.extend(check_artifacts(config, data, openapi, sql, markdown, html_doc))
        total_objects += len(data["objects"])
        for obj in data["objects"]:
            total_fields += len(obj["fields"])
            for field in obj["fields"]:
                total_values += len(allowed_values(field, data))
    errors.extend(check_trace_targets(decision_trace, known_field_refs))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(
        "dictionary-artifacts-ok "
        f"configs={len(CONFIGS)} objects={total_objects} fields={total_fields} values={total_values}"
    )


def check_dictionary_shape(config: dict, data: dict, decision_trace: dict[str, set[str]]) -> list[str]:
    errors = []
    seen_objects = set()
    seen_tables = set()
    seen_paths = set()
    allowed_refs = set(data.get("shared_allowed_values", {}))
    source_ref = config["source"].relative_to(ROOT).as_posix()
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
            decision_id = field.get("decision_id")
            field_ref = f"{source_ref}#{obj.get('object_key')}.{field.get('field_key')}"
            if decision_id:
                if decision_id not in decision_trace:
                    errors.append(
                        f"{config['name']} {field_ref} references unknown decision_id {decision_id}"
                    )
                elif field_ref not in decision_trace[decision_id]:
                    errors.append(
                        f"{config['name']} {field_ref} missing from produces_fields for {decision_id}"
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
                for key in ["value", "label", "plain_description", "sourceStandard"]:
                    if key not in value or not str(value[key]).strip():
                        errors.append(
                            f"{config['name']} {field.get('field_key')} value missing {key}: {value}"
                        )
    for item in data.get("unsupported_or_deferred", []):
        missing = REQUIRED_UNSUPPORTED_KEYS - set(item)
        if missing:
            errors.append(
                f"{config['name']} unsupported/deferred item missing keys "
                f"{sorted(missing)}: {item.get('area')}"
            )
        if not isinstance(item.get("sourceFieldsOrValues"), list) or not item.get("sourceFieldsOrValues"):
            errors.append(
                f"{config['name']} unsupported/deferred item missing non-empty sourceFieldsOrValues: "
                f"{item.get('area')}"
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
        if schema.get("x-sourceStandard") != obj.get("sourceStandard"):
            errors.append(f"{config['name']} OpenAPI sourceStandard mismatch for {schema_name}")
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
            decision_id = field.get("decision_id", "")
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
            if prop.get("x-decisionId") != decision_id:
                errors.append(
                    f"{config['name']} OpenAPI decision mismatch "
                    f"{schema_name}.{field['json_name']}"
                )
            if prop.get("x-sourceStandard") != field.get("sourceStandard"):
                errors.append(
                    f"{config['name']} OpenAPI sourceStandard mismatch "
                    f"{schema_name}.{field['json_name']}"
                )
            if f"`{field['column_name']}`" not in markdown:
                errors.append(
                    f"{config['name']} Markdown missing field {obj['table_name']}.{field['column_name']}"
                )
            field_source = format_source_standard(field.get("sourceStandard", {}))
            if field_source and field_source not in markdown:
                errors.append(
                    f"{config['name']} Markdown missing sourceStandard "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            if decision_id and f"`{decision_id}`" not in markdown:
                errors.append(
                    f"{config['name']} Markdown missing decision ID "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            if html_escape(field["plain_description"]) not in html_doc:
                errors.append(
                    f"{config['name']} HTML missing field description "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            if decision_id and html_escape(decision_id) not in html_doc:
                errors.append(
                    f"{config['name']} HTML missing decision ID "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            if field_source and html_escape(field_source) not in html_doc:
                errors.append(
                    f"{config['name']} HTML missing sourceStandard "
                    f"{obj['table_name']}.{field['column_name']}"
                )
            values = allowed_values(field, data)
            if values:
                expected_enum = [item["value"] for item in values]
                if prop.get("enum") != expected_enum:
                    errors.append(
                        f"{config['name']} OpenAPI enum mismatch {schema_name}.{field['json_name']}"
                    )
                expected_value_sources = {
                    item["value"]: item["sourceStandard"] for item in values
                }
                if prop.get("x-valueSourceStandards") != expected_value_sources:
                    errors.append(
                        f"{config['name']} OpenAPI enum sourceStandard mismatch "
                        f"{schema_name}.{field['json_name']}"
                    )
    return errors


def load_decision_trace() -> tuple[dict[str, set[str]], list[str]]:
    errors: list[str] = []
    if not DECISION_TRACE_DOC.exists():
        return {}, [f"missing decision trace doc: {DECISION_TRACE_DOC.relative_to(ROOT)}"]

    text = DECISION_TRACE_DOC.read_text()
    if DECISION_TRACE_START not in text or DECISION_TRACE_END not in text:
        return {}, ["standards-overlap-decisions.md missing decision-trace markers"]

    raw_block = text.split(DECISION_TRACE_START, 1)[1].split(DECISION_TRACE_END, 1)[0].strip()
    if raw_block.startswith("```"):
        lines = raw_block.splitlines()
        raw_block = "\n".join(lines[1:-1]).strip()

    try:
        trace_items = json.loads(raw_block)
    except json.JSONDecodeError as exc:
        return {}, [f"decision trace JSON is invalid: {exc}"]

    trace: dict[str, set[str]] = {}
    for index, item in enumerate(trace_items):
        decision_id = item.get("decision_id")
        produces_fields = item.get("produces_fields")
        if not decision_id:
            errors.append(f"decision trace item {index} missing decision_id")
            continue
        if not isinstance(produces_fields, list) or not produces_fields:
            errors.append(f"decision trace item {decision_id} missing non-empty produces_fields list")
            continue
        if decision_id in trace:
            errors.append(f"duplicate decision trace item {decision_id}")
            continue
        trace[decision_id] = set(produces_fields)
    return trace, errors


def dictionary_field_refs(config: dict, data: dict) -> set[str]:
    source_ref = config["source"].relative_to(ROOT).as_posix()
    return {
        f"{source_ref}#{obj['object_key']}.{field['field_key']}"
        for obj in data["objects"]
        for field in obj["fields"]
    }


def check_trace_targets(decision_trace: dict[str, set[str]], known_field_refs: set[str]) -> list[str]:
    errors = []
    for decision_id, field_refs in decision_trace.items():
        for field_ref in field_refs:
            if field_ref not in known_field_refs:
                errors.append(f"{decision_id} produces unknown dictionary field {field_ref}")
    return errors


def allowed_values(field: dict, data: dict) -> list[dict]:
    if "allowed_values" in field:
        return field["allowed_values"]
    ref = field.get("allowed_values_ref")
    if ref:
        return data.get("shared_allowed_values", {}).get(ref, [])
    return []


def format_source_standard(source: dict) -> str:
    if not isinstance(source, dict):
        return ""
    parts = [source.get("standard", ""), source.get("version", "")]
    target = ".".join(
        str(source[key])
        for key in ["object", "field", "vocabulary", "value"]
        if source.get(key)
    )
    if target:
        parts.append(target)
    coverage = source.get("coverage")
    if coverage and coverage != "mapped":
        parts.append(f"({coverage})")
    return " ".join(str(part) for part in parts if part)


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
