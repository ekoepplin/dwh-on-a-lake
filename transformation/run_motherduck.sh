#!/bin/bash
# Run dbt transformations against MotherDuck
# Requires: MOTHERDUCK_TOKEN environment variable

set -e

if [ -z "$MOTHERDUCK_TOKEN" ]; then
    echo "Error: MOTHERDUCK_TOKEN environment variable is not set"
    exit 1
fi

echo "Running dbt against MotherDuck..."
dbt run --target motherduck

echo "Running dbt tests..."
dbt test --target motherduck

echo "MotherDuck pipeline completed successfully!"
