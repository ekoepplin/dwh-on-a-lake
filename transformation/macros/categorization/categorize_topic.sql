{% macro categorize_topic(title_column, default_category='Other') %}
    {#-
    Macro to categorize articles based on title patterns.
    Uses the ref_topic_categories seed table for pattern matching rules.

    Args:
        title_column: The column name containing the article title
        default_category: Category to use when no pattern matches (default: 'Other')

    Returns:
        SQL CASE statement for topic categorization
    -#}
    CASE
        WHEN LOWER({{ title_column }}) LIKE '%data engineering%' THEN 'Data Engineering'
        WHEN LOWER({{ title_column }}) LIKE '%data pipeline%' THEN 'Data Engineering'
        WHEN LOWER({{ title_column }}) LIKE '%etl%' THEN 'Data Engineering'
        WHEN LOWER({{ title_column }}) LIKE '%data warehouse%' THEN 'Data Engineering'
        WHEN LOWER({{ title_column }}) LIKE '%artificial intelligence%' THEN 'AI'
        WHEN LOWER({{ title_column }}) LIKE '%ai%' THEN 'AI'
        WHEN LOWER({{ title_column }}) LIKE '%machine learning%' THEN 'AI'
        WHEN LOWER({{ title_column }}) LIKE '%technology%' THEN 'Tech'
        WHEN LOWER({{ title_column }}) LIKE '%tech%' THEN 'Tech'
        WHEN LOWER({{ title_column }}) LIKE '%startup%' THEN 'Startups'
        WHEN LOWER({{ title_column }}) LIKE '%venture%' THEN 'Startups'
        ELSE '{{ default_category }}'
    END
{% endmacro %}


{% macro is_pattern_match(column, pattern) %}
    {#-
    Helper macro to check if a column contains a pattern (case-insensitive).

    Args:
        column: The column name to check
        pattern: The pattern to search for

    Returns:
        Boolean expression
    -#}
    LOWER({{ column }}) LIKE '%' || LOWER('{{ pattern }}') || '%'
{% endmacro %}


{% macro flag_contains_any(column, patterns) %}
    {#-
    Macro to create a boolean flag that checks if column contains any of the patterns.

    Args:
        column: The column name to check
        patterns: List of patterns to search for

    Returns:
        Boolean CASE expression
    -#}
    CASE WHEN
        {% for pattern in patterns %}
            LOWER({{ column }}) LIKE '%{{ pattern | lower }}%'
            {%- if not loop.last %} OR {% endif %}
        {% endfor %}
    THEN TRUE ELSE FALSE END
{% endmacro %}
