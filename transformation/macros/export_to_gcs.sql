{% macro export_to_gcs() %}
    {# Export tables to local Parquet, then sync to GCS #}
    {# Run with: dbt run-operation export_to_gcs #}
    {# Note: This exports to /tmp/dbt_export/, then use sync_to_gcs.sh to upload #}

    {% if execute %}
        {% set export_dir = '/tmp/dbt_export' %}

        {% set models_to_export = [
            ('prod', 'stg_newsapi__articles_us_en', 'staging'),
            ('prod', 'int_newsapi__articles', 'intermediate'),
            ('prod', 'mart_newsapi__articles', 'mart')
        ] %}

        {% for schema, model, layer in models_to_export %}
            {% set local_path = export_dir ~ '/' ~ layer ~ '/' ~ model ~ '.parquet' %}
            {% set export_sql %}
                COPY "newsapi_articles"."{{ schema }}"."{{ model }}"
                TO '{{ local_path }}' (FORMAT PARQUET)
            {% endset %}

            {{ log("Exporting " ~ model ~ " to " ~ local_path, info=True) }}
            {% do run_query(export_sql) %}
            {{ log("Exported " ~ model, info=True) }}
        {% endfor %}

        {{ log("", info=True) }}
        {{ log("Local export complete. Run this to sync to GCS:", info=True) }}
        {{ log("gsutil -m rsync -r /tmp/dbt_export/ gs://dwh-on-a-lake-prod/dbt/", info=True) }}
    {% endif %}
{% endmacro %}
