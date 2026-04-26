#!/usr/bin/env python3
"""LLM-backed platform evaluator.

Replaces the deterministic score gate as the publish gate for the Codex loop.
Reads docs/eval-rubric.md, gathers evidence from the repo, calls Claude
(Anthropic API direct) to grade each requirement on substance, and writes
site/api/platform-evaluation.json.

Output schema (per item):
  { id, status: "pass"|"partial"|"fail"|"blocked",
    reason: str, evidence_paths: [str],
    blocked_prerequisites: [str] }

Overall:
  { rubricVersion, evaluatedAt, model,
    counts: {pass, partial, fail, blocked, total},
    done: bool, items: [...],
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
    "docs/spec-gap-backlog.md",
    "docs/dictionary-coverage-matrix.md",
    "docs/lead-spec-accounting.md",
    "docs/decisions/standards-overlap-decisions.md",
    "docs/admin-operations.md",
    "docs/supabase-hosted-database.md",
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
MAX_FILE_BYTES = 30000  # truncate large files when feeding to LLM
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

    verdicts = call_evaluator(
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
          - evidence_paths: list of file paths from the EVIDENCE section that
            informed your verdict.
          - blocked_prerequisites: list of strings naming external
            prerequisites that must be satisfied to make progress. Empty
            unless status == "blocked".

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
                         "evidence_paths": [...], "blocked_prerequisites": [...] }, ... ] }
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
) -> list[dict]:
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
    by_id = {it["id"]: it for it in items}
    verdicts: list[dict] = []
    for v in raw_items:
        item_id = v.get("id")
        if item_id not in by_id:
            continue
        verdicts.append(
            {
                "id": item_id,
                "status": v.get("status", "fail"),
                "reason": (v.get("reason") or "").strip(),
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
                    "evidence_paths": [],
                    "blocked_prerequisites": [],
                }
            )
    return verdicts


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
