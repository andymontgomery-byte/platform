# VERIFY

`scripts/codex_loop.py` runs the shell commands in the fenced block below after every Codex iteration.

Keep each command on one line. Avoid interactive commands.

```sh
python3 scripts/generate_spec_dictionaries.py --check
python3 scripts/generate_spec_fidelity_report.py --report-only
python3 scripts/generate_spec_fidelity_report.py --check
python3 scripts/generate_supabase_migrations.py --check
python3 scripts/generate_oneroster_core.py
python3 scripts/generate_qti_core.py
python3 scripts/generate_case_core.py
python3 scripts/generate_caliper_core.py
python3 scripts/generate_integration_governance_core.py
python3 scripts/build_static_api.py
python3 scripts/build_site_docs.py
python3 scripts/check_site_links.py
python3 scripts/check_dictionary_artifacts.py
python3 scripts/check_spec_conformance.py --write-report site/api/spec-conformance.json
python3 tests/supabase_tenant_rls_test.py
python3 tests/supabase_audit_log_test.py
python3 -m py_compile scripts/generate_spec_dictionaries.py scripts/generate_supabase_migrations.py scripts/generate_oneroster_core.py scripts/generate_qti_core.py scripts/generate_case_core.py scripts/generate_caliper_core.py scripts/generate_integration_governance_core.py scripts/build_static_api.py scripts/build_site_docs.py scripts/check_site_links.py scripts/check_dictionary_artifacts.py scripts/check_spec_conformance.py scripts/check_supabase_rest.py scripts/snapshot_pg_policies.py scripts/evaluate_platform.py scripts/codex_loop.py tests/supabase_tenant_rls_test.py tests/supabase_audit_log_test.py
python3 -m json.tool openapi/generated/oneroster-core.v0.json >/tmp/platform-oneroster-openapi.json
python3 -m json.tool openapi/generated/oneroster-core-static.v0.json >/tmp/platform-oneroster-static-openapi.json
python3 -m json.tool openapi/generated/qti-core.v0.json >/tmp/platform-qti-openapi.json
python3 -m json.tool openapi/generated/case-core.v0.json >/tmp/platform-case-openapi.json
python3 -m json.tool openapi/generated/caliper-core.v0.json >/tmp/platform-caliper-openapi.json
python3 -m json.tool openapi/generated/integration-governance-core.v0.json >/tmp/platform-integration-governance-openapi.json
python3 -m json.tool site/api/spec-conformance.json >/tmp/platform-spec-conformance.json
python3 -m json.tool site/api/index.json >/tmp/platform-api-index.json
node --check site/app.js
node --check demo/server.js
cd demo && npm run reset-db && npm test
git diff --check
python3 scripts/evaluate_platform.py --runs 3 --output site/api/platform-evaluation.json
```
