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
    {{ flag_contains_any('title', ['microsoft copilot', 'copilot']) }}
        OR {{ flag_contains_any('description', ['microsoft copilot', 'copilot']) }} AS is_copilot_related,
    {{ flag_contains_any('title', ['microsoft']) }}
        OR {{ flag_contains_any('description', ['microsoft']) }} AS is_microsoft_related,
    {{ flag_contains_any('title', ['ai']) }}
        OR {{ flag_contains_any('description', ['ai']) }} AS is_ai_related
FROM {{ ref('stg_newsapi__articles_us_en') }}
WHERE published_at IS NOT NULL
