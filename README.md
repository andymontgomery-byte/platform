# Platform

An educational data and API platform designed around 1EdTech standards.

The platform exposes two developer-facing layers:

- A relational SQL layer with a plain-language data dictionary.
- A JSON/HTTP API layer with OpenAPI documentation generated from the same dictionary.

## Current Artifacts

- [Customer-Facing Developer Portal](site/index.html)
- [Feedback Package](docs/feedback-package.md)
- [Supabase Hosted Database Setup](docs/supabase-hosted-database.md)
- [Rendered Docs Index](site/docs/index.html)
- [Hosted OneRoster JSON OpenAPI](site/openapi/hosted-json.html)
- [Local OneRoster Express OpenAPI](site/openapi/oneroster-core.html)
- [QTI Repository OpenAPI](site/openapi/qti-core.html)
- [Spec Gap Backlog](docs/spec-gap-backlog.md)
- [Dictionary Coverage Matrix](docs/dictionary-coverage-matrix.md)
- [Working OneRoster Core Demo API](demo/README.md)
- [1EdTech Platform Plan](docs/1edtech-platform-plan.md)
- [Phase 0 Standards and Dictionary](docs/phase-0-standards-and-dictionary.md)
- [Layperson Data Dictionary Index](docs/dictionaries/README.md)
- [OneRoster 1.2 Layperson Data Dictionary](docs/dictionaries/oneroster-1.2-layperson-dictionary.md)
- [CASE 1.1 Layperson Data Dictionary](docs/dictionaries/case-1.1-layperson-dictionary.md)
- [QTI 3 Layperson Data Dictionary](docs/dictionaries/qti-3-layperson-dictionary.md)
- [Caliper 1.2 Layperson Data Dictionary](docs/dictionaries/caliper-1.2-layperson-dictionary.md)
- [Integration, Packaging, Credentials, and Governance Layperson Data Dictionary](docs/dictionaries/integration-packaging-credentials-governance-layperson-dictionary.md)
- [Registry and Dictionary SQL](schema/0001_registry_and_dictionary.sql)
- [Standards Registry Seed](data/standards-registry.seed.json)
- [Data Dictionary Seed](data/data-dictionary.seed.json)
- [Dictionary API OpenAPI Draft](openapi/dictionary.v0.yaml)

## Phase 0 Goal

Phase 0 turns standards research into governed platform metadata:

1. A standards registry that records which 1EdTech standards, versions, links, and implementation postures the platform knows about.
2. A data dictionary that describes every database object, API resource, field, enum, and relationship in school-friendly language.
3. A single metadata source that can generate SQL comments, API descriptions, Markdown documentation, and AI-readable context.

No application framework is assumed yet.

## Local Website

Run the customer-facing portal from the repo root:

```sh
python3 -m http.server 8080
```

Then open `http://localhost:8080/site/`.

The public GitHub Pages portal is:

`https://andymontgomery-byte.github.io/platform/`

GitHub Pages has no server runtime, so the hosted demo exposes read-only static JSON endpoints and runs SQLite in the browser for SQL queries. The hosted JSON API is documented in `site/openapi/hosted-json.html`; the local API below provides the matching Express/SQLite server version and is documented in `site/openapi/oneroster-core.html`.

## Working Demo Slice

The first executable slice is OneRoster core:

```sh
cd demo
npm install
npm run reset-db
npm start
```

Then call the API at `http://localhost:8787`, for example:

```sh
curl http://localhost:8787/people
curl -X POST http://localhost:8787/sql/query \
  -H 'content-type: application/json' \
  -d '{"sql":"select display_name, primary_role from people order by display_name"}'
```

The generated OneRoster SQL comments, OpenAPI JSON, and Markdown/HTML dictionary come from `dictionary/oneroster-core.v1.json` via:

```sh
python3 scripts/generate_oneroster_core.py
```

The generated QTI repository SQL comments, OpenAPI JSON, and Markdown/HTML dictionary come from `dictionary/qti-core.v1.json` via:

```sh
python3 scripts/generate_qti_core.py
```

The generated CASE, Caliper, and integration/governance SQL comments, OpenAPI JSON, and Markdown/HTML dictionaries come from their structured sources via:

```sh
python3 scripts/generate_case_core.py
python3 scripts/generate_caliper_core.py
python3 scripts/generate_integration_governance_core.py
```

Build the GitHub Pages JSON endpoints and rendered HTML docs with:

```sh
python3 scripts/build_static_api.py
python3 scripts/build_site_docs.py
```

Check that structured dictionary sources still match generated SQL, OpenAPI, Markdown, and HTML artifacts with:

```sh
python3 scripts/check_dictionary_artifacts.py
```

## Supabase Hosted Database

The Supabase project URL is `https://qzxlgrerjoiamxvnkklq.supabase.co`.

Deploy-ready PostgreSQL setup files live in `supabase/`:

```sh
psql "$SUPABASE_DB_URL" -f supabase/migrations/0001_oneroster_core_demo.sql
psql "$SUPABASE_DB_URL" -f supabase/seed.sql
psql "$SUPABASE_DB_URL" -f supabase/smoke.sql
```

The URL is public, but the database connection string and API keys stay local in `.env`.
