# Platform

An educational data and API platform designed around 1EdTech standards.

The platform exposes two developer-facing layers:

- A relational SQL layer with a plain-language data dictionary.
- A JSON/HTTP API layer with OpenAPI documentation generated from the same dictionary.

## Current Artifacts

- [Customer-Facing Developer Portal](site/index.html)
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
- [Dictionary API OpenAPI Stub](openapi/dictionary.v0.yaml)

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
