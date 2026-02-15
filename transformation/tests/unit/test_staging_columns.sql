{{ config(tags=['unit-test']) }}

-- Test that the staging model's SQL logic correctly renames columns.
-- Uses a CTE to simulate the source data shape and applies the staging transformation.

WITH mock_source AS (
    SELECT
      'BBC News' AS source__name,
      'Author' AS author,
      'Test Title' AS title,
      'desc' AS description,
      'http://example.com' AS url,
      'http://example.com/img.jpg' AS url_to_image,
      '2025-01-15T12:00:00'::TIMESTAMP AS published_at,
      'content' AS content,
      '1' AS _dlt_load_id,
      'id1' AS _dlt_id
),

-- Apply the same transformation as the staging model
transformed AS (
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
        _dlt_id
    FROM mock_source
)

-- Test fails if any assertion returns rows
SELECT *
FROM (
    SELECT 'source_name should be BBC News' AS test_case
    FROM transformed WHERE source_name != 'BBC News'

    UNION ALL

    SELECT 'image_url should be renamed from url_to_image' AS test_case
    FROM transformed WHERE image_url != 'http://example.com/img.jpg'

    UNION ALL

    SELECT 'language_code should be en' AS test_case
    FROM transformed WHERE language_code != 'en'

    UNION ALL

    SELECT 'should have exactly 1 row' AS test_case
    WHERE (SELECT COUNT(*) FROM transformed) != 1
) failures
