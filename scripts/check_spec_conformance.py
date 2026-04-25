#!/usr/bin/env python3
"""Score repository artifacts against the platform spec.

ADVISORY ONLY as of the LLM-evaluator redesign. The Codex loop now gates
publish on `scripts/evaluate_platform.py` (LLM-graded against
`docs/eval-rubric.md`), not on this score. This script still runs each
iteration and writes `site/api/spec-conformance.json` so the LLM evaluator
has a deterministic signal to consider, and so external readers see whether
the file-presence checks pass.

Do not add new gating logic here. New requirements belong in the rubric.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = Path("/Users/andymontgomery/Downloads/WF - Platform - 260424-144348.md")
SCORE_SCOPE = (
    "Advisory file-presence signal for the LLM evaluator. "
    "Does NOT gate the Codex loop — publish is gated by "
    "scripts/evaluate_platform.py against docs/eval-rubric.md. "
    "This is not a platform completion metric."
)
KNOWN_NON_SCORED_GAPS = [
    "Full OneRoster 1.2 accounting beyond the current core demo slice.",
    "A platform-status manifest distinct from the score-gate report.",
    "Hosted Supabase database is live for the current OneRoster core demo slice; broader hosted database coverage is still pending.",
    "A real hosted JSON API runtime beyond static GitHub Pages and local Express.",
    "A real hosted SQL query endpoint against shared demo data.",
    "Tenant model, row-level isolation, OAuth scopes, and auth-boundary enforcement.",
    "Runnable CASE import/search, QTI package import/projection, Caliper event ingestion, and LTI launch/Advantage sandbox slices.",
    "Conformance-style fixtures, support notes, and formal certification evidence.",
    "Production deployment documentation.",
    "Generated dictionary portal canonical URL cleanup.",
    "Codex loop harness runbook and smoke tests.",
]


def main() -> int:
    args = parse_args()
    results = evaluate()
    total = sum(item["points"] for item in results)
    earned = sum(item["points"] for item in results if item["passed"])
    score = round((earned / total) * 100, 2) if total else 0.0
    report = {
        "metric": "score_gate",
        "scoreScope": SCORE_SCOPE,
        "notACompletionClaim": True,
        "score": score,
        "earnedPoints": earned,
        "totalPoints": total,
        "passed": all(item["passed"] for item in results),
        "items": results,
        "openScoredGaps": [
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "detail": item["detail"],
                "points": item["points"],
            }
            for item in results
            if not item["passed"]
        ],
        "openGaps": [
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "detail": item["detail"],
                "points": item["points"],
            }
            for item in results
            if not item["passed"]
        ],
        "knownNonScoredGaps": KNOWN_NON_SCORED_GAPS,
    }

    if args.write_report:
        target = Path(args.write_report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2) + "\n")

    if args.score_only:
        print(score)
    else:
        print(json.dumps(report, indent=2))

    if args.min_score is not None and score < args.min_score:
        print(f"spec score {score} is below required minimum {args.min_score}", file=sys.stderr)
        return 1
    if args.strict and not report["passed"]:
        print("strict spec conformance failed", file=sys.stderr)
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score repo artifacts against the platform spec.")
    parser.add_argument("--write-report", help="Optional JSON report path.")
    parser.add_argument("--score-only", action="store_true", help="Print only the numeric score.")
    parser.add_argument("--min-score", type=float, help="Fail if score is below this value.")
    parser.add_argument("--strict", action="store_true", help="Fail unless every requirement passes.")
    return parser.parse_args()


def evaluate() -> list[dict]:
    return [
        item("spec_available", "New platform spec is available to the loop.", 2, SPEC.exists(), str(SPEC)),
        item(
            "portal_rendered",
            "Customer-facing portal exists and renders docs as HTML.",
            5,
            exists("site/index.html") and exists("site/docs/index.html") and exists("index.html"),
            "site/index.html, site/docs/index.html, root index.html",
        ),
        item(
            "no_raw_doc_links",
            "Portal does not link users to raw Markdown or YAML docs.",
            4,
            not regex_in_files(r"href=[\"'][^\"']+\.(md|yaml|yml)[\"']", ["site"]),
            "No href to .md/.yaml/.yml under site/",
        ),
        item(
            "rendered_openapi",
            "API specs are rendered with Redoc or equivalent.",
            5,
            all_contains(
                {
                    "site/openapi/hosted-json.html": "redoc",
                    "site/openapi/oneroster-core.html": "redoc",
                    "site/openapi/qti-core.html": "redoc",
                }
            ),
            "Hosted JSON, local OneRoster, and QTI OpenAPI pages exist.",
        ),
        item(
            "one_roster_vertical_slice",
            "OneRoster core has runnable SQL and JSON demo surfaces.",
            8,
            all_exists(
                [
                    "demo/schema.sql",
                    "demo/seed.sql",
                    "demo/server.js",
                    "demo/test.js",
                    "site/api/index.json",
                    "site/api/people.json",
                    "site/api/views/class-roster.json",
                ]
            )
            and all_contains({"site/index.html": "Browser SQL console"}),
            "SQLite schema/seed/server/test plus hosted static JSON and browser SQL console.",
        ),
        item(
            "real_hosted_urls",
            "Hosted API URLs use real GitHub Pages URLs, not example.edu/example API hosts.",
            4,
            contains("site/api/index.json", "https://andymontgomery-byte.github.io/platform/site/api")
            and not regex_in_files(
                r"api\.example|example\.edu",
                ["site", "openapi", "dictionary", "demo"],
                exclude=[
                    "demo/node_modules",
                    "demo/platform-demo.sqlite",
                    "site/api/spec-conformance.json",
                    "site/api/platform-status.json",
                ],
            ),
            "GitHub Pages URL present and example API hosts absent.",
        ),
        item(
            "shared_dictionary_oneroster",
            "OneRoster core dictionary generates SQL comments, OpenAPI descriptions, and docs.",
            7,
            all_exists(
                [
                    "dictionary/oneroster-core.v1.json",
                    "scripts/generate_oneroster_core.py",
                    "schema/generated/oneroster_core_comments.sql",
                    "openapi/generated/oneroster-core.v0.json",
                    "docs/generated/oneroster-core-dictionary.md",
                    "site/docs/oneroster-core-dictionary.html",
                ]
            ),
            "OneRoster structured source and generated artifacts exist.",
        ),
        item(
            "shared_dictionary_qti",
            "QTI repository projection is structured and generated.",
            6,
            all_exists(
                [
                    "dictionary/qti-core.v1.json",
                    "scripts/generate_qti_core.py",
                    "schema/generated/qti_core_comments.sql",
                    "openapi/generated/qti-core.v0.json",
                    "docs/generated/qti-core-dictionary.md",
                    "site/docs/qti-core-dictionary.html",
                ]
            ),
            "QTI structured source and generated artifacts exist.",
        ),
        item(
            "shared_dictionary_case",
            "CASE is structured and generated.",
            6,
            all_exists(
                [
                    "dictionary/case-core.v1.json",
                    "scripts/generate_case_core.py",
                    "schema/generated/case_core_comments.sql",
                    "openapi/generated/case-core.v0.json",
                    "docs/generated/case-core-dictionary.md",
                    "site/docs/case-core-dictionary.html",
                ]
            ),
            "CASE structured source and generated artifacts are required.",
        ),
        item(
            "shared_dictionary_caliper",
            "Caliper is structured and generated.",
            6,
            all_exists(
                [
                    "dictionary/caliper-core.v1.json",
                    "scripts/generate_caliper_core.py",
                    "schema/generated/caliper_core_comments.sql",
                    "openapi/generated/caliper-core.v0.json",
                    "docs/generated/caliper-core-dictionary.md",
                    "site/docs/caliper-core-dictionary.html",
                ]
            ),
            "Caliper structured source and generated artifacts are required.",
        ),
        item(
            "shared_dictionary_lti_security_privacy",
            "LTI, Security Framework, and Data Privacy are structured/generated or explicitly deferred.",
            6,
            all_exists(
                [
                    "dictionary/integration-governance-core.v1.json",
                    "scripts/generate_integration_governance_core.py",
                    "openapi/generated/integration-governance-core.v0.json",
                    "site/docs/integration-governance-core-dictionary.html",
                ]
            ),
            "Integration/governance structured source and artifacts are required.",
        ),
        item(
            "dictionary_artifact_check",
            "Generated dictionary artifacts are checked for object/field/value coverage.",
            5,
            exists("scripts/check_dictionary_artifacts.py") and contains("VERIFY.md", "check_dictionary_artifacts.py"),
            "Coverage checker is in VERIFY.md.",
        ),
        item(
            "lead_spec_accounting",
            "Every Lead spec is accounted for in the Lead spec accounting page.",
            6,
            all_terms(
                "docs/lead-spec-accounting.md",
                ["OneRoster", "CASE", "QTI", "Caliper", "LTI", "Security Framework", "Data Privacy"],
            ),
            "Lead spec accounting includes all current Lead specs.",
        ),
        item(
            "overlap_decisions",
            "Required overlap decisions are documented.",
            7,
            all_terms(
                "docs/decisions/standards-overlap-decisions.md",
                [
                    "Person",
                    "Class",
                    "Roles",
                    "Enrollment and Membership",
                    "Results, Scores",
                    "Standards Alignment",
                    "Identifiers",
                    "Time",
                    "Content, Resources",
                    "Tenant",
                ],
            ),
            "Decision page covers the required overlap areas plus tenancy.",
        ),
        item(
            "developer_guide",
            "Portal explains what the platform provides and what app developers own.",
            4,
            all_terms("site/index.html", ["Platform Provides", "App Developer Owns"]),
            "Developer guide section exists.",
        ),
        item(
            "gap_backlog_tracks_missing",
            "Missing spec work is tracked as TODO backlog, not only in chat.",
            5,
            all_terms(
                "docs/spec-gap-backlog.md",
                [
                    "Convert CASE",
                    "Convert Caliper",
                    "Convert LTI",
                    "real hosted relational database",
                    "real hosted JSON API server",
                    "tenant model",
                    "OAuth scopes",
                ],
            ),
            "Backlog includes open spec gaps.",
        ),
        item(
            "coverage_matrix",
            "Coverage matrix distinguishes generated, runnable, deferred, and unsupported areas.",
            4,
            all_terms(
                "docs/dictionary-coverage-matrix.md",
                ["Structured source", "Generated artifacts", "Runnable slice", "Unsupported ledger"],
            ),
            "Coverage matrix exists with required columns.",
        ),
        item(
            "status_manifest",
            "Machine-readable status/spec report is published for AI agents.",
            3,
            exists("site/api/spec-conformance.json") or exists("site/api/platform-status.json"),
            "Expected site/api/spec-conformance.json or site/api/platform-status.json.",
        ),
        item(
            "real_backend_acknowledged",
            "Backend gap is explicit until a real database/API server exists.",
            2,
            all_terms("docs/spec-gap-backlog.md", ["GitHub Pages cannot host a database", "Static JSON is not enough"]),
            "Backlog explicitly states the remaining hosted backend gap.",
        ),
    ]


def item(id_: str, requirement: str, points: int, passed: bool, detail: str) -> dict:
    return {
        "id": id_,
        "requirement": requirement,
        "points": points,
        "passed": bool(passed),
        "detail": detail,
    }


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def all_exists(paths: list[str]) -> bool:
    return all(exists(path) for path in paths)


def contains(path: str, term: str) -> bool:
    target = ROOT / path
    return target.exists() and term in target.read_text(errors="ignore")


def all_contains(path_terms: dict[str, str]) -> bool:
    return all(contains(path, term) for path, term in path_terms.items())


def all_terms(path: str, terms: list[str]) -> bool:
    target = ROOT / path
    if not target.exists():
        return False
    text = target.read_text(errors="ignore")
    return all(term in text for term in terms)


def regex_in_files(pattern: str, roots: list[str], exclude: list[str] | None = None) -> bool:
    exclude = exclude or []
    rx = re.compile(pattern)
    for root in roots:
        base = ROOT / root
        if not base.exists():
            continue
        paths = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for path in paths:
            rel = path.relative_to(ROOT).as_posix()
            if any(rel.startswith(item) for item in exclude):
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            if rx.search(text):
                return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
