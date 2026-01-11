#!/usr/bin/env python3
"""
Sync staging table from local DuckDB to MotherDuck.

This script copies the deduplicated staging table from local DuckDB
(populated by dbt dev reading from GCS) to MotherDuck for production use.

Usage:
    python scripts/sync_to_motherduck.py

Requirements:
    - MOTHERDUCK_TOKEN environment variable must be set
    - Local DuckDB must have been populated by running: dbt run --target dev
"""

import os
import sys

import duckdb

LOCAL_DB = "/tmp/newsapi_articles.duckdb"
MOTHERDUCK_DB = "dwh_on_a_lake"
SCHEMA = "main"
TABLE = "stg_newsapi__articles_us_en"


def sync_staging_to_motherduck():
    # Get MotherDuck token
    motherduck_token = os.environ.get("MOTHERDUCK_TOKEN")
    if not motherduck_token:
        print("Error: MOTHERDUCK_TOKEN environment variable not set")
        sys.exit(1)

    # Check local DB exists
    if not os.path.exists(LOCAL_DB):
        print(f"Error: Local database not found: {LOCAL_DB}")
        print("Run 'dbt run --target dev' first to populate local DuckDB")
        sys.exit(1)

    # Connect to local DuckDB and read staging data
    print(f"Reading from local DuckDB: {LOCAL_DB}")
    local_conn = duckdb.connect(LOCAL_DB, read_only=True)

    try:
        row_count = local_conn.execute(
            f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}"
        ).fetchone()[0]
    except duckdb.CatalogException:
        print(f"Error: Table {SCHEMA}.{TABLE} not found in local DuckDB")
        print("Run 'dbt run --target dev' first")
        sys.exit(1)

    print(f"Found {row_count} rows in {SCHEMA}.{TABLE}")

    # Fetch data as DataFrame
    staging_data = local_conn.execute(f"SELECT * FROM {SCHEMA}.{TABLE}").fetchdf()
    local_conn.close()

    # Connect to MotherDuck
    print(f"Connecting to MotherDuck: {MOTHERDUCK_DB}")
    md_conn = duckdb.connect(f"md:{MOTHERDUCK_DB}?motherduck_token={motherduck_token}")

    # Create schema if needed
    md_conn.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    # Drop and recreate table for clean sync
    md_conn.execute(f"DROP TABLE IF EXISTS {SCHEMA}.{TABLE}")

    # Register DataFrame and create table
    md_conn.register("staging_df", staging_data)
    md_conn.execute(f"CREATE TABLE {SCHEMA}.{TABLE} AS SELECT * FROM staging_df")

    # Verify sync
    synced_count = md_conn.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}").fetchone()[
        0
    ]
    print(f"Synced {synced_count} rows to MotherDuck: {MOTHERDUCK_DB}.{SCHEMA}.{TABLE}")

    md_conn.close()
    print("Sync complete!")


if __name__ == "__main__":
    sync_staging_to_motherduck()
