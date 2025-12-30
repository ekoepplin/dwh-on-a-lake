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
    -- Article categorization
    CASE 
        WHEN LOWER(title) LIKE '%microsoft copilot%' OR LOWER(title) LIKE '%copilot%' THEN 'Microsoft Copilot'
        WHEN LOWER(title) LIKE '%ai%' OR LOWER(title) LIKE '%artificial intelligence%' THEN 'AI'
        WHEN LOWER(title) LIKE '%microsoft%' THEN 'Microsoft'
        WHEN LOWER(title) LIKE '%tech%' OR LOWER(title) LIKE '%technology%' THEN 'Tech'
        WHEN LOWER(title) LIKE '%startup%' OR LOWER(title) LIKE '%venture%' THEN 'Startups'
        ELSE 'Other'
    END AS topic_category,
    -- Flags
    CASE WHEN LOWER(title) LIKE '%microsoft copilot%' OR LOWER(title) LIKE '%copilot%' OR LOWER(description) LIKE '%microsoft copilot%' OR LOWER(description) LIKE '%copilot%' THEN TRUE ELSE FALSE END AS is_copilot_related,
    CASE WHEN LOWER(title) LIKE '%microsoft%' OR LOWER(description) LIKE '%microsoft%' THEN TRUE ELSE FALSE END AS is_microsoft_related,
    CASE WHEN LOWER(title) LIKE '%ai%' OR LOWER(description) LIKE '%ai%' THEN TRUE ELSE FALSE END AS is_ai_related
FROM {{ ref('stg_newsapi__articles_us_en') }}
WHERE published_at IS NOT NULL 