# How to restart the platform Codex loop

This file exists because the loop is currently halted with stranded local work that needs a one-time manual rebase before the harness can be safely restarted. Once the rebase succeeds and the harness runs one clean iteration, this file should be deleted.

## Current situation (as of 2026-04-27 01:00 UTC)

- The Codex loop on the Mac mini at `/Users/andymontgomery/projects/platform` last completed `iter14` at `2026-04-26T21:11Z` with `pass=18 partial=2 fail=0` against the previous (20-item) rubric.
- Iter9 through iter14 all logged `Publish result: commit succeeded, push failed: ! [rejected] main -> main (fetch first)`. Six iterations of substantive work (including the apex `buildable_by_layperson` flip and the addition of `case_target_uri`, `caliper_events`, and `class_activity_feed`) are stranded on local main.
- PR #9 (merge `79d3fa5`) is on remote main and patches `scripts/codex_loop.py.maybe_publish` to fetch + rebase before push and halt on conflict. After this rebase, the loop will publish durably going forward.
- The rubric is now 21 items. New: `loop_publishes_durably`. Tightened: `loop_terminates_on_done`.

## Restart procedure

Run on the Mac mini:

```sh
cd /Users/andymontgomery/projects/platform
git fetch origin main
git checkout main
git pull --rebase origin main
```

Expect rebase conflicts in roughly these paths (PR #5-#9 vs. iter9-14 both touched them):

- `data/data-dictionary.seed.json`
- `scripts/generate_spec_dictionaries.py`
- `dictionary/oneroster-core.v1.json` and other `dictionary/*.v1.json`
- `supabase/migrations/0001_oneroster_core_demo.sql`
- `docs/build-an-edtech-app.md`

Resolution rule: keep the union of changes. PR #8's shared `canonical_field_id` rewrite (and `shared_enums` table) is upstream of iter9-14's per-object work. Iter14's additions (`line_items.case_target_uri` column, `caliper_events` table, `class_activity_feed` view) should be preserved on top of PR #8's foundation.

After resolving each conflict file:

```sh
git add <file>
git rebase --continue
```

When the rebase finishes:

```sh
# verify everything still works
python3 scripts/generate_spec_dictionaries.py --check
python3 scripts/generate_supabase_migrations.py --check
python3 scripts/evaluate_platform.py --output site/api/platform-evaluation.json

# push
git push origin main

# delete this file once the loop has produced one clean iteration
rm RESTART.md
git add RESTART.md
git commit -m "Remove RESTART.md: harness restarted cleanly"
git push origin main

# restart the harness
./scripts/codex_loop.py --max-iterations 10
```

## Why this happened (one paragraph)

The loop driver was committing locally and pushing to remote without first fetching and rebasing. While the loop was running, four manual PRs (#5, #6, #7, #8) merged to remote main, so every subsequent push was rejected with `fetch first`. The loop kept iterating against stale local main and the public Pages evaluator stayed stuck at `pass=11/20` from iter8 because Pages re-runs against remote, not local. PR #9 patches the driver to halt the harness with a clear `DIVERGENCE` message on rebase conflict instead of silently stranding work. The rubric also now has `loop_publishes_durably` so this regression cannot reach `done` again.
