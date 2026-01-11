{{
    config(
        enabled = (target.name == 'dev')
    )
}}
-- Deduplicate articles since GCS storage is append-only
-- Keep the latest version of each article based on URL (primary key)
-- Only runs in dev - synced to MotherDuck for prod
WITH ranked_articles AS (
    SELECT
        source__name AS source_name,
        author,
        title,
        description,
        url,
        url_to_image AS image_url,
        published_at,
        content,
        'en' AS language_code,
        _dlt_load_id,
        _dlt_id,
        ROW_NUMBER() OVER (
            PARTITION BY url
            ORDER BY _dlt_load_id DESC
        ) AS row_num
    FROM {{ ref('src_newsapi__articles_us_en') }}
)

SELECT
    source_name,
    author,
    title,
    description,
    url,
    image_url,
    published_at,
    content,
    language_code,
    _dlt_load_id,
    _dlt_id
FROM ranked_articles
WHERE row_num = 1
