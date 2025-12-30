SELECT 
    article_date,
    source_name,
    total_articles,
    copilot_articles
FROM ingest_newsapi_v1.mart_newsapi__articles
ORDER BY article_date DESC, source_name
LIMIT 50

