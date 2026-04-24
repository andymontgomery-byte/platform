# OneRoster Core Demo API

This is the first working vertical slice of the platform. It proves the two-layer claim on a narrow OneRoster core dataset:

- A relational layer: SQLite tables and views seeded from `demo/schema.sql` and `demo/seed.sql`.
- A JSON/API layer: Express endpoints over the same data.
- A shared dictionary source: `dictionary/oneroster-core.v1.json` generates SQL comments, OpenAPI descriptions, and Markdown documentation.

## Run Locally

From the repo root:

```sh
cd demo
npm install
npm run reset-db
npm start
```

The API runs at `http://localhost:8787`.

## Try The JSON API

```sh
curl http://localhost:8787/organizations
curl 'http://localhost:8787/people?q=Ada'
curl http://localhost:8787/classes/class_math_6_a
curl http://localhost:8787/views/class-roster
curl http://localhost:8787/views/gradebook-results
```

## Try The SQL Layer Through JSON

```sh
curl -X POST http://localhost:8787/sql/query \
  -H 'content-type: application/json' \
  -d '{"sql":"select display_name, primary_role from people order by display_name"}'
```

Only read-only `SELECT` or `WITH` queries are accepted.

## Generated Artifacts

Run this from the repo root:

```sh
python3 scripts/generate_oneroster_core.py
```

It generates:

- `schema/generated/oneroster_core_comments.sql`
- `openapi/generated/oneroster-core.v0.json`
- `docs/generated/oneroster-core-dictionary.md`

That generator is intentionally small so the dictionary-to-SQL/OpenAPI/Markdown relationship is easy to inspect.
