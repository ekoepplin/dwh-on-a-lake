-- Read all Parquet files from GCS bucket (append-only lake storage from dlt)
-- This is the raw source layer - no transformations, just reading from lake
-- Supports multiple targets: DuckDB/MotherDuck (read_parquet) and BigQuery (external table)

{% if target.type == 'duckdb' %}
-- DuckDB/MotherDuck: use read_parquet() to query GCS directly
select * from read_parquet(
    'gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet',
    hive_partitioning = false
)

{% elif target.type == 'bigquery' %}
-- BigQuery: use external table pointing to GCS Parquet files
-- External table must be created first via: dbt run-operation create_bigquery_external_table
select * from `{{ target.project }}.{{ target.dataset }}.ext_newsapi__articles_us_en`
{% endif %}