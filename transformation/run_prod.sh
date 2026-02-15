#!/bin/bash
# Run full production pipeline: ingest to MotherDuck DuckLake + dbt transform + test
# Requires: MOTHERDUCK_TOKEN environment variable
set -e

echo "=== Ingesting data to MotherDuck DuckLake ==="
cd "$(dirname "$0")/../ingestion"
uv run python newsapi_pipeline.py --prod

echo ""
echo "=== Running dbt transformations ==="
cd "$(dirname "$0")"
dbt run --profiles-dir . --target motherduck

echo ""
echo "=== Running dbt tests ==="
dbt test --profiles-dir . --target motherduck

echo ""
echo "=== Done ==="
