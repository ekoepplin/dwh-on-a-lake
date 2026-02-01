{% macro create_bigquery_external_table(table_name, gcs_uri) %}
    {# Create a BigQuery external table pointing to Parquet files in GCS #}
    {# This macro only runs when targeting BigQuery #}
    {% if target.type != 'bigquery' %}
        {{ log("Skipping external table creation - not a BigQuery target", info=True) }}
        {{ return('') }}
    {% endif %}

    {% if execute %}
        {% set create_sql %}
            CREATE OR REPLACE EXTERNAL TABLE `{{ target.project }}.{{ target.dataset }}.{{ table_name }}`
            OPTIONS (
                format = 'PARQUET',
                uris = ['{{ gcs_uri }}']
            )
        {% endset %}

        {{ log("Creating BigQuery external table: " ~ table_name, info=True) }}
        {% do run_query(create_sql) %}
        {{ log("External table created successfully", info=True) }}
    {% endif %}
{% endmacro %}
