#!/usr/bin/env python3
"""Run Codex in a small eval-driven improvement loop for this repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import signal
import shlex
import subprocess
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "PLAN.md"
VERIFY = ROOT / "VERIFY.md"
PROGRESS = ROOT / "PROGRESS.md"
LOG_DIR = ROOT / ".codex-loop"
SPEC_REPORT = ROOT / "site" / "api" / "spec-conformance.json"
EVAL_REPORT = ROOT / "site" / "api" / "platform-evaluation.json"
RUBRIC_PATH = ROOT / "docs" / "eval-rubric.md"
OVERRIDES_PATH = ROOT / "docs" / "loop-overrides.md"
PAUSE_TOKEN = "PAUSE"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODELS_URL = "https://api.anthropic.com/v1/models"

# Safety rails for the LLM-evaluator loop.
DEFAULT_MAX_ITERATIONS = 25
DEFAULT_STALL_LIMIT = 3  # consecutive iterations with no rubric progress = stop
DEFAULT_COST_CEILING_USD = 50.0  # advisory; logged each iteration


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    LOG_DIR.mkdir(exist_ok=True)

    if args.dry_run:
        print(build_prompt(repo, 1, args.max_iterations))
        return 0

    stall_streak = 0
    last_eval_summary: dict | None = None
    for iteration in range(1, args.max_iterations + 1):
        started = timestamp()
        print(f"\n=== Codex loop iteration {iteration}/{args.max_iterations} at {started} ===")
        overrides = read_overrides(repo)
        if overrides_paused(overrides):
            print(
                "Pause flag set in docs/loop-overrides.md. "
                "Halting before iteration. Clear the PAUSE token to resume."
            )
            return 0
        before_score = spec_score(repo)
        before_eval = run_evaluator(repo, args, label="before")
        if before_eval and before_eval.get("done"):
            print("Evaluator reports `done` before any work. Nothing to do; exiting cleanly.")
            return 0
        print(
            f"Advisory score before: {before_score:.2f}; "
            f"rubric counts before: {before_eval.get('counts') if before_eval else 'n/a'}"
        )
        prompt = build_prompt(repo, iteration, args.max_iterations, before_eval, overrides)
        prompt_file = LOG_DIR / f"{started}-iteration-{iteration:03d}-prompt.md"
        codex_log = LOG_DIR / f"{started}-iteration-{iteration:03d}-codex.log"
        verify_log = LOG_DIR / f"{started}-iteration-{iteration:03d}-verify.log"
        last_message = LOG_DIR / "last-message.md"
        prompt_file.write_text(prompt)

        codex_result = run_codex(args, repo, prompt, codex_log, last_message)
        verify_result = run_verify(repo, verify_log, args.verify_command_timeout_minutes)
        after_score = spec_score(repo)
        after_eval = run_evaluator(repo, args, label="after")
        print(f"Advisory score after: {after_score:.2f}")
        if after_eval:
            print(f"Rubric counts after: {after_eval.get('counts')}")
        judge_log = LOG_DIR / f"{started}-iteration-{iteration:03d}-judge.log"
        judge_json = LOG_DIR / f"{started}-iteration-{iteration:03d}-judge.json"
        judge_result = maybe_run_llm_judge(
            args,
            repo,
            iteration,
            before_score,
            after_score,
            codex_log,
            verify_log,
            judge_log,
            judge_json,
            codex_result.returncode == 0 and verify_result.returncode == 0,
        )
        publish_result = maybe_publish(
            args,
            repo,
            iteration,
            before_score,
            after_score,
            codex_result.returncode,
            verify_result.returncode,
            judge_result,
            before_eval,
            after_eval,
        )
        append_machine_progress(
            iteration,
            codex_result,
            verify_result,
            codex_log,
            verify_log,
            judge_log,
            judge_json,
            before_score,
            after_score,
            judge_result,
            publish_result,
        )

        if publish_result.startswith("DIVERGENCE:"):
            print(publish_result)
            return 1

        if codex_result.returncode != 0:
            print(f"Codex exited with {codex_result.returncode}; see {codex_log}")
            if not args.continue_on_failure:
                return codex_result.returncode

        if verify_result.returncode != 0:
            print(f"Verify exited with {verify_result.returncode}; see {verify_log}")
            if not args.continue_on_failure:
                return verify_result.returncode

        # Termination: rubric reports done.
        if after_eval and after_eval.get("done"):
            print("Evaluator reports `done` after this iteration. Stopping the loop.")
            return 0

        # Stall detection: count items by status, stop if no progress for N iterations.
        if before_eval and after_eval:
            progressed = rubric_progressed(before_eval, after_eval)
            if progressed:
                stall_streak = 0
                print("Rubric progressed this iteration; stall counter reset.")
            else:
                stall_streak += 1
                print(
                    f"No rubric progress this iteration. Stall streak: "
                    f"{stall_streak}/{args.stall_limit}."
                )
            if stall_streak >= args.stall_limit:
                print(
                    f"Stall limit reached ({args.stall_limit} consecutive iterations "
                    "with no rubric progress). Stopping for human review."
                )
                return 0

        last_eval_summary = after_eval

        final_text = last_message.read_text() if last_message.exists() else ""
        if "LOOP_STATUS: COMPLETE" in final_text:
            # Codex thinks it's done. Trust the evaluator over Codex.
            if after_eval and after_eval.get("done"):
                print("Codex reported COMPLETE and evaluator agrees.")
                return 0
            print("Codex reported COMPLETE but evaluator says work remains. Continuing.")

        if iteration < args.max_iterations and args.interval_minutes > 0:
            seconds = args.interval_minutes * 60
            print(f"Sleeping {args.interval_minutes} minute(s) before next iteration...")
            time.sleep(seconds)

    print("Reached max iterations without `done`. Latest rubric state:")
    if last_eval_summary:
        print(json.dumps(last_eval_summary.get("counts", {}), indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch Codex repeatedly in this repo with PLAN/VERIFY/PROGRESS memory."
    )
    parser.add_argument("--repo", default=str(ROOT), help="Repository directory. Defaults to this repo.")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=f"Hard cap on iterations. Default {DEFAULT_MAX_ITERATIONS}.",
    )
    parser.add_argument(
        "--stall-limit",
        type=int,
        default=DEFAULT_STALL_LIMIT,
        help=f"Stop after this many consecutive iterations with no rubric progress. Default {DEFAULT_STALL_LIMIT}.",
    )
    parser.add_argument(
        "--evaluator-thinking-budget",
        type=int,
        default=int(os.environ.get("CODEX_EVALUATOR_THINKING_BUDGET", "12000")),
        help="Anthropic extended thinking budget for the platform evaluator.",
    )
    parser.add_argument(
        "--evaluator-max-tokens",
        type=int,
        default=int(os.environ.get("CODEX_EVALUATOR_MAX_TOKENS", "20000")),
        help="Max tokens for the platform evaluator response.",
    )
    parser.add_argument(
        "--evaluator-model",
        default=os.environ.get("CODEX_EVALUATOR_MODEL", "claude-opus-4-7"),
        help="Anthropic model used for the platform evaluator.",
    )
    parser.add_argument("--interval-minutes", type=float, default=0, help="Delay between iterations.")
    parser.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"), help="Codex executable.")
    parser.add_argument("--model", default=os.environ.get("CODEX_MODEL"), help="Optional Codex model.")
    parser.add_argument(
        "--judge-provider",
        default=os.environ.get("CODEX_JUDGE_PROVIDER", "anthropic-api"),
        choices=["anthropic-api", "codex-exec"],
        help="LLM judge provider. Defaults to direct Anthropic API.",
    )
    parser.add_argument(
        "--judge-model",
        default=os.environ.get("CODEX_JUDGE_MODEL", "opus-4.7"),
        help="LLM judge model. Defaults to opus-4.7.",
    )
    parser.add_argument(
        "--judge-reasoning-effort",
        default=os.environ.get("CODEX_JUDGE_REASONING_EFFORT", "xhigh"),
        help="LLM judge reasoning effort. For Anthropic API this maps to extended thinking budget.",
    )
    parser.add_argument(
        "--judge-api-profile",
        default=os.environ.get("CODEX_JUDGE_API_PROFILE", "~/.zprofile"),
        help="Shell profile to source for API keys before direct API judge calls.",
    )
    parser.add_argument(
        "--judge-api-key-env",
        default=os.environ.get("CODEX_JUDGE_API_KEY_ENV", "ANTHROPIC_API_KEY"),
        help="Environment variable containing the Anthropic API key.",
    )
    parser.add_argument(
        "--judge-api-version",
        default=os.environ.get("ANTHROPIC_VERSION", "2023-06-01"),
        help="Anthropic API version header for direct API judge calls.",
    )
    parser.add_argument(
        "--judge-max-tokens",
        type=int,
        default=int(os.environ.get("CODEX_JUDGE_MAX_TOKENS", "12000")),
        help="Max tokens for the judge response, including thinking tokens when enabled.",
    )
    parser.add_argument(
        "--judge-thinking-budget",
        type=int,
        default=os.environ.get("CODEX_JUDGE_THINKING_BUDGET"),
        help="Override Anthropic extended thinking budget tokens.",
    )
    parser.add_argument(
        "--skip-llm-judge",
        action="store_true",
        help="Skip the LLM judge gate. Not recommended for unattended runs.",
    )
    parser.add_argument(
        "--sandbox",
        default=os.environ.get("CODEX_SANDBOX", "danger-full-access"),
        choices=["read-only", "workspace-write", "danger-full-access"],
        help="Codex sandbox mode.",
    )
    parser.add_argument(
        "--approval",
        default=os.environ.get("CODEX_APPROVAL", "never"),
        choices=["untrusted", "on-failure", "on-request", "never"],
        help="Codex approval policy.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Keep looping even if Codex or verification fails.",
    )
    parser.add_argument(
        "--codex-timeout-minutes",
        type=float,
        default=float(os.environ.get("CODEX_TIMEOUT_MINUTES", "30")),
        help="Maximum wall-clock time for one Codex worker iteration before it is stopped.",
    )
    parser.add_argument(
        "--verify-command-timeout-minutes",
        type=float,
        default=float(os.environ.get("CODEX_VERIFY_COMMAND_TIMEOUT_MINUTES", "15")),
        help="Maximum wall-clock time for each VERIFY.md command before it is stopped.",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Do not commit successful improving iterations.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Do not push successful improving iteration commits.",
    )
    parser.add_argument(
        "--allow-score-stable",
        action="store_true",
        help="Allow commit/push when verification and LLM judge pass and spec score is unchanged.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the prompt without launching Codex.")
    return parser.parse_args()


def read_overrides(repo: Path) -> str:
    """Read docs/loop-overrides.md if present. Returns the file's text or ''."""
    path = repo / OVERRIDES_PATH.relative_to(ROOT)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Warning: could not read {path}: {exc}")
        return ""


def overrides_paused(overrides_text: str) -> bool:
    """True if a PAUSE token sits on its own line under the Pause section.

    We look for a line whose stripped, uncommented content equals PAUSE.
    Lines inside HTML comments are ignored so the template's example doesn't trigger.
    """
    if not overrides_text:
        return False
    in_comment = False
    for raw in overrides_text.splitlines():
        line = raw.strip()
        if "<!--" in line and "-->" not in line:
            in_comment = True
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if line == PAUSE_TOKEN:
            return True
    return False


def build_prompt(
    repo: Path,
    iteration: int,
    max_iterations: int,
    eval_state: dict | None = None,
    overrides_text: str = "",
) -> str:
    eval_summary = format_eval_for_prompt(eval_state)
    overrides_block = format_overrides_for_prompt(overrides_text)
    return textwrap.dedent(
        f"""
        You are Codex running inside an LLM-evaluator-driven improvement loop.

        Repository: {repo}
        Iteration: {iteration} of {max_iterations}

        The publish gate is `scripts/evaluate_platform.py` graded against
        `docs/eval-rubric.md`. The deterministic `check_spec_conformance.py` is
        advisory only — do not target it directly.

        Treat these files as persistent memory:
        - PLAN.md
        - VERIFY.md
        - PROGRESS.md
        - docs/eval-rubric.md  (THE GATE)
        - docs/spec-gap-backlog.md
        - docs/dictionary-coverage-matrix.md
        - site/api/platform-evaluation.json  (latest LLM verdict)
        - site/api/spec-conformance.json     (advisory only)

        Current evaluator state (from before this iteration):
        {eval_summary}

        Human overrides from `docs/loop-overrides.md` (AUTHORITATIVE — these supersede
        rubric defaults and any earlier decision when in conflict):
        {overrides_block}

        Loop protocol for this iteration:
        1. Read PLAN.md, VERIFY.md, PROGRESS.md, the rubric, and the latest evaluator report.
        2. Pick ONE rubric item that is `fail` or `partial`. Prefer the highest-leverage
           item you can fully move to `pass` in this iteration. Read the item's
           `requirement`, `how_to_verify`, and `substance_check` carefully — these are
           what the evaluator will grade against.
        3. Make exactly one focused improvement that targets that rubric item.
        4. Touch only files needed for that improvement.
        5. Run relevant local checks as you work. The harness will run VERIFY.md and
           the evaluator after you finish.
        6. Append an entry to PROGRESS.md with:
           - timestamp
           - chosen rubric item id
           - files changed
           - checks run and result
           - expected status change (e.g., `fail` -> `pass`)
           - what remains next
        7. If you discover a missing requirement not in the rubric, add it to the
           rubric file under the right category (with id, requirement, how_to_verify,
           substance_check, blocked_if) AND log it in docs/spec-gap-backlog.md.
        8. Finish with one of these exact markers:
           - LOOP_STATUS: CONTINUE
           - LOOP_STATUS: COMPLETE (only if you believe every rubric item is `pass` or `blocked`)

        Constraints:
        - Do not push manually; the harness owns commit/push after successful improving iterations.
        - Do not delete or revert user work.
        - If the tree is dirty, work with the existing changes.
        - Keep generated artifacts in sync with their structured dictionary sources.
        - Do not do broad refactors or unrelated cleanup.
        - Prefer the rubric item with the highest leverage that you can fully fix in one iteration. Lead with `fail` items over `partial` items unless a `partial` is one small change away from `pass`.
        - Do NOT edit `scripts/check_spec_conformance.py` to make a check pass. The deterministic gate is advisory; the evaluator is the gate.
        - Always honor `docs/loop-overrides.md` over your own judgment when they conflict. Do not edit that file yourself — it is the human-to-loop channel.
        """
    ).strip() + "\n"


def run_codex(
    args: argparse.Namespace,
    repo: Path,
    prompt: str,
    log_path: Path,
    last_message: Path,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        args.codex_bin,
        "exec",
        "-C",
        str(repo),
        "--sandbox",
        args.sandbox,
        "-c",
        f'approval_policy="{args.approval}"',
        "--output-last-message",
        str(last_message),
        "-",
    ]
    if args.model:
        cmd.extend(["--model", args.model])

    with log_path.open("w") as log:
        log.write("$ " + " ".join(shlex.quote(part) for part in cmd) + "\n\n")
        log.flush()
        result = run_process(
            cmd,
            input=prompt,
            cwd=repo,
            timeout_seconds=int(args.codex_timeout_minutes * 60),
        )
        log.write(result.stdout)
    print(result.stdout[-4000:])
    return result


def run_verify(
    repo: Path,
    log_path: Path,
    command_timeout_minutes: float = 15,
) -> subprocess.CompletedProcess[str]:
    commands = read_verify_commands()
    output_parts = []
    return_code = 0
    for command in commands:
        header = f"\n$ {command}\n"
        print(header, end="")
        output_parts.append(header)
        result = run_process(
            command,
            shell=True,
            cwd=repo,
            executable="/bin/zsh",
            timeout_seconds=int(command_timeout_minutes * 60),
        )
        print(result.stdout[-4000:])
        output_parts.append(result.stdout)
        if result.returncode != 0:
            return_code = result.returncode
            break
    log_path.write_text("".join(output_parts))
    return subprocess.CompletedProcess(commands, return_code, stdout="".join(output_parts), stderr=None)


def run_process(
    command: list[str] | str,
    *,
    cwd: Path,
    timeout_seconds: int,
    input: str | None = None,
    shell: bool = False,
    executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdin=subprocess.PIPE if input is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=shell,
        executable=executable,
        start_new_session=True,
    )
    try:
        stdout, _ = proc.communicate(input=input, timeout=timeout_seconds)
        return subprocess.CompletedProcess(command, proc.returncode, stdout=stdout or "", stderr=None)
    except subprocess.TimeoutExpired as exc:
        timeout_note = f"\nTIMEOUT: command exceeded {timeout_seconds} seconds and was stopped.\n"
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            stdout, _ = proc.communicate(timeout=5)
        except Exception:  # noqa: BLE001 - escalate to SIGKILL if graceful stop fails.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, _ = proc.communicate()
        partial = exc.output or ""
        return subprocess.CompletedProcess(
            command,
            124,
            stdout=(partial or "") + (stdout or "") + timeout_note,
            stderr=None,
        )


def read_verify_commands() -> list[str]:
    text = VERIFY.read_text()
    commands = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if not in_block or not stripped or stripped.startswith("#"):
            continue
        commands.append(stripped)
    return commands


def append_machine_progress(
    iteration: int,
    codex_result: subprocess.CompletedProcess[str],
    verify_result: subprocess.CompletedProcess[str],
    codex_log: Path,
    verify_log: Path,
    judge_log: Path,
    judge_json: Path,
    before_score: float,
    after_score: float,
    judge_result: dict,
    publish_result: str,
) -> None:
    status = "pass" if codex_result.returncode == 0 and verify_result.returncode == 0 else "fail"
    entry = textwrap.dedent(
        f"""

        ## {timestamp()} Harness Iteration {iteration}

        - Harness status: {status}
        - Codex exit code: {codex_result.returncode}
        - Verify exit code: {verify_result.returncode}
        - Spec score before: {before_score:.2f}
        - Spec score after: {after_score:.2f}
        - LLM judge ok: {judge_result.get("ok")}
        - LLM judge recommendation: {judge_result.get("publish_recommendation")}
        - LLM judge score: {judge_result.get("score")}
        - Publish result: {publish_result}
        - Codex log: `{codex_log.relative_to(ROOT)}`
        - Verify log: `{verify_log.relative_to(ROOT)}`
        - Judge log: `{judge_log.relative_to(ROOT)}`
        - Judge JSON: `{judge_json.relative_to(ROOT)}`
        """
    )
    with PROGRESS.open("a") as handle:
        handle.write(entry)


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def run_evaluator(repo: Path, args: argparse.Namespace, label: str) -> dict | None:
    """Run scripts/evaluate_platform.py and return the parsed JSON, or None on failure."""
    cmd = [
        "python3",
        "scripts/evaluate_platform.py",
        "--model",
        args.evaluator_model,
        "--thinking-budget",
        str(args.evaluator_thinking_budget),
        "--max-tokens",
        str(args.evaluator_max_tokens),
        "--api-profile",
        args.judge_api_profile,
        "--api-key-env",
        args.judge_api_key_env,
    ]
    print(f"[evaluator/{label}] running: {' '.join(shlex.quote(c) for c in cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=900,
            check=False,
        )
    except subprocess.SubprocessError as e:
        print(f"[evaluator/{label}] subprocess error: {e}")
        return None
    if result.returncode != 0:
        print(f"[evaluator/{label}] failed (exit {result.returncode}):\n{result.stdout[-2000:]}")
    target = repo / "site" / "api" / "platform-evaluation.json"
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"[evaluator/{label}] could not read evaluation JSON: {e}")
        return None


def rubric_progressed(before: dict, after: dict) -> bool:
    """True if any rubric item moved toward `pass` between two evaluations.

    Rules:
      - More `pass` items than before -> progress.
      - Same `pass` count but more `partial` (and fewer `fail`) -> progress.
      - Otherwise -> no progress.
    """
    bc = before.get("counts", {})
    ac = after.get("counts", {})
    if ac.get("pass", 0) > bc.get("pass", 0):
        return True
    if (
        ac.get("pass", 0) == bc.get("pass", 0)
        and ac.get("fail", 0) < bc.get("fail", 0)
        and ac.get("partial", 0) >= bc.get("partial", 0)
    ):
        return True
    return False


def format_eval_for_prompt(eval_state: dict | None) -> str:
    if not eval_state:
        return "(no prior evaluator report — first iteration or evaluator failed)"
    counts = eval_state.get("counts", {})
    lines = [
        f"- counts: pass={counts.get('pass', 0)} partial={counts.get('partial', 0)} "
        f"fail={counts.get('fail', 0)} blocked={counts.get('blocked', 0)} total={counts.get('total', 0)}",
        f"- done: {eval_state.get('done', False)}",
        "- non-pass items:",
    ]
    for item in eval_state.get("items", []):
        if item.get("status") != "pass":
            reason = (item.get("reason") or "").replace("\n", " ")[:200]
            lines.append(f"    - [{item.get('status')}] {item.get('id')}: {reason}")
    return "\n        ".join(lines)


def format_overrides_for_prompt(overrides_text: str) -> str:
    """Render the overrides file into the iteration prompt.

    Strips HTML comments so the inline instructions in the template don't pollute
    the prompt. If nothing meaningful is left, returns a short placeholder.
    """
    if not overrides_text:
        return "(no overrides file present)"
    cleaned_lines: list[str] = []
    in_comment = False
    for raw in overrides_text.splitlines():
        line = raw
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
            else:
                continue
        while "<!--" in line:
            before, _, rest = line.partition("<!--")
            if "-->" in rest:
                _, _, after = rest.partition("-->")
                line = before + after
            else:
                line = before
                in_comment = True
                break
        cleaned_lines.append(line.rstrip())
    cleaned = "\n".join(cleaned_lines).strip()
    if not cleaned:
        return "(overrides file present but empty)"
    # Indent so it nests cleanly inside the dedented prompt block.
    return "\n        ".join(cleaned.splitlines())


def spec_score(repo: Path) -> float:
    result = subprocess.run(
        ["python3", "scripts/check_spec_conformance.py", "--score-only"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        print(result.stdout[-2000:])
        return 0.0
    try:
        return float(result.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return 0.0


def maybe_publish(
    args: argparse.Namespace,
    repo: Path,
    iteration: int,
    before_score: float,
    after_score: float,
    codex_returncode: int,
    verify_returncode: int,
    judge_result: dict,
    before_eval: dict | None,
    after_eval: dict | None,
) -> str:
    if codex_returncode != 0:
        return f"skipped: Codex failed ({codex_returncode})"
    if verify_returncode != 0:
        return f"skipped: VERIFY failed ({verify_returncode})"
    if not judge_result.get("ok"):
        return f"skipped: LLM judge failed ({judge_result.get('reason', 'no reason')})"
    if judge_result.get("publish_recommendation") != "push":
        return f"skipped: LLM judge recommended {judge_result.get('publish_recommendation')}"
    if judge_result.get("regressed"):
        return "skipped: LLM judge found a regression"
    diff_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if not diff_result.stdout.strip():
        return "skipped: no git changes"

    # NEW GATE: rubric must have progressed, OR the iteration produced the
    # final `done` state (an iteration that fixes the last item shows progress
    # AND `done`). Falls back to the old advisory-score gate only if the
    # evaluator failed to run on either side.
    rubric_progress: bool | None
    if before_eval is None or after_eval is None:
        rubric_progress = None
    else:
        rubric_progress = rubric_progressed(before_eval, after_eval) or after_eval.get("done", False)

    if rubric_progress is False:
        return "skipped: rubric did not progress this iteration"
    if rubric_progress is None:
        improved = after_score > before_score
        stable_allowed = args.allow_score_stable and after_score == before_score
        if not improved and not stable_allowed:
            return (
                "skipped: evaluator unavailable and advisory score did not improve "
                f"({before_score:.2f} -> {after_score:.2f})"
            )

    if args.no_commit:
        return "skipped: --no-commit"

    run_git(repo, ["add", "-A"])
    if rubric_progress:
        ac = (after_eval or {}).get("counts", {})
        commit_message = (
            f"Codex loop iteration {iteration}: rubric "
            f"pass={ac.get('pass', 0)}/{ac.get('total', 0)}"
        )
    else:
        improved = after_score > before_score
        commit_message = (
            f"Codex loop iteration {iteration}: improve advisory score to {after_score:.2f}"
            if improved
            else f"Codex loop iteration {iteration}: preserve advisory score {after_score:.2f}"
        )
    commit = run_git(repo, ["commit", "-m", commit_message], check=False)
    if commit.returncode != 0:
        return f"commit failed: {commit.stdout.strip()[-500:]}"
    if args.no_push:
        return f"committed, push skipped: {commit_message}"
    # Fetch + rebase before push so that manual PRs landing on remote during a
    # run do not silently strand subsequent iterations on local main.
    fetch = run_git(repo, ["fetch", "origin", "main"], check=False)
    if fetch.returncode != 0:
        return f"commit succeeded, fetch failed: {fetch.stdout.strip()[-500:]}"
    rebase = run_git(repo, ["pull", "--rebase", "origin", "main"], check=False)
    if rebase.returncode != 0:
        # Rebase conflict — abort and signal divergence to the harness so the
        # next iteration does not run against an inconsistent local main.
        diff = run_git(repo, ["diff", "--name-only", "--diff-filter=U"], check=False)
        conflict_paths = [line.strip() for line in (diff.stdout or "").splitlines() if line.strip()]
        if not conflict_paths:
            status = run_git(repo, ["status", "--porcelain"], check=False)
            for line in (status.stdout or "").splitlines():
                if line.startswith("UU ") or line.startswith("AA "):
                    conflict_paths.append(line[3:])
        paths_str = ", ".join(conflict_paths) if conflict_paths else "unknown"
        run_git(repo, ["rebase", "--abort"], check=False)
        return (
            f"DIVERGENCE: commit succeeded, rebase failed. "
            f"Conflicting paths: {paths_str}. "
            "Recommended resolution: `git fetch origin main && "
            "git pull --rebase origin main`, resolve conflicts, then "
            "`git push origin main`. "
            "Loop halting until a human resolves divergence on origin/main."
        )
    push = run_git(repo, ["push", "origin", "main"], check=False)
    if push.returncode != 0:
        return f"commit succeeded, push failed: {push.stdout.strip()[-500:]}"
    return f"committed and pushed: {commit_message}"


def maybe_run_llm_judge(
    args: argparse.Namespace,
    repo: Path,
    iteration: int,
    before_score: float,
    after_score: float,
    codex_log: Path,
    verify_log: Path,
    judge_log: Path,
    judge_json: Path,
    verify_ready: bool,
) -> dict:
    if args.skip_llm_judge:
        return {
            "ok": True,
            "score": after_score,
            "improved": after_score > before_score,
            "regressed": after_score < before_score,
            "publish_recommendation": "push" if after_score >= before_score else "do_not_push",
            "reason": "LLM judge skipped by --skip-llm-judge.",
        }
    if not verify_ready:
        return {
            "ok": False,
            "score": after_score,
            "improved": False,
            "regressed": after_score < before_score,
            "publish_recommendation": "do_not_push",
            "reason": "Codex or VERIFY failed, so LLM judge was not run.",
        }

    schema = LOG_DIR / "judge-output.schema.json"
    schema_text = judge_schema()
    schema.write_text(schema_text)
    prompt = build_judge_prompt(repo, iteration, before_score, after_score, codex_log, verify_log)

    if args.judge_provider == "anthropic-api":
        return run_anthropic_api_judge(args, repo, prompt, schema_text, judge_log, judge_json, after_score)

    cmd = [
        args.codex_bin,
        "exec",
        "-C",
        str(repo),
        "--sandbox",
        "read-only",
        "-c",
        'approval_policy="never"',
        "--model",
        args.judge_model,
        "-c",
        f'model_reasoning_effort="{args.judge_reasoning_effort}"',
        "--output-schema",
        str(schema),
        "--output-last-message",
        str(judge_json),
        "-",
    ]
    with judge_log.open("w") as log:
        log.write("$ " + " ".join(shlex.quote(part) for part in cmd) + "\n\n")
        log.flush()
        result = subprocess.run(
            cmd,
            input=prompt,
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        log.write(result.stdout)
    if result.returncode != 0:
        return {
            "ok": False,
            "score": after_score,
            "improved": False,
            "regressed": True,
            "publish_recommendation": "do_not_push",
            "reason": f"LLM judge command failed with {result.returncode}. See {judge_log.relative_to(ROOT)}.",
        }
    try:
        parsed = parse_json(judge_json.read_text())
    except Exception as exc:  # noqa: BLE001 - report parse failure to the harness.
        return {
            "ok": False,
            "score": after_score,
            "improved": False,
            "regressed": True,
            "publish_recommendation": "do_not_push",
            "reason": f"LLM judge JSON parse failed: {exc}",
        }
    parsed["ok"] = True
    parsed["provider"] = "codex-exec"
    parsed["model"] = args.judge_model
    return parsed


def run_anthropic_api_judge(
    args: argparse.Namespace,
    repo: Path,
    prompt: str,
    schema_text: str,
    judge_log: Path,
    judge_json: Path,
    after_score: float,
) -> dict:
    env = load_profile_env(args.judge_api_profile)
    env = {**os.environ, **env}
    api_key = env.get(args.judge_api_key_env)
    if not api_key:
        return {
            "ok": False,
            "score": after_score,
            "improved": False,
            "regressed": True,
            "publish_recommendation": "do_not_push",
            "reason": f"{args.judge_api_key_env} was not found after sourcing {args.judge_api_profile}.",
        }

    requested_model = args.judge_model
    log_lines = [
        "$ anthropic.messages.create "
        f"--model {shlex.quote(requested_model)} "
        f"--effort {shlex.quote(args.judge_reasoning_effort)} "
        f"--profile {shlex.quote(args.judge_api_profile)} "
        f"--key-env {shlex.quote(args.judge_api_key_env)}\n\n"
    ]
    model = resolve_anthropic_model(requested_model, api_key, args.judge_api_version, log_lines)
    thinking = judge_thinking_config(args, model)
    budget = thinking.get("budget_tokens", 0)
    max_tokens = max(args.judge_max_tokens, budget + 1024 if budget else args.judge_max_tokens)
    schema = json.loads(schema_text)
    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [
            {
                "name": "record_iteration_judgment",
                "description": "Record whether this Codex iteration genuinely improves spec conformance.",
                "input_schema": schema,
            }
        ],
    }
    if thinking["type"] == "adaptive":
        payload["thinking"] = {"type": "adaptive"}
        payload["output_config"] = {"effort": thinking["effort"]}
    elif thinking["type"] == "enabled":
        payload["thinking"] = {"type": "enabled", "budget_tokens": budget}
    if thinking["type"] == "off":
        payload["tool_choice"] = {"type": "tool", "name": "record_iteration_judgment"}

    try:
        raw_response = anthropic_request(
            ANTHROPIC_MESSAGES_URL,
            api_key,
            args.judge_api_version,
            method="POST",
            payload=payload,
        )
        log_lines.append(raw_response + "\n")
        data = json.loads(raw_response)
        parsed = parse_anthropic_tool_response(data)
    except Exception as exc:  # noqa: BLE001 - keep the loop gate closed on any API failure.
        log_lines.append(f"\nERROR: {exc}\n")
        judge_log.write_text("".join(log_lines))
        return {
            "ok": False,
            "score": after_score,
            "improved": False,
            "regressed": True,
            "publish_recommendation": "do_not_push",
            "reason": f"Anthropic API judge failed: {exc}. See {judge_log.relative_to(ROOT)}.",
        }

    judge_json.write_text(json.dumps(parsed, indent=2) + "\n")
    judge_log.write_text("".join(log_lines))
    parsed["ok"] = True
    parsed["provider"] = "anthropic-api"
    parsed["model"] = model
    parsed["requested_model"] = requested_model
    parsed["reasoning_effort"] = args.judge_reasoning_effort
    parsed["thinking"] = thinking
    return parsed


def load_profile_env(profile: str) -> dict[str, str]:
    profile_path = Path(profile).expanduser()
    if not profile_path.exists():
        return {}
    command = f"source {shlex.quote(str(profile_path))} >/dev/null 2>&1; /usr/bin/env -0"
    result = subprocess.run(
        ["/bin/zsh", "-lc", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return {}
    env: dict[str, str] = {}
    for item in result.stdout.split(b"\0"):
        if not item or b"=" not in item:
            continue
        key, value = item.split(b"=", 1)
        env[key.decode()] = value.decode(errors="replace")
    return env


def resolve_anthropic_model(
    requested_model: str,
    api_key: str,
    api_version: str,
    log_lines: list[str],
) -> str:
    try:
        raw = anthropic_request(ANTHROPIC_MODELS_URL, api_key, api_version, method="GET")
        data = json.loads(raw).get("data", [])
    except Exception as exc:  # noqa: BLE001 - model listing is best-effort.
        log_lines.append(f"Model list unavailable; using requested model directly. Error: {exc}\n")
        return requested_model

    models = [
        {
            "id": str(item.get("id", "")),
            "created_at": str(item.get("created_at", "")),
            "display_name": str(item.get("display_name", "")),
        }
        for item in data
        if item.get("id")
    ]
    ids = {item["id"] for item in models}
    if requested_model in ids:
        log_lines.append(f"Resolved judge model: {requested_model}\n")
        return requested_model

    normalized = requested_model.lower().replace(".", "-")
    candidates = [item for item in models if "opus" in item["id"].lower()]
    if "4-7" in normalized:
        candidates_47 = [
            item
            for item in candidates
            if "4-7" in item["id"].lower() or "4.7" in item["id"].lower()
        ]
        if candidates_47:
            chosen = latest_model_id(candidates_47)
            log_lines.append(f"Resolved judge model alias {requested_model} -> {chosen}\n")
            return chosen

    if requested_model.lower() in {"opus", "claude-opus"} and candidates:
        chosen = latest_model_id(candidates)
        log_lines.append(f"Resolved judge model alias {requested_model} -> {chosen}\n")
        return chosen

    available = ", ".join(item["id"] for item in candidates[:10]) or "no Opus models returned"
    log_lines.append(
        f"Could not resolve {requested_model}; using it directly. Available Opus candidates: {available}\n"
    )
    return requested_model


def latest_model_id(models: list[dict[str, str]]) -> str:
    return sorted(models, key=lambda item: (item.get("created_at", ""), item["id"]), reverse=True)[0]["id"]


def anthropic_request(
    url: str,
    api_key: str,
    api_version: str,
    *,
    method: str,
    payload: dict | None = None,
) -> str:
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "anthropic-version": api_version,
            "x-api-key": api_key,
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read().decode()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc


def parse_anthropic_tool_response(data: dict) -> dict:
    text_blocks = []
    for block in data.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "record_iteration_judgment":
            tool_input = block.get("input")
            if isinstance(tool_input, dict):
                return tool_input
            if isinstance(tool_input, str):
                return parse_json(tool_input)
        if block.get("type") == "text":
            text_blocks.append(block.get("text", ""))
    if text_blocks:
        return parse_json("\n".join(text_blocks))
    raise ValueError("Anthropic response did not include the expected tool call or JSON text.")


def judge_thinking_config(args: argparse.Namespace, model: str) -> dict:
    effort = (args.judge_reasoning_effort or "").lower()
    if effort in {"", "none", "off", "disabled"}:
        return {"type": "off"}
    if "4-7" in model or "4.7" in model:
        return {"type": "adaptive", "effort": effort}
    if args.judge_thinking_budget:
        return {"type": "enabled", "budget_tokens": int(args.judge_thinking_budget)}
    budgets = {
        "low": 1024,
        "medium": 2048,
        "high": 4096,
        "xhigh": 8192,
        "max": 16000,
    }
    return {"type": "enabled", "budget_tokens": budgets.get(effort, 8192)}


def build_judge_prompt(
    repo: Path,
    iteration: int,
    before_score: float,
    after_score: float,
    codex_log: Path,
    verify_log: Path,
) -> str:
    return textwrap.dedent(
        f"""
        You are an independent LLM judge for an unattended Codex improvement loop.

        Use xhigh reasoning internally. Return only JSON that matches the provided schema.
        Do not modify files.

        Repository: {repo}
        Iteration: {iteration}
        Deterministic spec score before: {before_score:.2f}
        Deterministic spec score after: {after_score:.2f}

        Evidence is embedded below because the API judge has no repository tools.

        Judge whether this iteration is a real improvement toward meeting the
        spirit and letter of the platform spec, not merely a syntactic change.

        Publishing rules:
        - Recommend "push" only if deterministic verification passed, there is no regression,
          newly discovered gaps are tracked in repo memory, and the diff is a focused improvement.
        - Recommend "do_not_push" if the change is incomplete, misleading, untracked, broad,
          regressive, or only improves a superficial metric.
        - If the deterministic score did not improve, recommend "push" only when the change is
          clearly necessary groundwork and no regression exists.

        Return JSON with:
        - score: integer 0-100
        - improved: boolean
        - regressed: boolean
        - publish_recommendation: "push" or "do_not_push"
        - missing_requirements: array of strings
        - new_backlog_items: array of strings that should be tracked if not already tracked
        - regressions: array of strings
        - reason: concise string

        If the API offers a tool named `record_iteration_judgment`, use it.
        If extended thinking prevents forced tool use, put the final judgment as
        one valid JSON object in the final text response and nothing else.

        {judge_evidence(repo, codex_log, verify_log)}
        """
    ).strip() + "\n"


def judge_evidence(repo: Path, codex_log: Path, verify_log: Path) -> str:
    spec = Path("/Users/andymontgomery/Downloads/WF - Platform - 260424-144348.md")
    parts = [
        evidence_block("SPEC", read_limited(spec, 20000)),
        evidence_block("PLAN.md", read_limited(repo / "PLAN.md", 12000)),
        evidence_block("VERIFY.md", read_limited(repo / "VERIFY.md", 12000)),
        evidence_block("PROGRESS.md", read_limited(repo / "PROGRESS.md", 20000)),
        evidence_block("docs/spec-gap-backlog.md", read_limited(repo / "docs/spec-gap-backlog.md", 20000)),
        evidence_block(
            "docs/dictionary-coverage-matrix.md",
            read_limited(repo / "docs/dictionary-coverage-matrix.md", 16000),
        ),
        evidence_block("site/api/spec-conformance.json", read_limited(repo / "site/api/spec-conformance.json", 20000)),
        evidence_block("git status --short", git_output(repo, ["status", "--short"], 12000)),
        evidence_block("git diff --stat", git_output(repo, ["diff", "--stat"], 12000)),
        evidence_block("git diff", git_output(repo, ["diff"], 60000)),
        evidence_block(str(codex_log.relative_to(ROOT)), read_limited(codex_log, 24000)),
        evidence_block(str(verify_log.relative_to(ROOT)), read_limited(verify_log, 24000)),
    ]
    return "\n\n".join(parts)


def evidence_block(label: str, text: str) -> str:
    return f"<evidence label={json.dumps(label)}>\n{text}\n</evidence>"


def read_limited(path: Path, limit: int) -> str:
    if not path.exists():
        return "[missing]"
    text = path.read_text(errors="ignore")
    if len(text) <= limit:
        return text
    keep_head = limit // 2
    keep_tail = limit - keep_head
    return text[:keep_head] + f"\n...[truncated {len(text) - limit} chars]...\n" + text[-keep_tail:]


def git_output(repo: Path, args: list[str], limit: int) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    text = result.stdout
    if len(text) <= limit:
        return text
    return text[: limit // 2] + f"\n...[truncated {len(text) - limit} chars]...\n" + text[-(limit // 2) :]


def judge_schema() -> str:
    return """
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "score",
    "improved",
    "regressed",
    "publish_recommendation",
    "missing_requirements",
    "new_backlog_items",
    "regressions",
    "reason"
  ],
  "properties": {
    "score": {"type": "integer", "minimum": 0, "maximum": 100},
    "improved": {"type": "boolean"},
    "regressed": {"type": "boolean"},
    "publish_recommendation": {"type": "string", "enum": ["push", "do_not_push"]},
    "missing_requirements": {"type": "array", "items": {"type": "string"}},
    "new_backlog_items": {"type": "array", "items": {"type": "string"}},
    "regressions": {"type": "array", "items": {"type": "string"}},
    "reason": {"type": "string"}
  }
}
"""


def parse_json(text: str) -> dict:
    import json

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    return json.loads(stripped)


def run_git(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
