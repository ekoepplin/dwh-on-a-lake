-- Intermediate model: Clean and enrich articles with basic derived fields
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
    _dlt_id,
    -- Date dimension
    CAST(published_at AS DATE) AS article_date,
    -- Article categorization using macro
    {{ categorize_topic('title') }} AS topic_category,
    -- Flags using macro for cleaner code
    {{ flag_contains_any('title', ['data engineering', 'data pipeline', 'etl', 'data warehouse']) }}
        OR {{ flag_contains_any('description', ['data engineering', 'data pipeline', 'etl', 'data warehouse']) }} AS is_data_engineering_related,
    {{ flag_contains_any('title', ['ai', 'artificial intelligence', 'machine learning']) }}
        OR {{ flag_contains_any('description', ['ai', 'artificial intelligence', 'machine learning']) }} AS is_ai_related
FROM {{ ref('stg_newsapi__articles_us_en') }}

WHERE published_at IS NOT NULL
