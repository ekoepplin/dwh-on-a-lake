SELECT 
    source_name,
    SUM(total_articles) AS total_articles,
    SUM(copilot_articles) AS copilot_articles
FROM ingest_newsapi_v1.mart_newsapi__articles
GROUP BY source_name
ORDER BY total_articles DESC

