"""Rule function definitions for metadata validation.

Rule functions contain the validation logic.
Rule configuration (enabled/disabled, severity) is in rules_config.yml
"""
from typing import List, Dict, Any, Tuple
from pathlib import Path


# Rule function registry - maps function names to actual functions
RULE_FUNCTIONS = {}


def detect_models_with_empty_metadata(
    models: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """Detect models that have no metadata defined."""
    errors = []
    for model in models:
        if "meta" not in model or not model.get("meta"):
            errors.append(f"Model '{model.get('name', 'unknown')}' has no metadata")
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_models_with_empty_metadata"] = detect_models_with_empty_metadata


def detect_models_with_invalid_metadata(
    models: List[Dict[str, Any]],
    validator
) -> Tuple[bool, List[str]]:
    """Detect models with invalid metadata (using StandardMetadata validation)."""
    errors = []
    for model in models:
        if "meta" in model and model.get("meta"):
            meta = model["meta"]
            flattened_meta = validator._flatten_meta(meta)
            is_valid, validation_errors = validator._validate_metadata_schema(flattened_meta)
            if not is_valid:
                for error in validation_errors:
                    errors.append(f"Model '{model.get('name', 'unknown')}': {error}")
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_models_with_invalid_metadata"] = detect_models_with_invalid_metadata


def detect_models_without_sql_file(
    models: List[Dict[str, Any]],
    validator,
    yaml_file: Path
) -> Tuple[bool, List[str]]:
    """Detect models that don't have a corresponding SQL file."""
    errors = []
    for model in models:
        model_name = model.get("name")
        if not model_name:
            continue
        sql_file = validator.find_sql_file_for_model(model_name, yaml_file)
        if not sql_file:
            errors.append(f"Model '{model_name}' has no corresponding SQL file")
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_models_without_sql_file"] = detect_models_without_sql_file


def detect_column_mismatches(
    models: List[Dict[str, Any]],
    validator,
    yaml_content: Dict[str, Any],
    yaml_file: Path
) -> Tuple[bool, List[str]]:
    """Detect mismatches between SQL columns and YAML column definitions."""
    errors = []
    for model in models:
        model_name = model.get("name")
        if not model_name:
            continue
        sql_file = validator.find_sql_file_for_model(model_name, yaml_file)
        if sql_file:
            is_valid, validation_errors = validator.validate_column_sync(
                model_name, sql_file, yaml_content
            )
            if not is_valid:
                errors.extend(validation_errors)
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_column_mismatches"] = detect_column_mismatches


def detect_pii_without_retention_days(
    models: List[Dict[str, Any]],
    validator
) -> Tuple[bool, List[str]]:
    """Detect PII models that don't have retention_days specified."""
    errors = []
    for model in models:
        if "meta" in model and model.get("meta"):
            meta = model["meta"]
            flattened = validator._flatten_meta(meta)
            has_pii = flattened.get("data_governance.has_pii", False)
            
            if has_pii:
                retention_days = flattened.get("data_governance.pii_retention_days")
                if retention_days is None:
                    errors.append(
                        f"Model '{model.get('name', 'unknown')}': "
                        f"has_pii is True but pii_retention_days is not specified"
                    )
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_pii_without_retention_days"] = detect_pii_without_retention_days


def detect_invalid_retention_periods(
    models: List[Dict[str, Any]],
    validator
) -> Tuple[bool, List[str]]:
    """Detect models with retention periods that don't meet policy requirements."""
    import yaml
    from pathlib import Path
    
    errors = []
    
    # Load retention policies
    policies_path = Path(__file__).parent.parent / "policies" / "retention_policies.yml"
    policies = {}
    if policies_path.exists():
        with open(policies_path, 'r') as f:
            policies = yaml.safe_load(f) or {}
    
    retention_config = policies.get("retention_policies", {})
    pii_config = retention_config.get("pii_retention", {})
    min_days = pii_config.get("minimum_days", 90)
    max_days = pii_config.get("maximum_days", 2555)
    
    for model in models:
        if "meta" in model and model.get("meta"):
            meta = model["meta"]
            flattened = validator._flatten_meta(meta)
            has_pii = flattened.get("data_governance.has_pii", False)
            
            if has_pii:
                retention_days = flattened.get("data_governance.pii_retention_days")
                if retention_days is not None:
                    if retention_days < min_days:
                        errors.append(
                            f"Model '{model.get('name', 'unknown')}': "
                            f"pii_retention_days ({retention_days}) is below minimum ({min_days} days)"
                        )
                    if retention_days > max_days:
                        errors.append(
                            f"Model '{model.get('name', 'unknown')}': "
                            f"pii_retention_days ({retention_days}) exceeds maximum ({max_days} days)"
                        )
    
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_invalid_retention_periods"] = detect_invalid_retention_periods


def detect_pii_without_retention_date_field(
    models: List[Dict[str, Any]],
    validator,
    yaml_content: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """Detect PII models that don't have a retention_date_field specified in columns."""
    errors = []
    
    for model in models:
        if "meta" in model and model.get("meta"):
            meta = model["meta"]
            flattened = validator._flatten_meta(meta)
            has_pii = flattened.get("data_governance.has_pii", False)
            
            if has_pii:
                model_name = model.get("name")
                # Check if any column has retention_date_field flag
                has_retention_field = False
                
                if "columns" in model:
                    for col in model["columns"]:
                        col_meta = col.get("meta", {})
                        col_flattened = validator._flatten_meta(col_meta)
                        if col_flattened.get("data_governance.retention_date_field") is True:
                            has_retention_field = True
                            break
                
                if not has_retention_field:
                    errors.append(
                        f"Model '{model_name}': "
                        f"has_pii is True but no column has retention_date_field set to true"
                    )
    
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_pii_without_retention_date_field"] = detect_pii_without_retention_date_field


def detect_pii_without_anonymization_method(
    models: List[Dict[str, Any]],
    validator,
    yaml_content: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """Detect PII columns that don't have anonymization_method specified."""
    errors = []
    
    for model in models:
        if "meta" in model and model.get("meta"):
            meta = model["meta"]
            flattened = validator._flatten_meta(meta)
            has_pii = flattened.get("data_governance.has_pii", False)
            
            if has_pii:
                model_name = model.get("name")
                # Check columns for PII
                if "columns" in model:
                    for col in model["columns"]:
                        col_meta = col.get("meta", {})
                        col_flattened = validator._flatten_meta(col_meta)
                        is_pii = col_flattened.get("data_governance.is_pii", False)
                        
                        if is_pii:
                            anonymization_method = col_flattened.get(
                                "data_governance.anonymization_method"
                            )
                            if not anonymization_method:
                                errors.append(
                                    f"Model '{model_name}', Column '{col.get('name', 'unknown')}': "
                                    f"is_pii is True but anonymization_method is not specified"
                                )
    
    return len(errors) == 0, errors


RULE_FUNCTIONS["detect_pii_without_anonymization_method"] = detect_pii_without_anonymization_method

