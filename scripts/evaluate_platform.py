#!/usr/bin/env python3
"""LLM-backed platform evaluator.

Replaces the deterministic score gate as the publish gate for the Codex loop.
Reads docs/eval-rubric.md, gathers evidence from the repo, calls Claude
(Anthropic API direct) to grade each requirement on substance, and writes
site/api/platform-evaluation.json.

Output schema (per item):
  { id, status: "pass"|"partial"|"fail"|"blocked",
    reason: str, traced_cause: str, evidence_paths: [str],
    blocked_prerequisites: [str] }

Overall:
  { rubricVersion, evaluatedAt, model,
    counts: {pass, partial, fail, blocked, total},
    done: bool, items: [...], buildability_gaps: [...], projections: {...},
    advisoryScoreGate: {score, passed} }

`done` is True iff every item is `pass`, OR every non-pass item is `blocked`
with at least one documented prerequisite.

Exit code: 0 always (the loop reads the JSON to decide what to do). Non-zero
only on hard internal errors (rubric missing, API auth missing, etc.).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "docs" / "eval-rubric.md"
DEFAULT_OUTPUT = ROOT / "site" / "api" / "platform-evaluation.json"
ADVISORY_REPORT = ROOT / "site" / "api" / "spec-conformance.json"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"

# Files always included as evidence regardless of which rubric item is being graded.
ALWAYS_EVIDENCE = [
    "README.md",
    "PLAN.md",
    "VERIFY.md",
    "docs/eval-rubric.md",
    "docs/loop-overrides.md",
    "docs/spec-gap-backlog.md",
    "docs/dictionary-coverage-matrix.md",
    "docs/lead-spec-accounting.md",
    "docs/decisions/standards-overlap-decisions.md",
    "docs/decisions/decisions-pending.md",
    "docs/decisions/decisions-needed.md",
    "docs/admin-operations.md",
    "docs/supabase-hosted-database.md",
    "data/data-dictionary.seed.json",
    "site/api/spec-conformance.json",
    ".env.example",
]

# Globs collected as evidence; capped at MAX_EVIDENCE_FILES total.
EVIDENCE_GLOBS = [
    "dictionary/*.json",
    "scripts/generate_*.py",
    "scripts/check_*.py",
    "scripts/snapshot_*.py",
    "scripts/codex_loop.py",
    "scripts/evaluate_platform.py",
    "tests/*.py",
    "supabase/migrations/*.sql",
    "supabase/policies/*.json",
    "supabase/functions/*/index.ts",
    "supabase/functions/*/deno.json",
    "demo/schema.sql",
    "demo/server.js",
    "demo/test.js",
    "site/index.html",
    "site/app.js",
    "site/docs/index.html",
    "openapi/generated/*.json",
    "schema/generated/*.sql",
    "docs/decisions/*.md",
    "docs/generated/*-dictionary.md",
]

MAX_EVIDENCE_FILES = 80
MAX_FILE_BYTES = 45000  # keep the full decision register visible to the LLM
MAX_TOTAL_EVIDENCE_BYTES = 800000  # ~200k tokens worst case

# Prerequisite environment variables that flip runtime items to `blocked`
# instead of `fail` when missing.
RUNTIME_PREREQS = {
    "edge_functions_for_non_crud_endpoints": [
        ("supabase_cli", "Supabase CLI installed (`supabase --version` works)"),
        ("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_ROLE_KEY set in .env.local"),
    ],
    "hosted_database_live": [
        ("SUPABASE_PUBLISHABLE_KEY_OR_ANON", "SUPABASE_PUBLISHABLE_KEY or SUPABASE_ANON_KEY set"),
    ],
    "hosted_api_callable_no_setup": [
        ("SUPABASE_PUBLISHABLE_KEY_OR_ANON", "SUPABASE_PUBLISHABLE_KEY or SUPABASE_ANON_KEY set"),
    ],
}


def main() -> int:
    args = parse_args()
    if not RUBRIC.exists():
        print(f"Rubric not found at {RUBRIC}", file=sys.stderr)
        return 2

    items = parse_rubric(RUBRIC.read_text())
    if not items:
        print("Parsed zero rubric items \u2014 check the rubric format.", file=sys.stderr)
        return 2

    advisory = load_advisory_report()
    prereqs = check_runtime_prereqs(args.env_file)
    evidence = gather_evidence()

    if args.dry_run:
        print(f"Rubric items parsed: {len(items)}")
        for it in items:
            print(f"  - {it['id']}")
        print(f"Evidence files: {len(evidence)}")
        print(f"Advisory score: {advisory.get('score')}")
        print(f"Prereqs: {prereqs}")
        return 0

    api_key = resolve_api_key(args)
    if not api_key:
        print(
            "Anthropic API key not found. Set ANTHROPIC_API_KEY or "
            "pass --api-key-env / --api-profile.",
            file=sys.stderr,
        )
        return 3

    verdicts, buildability_gaps = call_evaluator(
        api_key=api_key,
        model=args.model,
        thinking_budget=args.thinking_budget,
        max_tokens=args.max_tokens,
        api_version=args.api_version,
        items=items,
        evidence=evidence,
        advisory=advisory,
        prereqs=prereqs,
    )

    # Apply prereq-based blocking AFTER the LLM verdict so missing infra
    # never silently turns into a `fail` the loop will spin on.
    verdicts = apply_prereq_blocks(verdicts, prereqs)
    verdicts = ensure_traced_causes(verdicts)
    buildability_gaps = normalize_buildability_gaps(buildability_gaps, verdicts)

    counts = tally(verdicts)
    done = counts["fail"] == 0 and counts["partial"] == 0 and (
        counts["blocked"] == 0 or all_blocked_have_prereqs(verdicts)
    )

    report = {
        "rubricVersion": rubric_version(RUBRIC.read_text()),
        "evaluatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "model": args.model,
        "counts": counts,
        "done": done,
        "items": verdicts,
        "buildability_gaps": buildability_gaps,
        "projections": build_projection_summary(verdicts),
        "advisoryScoreGate": {
            "score": advisory.get("score"),
            "passed": advisory.get("passed"),
            "note": (
                "Advisory only. The deterministic score gate no longer gates publish; "
                "this evaluator does."
            ),
        },
        "runtimePrereqStatus": prereqs,
    }

    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps({"counts": counts, "done": done, "output": str(output_path)}, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Where to write the evaluation JSON.")
    parser.add_argument(
        "--model",
        default="claude-opus-4-7",
        help="Anthropic model name. Default: claude-opus-4-7.",
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=12000,
        help="Extended thinking budget in tokens. Default: 12000.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=20000,
        help="Max response tokens (includes thinking). Default: 20000.",
    )
    parser.add_argument(
        "--api-version",
        default="2023-06-01",
        help="Anthropic API version header.",
    )
    parser.add_argument(
        "--api-key-env",
        default="ANTHROPIC_API_KEY",
        help="Env var name to read the Anthropic API key from.",
    )
    parser.add_argument(
        "--api-profile",
        default=str(Path.home() / ".zprofile"),
        help="Shell profile to source for the API key if env is not set.",
    )
    parser.add_argument(
        "--env-file",
        default=str(ROOT / ".env.local"),
        help="Env file to inspect for runtime prereqs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip the API call; print evidence summary only.",
    )
    return parser.parse_args()


# ---------- rubric parsing ----------

ITEM_HEADER = re.compile(r"^###\s+([a-z][a-z0-9_]+)\s*$", re.MULTILINE)


def rubric_version(text: str) -> str:
    # Use a hash of the rubric so the report can show that the rubric changed.
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def parse_rubric(text: str) -> list[dict]:
    """Pull each `### item_id` block and its bullet body."""
    matches = list(ITEM_HEADER.finditer(text))
    items: list[dict] = []
    for i, m in enumerate(matches):
        item_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        # Stop at next H2 if the rubric block ends mid-section.
        h2 = re.search(r"^##\s+", body, re.MULTILINE)
        if h2:
            body = body[: h2.start()].strip()
        items.append({"id": item_id, "body": body})
    return items


# ---------- evidence ----------


def gather_evidence() -> list[dict]:
    seen: set[str] = set()
    files: list[Path] = []
    for rel in ALWAYS_EVIDENCE:
        p = ROOT / rel
        if p.exists() and rel not in seen:
            files.append(p)
            seen.add(rel)
    for pattern in EVIDENCE_GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in seen:
                files.append(p)
                seen.add(rel)
            if len(files) >= MAX_EVIDENCE_FILES:
                break
        if len(files) >= MAX_EVIDENCE_FILES:
            break

    out: list[dict] = []
    total = 0
    for p in files:
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        truncated = False
        if len(text.encode("utf-8")) > MAX_FILE_BYTES:
            text = text[:MAX_FILE_BYTES] + "\n... [truncated]\n"
            truncated = True
        chunk = {
            "path": p.relative_to(ROOT).as_posix(),
            "bytes": len(text.encode("utf-8")),
            "truncated": truncated,
            "content": text,
        }
        if total + chunk["bytes"] > MAX_TOTAL_EVIDENCE_BYTES:
            break
        total += chunk["bytes"]
        out.append(chunk)
    return out


def load_advisory_report() -> dict:
    if not ADVISORY_REPORT.exists():
        return {}
    try:
        return json.loads(ADVISORY_REPORT.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def check_runtime_prereqs(env_file: str) -> dict:
    env = dict(os.environ)
    p = Path(env_file)
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip().strip("\"'"))
    return {
        "supabase_cli": shutil.which("supabase") is not None,
        "SUPABASE_SERVICE_ROLE_KEY": bool(env.get("SUPABASE_SERVICE_ROLE_KEY")),
        "SUPABASE_PUBLISHABLE_KEY_OR_ANON": bool(
            env.get("SUPABASE_PUBLISHABLE_KEY") or env.get("SUPABASE_ANON_KEY")
        ),
    }


# ---------- projection summary ----------

DECISION_REGISTER = ROOT / "docs" / "decisions" / "standards-overlap-decisions.md"
DECISION_SECTION = re.compile(r"^##\s+(DEC-\d{3}[^\n]*)$", re.MULTILINE)


def build_projection_summary(verdicts: list[dict]) -> dict:
    """Build a per-decision summary of declared projections and local evidence.

    This is intentionally deterministic and structural. The LLM verdict for
    `projections_match_reality` remains the semantic contradiction check; this
    section gives the loop a stable spine index for every decision's declared
    artifact projections.
    """

    semantic_status = next(
        (item.get("status") for item in verdicts if item.get("id") == "projections_match_reality"),
        "unknown",
    )
    decisions = parse_decision_register()
    summary_items = []
    totals = {
        "decisions": len(decisions),
        "projectionRefs": 0,
        "present": 0,
        "missing": 0,
        "unverifiedFragments": 0,
    }
    for decision in decisions:
        projection_checks = [check_projection_ref(ref) for ref in decision["projects_to"]]
        totals["projectionRefs"] += len(projection_checks)
        totals["present"] += sum(1 for item in projection_checks if item["status"].startswith("present"))
        totals["missing"] += sum(1 for item in projection_checks if item["status"].startswith("missing"))
        totals["unverifiedFragments"] += sum(
            1 for item in projection_checks if item["status"] == "present_unverified_fragment"
        )

        if any(item["status"].startswith("missing") for item in projection_checks):
            match_status = "missing_projection"
        elif any(item["status"] == "present_unverified_fragment" for item in projection_checks):
            match_status = "present_with_unverified_fragments"
        else:
            match_status = "present"

        summary_items.append(
            {
                "decision_id": decision["id"],
                "title": decision["title"],
                "choice": decision["choice"],
                "match_status": match_status,
                "projection_count": len(projection_checks),
                "projections": projection_checks,
            }
        )

    return {
        "source": DECISION_REGISTER.relative_to(ROOT).as_posix(),
        "projectionMatchItemStatus": semantic_status,
        "note": (
            "Structural per-decision projection index generated from `projects_to`; "
            "semantic contradictions are graded by the projections_match_reality rubric item."
        ),
        "counts": totals,
        "decisions": summary_items,
    }


def parse_decision_register() -> list[dict]:
    if not DECISION_REGISTER.exists():
        return []

    text = DECISION_REGISTER.read_text()
    matches = list(DECISION_SECTION.finditer(text))
    decisions = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        decision_id = parse_backticked_field(block, "id")
        if not decision_id:
            continue
        decisions.append(
            {
                "id": decision_id,
                "title": title,
                "choice": parse_text_field(block, "choice"),
                "projects_to": parse_projects_to(block),
            }
        )
    return decisions


def parse_backticked_field(block: str, field_name: str) -> str:
    pattern = re.compile(rf"^-\s+{re.escape(field_name)}:\s+`([^`]+)`\s*$", re.MULTILINE)
    match = pattern.search(block)
    return match.group(1).strip() if match else ""


def parse_text_field(block: str, field_name: str) -> str:
    pattern = re.compile(rf"^-\s+{re.escape(field_name)}:\s+(.+?)\s*$", re.MULTILINE)
    match = pattern.search(block)
    return match.group(1).strip() if match else ""


def parse_projects_to(block: str) -> list[str]:
    refs = []
    in_projects = False
    for line in block.splitlines():
        if line.strip() == "- projects_to:":
            in_projects = True
            continue
        if not in_projects:
            continue
        if line.startswith("  - "):
            value = line[4:].strip()
            if value.startswith("`") and value.endswith("`"):
                value = value[1:-1]
            refs.append(value)
            continue
        if line.startswith("- ") or line.startswith("## "):
            break
    return refs


def check_projection_ref(ref: str) -> dict:
    path_text, _, fragment = ref.partition("#")
    result = {
        "ref": ref,
        "path": path_text,
        "fragment": fragment,
        "status": "missing_path",
        "detail": "",
    }
    path = ROOT / path_text
    if not path.exists():
        result["detail"] = "Referenced path does not exist."
        return result

    if not fragment:
        result["status"] = "present_path"
        result["detail"] = "Referenced path exists."
        return result

    if path_text.startswith("dictionary/") and path.suffix == ".json":
        status, detail = check_dictionary_projection(path, fragment)
        result["status"] = status
        result["detail"] = detail
        return result

    status, detail = check_text_projection(path, fragment)
    result["status"] = status
    result["detail"] = detail
    return result


def check_dictionary_projection(path: Path, fragment: str) -> tuple[str, str]:
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return "missing_fragment", f"Could not parse dictionary JSON: {exc}"

    object_key, _, field_key = fragment.partition(".")
    for obj in data.get("objects", []):
        if obj.get("object_key") != object_key:
            continue
        if not field_key:
            return "present_dictionary_object", "Dictionary object exists."
        if any(field.get("field_key") == field_key for field in obj.get("fields", [])):
            return "present_dictionary_field", "Dictionary field exists."
        return "missing_fragment", "Dictionary object exists but field is missing."
    return "missing_fragment", "Dictionary object is missing."


def check_text_projection(path: Path, fragment: str) -> tuple[str, str]:
    try:
        text = path.read_text(errors="replace")
    except OSError as exc:
        return "missing_fragment", f"Could not read referenced path: {exc}"

    if fragment in text:
        return "present_text_fragment", "Fragment text appears in the referenced artifact."

    normalized_text = normalize_ref_text(text)
    normalized_fragment = normalize_ref_text(fragment)
    if normalized_fragment and normalized_fragment in normalized_text:
        return "present_text_fragment", "Normalized fragment text appears in the referenced artifact."

    tokens = [token for token in re.split(r"[^A-Za-z0-9]+", fragment) if token]
    if tokens and tokens[0].lower() in normalized_text:
        return "present_text_hint", "Referenced artifact contains the projection's primary token."

    return "present_unverified_fragment", "Referenced path exists, but the fragment is not directly verifiable."


def normalize_ref_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9]+", " ", value.lower())).strip()


# ---------- API ----------


def resolve_api_key(args: argparse.Namespace) -> str | None:
    key = os.environ.get(args.api_key_env)
    if key:
        return key
    profile = Path(args.api_profile)
    if not profile.exists():
        return None
    try:
        out = subprocess.run(
            ["/bin/zsh", "-c", f"source {profile} >/dev/null 2>&1 && printf %s \"${{{args.api_key_env}}}\""],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
            check=False,
        )
        value = out.stdout.strip()
        return value or None
    except (subprocess.SubprocessError, OSError):
        return None


def build_evaluator_prompt(items: list[dict], evidence: list[dict], advisory: dict, prereqs: dict) -> str:
    rubric_block = "\n\n".join(
        f"### {it['id']}\n{it['body']}" for it in items
    )
    evidence_block_parts = []
    for e in evidence:
        header = f"--- FILE: {e['path']} ({e['bytes']} bytes{', TRUNCATED' if e['truncated'] else ''}) ---"
        evidence_block_parts.append(f"{header}\n{e['content']}")
    evidence_block = "\n\n".join(evidence_block_parts)

    advisory_block = json.dumps(advisory, indent=2)[:8000] if advisory else "(no advisory report)"
    prereq_block = json.dumps(prereqs, indent=2)

    instructions = textwrap.dedent(
        """
        You are the platform evaluator. You grade a software repository against
        the rubric below on SUBSTANCE, not file presence. You are the publish
        gate for an autonomous code-improvement loop \u2014 your verdict decides
        whether the next iteration runs.

        For EACH rubric item, return one verdict object with these fields:
          - id: the rubric item id (must match exactly)
          - status: "pass" | "partial" | "fail" | "blocked"
          - reason: 1\u20133 sentences. Specific. Cite file paths or quoted snippets.
            No hedging.
          - traced_cause: required and non-empty whenever status is not "pass".
            Name the lowest-layer artifact that must change and the required
            change, e.g. "dictionary/oneroster-core.v1.json#person.email:
            add canonical_field_id pointing to the shared email field". Use
            "" only when status is "pass".
          - evidence_paths: list of file paths from the EVIDENCE section that
            informed your verdict.
          - blocked_prerequisites: list of strings naming external
            prerequisites that must be satisfied to make progress. Empty
            unless status == "blocked".

        Also return a top-level buildability_gaps array. If
        buildable_by_layperson is non-pass, include one object for each gap
        encountered by the layperson simulation with:
          - step: one of "create_school", "create_class", "post_grade",
            "link_case_standard", "read_caliper_feed", or "cross_step"
          - gap: the missing/ambiguous thing
          - traced_cause: the specific decision, dictionary entry, or doc that
            must change. This must be non-empty for every gap.
        If buildable_by_layperson passes, return an empty array.

        Status rules:
          - "pass": the requirement's substance_check is fully met.
          - "partial": some required elements present, others missing or weak.
            Use this for "right shape, wrong depth" cases.
          - "fail": missing or contradicted by the evidence. The loop CAN fix
            this with normal code/doc work. Do NOT use "fail" if a documented
            external prerequisite is missing \u2014 use "blocked" instead.
          - "blocked": cannot progress without an external prerequisite the
            loop cannot satisfy on its own (e.g., missing API credentials,
            external service down). Name the prerequisite explicitly.

        Be strict. The previous gate accepted file-presence checks and gave
        100/100 to a platform that hadn't shipped a real API. Do not repeat
        that mistake. If a section header exists but its content is a stub,
        that is "partial" or "fail", not "pass".

        Return ONLY valid JSON with this shape, nothing else:
          { "items": [ { "id": "...", "status": "...", "reason": "...",
                         "traced_cause": "...", "evidence_paths": [...],
                         "blocked_prerequisites": [...] }, ... ],
            "buildability_gaps": [
              { "step": "...", "gap": "...", "traced_cause": "..." }
            ] }
        """
    ).strip()

    return (
        f"{instructions}\n\n"
        f"=== RUBRIC ===\n{rubric_block}\n\n"
        f"=== ADVISORY DETERMINISTIC REPORT (signal only, do not defer to it) ===\n{advisory_block}\n\n"
        f"=== RUNTIME PREREQUISITE STATUS ===\n{prereq_block}\n\n"
        f"=== EVIDENCE FILES ===\n{evidence_block}\n"
    )


def call_evaluator(
    *,
    api_key: str,
    model: str,
    thinking_budget: int,
    max_tokens: int,
    api_version: str,
    items: list[dict],
    evidence: list[dict],
    advisory: dict,
    prereqs: dict,
) -> tuple[list[dict], list[dict]]:
    prompt = build_evaluator_prompt(items, evidence, advisory, prereqs)
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if model == "claude-opus-4-7":
        body["thinking"] = {"type": "adaptive"}
        body["output_config"] = {"effort": "high"}
    else:
        body["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
    req = urllib.request.Request(
        ANTHROPIC_MESSAGES_URL,
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": api_version,
            "content-type": "application/json",
        },
    )
    raw = _retry_post(req)
    payload = json.loads(raw)

    text = ""
    for block in payload.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")
    if not text:
        raise SystemExit(f"Anthropic API returned no text content: {payload}")

    parsed = _extract_json(text)
    raw_items = parsed.get("items", [])
    buildability_gaps = parsed.get("buildability_gaps", [])
    by_id = {it["id"]: it for it in items}
    verdicts: list[dict] = []
    for v in raw_items:
        item_id = v.get("id")
        if item_id not in by_id:
            continue
        status = normalize_status(v.get("status"))
        reason = (v.get("reason") or "").strip()
        verdicts.append(
            {
                "id": item_id,
                "status": status,
                "reason": reason,
                "traced_cause": normalize_traced_cause(
                    v.get("traced_cause"),
                    item_id=item_id,
                    status=status,
                    reason=reason,
                    blocked_prerequisites=v.get("blocked_prerequisites", []),
                ),
                "evidence_paths": v.get("evidence_paths", []),
                "blocked_prerequisites": v.get("blocked_prerequisites", []),
            }
        )
    # Fill in any rubric items the model dropped.
    seen = {v["id"] for v in verdicts}
    for it in items:
        if it["id"] not in seen:
            verdicts.append(
                {
                    "id": it["id"],
                    "status": "fail",
                    "reason": "Evaluator did not return a verdict for this item.",
                    "traced_cause": default_traced_cause(it["id"]),
                    "evidence_paths": [],
                    "blocked_prerequisites": [],
                }
            )
    return verdicts, buildability_gaps


def _retry_post(req: urllib.request.Request, attempts: int = 3) -> str:
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            last_err = SystemExit(f"Anthropic HTTP {e.code}: {body[:2000]}")
            if e.code in (429, 500, 502, 503, 504) and i < attempts - 1:
                time.sleep(2 ** (i + 1))
                continue
            raise last_err
        except urllib.error.URLError as e:
            last_err = e
            time.sleep(2 ** (i + 1))
    raise SystemExit(f"Anthropic API failed after {attempts} attempts: {last_err}")


_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _extract_json(text: str) -> dict:
    fence = _JSON_FENCE.search(text)
    candidate = fence.group(1) if fence else text
    # Trim to outermost braces if the model added prose.
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start >= 0 and end > start:
        candidate = candidate[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Could not parse evaluator JSON: {e}\n---\n{text[:2000]}")


# ---------- post-processing ----------


VALID_STATUSES = {"pass", "partial", "fail", "blocked"}

DEFAULT_TRACED_CAUSES = {
    "decisions_complete": (
        "docs/decisions/standards-overlap-decisions.md and "
        "docs/decisions/decisions-needed.md: add or sharpen the missing "
        "six-field decision and align projects_to with the artifact it governs."
    ),
    "no_unforced_decisions": (
        "docs/decisions/decisions-pending.md: add owner, target_date, blocker, "
        "and rationale for every undecided platform choice."
    ),
    "decisions_simplify": (
        "docs/decisions/standards-overlap-decisions.md: update consequences to "
        "name the concrete artifact, code path, or category each decision removes."
    ),
    "decisions_have_real_alternatives": (
        "docs/decisions/standards-overlap-decisions.md: add credible aggressive "
        "and permissive architectural alternatives for each weak decision."
    ),
    "dictionary_single_source_of_truth": (
        "data/data-dictionary.seed.json and scripts/generate_spec_dictionaries.py: "
        "implement DEC-016 so the shared dictionary generates every per-spec projection."
    ),
    "dictionary_resolves_cross_spec_overlaps": (
        "data/data-dictionary.seed.json and dictionary/*.v1.json: implement DEC-017 "
        "with canonical_field_id on overlapping fields or documented spec_only exceptions."
    ),
    "dictionary_unifies_identity": (
        "data/data-dictionary.seed.json and dictionary/*.v1.json: add the canonical "
        "identity object and canonical_object_id projections for identity-shaped spec objects."
    ),
    "dictionary_global_enums": (
        "data/data-dictionary.seed.json and dictionary/*.v1.json: implement DEC-018 "
        "with shared_enum_id references and bidirectional spec value crosswalks."
    ),
    "dictionary_closed_privacy_classes": (
        "data/data-dictionary.seed.json and dictionary/*.v1.json: implement DEC-019 "
        "with one closed privacy class list and no depends_on_* placeholders."
    ),
    "dictionary_carries_relational_graph": (
        "data/data-dictionary.seed.json and supabase/migrations/*.sql: implement "
        "DEC-020 relationships and migration generation from the dictionary graph."
    ),
    "dictionary_artifacts_cite_decisions": (
        "dictionary/*.v1.json and docs/decisions/standards-overlap-decisions.md: "
        "add decision_id citations for orphaned dictionary artifacts."
    ),
    "docs_generated_from_dictionary": (
        "scripts/build_site_docs.py, docs/generated/*-dictionary.md, and prose docs: "
        "regenerate dictionary-backed references and link load-bearing claims to anchors."
    ),
    "docs_explain_why_not_only_what": (
        "docs/*.md and docs/decisions/standards-overlap-decisions.md: add plain-language "
        "decision explanations where generated concepts are introduced."
    ),
    "docs_include_buildability_guide": (
        "docs/build-an-edtech-app.md: write the end-to-end executable guide with "
        "dictionary and enum links for each required step."
    ),
    "docs_no_dead_links_or_orphans": (
        "site/docs/index.html and rendered site docs: add link-check evidence and "
        "make every dictionary entry, decision, endpoint, and guide reachable."
    ),
    "buildable_by_layperson": (
        "docs/build-an-edtech-app.md plus the traced dictionary/decision gaps: "
        "make the five-step teaching-app scenario executable from docs alone."
    ),
    "evaluator_traces_failures_backward": (
        "scripts/evaluate_platform.py: emit traced_cause for every non-pass item "
        "and include buildability_gaps with traced causes."
    ),
    "evaluator_runs_each_iteration": (
        "scripts/evaluate_platform.py and VERIFY.md: run the evaluator at iteration "
        "end and write traced_cause plus buildability_gaps to the report."
    ),
    "loop_overrides_respected": (
        "scripts/codex_loop.py and docs/loop-overrides.md: read, inject, and honor "
        "human overrides before starting an iteration."
    ),
    "loop_terminates_on_done": (
        "scripts/codex_loop.py: terminate from the evaluator done flag rather than "
        "a numeric threshold."
    ),
}


def normalize_status(value: object) -> str:
    status = str(value or "fail").strip().lower()
    return status if status in VALID_STATUSES else "fail"


def ensure_traced_causes(verdicts: list[dict]) -> list[dict]:
    normalized = []
    for verdict in verdicts:
        status = normalize_status(verdict.get("status"))
        verdict = {**verdict, "status": status}
        verdict["traced_cause"] = normalize_traced_cause(
            verdict.get("traced_cause"),
            item_id=str(verdict.get("id", "")),
            status=status,
            reason=str(verdict.get("reason", "")),
            blocked_prerequisites=verdict.get("blocked_prerequisites", []),
        )
        normalized.append(verdict)
    return normalized


def normalize_traced_cause(
    value: object,
    *,
    item_id: str,
    status: str,
    reason: str,
    blocked_prerequisites: object,
) -> str:
    if status == "pass":
        return ""

    if isinstance(value, dict):
        parts = []
        for key in ("artifact", "required_change", "cause", "details"):
            if value.get(key):
                parts.append(str(value[key]).strip())
        if parts:
            return ": ".join(parts)

    if isinstance(value, str) and value.strip():
        return value.strip()

    if status == "blocked":
        prereqs = normalize_string_list(blocked_prerequisites)
        if prereqs:
            return f"external prerequisite: {', '.join(prereqs)}"

    extracted = extract_trace_from_reason(reason)
    if extracted:
        return extracted

    return default_traced_cause(item_id)


def default_traced_cause(item_id: str) -> str:
    return DEFAULT_TRACED_CAUSES.get(
        item_id,
        f"docs/eval-rubric.md#{item_id}: update the lowest-layer artifact named by the non-pass verdict.",
    )


def normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def extract_trace_from_reason(reason: str) -> str:
    if not reason:
        return ""
    patterns = [
        r"Traces to:\s*([^;\n]+)",
        r"traces to\s+([^;\n]+)",
        r"traces back to\s+([^;\n]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, reason)
        if match:
            return match.group(1).strip(" .;)")
    return ""


def normalize_buildability_gaps(raw_gaps: object, verdicts: list[dict]) -> list[dict]:
    buildability = next((v for v in verdicts if v.get("id") == "buildable_by_layperson"), None)
    fallback_trace = (
        str(buildability.get("traced_cause", "")).strip()
        if buildability
        else default_traced_cause("buildable_by_layperson")
    )

    gaps: list[dict] = []
    if isinstance(raw_gaps, list):
        for index, raw_gap in enumerate(raw_gaps, start=1):
            gap = normalize_buildability_gap(raw_gap, index, fallback_trace)
            if gap:
                gaps.append(gap)

    if gaps:
        return gaps

    if buildability and buildability.get("status") != "pass":
        return extract_buildability_gaps_from_reason(
            str(buildability.get("reason", "")),
            fallback_trace=fallback_trace or default_traced_cause("buildable_by_layperson"),
        )

    return []


def normalize_buildability_gap(raw_gap: object, index: int, fallback_trace: str) -> dict:
    if isinstance(raw_gap, dict):
        gap_text = str(raw_gap.get("gap") or raw_gap.get("reason") or "").strip()
        step = str(raw_gap.get("step") or f"gap_{index}").strip()
        trace = normalize_gap_trace(raw_gap.get("traced_cause"), gap_text, fallback_trace)
    else:
        gap_text = str(raw_gap).strip()
        step = f"gap_{index}"
        trace = normalize_gap_trace(None, gap_text, fallback_trace)

    if not gap_text:
        return {}
    return {"step": step, "gap": gap_text, "traced_cause": trace}


def normalize_gap_trace(value: object, gap_text: str, fallback_trace: str) -> str:
    if isinstance(value, dict):
        parts = [str(v).strip() for v in value.values() if str(v).strip()]
        if parts:
            return ": ".join(parts)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return extract_trace_from_reason(gap_text) or fallback_trace


def extract_buildability_gaps_from_reason(reason: str, *, fallback_trace: str) -> list[dict]:
    if not reason:
        return [
            {
                "step": "cross_step",
                "gap": "buildable_by_layperson is non-pass but the evaluator did not list individual gaps.",
                "traced_cause": fallback_trace,
            }
        ]

    _, marker, tail = reason.partition("Gaps:")
    gap_text = tail if marker else reason
    parts = [part.strip(" ;.") for part in re.split(r"\s*\(\d+\)\s*", gap_text) if part.strip(" ;.")]
    if not parts:
        parts = [gap_text.strip(" ;.")]

    gaps = []
    for index, part in enumerate(parts, start=1):
        trace = extract_trace_from_reason(part) or fallback_trace
        gaps.append({"step": f"gap_{index}", "gap": part, "traced_cause": trace})
    return gaps


def apply_prereq_blocks(verdicts: list[dict], prereqs: dict) -> list[dict]:
    out = []
    for v in verdicts:
        rule = RUNTIME_PREREQS.get(v["id"])
        if rule:
            missing = [desc for key, desc in rule if not prereqs.get(key)]
            if missing and v["status"] in ("fail", "partial"):
                v = {
                    **v,
                    "status": "blocked",
                    "blocked_prerequisites": list(
                        dict.fromkeys((v.get("blocked_prerequisites") or []) + missing)
                    ),
                    "reason": (
                        v.get("reason", "")
                        + f" [auto-blocked: missing {', '.join(missing)}]"
                    ).strip(),
                    "traced_cause": f"external prerequisite: {', '.join(missing)}",
                }
        out.append(v)
    return out


def tally(verdicts: list[dict]) -> dict:
    counts = {"pass": 0, "partial": 0, "fail": 0, "blocked": 0, "total": len(verdicts)}
    for v in verdicts:
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    return counts


def all_blocked_have_prereqs(verdicts: list[dict]) -> bool:
    for v in verdicts:
        if v["status"] == "blocked" and not v.get("blocked_prerequisites"):
            return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
