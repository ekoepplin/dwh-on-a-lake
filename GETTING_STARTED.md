# Getting Started

Hands-on steps to install, configure, and run `dwh-on-a-lake`, covering local development and cloud deployment with MotherDuck.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- DuckDB (installed via deps)
- NewsAPI key (for ingestion) - get a free developer API key at https://newsapi.org/

**For cloud targets (optional):**
- MotherDuck account and token (for MotherDuck target)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd dwh-on-a-lake

# Install Python deps and dbt packages
uv sync
cd transformation && dbt deps --profiles-dir . && cd ..

# Configure credentials
# Edit ingestion/.dlt/secrets.toml with your NewsAPI key:
# [sources.newsapi_pipeline]
# api_key = "YOUR_NEWSAPI_KEY_HERE"
#
# Replace YOUR_NEWSAPI_KEY_HERE with your actual API key from https://newsapi.org/
```

## Environment Variables

Configure based on your target environment:

| Target | Required Variables |
|--------|-------------------|
| **dev** (local DuckLake) | None (uses local files) |
| **motherduck** | `MOTHERDUCK_TOKEN` |

```bash
# For MotherDuck
export MOTHERDUCK_TOKEN="your_motherduck_token"
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DuckLake Lakehouse Architecture                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐                                                                │
│  │ NewsAPI │                                                                │
│  └────┬────┘                                                                │
│       │ dlt (merge on URL)                                                  │
│       ▼                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      DuckLake (Data Lake)                             │  │
│  │  Catalog: /tmp/newsapi_ducklake_catalog.duckdb (dev)                  │  │
│  │  Data:    /tmp/newsapi_ducklake_data/*.parquet  (dev)                  │  │
│  │  ACID transactions · Merge dedup · Time travel                        │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                           │
│            ┌────────────────────┴────────────────────┐                      │
│            │                                         │                      │
│            ▼                                         ▼                      │
│  ┌──────────────────┐                 ┌──────────────────┐                  │
│  │     DuckDB       │                 │   MotherDuck     │                  │
│  │   (dbt: dev)     │                 │ (dbt: motherduck)│                  │
│  │  attach DuckLake │                 │  is_ducklake     │                  │
│  └────────┬─────────┘                 └────────┬─────────┘                  │
│           │                                    │                            │
│           └────────────────┬───────────────────┘                            │
│                            │ dbt                                            │
│                            ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Transformation Layers (same SQL across all targets)                 │   │
│  │  staging ──▶ intermediate ──▶ mart                                   │   │
│  │  (rename)    (enrich)         (aggregate)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Environments

| Target | Type | Storage | Use Case |
|--------|------|---------|----------|
| **dev** | Local DuckDB + DuckLake | `/tmp/newsapi_ducklake_*` | Local development |
| **motherduck** | MotherDuck DuckLake | MotherDuck + GCS | Cloud analytics, sharing |

Both targets use DuckLake for ACID transactions and merge deduplication on Parquet files.

## Typical Development Flow

### 1. Local Development (Dev)

For quick iteration and testing, use the local DuckLake workflow:

```bash
# Step 1: Ingest data to local DuckLake
cd ingestion
uv run python newsapi_pipeline.py --dev

# Step 2: Run dbt transformations (reads from DuckLake via attach)
cd ../transformation
dbt run --profiles-dir . --target dev

# Step 3: Verify results
dbt test --profiles-dir . --target dev
```

Or use the Makefile:

```bash
make pipeline-dev
```

This is useful for:
- Developing new models
- Testing transformation logic
- Debugging data issues
- Quick prototyping

### 2. MotherDuck (Cloud DuckLake)

For cloud-based analytics with MotherDuck:

```bash
# Set your MotherDuck token
export MOTHERDUCK_TOKEN="your_token_here"

# Option A: Use the convenience script
cd transformation
./run_motherduck.sh

# Option B: Run manually
dbt run --profiles-dir . --target motherduck
dbt test --profiles-dir . --target motherduck
```

MotherDuck provides:
- Cloud-hosted DuckDB with DuckLake support
- Same SQL syntax as local DuckDB
- Sharing and collaboration features

### 3. End-to-End Example

Here's a complete workflow from ingestion to analytics:

```bash
# 1. Fetch fresh articles from NewsAPI and store in DuckLake
cd ingestion
uv run python newsapi_pipeline.py --dev

# 2. Run transformations
cd ../transformation
dbt run --profiles-dir . --target dev && dbt test --profiles-dir . --target dev

# 3. Query the results
duckdb << 'EOF'
INSTALL ducklake; LOAD ducklake;
ATTACH '/tmp/newsapi_ducklake_catalog.duckdb' AS lake (TYPE DUCKLAKE, DATA_PATH '/tmp/newsapi_ducklake_data/');
SELECT * FROM lake.ingest_newsapi_v1.articles_us_en LIMIT 10;
EOF
```

### 4. Incremental Updates

The pipeline is designed for incremental updates:

```bash
# Run daily to fetch new articles and update the warehouse
cd ingestion && uv run python newsapi_pipeline.py --dev

# Then refresh transformations
cd ../transformation
dbt run --profiles-dir . --target dev
```

- **Raw layer** (dlt): Merges new data into DuckLake (deduplicates on URL)
- **Staging layer** (dbt): Renames and standardizes columns (no dedup needed)
- **Mart layer** (dbt): Aggregates all data

### 5. Time Travel

DuckLake provides time travel on your data:

```sql
-- Query data as it was at a specific point in time
SELECT * FROM lake.ingest_newsapi_v1.articles_us_en
AT (TIMESTAMP => '2025-01-15 12:00:00');
```

## Usage Examples

### Running dbt tests

```bash
cd transformation
dbt test --profiles-dir .                      # Run all tests
dbt test --profiles-dir . --select mart.*      # Run tests for mart models only
dbt test --profiles-dir . --select stg_*       # Run tests for staging models
```

### Debugging data issues

```bash
# Query DuckLake directly
duckdb << 'EOF'
INSTALL ducklake; LOAD ducklake;
ATTACH '/tmp/newsapi_ducklake_catalog.duckdb' AS lake (TYPE DUCKLAKE, DATA_PATH '/tmp/newsapi_ducklake_data/');
SELECT COUNT(*) FROM lake.ingest_newsapi_v1.articles_us_en;
EOF
```

### Viewing dbt lineage

```bash
cd transformation
dbt ls --profiles-dir . --select +mart_newsapi__articles  # Show upstream dependencies
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .  # Visual documentation
```

## Target Configuration

Targets are defined in `transformation/profiles.yml`:

| Target | Connection | DuckLake Access |
|--------|------------|-----------------|
| dev | In-memory DuckDB | Attach local DuckLake catalog |
| motherduck | MotherDuck | is_ducklake (native) |
