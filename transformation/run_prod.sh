#!/bin/bash
# Run dbt prod pipeline and sync to GCS
set -e

echo "=== Running dbt with prod target ==="
dbt run --target prod

echo ""
echo "=== Exporting tables to local Parquet ==="
mkdir -p /tmp/dbt_export/staging /tmp/dbt_export/intermediate /tmp/dbt_export/mart
dbt run-operation export_to_gcs --target prod

echo ""
echo "=== Syncing to GCS ==="
gsutil -m rsync -r /tmp/dbt_export/ gs://dwh-on-a-lake-prod/dbt/

echo ""
echo "=== Done ==="
gsutil ls -r gs://dwh-on-a-lake-prod/dbt/
