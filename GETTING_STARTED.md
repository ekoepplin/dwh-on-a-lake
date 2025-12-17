# Getting Started

Hands-on steps to install, configure, and run `dwh-in-a-box`, covering dev (DuckDB) and prod (BigQuery) paths, plus Evidence dashboards.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ and npm (for Evidence)
- DuckDB (installed via deps)
- NewsAPI key (for ingestion)
- BigQuery service account JSON (for prod)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd dwh-in-a-box

# Install Python deps
uv sync

# Configure credentials
cp credentials/dlt-newsapi-secrets.toml.example credentials/dlt-newsapi-secrets.toml
# Add your NewsAPI key to the secrets file
```

## Environments

- Dev (DuckDB): uses local file `/tmp/newsapi_articles.duckdb`; dbt `profiles.yml` targets DuckDB by default.
- Prod (BigQuery): set `GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json`; add a BigQuery target to `transformation/profiles.yml` and run dbt with `--target prod`.

## Run the pipeline

```bash
# 1. Ingest data from NewsAPI
cd ingestion
# Dev: loads to DuckDB (local)
uv run python newsapi_pipeline.py --dev
# Prod: loads to BigQuery (requires credentials)
GOOGLE_APPLICATION_CREDENTIALS=../credentials/service-account.json \
  uv run python newsapi_pipeline.py --prod

# 2. Transform data with dbt
cd ../transformation
dbt run                # dev (DuckDB)
dbt run --target prod  # prod (BigQuery), once configured

# 3. Validate governance metadata
cd ..
make validate-governance

# 4. Run Evidence (BI as Code) against marts
cd dashboard
npm install
npm run dev        # dev; points to DuckDB when configured
npm run preview    # prod; configure BigQuery source + credentials
```

## Evidence sources

- Dev (DuckDB): point `dashboard/sources/` to your DuckDB file (e.g., `/tmp/newsapi_articles.duckdb`).
- Prod (BigQuery): update `dashboard/sources/` to your BigQuery project/dataset and set `GOOGLE_APPLICATION_CREDENTIALS`.

## Usage examples

### dbt metadata snippet

```yaml
# transformation/models/mart/example_model.yml
version: 2

models:
  - name: example_model
    description: "Example model with governance metadata"
    meta:
      data_governance:
        business_owner: "alice@company.com"
        team_owner: "data-team"
        data_classification: "PUBLIC"
        data_lifecycle: "PRODUCTION"
        has_pii: false
        can_be_referenced: true
        update_schedule: "daily"
        sla: "daily"
```

### Validate governance metadata

```bash
# Validate all models
make validate-governance

# Or directly
uv run python data-governance-as-code/validators/metadata_validator.py \
  --dbt-project transformation
```

### Example validation output

```
============================================================
DATA GOVERNANCE METADATA VALIDATION REPORT
============================================================

✅ No errors found!
============================================================

✅ Validation PASSED
```

