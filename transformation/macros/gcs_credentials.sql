{% macro setup_gcs_credentials() %}
    {# Only set up GCS credentials for local DuckDB (dev) #}
    {# MotherDuck (prod) uses its own GCS integration configured in the UI #}
    {% if execute and target.name == 'dev' %}
        {% set gcs_key_path = env_var('GOOGLE_SERVICE_ACCOUNT_KEY_PATH', '') %}
        {% if gcs_key_path %}
            -- Install and load the community GCS extension for native GCS support
            {% do run_query("INSTALL gcs FROM community") %}
            {% do run_query("LOAD gcs") %}
            -- Create secret with service account authentication
            {% do run_query("CREATE SECRET IF NOT EXISTS gcs_secret (TYPE GCP, PROVIDER service_account, SERVICE_ACCOUNT_KEY_PATH '" ~ gcs_key_path ~ "')") %}
        {% endif %}
    {% endif %}
{% endmacro %}
