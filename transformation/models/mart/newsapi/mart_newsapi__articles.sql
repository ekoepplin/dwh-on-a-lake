{{ config(materialized = 'table') }}
-- Minimal mart model: One time variable, one dimension, and two key metrics
SELECT 
    article_date,
    source_name,
    COUNT(*) AS total_articles,
    SUM(CASE WHEN is_data_engineering_related THEN 1 ELSE 0 END) AS data_engineering_articles
FROM {{ ref('int_newsapi__articles') }}
GROUP BY article_date, source_name
ORDER BY article_date DESC, source_name

