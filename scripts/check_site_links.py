#!/usr/bin/env python3
"""Check rendered-site links and portal reachability.

The evaluator rubric treats rendered documentation reachability as a platform
contract: broken anchors and orphaned docs make the platform harder to build
against. This script keeps that evidence deterministic for CI and for the
LLM-backed evaluator.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DEFAULT_REPORT = SITE / "api" / "site-link-check.json"
START_PAGE = SITE / "index.html"
MAX_CLICKS = 3

DICTIONARY_PAGES = {
    "dictionary/oneroster-core.v1.json": "site/docs/oneroster-core-dictionary.html",
    "dictionary/qti-core.v1.json": "site/docs/qti-core-dictionary.html",
    "dictionary/case-core.v1.json": "site/docs/case-core-dictionary.html",
    "dictionary/caliper-core.v1.json": "site/docs/caliper-core-dictionary.html",
    "dictionary/integration-governance-core.v1.json": (
        "site/docs/integration-governance-core-dictionary.html"
    ),
}

DECISION_REGISTER = ROOT / "docs" / "decisions" / "standards-overlap-decisions.md"
DECISION_PAGE = SITE / "docs" / "decisions-standards-overlap-decisions.html"
STATIC_API_INDEX = SITE / "api" / "index.json"
BUILDABILITY_GUIDE = SITE / "docs" / "build-an-edtech-app.html"


class ParsedHtml:
    def __init__(self) -> None:
        self.links: list[tuple[str, str]] = []
        self.anchors: set[str] = set()
        self.duplicate_anchors: set[str] = set()


class LinkParser(HTMLParser):
    LINK_ATTRS = {"href", "src", "spec-url"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parsed = ParsedHtml()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if name in {"id", "name"} and value:
                if value in self.parsed.anchors:
                    self.parsed.duplicate_anchors.add(value)
                self.parsed.anchors.add(value)
            if name in self.LINK_ATTRS:
                self.parsed.links.append((name, value))


def main() -> int:
    args = parse_args()
    report_path = Path(args.report) if args.report else DEFAULT_REPORT
    html_pages = sorted(SITE.rglob("*.html"))
    parsed_pages = parse_html_pages(html_pages)

    errors: list[str] = []
    errors.extend(check_local_links(parsed_pages))
    errors.extend(check_duplicate_anchors(parsed_pages))

    depths = crawl_html_pages(parsed_pages)
    errors.extend(check_page_reachability(depths))
    errors.extend(check_dictionary_reachability(parsed_pages, depths))
    errors.extend(check_decision_reachability(parsed_pages, depths))
    errors.extend(check_api_reachability(parsed_pages, depths))
    errors.extend(check_buildability_guide(depths))

    report = build_report(parsed_pages, depths, errors)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    summary = report["summary"]
    print(
        "site-links-ok "
        f"html_pages={summary['html_pages']} "
        f"local_links={summary['local_links_checked']} "
        f"dictionary_entries={summary['dictionary_entries_checked']} "
        f"decisions={summary['decisions_checked']} "
        f"api_endpoints={summary['api_endpoints_checked']}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Deterministic JSON report path. Default: site/api/site-link-check.json.",
    )
    return parser.parse_args()


def parse_html_pages(html_pages: list[Path]) -> dict[Path, ParsedHtml]:
    parsed: dict[Path, ParsedHtml] = {}
    for page in html_pages:
        parser = LinkParser()
        parser.feed(page.read_text(errors="replace"))
        parsed[page.resolve()] = parser.parsed
    return parsed


def check_local_links(parsed_pages: dict[Path, ParsedHtml]) -> list[str]:
    errors: list[str] = []
    for source, parsed in parsed_pages.items():
        for attr, href in parsed.links:
            target = resolve_local_target(source, href)
            if target is None:
                continue
            target_path, fragment = target
            if not target_path.exists():
                errors.append(f"{rel(source)} {attr}={href!r} points to missing {rel(target_path)}")
                continue
            if fragment and target_path.suffix == ".html":
                anchors = parsed_pages.get(target_path.resolve(), ParsedHtml()).anchors
                if fragment not in anchors:
                    errors.append(
                        f"{rel(source)} {attr}={href!r} points to missing anchor "
                        f"#{fragment} in {rel(target_path)}"
                    )
    return errors


def check_duplicate_anchors(parsed_pages: dict[Path, ParsedHtml]) -> list[str]:
    errors: list[str] = []
    for page, parsed in parsed_pages.items():
        for anchor in sorted(parsed.duplicate_anchors):
            errors.append(f"{rel(page)} has duplicate anchor #{anchor}")
    return errors


def crawl_html_pages(parsed_pages: dict[Path, ParsedHtml]) -> dict[Path, int]:
    start = START_PAGE.resolve()
    depths: dict[Path, int] = {start: 0}
    queue: deque[Path] = deque([start])
    while queue:
        page = queue.popleft()
        depth = depths[page]
        if depth >= MAX_CLICKS:
            continue
        for _attr, href in parsed_pages.get(page, ParsedHtml()).links:
            target = resolve_local_target(page, href)
            if target is None:
                continue
            target_path, _fragment = target
            target_path = normalize_html_target(target_path)
            if target_path.suffix != ".html" or not target_path.exists():
                continue
            resolved = target_path.resolve()
            if resolved not in parsed_pages:
                continue
            if resolved not in depths or depth + 1 < depths[resolved]:
                depths[resolved] = depth + 1
                queue.append(resolved)
    return depths


def check_page_reachability(depths: dict[Path, int]) -> list[str]:
    errors: list[str] = []
    for page in sorted((SITE / "docs").glob("*.html")):
        if page.resolve() not in depths:
            errors.append(f"{rel(page)} is not reachable from {rel(START_PAGE)} within {MAX_CLICKS} clicks")
    for page in sorted((SITE / "openapi").glob("*.html")):
        if page.resolve() not in depths:
            errors.append(f"{rel(page)} is not reachable from {rel(START_PAGE)} within {MAX_CLICKS} clicks")
    return errors


def check_dictionary_reachability(
    parsed_pages: dict[Path, ParsedHtml], depths: dict[Path, int]
) -> list[str]:
    errors: list[str] = []
    for dictionary_rel, page_rel in DICTIONARY_PAGES.items():
        dictionary = ROOT / dictionary_rel
        page = ROOT / page_rel
        data = json.loads(dictionary.read_text())
        anchors = parsed_pages.get(page.resolve(), ParsedHtml()).anchors
        if page.resolve() not in depths:
            errors.append(f"{page_rel} is not reachable for dictionary {dictionary_rel}")
            continue
        for obj in data.get("objects", []):
            object_key = obj.get("object_key")
            if object_key not in anchors:
                errors.append(f"{page_rel} is missing dictionary object anchor #{object_key}")
            for field in obj.get("fields", []):
                field_anchor = f"{object_key}.{field.get('column_name')}"
                if field_anchor not in anchors:
                    errors.append(f"{page_rel} is missing dictionary field anchor #{field_anchor}")
    return errors


def check_decision_reachability(
    parsed_pages: dict[Path, ParsedHtml], depths: dict[Path, int]
) -> list[str]:
    errors: list[str] = []
    decision_ids = parse_decision_ids()
    decision_page = DECISION_PAGE.resolve()
    anchors = parsed_pages.get(decision_page, ParsedHtml()).anchors
    if decision_page not in depths:
        errors.append(f"{rel(DECISION_PAGE)} is not reachable from {rel(START_PAGE)}")
        return errors
    for decision_id in decision_ids:
        if decision_id not in anchors:
            errors.append(f"{rel(DECISION_PAGE)} is missing decision anchor #{decision_id}")
    return errors


def check_api_reachability(
    parsed_pages: dict[Path, ParsedHtml], depths: dict[Path, int]
) -> list[str]:
    errors: list[str] = []
    if not STATIC_API_INDEX.exists():
        return [f"{rel(STATIC_API_INDEX)} is missing"]
    if not has_link_to(START_PAGE.resolve(), STATIC_API_INDEX.resolve(), parsed_pages):
        errors.append(f"{rel(START_PAGE)} does not link to {rel(STATIC_API_INDEX)}")
    api_index = json.loads(STATIC_API_INDEX.read_text())
    for endpoint in api_index.get("endpoints", []):
        relative_url = endpoint.get("relativeUrl")
        if not relative_url:
            errors.append(f"{rel(STATIC_API_INDEX)} endpoint missing relativeUrl: {endpoint}")
            continue
        target = (SITE / relative_url).resolve()
        if not target.exists():
            errors.append(f"{rel(STATIC_API_INDEX)} lists missing endpoint {relative_url}")
    for page in ["site/openapi/index.html", "site/openapi/hosted-json.html", "site/openapi/oneroster-core.html"]:
        target = (ROOT / page).resolve()
        if target not in depths:
            errors.append(f"{page} is not reachable from {rel(START_PAGE)} within {MAX_CLICKS} clicks")
    return errors


def check_buildability_guide(depths: dict[Path, int]) -> list[str]:
    guide = BUILDABILITY_GUIDE.resolve()
    if guide not in depths:
        return [f"{rel(BUILDABILITY_GUIDE)} is not reachable from {rel(START_PAGE)}"]
    if depths[guide] > MAX_CLICKS:
        return [f"{rel(BUILDABILITY_GUIDE)} is reachable only after {depths[guide]} clicks"]
    return []


def build_report(
    parsed_pages: dict[Path, ParsedHtml], depths: dict[Path, int], errors: list[str]
) -> dict:
    dictionary_entries = count_dictionary_entries()
    decision_ids = parse_decision_ids()
    api_endpoints = json.loads(STATIC_API_INDEX.read_text()).get("endpoints", [])
    local_links_checked = sum(
        1
        for source, parsed in parsed_pages.items()
        for _attr, href in parsed.links
        if resolve_local_target(source, href) is not None
    )
    return {
        "status": "fail" if errors else "pass",
        "summary": {
            "html_pages": len(parsed_pages),
            "local_links_checked": local_links_checked,
            "reachable_html_pages": len(depths),
            "max_clicks": MAX_CLICKS,
            "dictionary_entries_checked": dictionary_entries,
            "decisions_checked": len(decision_ids),
            "api_endpoints_checked": len(api_endpoints),
            "errors": len(errors),
        },
        "reachability": {
            "start": rel(START_PAGE),
            "docs_pages": sorted(rel(path) for path in (SITE / "docs").glob("*.html")),
            "openapi_pages": sorted(rel(path) for path in (SITE / "openapi").glob("*.html")),
            "reachable": {
                rel(path): depth for path, depth in sorted(depths.items(), key=lambda item: rel(item[0]))
            },
            "buildability_guide": {
                "target": rel(BUILDABILITY_GUIDE),
                "clicks": depths.get(BUILDABILITY_GUIDE.resolve()),
            },
        },
        "errors": errors,
    }


def count_dictionary_entries() -> int:
    count = 0
    for dictionary_rel in DICTIONARY_PAGES:
        data = json.loads((ROOT / dictionary_rel).read_text())
        for obj in data.get("objects", []):
            count += 1
            count += len(obj.get("fields", []))
    return count


def parse_decision_ids() -> list[str]:
    ids: list[str] = []
    for line in DECISION_REGISTER.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- id: `") and stripped.endswith("`"):
            ids.append(stripped.removeprefix("- id: `").removesuffix("`"))
    return ids


def has_link_to(source: Path, expected: Path, parsed_pages: dict[Path, ParsedHtml]) -> bool:
    for _attr, href in parsed_pages.get(source, ParsedHtml()).links:
        target = resolve_local_target(source, href)
        if target and target[0].resolve() == expected:
            return True
    return False


def resolve_local_target(source: Path, href: str) -> tuple[Path, str] | None:
    href = href.strip()
    if not href:
        return None
    split = urlsplit(href)
    if split.scheme or split.netloc or href.startswith("//"):
        return None
    if split.path.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    if split.path.startswith("/"):
        target = (SITE / split.path.lstrip("/")).resolve()
    elif split.path:
        target = (source.parent / unquote(split.path)).resolve()
    else:
        target = source.resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return target, unquote(split.fragment)
    return normalize_html_target(target), unquote(split.fragment)


def normalize_html_target(path: Path) -> Path:
    if path.exists() and path.is_dir():
        return path / "index.html"
    if not path.suffix and (path / "index.html").exists():
        return path / "index.html"
    return path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
