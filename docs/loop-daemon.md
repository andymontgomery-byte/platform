# Loop Daemon

The loop daemon (`scripts/loop_daemon.py`) is a GitHub-issue-driven process that lets a remote
operator drive the local Codex loop without direct shell access.

---

## Protocol

The daemon polls a designated GitHub issue (the "control issue") every 30 seconds.
To issue a command, post a comment on the control issue containing a fenced code block
tagged `loop-cmd` with a JSON payload:

    ```loop-cmd
    {"cmd": "<command>", ...}
    ```

Only comments from authors listed in `.loop-daemon.config.json` `allowed_authors` are processed.

### Commands

| Command | Description |
|---|---|
| `kickoff_loop` | Starts `scripts/codex_loop.py --max-iterations 25 --stall-limit 3`. Streams output back in `loop-out` comments. |
| `halt_loop` | Sends SIGTERM to the running loop process, waits 30 s, then SIGKILL if needed. |
| `git_status` | Posts `git status --porcelain` and recent log. |
| `git_rebase_main` | Stashes, fetches, rebases onto `origin/main`, pops stash. Posts conflicts or new HEAD. |
| `discard_paths` | Discards specific files via `git checkout --`. Only whitelisted paths are accepted. |
| `tail_log` | Posts the tail of the most recent `.codex-loop/*.log` file. |
| `ping` | Posts a heartbeat reply with daemon pid, uptime, git HEAD. |

### JSON shapes

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
{"cmd": "discard_paths", "paths": ["docs/spec-fidelity-report.md", "docs/generated/example.md"]}
```

```loop-cmd
{"cmd": "tail_log", "lines": 200}
```

```loop-cmd
{"cmd": "ping"}
```

### Replies

The daemon posts replies as comments tagged `loop-out` (command output) or
`loop-heartbeat` (automatic 5-minute heartbeats).

---

## One-time install (Andy runs these once)

```sh
# 1. Copy the plist into ~/Library/LaunchAgents/
cp /Users/andymontgomery/projects/platform/scripts/com.platform.loop-daemon.plist \
   ~/Library/LaunchAgents/com.platform.loop-daemon.plist

# 2. Load and start the daemon
launchctl load ~/Library/LaunchAgents/com.platform.loop-daemon.plist

# 3. Verify it started
launchctl list | grep com.platform.loop-daemon
```

On first run the daemon creates the control issue and writes its number into
`.loop-daemon.config.json`. That file is committed; `.loop-daemon.state.json`
and `.loop-daemon.log` are gitignored.

---

## Security model

- **Whitelist only.** The daemon recognises exactly seven commands. Any unrecognised
  command name is rejected with `{"error": "unknown_cmd"}`.
- **No shell injection.** Commands are parsed from JSON only; no string is ever
  passed to a shell interpreter. All subprocess calls use list-form `subprocess.run` /
  `subprocess.Popen` with no `shell=True`.
- **Allowed authors.** Only GitHub logins listed in `.loop-daemon.config.json`
  `allowed_authors` can trigger commands. Comments from other users are silently ignored.
- **Path whitelist for `discard_paths`.** The daemon will only run
  `git checkout --` on paths matching:
  - `docs/spec-fidelity-report.md`
  - `docs/generated/*.md`
  - `dictionary/*.v1.json`
  - `openapi/generated/*.json`
  - `site/**`

  `PROGRESS.md` and any other files are never discarded.
- **No system side-effects.** The daemon never writes outside the repo working tree
  (except its own `.loop-daemon.log`), never installs packages, and never runs
  commands not in its whitelist.
- **No secrets in code.** GitHub authentication is delegated entirely to Andy's
  existing `gh auth` setup. No token appears in any file.

---

## Debugging

### Check daemon logs

```sh
# Daemon's own structured log
tail -f /Users/andymontgomery/projects/platform/.loop-daemon.log

# launchd stdout/stderr
tail -f ~/Library/Logs/platform-loop-daemon.out.log
tail -f ~/Library/Logs/platform-loop-daemon.err.log
```

### Restart the daemon via launchctl

```sh
launchctl unload ~/Library/LaunchAgents/com.platform.loop-daemon.plist
launchctl load   ~/Library/LaunchAgents/com.platform.loop-daemon.plist
```

### Force a state reset

Delete `.loop-daemon.state.json` in the repo root and restart the daemon.
The daemon will re-read comment history from the beginning of the control issue.

### Check the control issue number

```sh
cat /Users/andymontgomery/projects/platform/.loop-daemon.config.json
```
