SELECT 
    article_date,
    SUM(total_articles) AS total_articles,
    SUM(copilot_articles) AS copilot_articles
FROM ingest_newsapi_v1.mart_newsapi__articles
GROUP BY article_date
ORDER BY article_date DESC

