# Loop overrides

This file is the **human-to-loop channel**. The Codex loop reads it at the start of every iteration and treats its contents as authoritative — they supersede rubric defaults and any prior decision recorded elsewhere.

Edit this file (commit + push to `main`) to communicate with the running loop. The loop picks up changes on the next iteration.

## Pause

<!--
Leave the section below empty to keep running.
Write the literal token PAUSE on its own line to halt the loop after the current iteration finishes.
-->



## Decisions

<!--
One bullet per override. Format:
- For `<rubric-item-id>`: <what to accept / reject / treat differently and why>.
Codex must follow these even if they conflict with the rubric's substance_check.
Move stale entries to the bottom of this section under "## Decisions (archived)" once they are no longer in effect.
-->

- **Priority order for the next 5 iterations** (cron set, 2026-04-25 21:00 UTC): work the hard items, not the easy ones. In order:
  1. `tenant_isolation_enforced` — add `tenant_id` columns + replace `using (true)` with `using (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid)` on every fact table; commit a cross-tenant integration test.
  2. `rls_enabled_on_referenced_tables` — set `force row level security` and regenerate the policy snapshot.
  3. `edge_functions_for_non_crud_endpoints` — ship at least one real Edge Function (suggest: gradebook bulk submit) that propagates the user JWT.
  4. `audit_log_for_sensitive_reads` — add `audit_log` table + trigger or Edge Function wrapper for restricted fields.
  5. `developer_guide_present` and `lead_spec_full_accounting` — finish the partials.
- **For `rls_enabled_on_referenced_tables`:** the prior `partial` verdict is REVOKED. `using (true)` is no isolation. Treat the current snapshot as failing until policies reference a JWT claim AND `forceRowSecurity = true`.



## Unblocks

<!--
One bullet per unblock signal. Format:
- <timestamp ET>: <prereq that is now satisfied>. Retry items previously blocked on this.
Codex should re-attempt the listed blocked items on the next iteration.
-->



## Notes to Codex

<!--
Free-form guidance: hints about which file to look at, what NOT to try, what we already ruled out.
Keep entries short. Stale entries belong in git history, not here — delete when no longer relevant.
-->


