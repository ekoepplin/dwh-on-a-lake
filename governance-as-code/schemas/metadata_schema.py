"""Standard metadata schema definitions for data governance."""
from typing import Optional, Dict, Any
from enum import Enum


class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class DataLifecycle(str, Enum):
    """Data lifecycle stages."""
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"


class StandardMetadata:
    """Standard metadata structure for dbt models."""
    
    REQUIRED_FIELDS = {
        "data_governance.business_owner": str,
        "data_governance.team_owner": str,
        "data_governance.data_classification": str,
        "data_governance.data_lifecycle": str,
    }
    
    OPTIONAL_FIELDS = {
        "data_governance.has_pii": bool,
        "data_governance.pii_retention_days": int,
        "data_governance.can_be_referenced": bool,
        "data_governance.update_schedule": str,
        "data_governance.sla": str,
    }
    
    @staticmethod
    def validate_metadata(meta: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate metadata against standard schema.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field, field_type in StandardMetadata.REQUIRED_FIELDS.items():
            if field not in meta:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(meta[field], field_type):
                errors.append(
                    f"Field {field} must be of type {field_type.__name__}, "
                    f"got {type(meta[field]).__name__}"
                )
        
        # Validate data_classification
        if "data_governance.data_classification" in meta:
            classification = meta["data_governance.data_classification"]
            valid_classifications = [c.value for c in DataClassification]
            if classification not in valid_classifications:
                errors.append(
                    f"Invalid data_classification: {classification}. "
                    f"Must be one of: {valid_classifications}"
                )
        
        # Validate data_lifecycle
        if "data_governance.data_lifecycle" in meta:
            lifecycle = meta["data_governance.data_lifecycle"]
            valid_lifecycles = [l.value for l in DataLifecycle]
            if lifecycle not in valid_lifecycles:
                errors.append(
                    f"Invalid data_lifecycle: {lifecycle}. "
                    f"Must be one of: {valid_lifecycles}"
                )
        
        # Validate PII fields if has_pii is True
        if meta.get("data_governance.has_pii") is True:
            if "data_governance.pii_retention_days" not in meta:
                errors.append(
                    "Field data_governance.pii_retention_days is required "
                    "when data_governance.has_pii is True"
                )
        
        return len(errors) == 0, errors

