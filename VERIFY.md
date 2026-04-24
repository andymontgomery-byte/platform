# VERIFY

`scripts/codex_loop.py` runs the shell commands in the fenced block below after every Codex iteration.

Keep each command on one line. Avoid interactive commands.

```sh
python3 scripts/generate_oneroster_core.py
python3 scripts/generate_qti_core.py
python3 scripts/build_static_api.py
python3 scripts/build_site_docs.py
python3 scripts/check_dictionary_artifacts.py
python3 -m py_compile scripts/generate_oneroster_core.py scripts/generate_qti_core.py scripts/build_static_api.py scripts/build_site_docs.py scripts/check_dictionary_artifacts.py scripts/codex_loop.py
python3 -m json.tool openapi/generated/oneroster-core.v0.json >/tmp/platform-oneroster-openapi.json
python3 -m json.tool openapi/generated/oneroster-core-static.v0.json >/tmp/platform-oneroster-static-openapi.json
python3 -m json.tool openapi/generated/qti-core.v0.json >/tmp/platform-qti-openapi.json
python3 -m json.tool site/api/index.json >/tmp/platform-api-index.json
node --check site/app.js
node --check demo/server.js
cd demo && npm run reset-db && npm test
git diff --check
```
