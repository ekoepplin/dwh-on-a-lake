#!/bin/bash
# Run dbt transformations against BigQuery
# Requires: GOOGLE_APPLICATION_CREDENTIALS and GCP_PROJECT_ID environment variables

set -e

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
    exit 1
fi

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

echo "Creating BigQuery external table..."
dbt run-operation create_bigquery_external_table \
    --args '{table_name: ext_newsapi__articles_us_en, gcs_uri: gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet}' \
    --target bigquery

echo "Running dbt against BigQuery..."
dbt run --target bigquery

echo "Running dbt tests..."
dbt test --target bigquery

echo "BigQuery pipeline completed successfully!"
