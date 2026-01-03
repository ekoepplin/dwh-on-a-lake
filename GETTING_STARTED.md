# Getting Started

Hands-on steps to install, configure, and run `dwh-in-a-box`, covering dev and prod paths with DuckDB.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
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

- Dev (DuckDB): uses local DuckDB file; dbt `profiles.yml` targets DuckDB by default.
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
```

## Usage examples

### Running dbt tests

```bash
cd transformation
dbt test  # Run all tests
dbt test --select mart.*  # Run tests for mart models only
```

