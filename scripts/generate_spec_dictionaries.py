#!/usr/bin/env python3
"""Generate per-spec dictionary projections from the shared seed dictionary."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "data-dictionary.seed.json"


def main() -> int:
    args = parse_args()
    seed = load_seed()
    projections = seed.get("spec_dictionary_projections", [])
    objects = seed.get("objects", [])
    errors = validate_seed(objects, projections)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.check:
        return check_projection_drift(objects, projections)

    for projection in projections:
        output_path = ROOT / projection["path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_dictionary(project_dictionary(objects, projection)))
        print(f"generated {output_path.relative_to(ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated per-spec dictionaries differ from committed files.",
    )
    return parser.parse_args()


def load_seed() -> dict:
    if not SEED.exists():
        raise SystemExit(f"missing shared seed dictionary: {SEED.relative_to(ROOT)}")
    return json.loads(SEED.read_text())


def validate_seed(objects: object, projections: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(objects, list) or not objects:
        errors.append("shared seed missing non-empty objects")
    if not isinstance(projections, list) or not projections:
        errors.append("shared seed missing non-empty spec_dictionary_projections")
        return errors

    seen_paths: set[str] = set()
    seen_object_ids: set[str] = set()
    seen_projection_objects: set[tuple[str, str]] = set()
    fields_by_spec: dict[str, int] = {}
    for index, obj in enumerate(objects if isinstance(objects, list) else []):
        object_id = obj.get("canonical_object_id")
        spec_key = obj.get("spec_key")
        object_key = obj.get("object_key")
        spec_object = obj.get("spec_object")
        fields = obj.get("fields")
        if not object_id:
            errors.append(f"seed object {index} missing canonical_object_id")
        elif object_id in seen_object_ids:
            errors.append(f"duplicate canonical_object_id: {object_id}")
        seen_object_ids.add(object_id)
        if not spec_key:
            errors.append(f"seed object {object_key or index} missing spec_key")
        if not object_key:
            errors.append(f"seed object {index} missing object_key")
        if spec_key and object_key:
            seen_projection_objects.add((spec_key, object_key))
        if not isinstance(spec_object, dict) or not spec_object:
            errors.append(f"seed object {object_key or index} missing spec_object")
        elif "fields" in spec_object:
            errors.append(f"seed object {object_key} spec_object must not embed fields")
        if not isinstance(fields, list) or not fields:
            errors.append(f"seed object {object_key or index} has no fields")
            continue
        seen_field_ids: set[str] = set()
        for field in fields:
            field_id = field.get("canonical_field_id")
            field_key = field.get("field_key")
            spec_field = field.get("spec_field")
            if not field_id:
                errors.append(f"seed object {object_key} field {field_key} missing canonical_field_id")
            elif field_id in seen_field_ids:
                errors.append(f"seed object {object_key} duplicate canonical_field_id: {field_id}")
            seen_field_ids.add(field_id)
            if not field_key:
                errors.append(f"seed object {object_key} has field without field_key")
            if not isinstance(spec_field, dict) or not spec_field:
                errors.append(f"seed object {object_key}.{field_key} missing spec_field")
            elif spec_field.get("field_key") != field_key:
                errors.append(f"seed object {object_key}.{field_key} spec_field field_key mismatch")
            if spec_key:
                fields_by_spec[spec_key] = fields_by_spec.get(spec_key, 0) + 1

    for index, projection in enumerate(projections):
        if not isinstance(projection, dict):
            errors.append(f"projection {index} is not an object")
            continue
        for key in ["spec_key", "path", "decision_id", "dictionary_header", "dictionary_key_order"]:
            if key not in projection or not projection[key]:
                errors.append(f"projection {index} missing {key}")
        spec_key = projection.get("spec_key")
        path = projection.get("path")
        if path:
            if path in seen_paths:
                errors.append(f"duplicate projection path: {path}")
            seen_paths.add(path)
            if not str(path).startswith("dictionary/") or not str(path).endswith(".v1.json"):
                errors.append(f"projection path must target dictionary/*.v1.json: {path}")
        header = projection.get("dictionary_header")
        if not isinstance(header, dict):
            errors.append(f"projection {spec_key or index} dictionary_header is not an object")
            continue
        if "objects" in header:
            errors.append(f"projection {spec_key or index} dictionary_header must not embed objects")
        key_order = projection.get("dictionary_key_order")
        if not isinstance(key_order, list) or "objects" not in key_order:
            errors.append(f"projection {spec_key or index} dictionary_key_order must include objects")
        elif set(key_order) != set(header) | {"objects"}:
            errors.append(
                f"projection {spec_key or index} dictionary_key_order does not match header keys plus objects"
            )
        expected_objects = projection.get("object_count")
        expected_fields = projection.get("field_count")
        if isinstance(expected_objects, int) and spec_key:
            actual_objects = sum(1 for item in seen_projection_objects if item[0] == spec_key)
            if actual_objects != expected_objects:
                errors.append(
                    f"projection {spec_key} object_count {expected_objects} does not match seed {actual_objects}"
                )
        if isinstance(expected_fields, int) and spec_key:
            actual_fields = fields_by_spec.get(spec_key, 0)
            if actual_fields != expected_fields:
                errors.append(
                    f"projection {spec_key} field_count {expected_fields} does not match seed {actual_fields}"
                )
    return errors


def check_projection_drift(objects: list[dict], projections: list[dict]) -> int:
    drift: list[str] = []
    for projection in projections:
        output_path = ROOT / projection["path"]
        expected = render_dictionary(project_dictionary(objects, projection))
        if not output_path.exists():
            drift.append(f"missing generated dictionary: {projection['path']}")
            continue
        actual = output_path.read_text()
        if actual != expected:
            drift.append(
                f"{projection['path']} differs from data/data-dictionary.seed.json; "
                "run `python3 scripts/generate_spec_dictionaries.py`"
            )

    if drift:
        for item in drift:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1

    total_objects = sum(1 for obj in objects if obj.get("spec_key"))
    total_fields = sum(len(obj.get("fields", [])) for obj in objects if obj.get("spec_key"))
    print(
        "spec-dictionaries-ok "
        f"projections={len(projections)} objects={total_objects} fields={total_fields}"
    )
    return 0


def render_dictionary(dictionary: dict) -> str:
    return json.dumps(dictionary, indent=2) + "\n"


def project_dictionary(objects: list[dict], projection: dict) -> dict:
    spec_key = projection["spec_key"]
    projected_objects = []
    for obj in objects:
        if obj.get("spec_key") != spec_key:
            continue
        spec_object = copy.deepcopy(obj["spec_object"])
        spec_object["fields"] = [copy.deepcopy(field["spec_field"]) for field in obj["fields"]]
        projected_objects.append(spec_object)

    dictionary = {}
    header = projection["dictionary_header"]
    for key in projection["dictionary_key_order"]:
        if key == "objects":
            dictionary[key] = projected_objects
        else:
            dictionary[key] = copy.deepcopy(header[key])
    return dictionary


if __name__ == "__main__":
    raise SystemExit(main())
