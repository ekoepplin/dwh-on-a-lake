{% macro get_standard_metadata(
    business_owner,
    team_owner,
    data_classification,
    data_lifecycle,
    has_pii=false,
    pii_retention_days=none,
    can_be_referenced=true,
    update_schedule=none,
    sla=none
) %}
    {#-
    Macro to generate standardized metadata structure.
    
    Usage in model YAML:
        meta:
          {{ governance.get_standard_metadata(
            business_owner="alice@company.com",
            team_owner="data-team",
            data_classification="CONFIDENTIAL",
            data_lifecycle="PRODUCTION"
          ) }}
    -#}
    
    {% set metadata = {
        "data_governance": {
            "business_owner": business_owner,
            "team_owner": team_owner,
            "data_classification": data_classification,
            "data_lifecycle": data_lifecycle,
            "has_pii": has_pii,
            "can_be_referenced": can_be_referenced
        }
    } %}
    
    {% if pii_retention_days is not none %}
        {% set _ = metadata["data_governance"].update({"pii_retention_days": pii_retention_days}) %}
    {% endif %}
    
    {% if update_schedule is not none %}
        {% set _ = metadata["data_governance"].update({"update_schedule": update_schedule}) %}
    {% endif %}
    
    {% if sla is not none %}
        {% set _ = metadata["data_governance"].update({"sla": sla}) %}
    {% endif %}
    
    {{ return(metadata) }}
{% endmacro %}


{% macro validate_metadata_required(model_name, meta) %}
    {#-
    Macro to validate that required metadata fields are present.
    This can be used in dbt tests.
    -#}
    
    {% set required_fields = [
        "data_governance.business_owner",
        "data_governance.team_owner",
        "data_governance.data_classification",
        "data_governance.data_lifecycle"
    ] %}
    
    {% set missing_fields = [] %}
    
    {% for field in required_fields %}
        {% if field not in meta %}
            {% set _ = missing_fields.append(field) %}
        {% endif %}
    {% endfor %}
    
    {% if missing_fields | length > 0 %}
        {% do exceptions.raise_compiler_error(
            "Model " ~ model_name ~ " is missing required metadata fields: " ~ 
            missing_fields | join(", ")
        ) %}
    {% endif %}
    
    {{ return(true) }}
{% endmacro %}

