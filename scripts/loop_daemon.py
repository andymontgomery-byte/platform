#!/usr/bin/env python3
"""
loop_daemon.py - GitHub-issue-driven daemon for the Codex loop.

Polls a designated GitHub control issue every POLL_INTERVAL seconds,
reads new comments from allowed authors, executes whitelisted commands,
and posts results back as issue comments.
"""

from __future__ import annotations

import fnmatch
import glob
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants / config defaults
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".loop-daemon.config.json"
STATE_PATH = ROOT / ".loop-daemon.state.json"
LOG_PATH = ROOT / ".loop-daemon.log"
EVAL_REPORT = ROOT / "site" / "api" / "platform-evaluation.json"
LOG_DIR = ROOT / ".codex-loop"

REPO_SLUG = "andymontgomery-byte/platform"
POLL_INTERVAL = 30          # seconds between comment polls
HEARTBEAT_INTERVAL = 300    # seconds between heartbeat comments (5 min)
STREAM_CHUNK = 4096         # bytes per streamed log comment

# Paths the daemon is allowed to discard (checkout --).
DISCARD_WHITELIST_GLOBS = [
    "docs/spec-fidelity-report.md",
    "docs/generated/*.md",
    "dictionary/*.v1.json",
    "openapi/generated/*.json",
    "site/**",
]

CONTROL_ISSUE_TITLE = "Loop control [DO NOT CLOSE]"
CONTROL_ISSUE_BODY = """\
This issue is the control channel for the GitHub-issue-driven loop daemon.

Protocol
--------
Post a comment containing a fenced code block tagged `loop-cmd` with a JSON payload.
Only comments from allowed authors are processed.

Supported commands:

    ```loop-cmd
    {"cmd": "kickoff_loop"}
    ```

    ```loop-cmd
    {"cmd": "halt_loop"}
    ```

    ```loop-cmd
    {"cmd": "git_status"}
    ```

    ```loop-cmd
    {"cmd": "git_rebase_main"}
    ```

    ```loop-cmd
    {"cmd": "discard_paths", "paths": ["docs/spec-fidelity-report.md"]}
    ```

    ```loop-cmd
    {"cmd": "tail_log", "lines": 100}
    ```

    ```loop-cmd
    {"cmd": "ping"}
    ```

The daemon replies with comments tagged `loop-out` or `loop-heartbeat`.
Do not close this issue.
"""

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("loop_daemon")

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2))


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception as exc:
            log.error("Failed to read config: %s", exc)
            sys.exit(1)
    log.error("Config file %s not found", CONFIG_PATH)
    sys.exit(1)

# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def gh_api(
    method: str,
    path: str,
    fields: dict[str, str] | None = None,
    paginate: bool = False,
    retries: int = 5,
) -> Any:
    """
    Call the gh CLI with exponential backoff on 5xx.
    Returns parsed JSON.
    """
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["-X", method]
    if paginate:
        cmd.append("--paginate")
    if fields:
        for k, v in fields.items():
            cmd += ["-f", f"{k}={v}"]
    cmd.append(path)

    delay = 2
    for attempt in range(retries):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            raw = result.stdout.strip()
            if not raw:
                return None
            # --paginate may return multiple JSON arrays; merge them
            if paginate:
                combined: list = []
                for line in raw.splitlines():
                    line = line.strip()
                    if line:
                        parsed = json.loads(line)
                        if isinstance(parsed, list):
                            combined.extend(parsed)
                        else:
                            combined.append(parsed)
                return combined
            return json.loads(raw)
        # Check for 5xx in stderr
        if "5" in result.stderr[:3] or attempt < retries - 1:
            log.warning(
                "gh api %s %s failed (attempt %d/%d): %s",
                method, path, attempt + 1, retries, result.stderr.strip(),
            )
            time.sleep(delay)
            delay = min(delay * 2, 60)
        else:
            break
    log.error("gh api %s %s permanently failed: %s", method, path, result.stderr.strip())
    return None


def post_comment(issue_number: int, body: str) -> int | None:
    """Post a comment; return the new comment id."""
    path = f"repos/{REPO_SLUG}/issues/{issue_number}/comments"
    resp = gh_api("POST", path, fields={"body": body})
    if resp and "id" in resp:
        return resp["id"]
    return None


def list_comments(issue_number: int) -> list[dict]:
    path = f"repos/{REPO_SLUG}/issues/{issue_number}/comments"
    result = gh_api("GET", path, paginate=True)
    if result is None:
        return []
    return result


def create_issue(title: str, body: str) -> int:
    resp = gh_api(
        "POST",
        f"repos/{REPO_SLUG}/issues",
        fields={"title": title, "body": body},
    )
    if resp and "number" in resp:
        return resp["number"]
    raise RuntimeError(f"Failed to create control issue: {resp}")


def get_git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"

# ---------------------------------------------------------------------------
# Control issue bootstrap
# ---------------------------------------------------------------------------

def ensure_control_issue(config: dict, state: dict) -> tuple[int, dict]:
    issue_number = config.get("control_issue")
    if issue_number:
        return issue_number, state

    # Try to read from state
    if "control_issue" in state:
        return state["control_issue"], state

    log.info("No control issue configured. Creating one now.")
    number = create_issue(CONTROL_ISSUE_TITLE, CONTROL_ISSUE_BODY)
    log.info("Created control issue #%d", number)
    state["control_issue"] = number
    save_state(state)

    # Update config file
    config["control_issue"] = number
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    log.info("Updated %s with control_issue=%d", CONFIG_PATH, number)
    return number, state

# ---------------------------------------------------------------------------
# Command parsing
# ---------------------------------------------------------------------------

def extract_loop_cmds(body: str) -> list[dict]:
    """Extract all ```loop-cmd ... ``` fenced blocks and parse as JSON."""
    cmds = []
    lines = body.splitlines()
    inside = False
    buf: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not inside and stripped.startswith("```loop-cmd"):
            inside = True
            buf = []
        elif inside and stripped == "```":
            raw = "\n".join(buf).strip()
            if raw:
                try:
                    cmds.append(json.loads(raw))
                except json.JSONDecodeError as exc:
                    log.warning("Failed to parse loop-cmd JSON: %s | %s", exc, raw)
            inside = False
            buf = []
        elif inside:
            buf.append(line)
    return cmds

# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------

def run_capture(args: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    """Run a command, return (returncode, combined_output)."""
    result = subprocess.run(
        args, capture_output=True, text=True, cwd=cwd,
    )
    combined = result.stdout + result.stderr
    return result.returncode, combined


def stream_subprocess(
    args: list[str],
    issue_number: int,
    cwd: Path = ROOT,
    env: dict | None = None,
) -> tuple[int, list[str]]:
    """
    Run args, stream stdout+stderr to the control issue in STREAM_CHUNK chunks.
    Returns (returncode, all_lines).
    """
    proc_env = os.environ.copy()
    if env:
        proc_env.update(env)

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=cwd,
        env=proc_env,
    )

    all_lines: list[str] = []
    chunk_lines: list[str] = []
    chunk_bytes = 0

    def flush_chunk() -> None:
        nonlocal chunk_lines, chunk_bytes
        if not chunk_lines:
            return
        body = "```loop-out\n" + "".join(chunk_lines) + "```"
        post_comment(issue_number, body)
        chunk_lines = []
        chunk_bytes = 0

    for line in proc.stdout:  # type: ignore[union-attr]
        all_lines.append(line)
        chunk_lines.append(line)
        chunk_bytes += len(line.encode())
        if chunk_bytes >= STREAM_CHUNK:
            flush_chunk()

    flush_chunk()
    proc.wait()
    return proc.returncode, all_lines

# ---------------------------------------------------------------------------
# Command executors
# ---------------------------------------------------------------------------

def cmd_kickoff_loop(issue_number: int, state: dict) -> dict:
    # Check if already running
    running_pid = state.get("running_pid")
    if running_pid and pid_alive(running_pid):
        post_comment(
            issue_number,
            "```loop-out\nLoop is already running (pid %d). Use halt_loop first.\n```" % running_pid,
        )
        return state

    log.info("Starting codex loop subprocess")
    loop_script = ROOT / "scripts" / "codex_loop.py"
    args = [sys.executable, str(loop_script), "--max-iterations", "25", "--stall-limit", "3"]

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=ROOT,
        env=os.environ.copy(),
    )

    state["running_pid"] = proc.pid
    state["last_loop_run"] = time.time()
    save_state(state)

    post_comment(
        issue_number,
        "```loop-out\nStarted codex loop (pid %d).\n```" % proc.pid,
    )

    # Stream in background thread-like fashion (blocking in daemon main loop)
    all_lines: list[str] = []
    chunk_lines: list[str] = []
    chunk_bytes = 0

    def flush_chunk() -> None:
        nonlocal chunk_lines, chunk_bytes
        if not chunk_lines:
            return
        body = "```loop-out\n" + "".join(chunk_lines) + "```"
        post_comment(issue_number, body)
        chunk_lines = []
        chunk_bytes = 0

    for line in proc.stdout:  # type: ignore[union-attr]
        all_lines.append(line)
        chunk_lines.append(line)
        chunk_bytes += len(line.encode())
        if chunk_bytes >= STREAM_CHUNK:
            flush_chunk()

    flush_chunk()
    proc.wait()
    rc = proc.returncode

    last_50 = "".join(all_lines[-50:])
    state["running_pid"] = None
    state["last_loop_exit"] = rc
    save_state(state)

    post_comment(
        issue_number,
        "```loop-out\nLoop finished. Exit code: %d\n\nLast 50 lines:\n%s\n```" % (rc, last_50),
    )
    return state


def cmd_git_status(issue_number: int) -> None:
    _, porcelain = run_capture(["git", "status", "--porcelain"])
    _, ahead = run_capture(["git", "log", "--oneline", "-5", "origin/main..HEAD"])
    _, recent = run_capture(["git", "log", "--oneline", "-5"])
    body = (
        "```loop-out\n"
        "git status --porcelain:\n%s\n"
        "git log origin/main..HEAD (last 5):\n%s\n"
        "git log (last 5):\n%s\n"
        "```"
    ) % (porcelain or "(clean)", ahead or "(none)", recent or "(none)")
    post_comment(issue_number, body)


def cmd_git_rebase_main(issue_number: int) -> None:
    # Stash
    run_capture(["git", "stash", "push", "-u", "-m", "loop-daemon-prerebase"])
    # Fetch
    rc_fetch, out_fetch = run_capture(["git", "fetch", "origin", "main"])
    if rc_fetch != 0:
        post_comment(issue_number, "```loop-out\nFetch failed:\n%s\n```" % out_fetch)
        return
    # Rebase
    rc_rebase, out_rebase = run_capture(["git", "rebase", "origin/main"])
    if rc_rebase != 0:
        # Get conflict paths
        _, conflicts = run_capture(["git", "diff", "--name-only", "--diff-filter=U"])
        post_comment(
            issue_number,
            (
                "```loop-out\nRebase conflict.\n\nConflict paths:\n%s\n\n"
                "Rebase output:\n%s\n\n"
                "Use discard_paths to discard generated files, then retry.\n```"
            ) % (conflicts or "(none)", out_rebase),
        )
        # Abort rebase to leave repo clean
        run_capture(["git", "rebase", "--abort"])
        return
    # Pop stash
    run_capture(["git", "stash", "pop"])
    _, head = run_capture(["git", "log", "--oneline", "-1"])
    post_comment(
        issue_number,
        "```loop-out\nRebase succeeded.\nNew HEAD: %s\n```" % head,
    )


def cmd_discard_paths(issue_number: int, paths: list) -> None:
    if not isinstance(paths, list):
        post_comment(issue_number, '{"error": "paths must be a list"}')
        return

    allowed: list[str] = []
    rejected: list[str] = []
    for p in paths:
        p_str = str(p)
        matched = any(
            fnmatch.fnmatch(p_str, pat) for pat in DISCARD_WHITELIST_GLOBS
        )
        if matched:
            allowed.append(p_str)
        else:
            rejected.append(p_str)

    result_lines = []
    if allowed:
        rc, out = run_capture(["git", "checkout", "--"] + allowed)
        result_lines.append("Discarded: %s" % ", ".join(allowed))
        if out.strip():
            result_lines.append(out.strip())
    if rejected:
        result_lines.append("Refused (not in whitelist): %s" % ", ".join(rejected))

    post_comment(issue_number, "```loop-out\n%s\n```" % "\n".join(result_lines))


def cmd_halt_loop(issue_number: int, state: dict) -> dict:
    pid = state.get("running_pid")
    if not pid:
        post_comment(issue_number, "```loop-out\nNo running loop to halt.\n```")
        return state

    if not pid_alive(pid):
        state["running_pid"] = None
        save_state(state)
        post_comment(issue_number, "```loop-out\nPid %d was already dead. Cleared.\n```" % pid)
        return state

    try:
        os.kill(pid, signal.SIGTERM)
        log.info("Sent SIGTERM to pid %d", pid)
        deadline = time.time() + 30
        while time.time() < deadline:
            if not pid_alive(pid):
                break
            time.sleep(1)
        if pid_alive(pid):
            os.kill(pid, signal.SIGKILL)
            log.info("Sent SIGKILL to pid %d", pid)
    except ProcessLookupError:
        pass

    state["running_pid"] = None
    save_state(state)
    post_comment(issue_number, "```loop-out\nLoop pid %d halted.\n```" % pid)
    return state


def cmd_tail_log(issue_number: int, lines: int = 100) -> None:
    log_files = sorted(
        LOG_DIR.glob("*-iteration-*-*.log"),
        key=lambda p: p.stat().st_mtime,
    ) if LOG_DIR.exists() else []

    if not log_files:
        post_comment(issue_number, "```loop-out\nNo log files found in .codex-loop/\n```")
        return

    newest = log_files[-1]
    all_lines = newest.read_text(errors="replace").splitlines()
    tail = "\n".join(all_lines[-lines:])
    post_comment(
        issue_number,
        "```loop-out\nFile: %s\n\n%s\n```" % (newest.name, tail),
    )


def cmd_ping(issue_number: int, state: dict, start_time: float) -> None:
    head = get_git_head()
    pid = state.get("running_pid")
    last_cmd = state.get("last_cmd", "none")
    last_loop_run = state.get("last_loop_run")
    uptime = int(time.time() - start_time)
    body = (
        "```loop-out\n"
        "ping reply\n"
        "daemon pid: %d\n"
        "uptime_seconds: %d\n"
        "running_loop_pid: %s\n"
        "last_cmd: %s\n"
        "last_loop_run: %s\n"
        "git HEAD: %s\n"
        "```"
    ) % (
        os.getpid(),
        uptime,
        str(pid) if pid else "none",
        last_cmd,
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_loop_run)) if last_loop_run else "never",
        head,
    )
    post_comment(issue_number, body)

# ---------------------------------------------------------------------------
# Heartbeat
# ---------------------------------------------------------------------------

def post_heartbeat(issue_number: int, state: dict, start_time: float) -> None:
    head = get_git_head()
    pid = state.get("running_pid")
    last_cmd = state.get("last_cmd", "none")
    last_loop_run = state.get("last_loop_run")

    eval_counts = ""
    if EVAL_REPORT.exists():
        try:
            data = json.loads(EVAL_REPORT.read_text())
            passed = data.get("passed", "?")
            total = data.get("total", "?")
            eval_counts = "evaluator: %s/%s passed" % (passed, total)
        except Exception:
            eval_counts = "evaluator: (parse error)"

    body = (
        "```loop-heartbeat\n"
        "daemon heartbeat\n"
        "daemon pid: %d\n"
        "uptime_seconds: %d\n"
        "running_loop_pid: %s\n"
        "last_cmd: %s\n"
        "last_loop_run: %s\n"
        "git HEAD: %s\n"
        "%s\n"
        "```"
    ) % (
        os.getpid(),
        int(time.time() - start_time),
        str(pid) if pid else "none",
        last_cmd,
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_loop_run)) if last_loop_run else "never",
        head,
        eval_counts,
    )
    post_comment(issue_number, body)

# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------

def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False

# ---------------------------------------------------------------------------
# Main poll loop
# ---------------------------------------------------------------------------

def process_comment(
    comment: dict,
    issue_number: int,
    allowed_authors: list[str],
    state: dict,
    start_time: float,
) -> dict:
    author = comment.get("user", {}).get("login", "")
    if author not in allowed_authors:
        return state

    body = comment.get("body", "") or ""
    cmds = extract_loop_cmds(body)
    if not cmds:
        return state

    for payload in cmds:
        if not isinstance(payload, dict) or "cmd" not in payload:
            post_comment(issue_number, '{"error": "malformed payload"}')
            continue

        cmd = payload["cmd"]
        log.info("Executing command: %s from author: %s", cmd, author)
        state["last_cmd"] = cmd

        if cmd == "kickoff_loop":
            state = cmd_kickoff_loop(issue_number, state)

        elif cmd == "git_status":
            cmd_git_status(issue_number)

        elif cmd == "git_rebase_main":
            cmd_git_rebase_main(issue_number)

        elif cmd == "discard_paths":
            paths = payload.get("paths", [])
            cmd_discard_paths(issue_number, paths)

        elif cmd == "halt_loop":
            state = cmd_halt_loop(issue_number, state)

        elif cmd == "tail_log":
            lines = int(payload.get("lines", 100))
            cmd_tail_log(issue_number, lines)

        elif cmd == "ping":
            cmd_ping(issue_number, state, start_time)

        else:
            post_comment(issue_number, '{"error": "unknown_cmd", "cmd": "%s"}' % cmd)

        save_state(state)

    return state


def main() -> None:
    log.info("loop_daemon starting (pid=%d)", os.getpid())
    start_time = time.time()

    config = load_config()
    allowed_authors: list[str] = config.get("allowed_authors", [])
    state = load_state()

    issue_number, state = ensure_control_issue(config, state)
    log.info("Using control issue #%d", issue_number)

    # Crash recovery
    running_pid = state.get("running_pid")
    if running_pid and not pid_alive(running_pid):
        log.info("Prior loop pid %d exited (not alive). Clearing.", running_pid)
        post_comment(
            issue_number,
            "```loop-out\nDaemon restarted. Prior loop pid %d exited.\n```" % running_pid,
        )
        state["running_pid"] = None
        save_state(state)

    last_heartbeat = 0.0
    last_seen_id: int = state.get("last_seen_comment_id", 0)

    while True:
        try:
            comments = list_comments(issue_number)
            new_comments = [c for c in comments if c.get("id", 0) > last_seen_id]

            for comment in new_comments:
                state = process_comment(
                    comment, issue_number, allowed_authors, state, start_time
                )
                cid = comment.get("id", 0)
                if cid > last_seen_id:
                    last_seen_id = cid
                    state["last_seen_comment_id"] = last_seen_id
                    save_state(state)

            # Heartbeat: post if state changed OR 5+ min elapsed
            now = time.time()
            if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                post_heartbeat(issue_number, state, start_time)
                last_heartbeat = now

        except KeyboardInterrupt:
            log.info("loop_daemon interrupted, exiting.")
            break
        except Exception as exc:
            log.exception("Unhandled error in poll loop: %s", exc)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
