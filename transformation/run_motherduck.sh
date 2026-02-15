#!/bin/bash
# Run dbt transformations against MotherDuck DuckLake
# Requires: MOTHERDUCK_TOKEN environment variable

set -e

if [ -z "$MOTHERDUCK_TOKEN" ]; then
    echo "Error: MOTHERDUCK_TOKEN environment variable is not set"
    exit 1
fi

echo "Running dbt against MotherDuck DuckLake..."
dbt run --profiles-dir . --target motherduck

echo "Running dbt tests..."
dbt test --profiles-dir . --target motherduck

echo "MotherDuck DuckLake pipeline completed successfully!"
