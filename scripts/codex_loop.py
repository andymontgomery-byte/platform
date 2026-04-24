#!/usr/bin/env python3
"""Run Codex in a small eval-driven improvement loop for this repository."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shlex
import subprocess
import sys
import textwrap
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "PLAN.md"
VERIFY = ROOT / "VERIFY.md"
PROGRESS = ROOT / "PROGRESS.md"
LOG_DIR = ROOT / ".codex-loop"


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    LOG_DIR.mkdir(exist_ok=True)

    if args.dry_run:
        print(build_prompt(repo, 1, args.max_iterations))
        return 0

    for iteration in range(1, args.max_iterations + 1):
        started = timestamp()
        print(f"\n=== Codex loop iteration {iteration}/{args.max_iterations} at {started} ===")
        prompt = build_prompt(repo, iteration, args.max_iterations)
        prompt_file = LOG_DIR / f"{started}-iteration-{iteration:03d}-prompt.md"
        codex_log = LOG_DIR / f"{started}-iteration-{iteration:03d}-codex.log"
        verify_log = LOG_DIR / f"{started}-iteration-{iteration:03d}-verify.log"
        last_message = LOG_DIR / "last-message.md"
        prompt_file.write_text(prompt)

        codex_result = run_codex(args, repo, prompt, codex_log, last_message)
        verify_result = run_verify(repo, verify_log)
        append_machine_progress(iteration, codex_result, verify_result, codex_log, verify_log)

        if codex_result.returncode != 0:
            print(f"Codex exited with {codex_result.returncode}; see {codex_log}")
            if not args.continue_on_failure:
                return codex_result.returncode

        if verify_result.returncode != 0:
            print(f"Verify exited with {verify_result.returncode}; see {verify_log}")
            if not args.continue_on_failure:
                return verify_result.returncode

        final_text = last_message.read_text() if last_message.exists() else ""
        if "LOOP_STATUS: COMPLETE" in final_text:
            print("Codex reported LOOP_STATUS: COMPLETE.")
            return 0

        if iteration < args.max_iterations and args.interval_minutes > 0:
            seconds = args.interval_minutes * 60
            print(f"Sleeping {args.interval_minutes} minute(s) before next iteration...")
            time.sleep(seconds)

    print("Reached max iterations.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch Codex repeatedly in this repo with PLAN/VERIFY/PROGRESS memory."
    )
    parser.add_argument("--repo", default=str(ROOT), help="Repository directory. Defaults to this repo.")
    parser.add_argument("--max-iterations", type=int, default=1, help="Number of Codex iterations to run.")
    parser.add_argument("--interval-minutes", type=float, default=0, help="Delay between iterations.")
    parser.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"), help="Codex executable.")
    parser.add_argument("--model", default=os.environ.get("CODEX_MODEL"), help="Optional Codex model.")
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
    parser.add_argument("--dry-run", action="store_true", help="Print the prompt without launching Codex.")
    return parser.parse_args()


def build_prompt(repo: Path, iteration: int, max_iterations: int) -> str:
    return textwrap.dedent(
        f"""
        You are Codex running inside an eval-driven improvement loop.

        Repository: {repo}
        Iteration: {iteration} of {max_iterations}

        Treat these files as persistent memory:
        - PLAN.md
        - VERIFY.md
        - PROGRESS.md
        - docs/spec-gap-backlog.md
        - docs/dictionary-coverage-matrix.md

        Loop protocol for this iteration:
        1. Read PLAN.md, VERIFY.md, PROGRESS.md, and the backlog/coverage docs.
        2. Identify the single easiest high-value unmet checklist item.
        3. Make exactly one focused improvement toward meeting the platform spec.
        4. Touch only files needed for that improvement.
        5. Run relevant local checks as you work. The harness will run VERIFY.md after you finish.
        6. Append an entry to PROGRESS.md with:
           - timestamp
           - chosen checklist item
           - files changed
           - checks run and result
           - what remains next
        7. Finish with one of these exact markers:
           - LOOP_STATUS: CONTINUE
           - LOOP_STATUS: COMPLETE

        Constraints:
        - Do not push to GitHub.
        - Do not delete or revert user work.
        - If the tree is dirty, work with the existing changes.
        - Keep generated artifacts in sync with their structured dictionary sources.
        - Do not do broad refactors or unrelated cleanup.
        - Prefer the easiest open backlog item first.
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
        "--ask-for-approval",
        args.approval,
        "--output-last-message",
        str(last_message),
        "-",
    ]
    if args.model:
        cmd.extend(["--model", args.model])

    with log_path.open("w") as log:
        log.write("$ " + " ".join(shlex.quote(part) for part in cmd) + "\n\n")
        log.flush()
        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        log.write(result.stdout)
    print(result.stdout[-4000:])
    return result


def run_verify(repo: Path, log_path: Path) -> subprocess.CompletedProcess[str]:
    commands = read_verify_commands()
    output_parts = []
    return_code = 0
    for command in commands:
        header = f"\n$ {command}\n"
        print(header, end="")
        output_parts.append(header)
        result = subprocess.run(
            command,
            shell=True,
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            executable="/bin/zsh",
        )
        print(result.stdout[-4000:])
        output_parts.append(result.stdout)
        if result.returncode != 0:
            return_code = result.returncode
            break
    log_path.write_text("".join(output_parts))
    return subprocess.CompletedProcess(commands, return_code, stdout="".join(output_parts), stderr=None)


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
) -> None:
    status = "pass" if codex_result.returncode == 0 and verify_result.returncode == 0 else "fail"
    entry = textwrap.dedent(
        f"""

        ## {timestamp()} Harness Iteration {iteration}

        - Harness status: {status}
        - Codex exit code: {codex_result.returncode}
        - Verify exit code: {verify_result.returncode}
        - Codex log: `{codex_log.relative_to(ROOT)}`
        - Verify log: `{verify_log.relative_to(ROOT)}`
        """
    )
    with PROGRESS.open("a") as handle:
        handle.write(entry)


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
