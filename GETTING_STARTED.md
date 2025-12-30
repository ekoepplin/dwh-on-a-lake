# Getting Started

Hands-on steps to install, configure, and run `dwh-in-a-box`, covering dev and prod paths with DuckDB, plus Evidence dashboards.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ and npm (for Evidence)
- DuckDB (installed via deps)
- NewsAPI key (for ingestion) - get a free developer API key at https://newsapi.org/

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd dwh-in-a-box

# Install Python deps
uv sync

# Configure credentials
# Create credentials/dlt-newsapi-secrets.toml with the following content:
# [sources.newsapi_pipeline]
# api_key = "YOUR_NEWSAPI_KEY_HERE"
#
# [newsapi_pipeline.destination]
# schema_name = "ingest_newsapi_v1"
#
# Replace YOUR_NEWSAPI_KEY_HERE with your actual API key from https://newsapi.org/
# Note: If using BigQuery as destination, also add [destination.bigquery] section with your credentials
```

## Environments

- Dev (DuckDB): uses local file `reports/sources/duckdb/newsapi_articles.duckdb`; dbt `profiles.yml` targets DuckDB by default.
- Prod (DuckDB/MotherDuck): configure your production DuckDB connection in `transformation/profiles.yml` and run dbt with `--target prod`.

## Run the pipeline

```bash
# 1. Ingest data from NewsAPI
cd ingestion
# Dev: loads to DuckDB (local)
uv run python newsapi_pipeline.py --dev
# Prod: loads to DuckDB/MotherDuck
uv run python newsapi_pipeline.py --prod

# 2. Transform data with dbt
cd ../transformation
dbt run                # dev (DuckDB)
dbt run --target prod  # prod (DuckDB/MotherDuck), once configured

# 3. Validate governance metadata
cd ..
make validate-governance

# 4. Run Evidence (BI as Code) against marts
cd reports
npm install
npm run dev        # dev; points to DuckDB when configured
npm run preview    # prod; configure DuckDB/MotherDuck source
```

## Evidence sources

- Dev (DuckDB): point `reports/sources/duckdb/connection.yaml` to your DuckDB file (e.g., `reports/sources/duckdb/newsapi_articles.duckdb`).
- Prod (DuckDB/MotherDuck): update `reports/sources/` to your production DuckDB or MotherDuck connection.

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

