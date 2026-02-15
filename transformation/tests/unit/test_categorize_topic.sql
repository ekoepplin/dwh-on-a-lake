{{ config(tags=['unit-test']) }}

-- Test that the categorize_topic macro produces correct categories.
-- This is a standalone SQL test that validates macro logic directly.

WITH test_data AS (
    SELECT 'New data pipeline tool released' AS title
    UNION ALL SELECT 'AI startup raises funding'
    UNION ALL SELECT 'Machine learning breakthrough announced'
    UNION ALL SELECT 'Random news about sports'
    UNION ALL SELECT 'New technology company launches'
    UNION ALL SELECT 'Startup venture capital news'
),

categorized AS (
    SELECT
        title,
        {{ categorize_topic('title') }} AS topic_category
    FROM test_data
)

SELECT *
FROM (
    -- Verify Data Engineering category
    SELECT 'data pipeline should be Data Engineering' AS test_case
    FROM categorized
    WHERE title = 'New data pipeline tool released'
      AND topic_category != 'Data Engineering'

    UNION ALL

    -- Verify AI category
    SELECT 'AI startup should be AI' AS test_case
    FROM categorized
    WHERE title = 'AI startup raises funding'
      AND topic_category != 'AI'

    UNION ALL

    -- Verify AI category for machine learning
    SELECT 'Machine learning should be AI' AS test_case
    FROM categorized
    WHERE title = 'Machine learning breakthrough announced'
      AND topic_category != 'AI'

    UNION ALL

    -- Verify Other category
    SELECT 'Sports should be Other' AS test_case
    FROM categorized
    WHERE title = 'Random news about sports'
      AND topic_category != 'Other'

    UNION ALL

    -- Verify Tech category
    SELECT 'Technology should be Tech' AS test_case
    FROM categorized
    WHERE title = 'New technology company launches'
      AND topic_category != 'Tech'

    UNION ALL

    -- Verify Startups category
    SELECT 'Startup venture should be Startups' AS test_case
    FROM categorized
    WHERE title = 'Startup venture capital news'
      AND topic_category != 'Startups'
) failures
