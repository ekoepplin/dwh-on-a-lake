-- Raw source from DuckLake - already deduplicated at ingestion time via merge
SELECT * FROM {{ source('newsapi_ducklake', 'articles_us_en') }}
