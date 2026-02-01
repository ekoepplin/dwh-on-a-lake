{% macro setup_gcs_credentials() %}
    {# Set up GCS credentials based on target type #}
    {# Supports: local DuckDB, MotherDuck, and BigQuery #}
    {% if execute %}
        {% if target.type == 'duckdb' %}
            {% if target.path is defined and target.path.startswith('md:') %}
                {# MotherDuck: GCS configured at account level via MotherDuck UI #}
                {{ log("MotherDuck target - GCS access via account settings", info=True) }}
            {% else %}
                {# Local DuckDB: install GCS extension and configure credentials #}
                {% set gcs_key_path = env_var('GOOGLE_SERVICE_ACCOUNT_KEY_PATH', '') %}
                {% if gcs_key_path %}
                    -- Install and load the community GCS extension for native GCS support
                    {% do run_query("INSTALL gcs FROM community") %}
                    {% do run_query("LOAD gcs") %}
                    -- Create secret with service account authentication
                    {% do run_query("CREATE SECRET IF NOT EXISTS gcs_secret (TYPE GCP, PROVIDER service_account, SERVICE_ACCOUNT_KEY_PATH '" ~ gcs_key_path ~ "')") %}
                {% endif %}
            {% endif %}
        {% elif target.type == 'bigquery' %}
            {# BigQuery: native GCS integration via service account #}
            {{ log("BigQuery target - native GCS access via service account", info=True) }}
        {% endif %}
    {% endif %}
{% endmacro %}
