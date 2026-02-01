# Getting Started

Hands-on steps to install, configure, and run `dwh-on-a-lake`, covering local development and cloud deployment with MotherDuck or BigQuery.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- DuckDB (installed via deps)
- NewsAPI key (for ingestion) - get a free developer API key at https://newsapi.org/
- Google Cloud SDK (for GCS access) - `gcloud` and `gsutil` CLI tools

**For cloud targets (optional):**
- MotherDuck account and token (for MotherDuck target)
- Google Cloud project with BigQuery enabled (for BigQuery target)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd dwh-on-a-lake

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
```

## Environment Variables

Configure based on your target environment:

| Target | Required Variables |
|--------|-------------------|
| **dev** (local DuckDB) | `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` (for GCS access) |
| **motherduck** | `MOTHERDUCK_TOKEN` |
| **bigquery** | `GOOGLE_APPLICATION_CREDENTIALS`, `GCP_PROJECT_ID` |

```bash
# For local development with GCS
export GOOGLE_SERVICE_ACCOUNT_KEY_PATH="$HOME/your-service-account-key.json"

# For MotherDuck
export MOTHERDUCK_TOKEN="your_motherduck_token"

# For BigQuery
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/your-service-account-key.json"
export GCP_PROJECT_ID="your-gcp-project-id"
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Lakehouse Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐                                                                │
│  │ NewsAPI │                                                                │
│  └────┬────┘                                                                │
│       │ dlt --gcs                                                           │
│       ▼                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GCS Bucket (Data Lake)                           │  │
│  │  gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet│ │
│  │                        (Raw, append-only)                             │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                           │
│            ┌────────────────────┼────────────────────┐                      │
│            │                    │                    │                      │
│            ▼                    ▼                    ▼                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐            │
│  │     DuckDB       │ │   MotherDuck     │ │    BigQuery      │            │
│  │   (dbt: dev)     │ │ (dbt: motherduck)│ │  (dbt: bigquery) │            │
│  │  read_parquet()  │ │  read_parquet()  │ │  external table  │            │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘            │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                │ dbt                                        │
│                                ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Transformation Layers (same SQL across all targets)                 │   │
│  │  staging ──▶ intermediate ──▶ mart                                   │   │
│  │  (dedup)     (enrich)         (aggregate)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Environments

| Target | Type | Storage | Use Case |
|--------|------|---------|----------|
| **dev** | Local DuckDB | `/tmp/newsapi_articles.duckdb` | Local development |
| **motherduck** | MotherDuck (cloud) | MotherDuck database | Cloud analytics, sharing |
| **bigquery** | BigQuery | BigQuery dataset | Enterprise, large scale |

All targets read raw data from GCS Parquet files—no data duplication.

## Typical Development Flow

### 1. Local Development (Dev)

For quick iteration and testing, use the local DuckDB workflow:

```bash
# Step 1: Ingest data to GCS (or use existing data)
cd ingestion
uv run python newsapi_pipeline.py --gcs

# Step 2: Run dbt transformations (reads from GCS)
cd ../transformation
dbt run --target dev

# Step 3: Verify results
dbt test --target dev
duckdb /tmp/newsapi_articles.duckdb -c "SELECT * FROM ingest_newsapi_v1.mart_newsapi__articles LIMIT 5;"
```

This is useful for:
- Developing new models
- Testing transformation logic
- Debugging data issues
- Quick prototyping

### 2. MotherDuck (Cloud DuckDB)

For cloud-based analytics with MotherDuck:

```bash
# Set your MotherDuck token
export MOTHERDUCK_TOKEN="your_token_here"

# Option A: Use the convenience script
cd transformation
./run_motherduck.sh

# Option B: Run manually
dbt run --target motherduck
dbt test --target motherduck
```

MotherDuck provides:
- Cloud-hosted DuckDB with sharing capabilities
- Same SQL syntax as local DuckDB
- GCS access configured at account level

### 3. BigQuery (Enterprise)

For enterprise-scale analytics with BigQuery:

```bash
# Set your GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/your-service-account-key.json"
export GCP_PROJECT_ID="your-gcp-project-id"

# Option A: Use the convenience script (creates external table + runs dbt)
cd transformation
./run_bigquery.sh

# Option B: Run manually
# First, create the external table pointing to GCS
dbt run-operation create_bigquery_external_table \
    --args '{table_name: ext_newsapi__articles_us_en, gcs_uri: gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet}' \
    --target bigquery

# Then run transformations
dbt run --target bigquery
dbt test --target bigquery
```

BigQuery provides:
- Enterprise-grade scalability
- Native GCS integration via external tables
- Advanced analytics and ML capabilities

### 4. End-to-End Example

Here's a complete workflow from ingestion to analytics:

```bash
# 1. Fetch fresh articles from NewsAPI and store in GCS
cd ingestion
uv run python newsapi_pipeline.py --gcs

# 2. Run transformations on your target of choice
cd ../transformation

# Local DuckDB
dbt run --target dev && dbt test --target dev

# Or MotherDuck
./run_motherduck.sh

# Or BigQuery
./run_bigquery.sh

# 3. Query the results
duckdb /tmp/newsapi_articles.duckdb << 'EOF'
-- Check deduplicated article count
SELECT COUNT(*) as total_articles FROM ingest_newsapi_v1.stg_newsapi__articles_us_en;

-- View aggregated metrics
SELECT * FROM ingest_newsapi_v1.mart_newsapi__articles ORDER BY article_date DESC LIMIT 10;
EOF

# 4. Or query directly from GCS Parquet files (no dbt needed)
duckdb << 'EOF'
INSTALL httpfs; LOAD httpfs;
SELECT * FROM read_parquet('gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet') LIMIT 10;
EOF
```

### 5. Incremental Updates

The pipeline is designed for incremental updates:

```bash
# Run daily to fetch new articles and update the warehouse
cd ingestion && uv run python newsapi_pipeline.py --gcs

# Then refresh any/all targets
cd ../transformation
dbt run --target dev           # Local
./run_motherduck.sh            # MotherDuck
./run_bigquery.sh              # BigQuery
```

- **Raw layer** (dlt): Appends new Parquet files to GCS (no overwrites)
- **Staging layer** (dbt): Deduplicates using `ROW_NUMBER()` on URL, keeping the latest version
- **Mart layer** (dbt): Aggregates all deduplicated data

All targets read from the same GCS source—run dbt against any target without re-ingesting.

## Deduplication Logic

The staging model (`stg_newsapi__articles_us_en.sql`) handles deduplication:

```sql
-- Keep only the latest version of each article (by URL)
ROW_NUMBER() OVER (
    PARTITION BY url
    ORDER BY _dlt_load_id DESC
) AS row_num
...
WHERE row_num = 1
```

This ensures that even with append-only raw storage, you always get clean, deduplicated data in downstream models.

## Usage Examples

### Running dbt tests

```bash
cd transformation
dbt test                      # Run all tests
dbt test --select mart.*      # Run tests for mart models only
dbt test --select stg_*       # Run tests for staging models
```

### Debugging data issues

```bash
# Check raw data count
duckdb /tmp/newsapi_articles.duckdb -c "SELECT COUNT(*) FROM ingest_newsapi_v1.src_newsapi__articles_us_en;"

# Check for duplicates before dedup
duckdb /tmp/newsapi_articles.duckdb -c "
  SELECT url, COUNT(*) as cnt
  FROM ingest_newsapi_v1.src_newsapi__articles_us_en
  GROUP BY url HAVING cnt > 1;
"

# Verify dedup worked
duckdb /tmp/newsapi_articles.duckdb -c "SELECT COUNT(*) FROM ingest_newsapi_v1.stg_newsapi__articles_us_en;"
```

### Viewing dbt lineage

```bash
cd transformation
dbt ls --select +mart_newsapi__articles  # Show upstream dependencies
dbt docs generate && dbt docs serve       # Visual documentation
```

## How Multi-Target Works

The source model (`src_newsapi__articles_us_en.sql`) uses Jinja conditionals to handle different targets:

```sql
{% if target.type == 'duckdb' %}
-- DuckDB/MotherDuck: use read_parquet() directly from GCS
select * from read_parquet('gs://.../*.parquet')

{% elif target.type == 'bigquery' %}
-- BigQuery: use external table pointing to GCS
select * from `project.dataset.ext_newsapi__articles_us_en`
{% endif %}
```

All downstream models (staging, intermediate, mart) use standard SQL and work unchanged across all targets.

### Target Configuration

Targets are defined in `transformation/profiles.yml`:

| Target | Connection | GCS Access |
|--------|------------|------------|
| dev | Local DuckDB file | GCS extension with service account |
| motherduck | `md:dwh_on_a_lake` | Configured in MotherDuck account |
| bigquery | BigQuery API | Native (external table) |

