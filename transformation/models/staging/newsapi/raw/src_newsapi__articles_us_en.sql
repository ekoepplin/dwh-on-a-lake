{{
    config(
        enabled = (target.name == 'dev')
    )
}}
-- Read all Parquet files from GCS bucket (append-only lake storage)
-- Only runs in dev - prod uses synced staging table in MotherDuck
with source as (
    select * from read_parquet(
        'gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet',
        hive_partitioning = false
    )
)

select * from source