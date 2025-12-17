"""Validator for dbt model metadata against governance standards."""
import os
import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger

# Add parent directory to path to import schemas
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.metadata_schema import StandardMetadata
from validators.rule_loader import get_default_rules, Rule


class MetadataValidator:
    """Validates dbt model metadata against governance standards."""
    
    def __init__(self, dbt_project_path: str, rules: Optional[List[Rule]] = None, rules_config_path: Optional[Path] = None):
        self.dbt_project_path = Path(dbt_project_path)
        self.models_path = self.dbt_project_path / "models"
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        
        # Load rules from config file if not provided
        if rules is None:
            from validators.rule_loader import load_rules
            try:
                self.rules = load_rules(rules_config_path)
            except FileNotFoundError:
                logger.warning("Rules config file not found, using default rules")
                self.rules = get_default_rules()
        else:
            self.rules = rules
    
    def find_yaml_files(self) -> List[Path]:
        """Find all YAML files in models directory."""
        yaml_files = []
        if self.models_path.exists():
            yaml_files = list(self.models_path.rglob("*.yml")) + \
                         list(self.models_path.rglob("*.yaml"))
        return yaml_files
    
    def find_sql_files(self) -> List[Path]:
        """Find all SQL model files in models directory."""
        sql_files = []
        if self.models_path.exists():
            sql_files = list(self.models_path.rglob("*.sql"))
        return sql_files
    
    def find_sql_file_for_model(self, model_name: str, yaml_file_path: Path) -> Optional[Path]:
        """Find the corresponding SQL file for a model."""
        # Try to find SQL file in the same directory as YAML
        yaml_dir = yaml_file_path.parent
        sql_file = yaml_dir / f"{model_name}.sql"
        
        if sql_file.exists():
            return sql_file
        
        # If not found, search in models directory
        sql_files = self.find_sql_files()
        for sql_file in sql_files:
            if sql_file.stem == model_name:
                return sql_file
        
        return None
    
    def extract_columns_from_sql(self, sql_file: Path) -> List[str]:
        """
        Extract column names from a SQL SELECT statement.
        
        This is a simplified parser that:
        1. Finds the final SELECT statement (after all CTEs)
        2. Extracts column names from the SELECT clause
        3. Handles basic aliases (column AS alias)
        """
        try:
            with open(sql_file, 'r') as f:
                content = f.read()
            
            # Remove comments
            content = re.sub(r'--.*?$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # Find all SELECT statements
            # Pattern to match SELECT ... FROM (handling CTEs)
            select_pattern = r'SELECT\s+(.*?)\s+FROM'
            
            matches = list(re.finditer(select_pattern, content, re.IGNORECASE | re.DOTALL))
            
            if not matches:
                return []
            
            # Get the last SELECT (final output)
            last_match = matches[-1]
            select_clause = last_match.group(1).strip()
            
            # Split by comma, handling nested parentheses
            columns = []
            current_col = ""
            paren_depth = 0
            
            for char in select_clause:
                if char == '(':
                    paren_depth += 1
                    current_col += char
                elif char == ')':
                    paren_depth -= 1
                    current_col += char
                elif char == ',' and paren_depth == 0:
                    # End of column
                    col = current_col.strip()
                    if col:
                        # Extract column name (handle AS alias)
                        col_name = self._extract_column_name(col)
                        if col_name:
                            columns.append(col_name)
                    current_col = ""
                else:
                    current_col += char
            
            # Add last column
            if current_col.strip():
                col = current_col.strip()
                col_name = self._extract_column_name(col)
                if col_name:
                    columns.append(col_name)
            
            return columns
            
        except Exception as e:
            self.warnings.append({
                "message": f"Failed to parse SQL file {sql_file}: {str(e)}"
            })
            return []
    
    def _extract_column_name(self, column_expr: str) -> Optional[str]:
        """Extract column name from a column expression, handling aliases."""
        column_expr = column_expr.strip()
        
        # Handle AS alias: column AS alias or column alias
        # Pattern: ... AS alias or ... alias
        as_pattern = r'\s+AS\s+(\w+)'
        match = re.search(as_pattern, column_expr, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # If no AS, check if it's a simple column reference
        # Remove any function calls or expressions
        # Simple case: just a column name
        simple_col = re.match(r'^[\w.]+$', column_expr)
        if simple_col:
            # Get the last part after dot (table.column -> column)
            parts = column_expr.split('.')
            return parts[-1]
        
        # For complex expressions, try to extract a reasonable name
        # This is a fallback - may not be perfect
        # Look for quoted identifiers
        quoted = re.search(r'["\']([^"\']+)["\']', column_expr)
        if quoted:
            return quoted.group(1)
        
        # Last resort: use the expression itself (truncated)
        return column_expr[:50] if column_expr else None
    
    def extract_columns_from_yaml(self, yaml_content: Dict[str, Any], model_name: str) -> List[str]:
        """Extract column names from YAML content for a specific model."""
        columns = []
        
        if "models" in yaml_content:
            for model in yaml_content["models"]:
                if model.get("name") == model_name:
                    if "columns" in model:
                        for col in model["columns"]:
                            if "name" in col:
                                columns.append(col["name"])
                    break
        
        return columns
    
    def validate_column_sync(self, model_name: str, sql_file: Path, yaml_content: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that columns in SQL match columns in YAML.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        sql_columns = self.extract_columns_from_sql(sql_file)
        yaml_columns = self.extract_columns_from_yaml(yaml_content, model_name)
        
        if not sql_columns:
            errors.append(f"Could not extract columns from SQL file: {sql_file}")
            return False, errors
        
        if not yaml_columns:
            errors.append(f"No columns defined in YAML for model '{model_name}'")
            return False, errors
        
        # Check column count
        if len(sql_columns) != len(yaml_columns):
            errors.append(
                f"Column count mismatch: SQL has {len(sql_columns)} columns, "
                f"YAML has {len(yaml_columns)} columns"
            )
        
        # Check for missing columns in YAML
        missing_in_yaml = set(sql_columns) - set(yaml_columns)
        if missing_in_yaml:
            errors.append(
                f"Columns in SQL but not in YAML: {sorted(missing_in_yaml)}"
            )
        
        # Check for extra columns in YAML (warn, not error)
        extra_in_yaml = set(yaml_columns) - set(sql_columns)
        if extra_in_yaml:
            self.warnings.append({
                "message": (
                    f"Model '{model_name}': Columns in YAML but not in SQL: "
                    f"{sorted(extra_in_yaml)}"
                )
            })
        
        return len(errors) == 0, errors
    
    def parse_yaml_file(self, yaml_file: Path) -> Dict[str, Any]:
        """Parse a YAML file and return its contents."""
        try:
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f)
                if content is None:
                    return {}
                return content
        except Exception as e:
            self.errors.append({
                "file": str(yaml_file),
                "error": f"Failed to parse YAML: {str(e)}"
            })
            return {}
    
    def extract_model_metadata(self, yaml_content: Dict[str, Any], file_path: str) -> List[Dict[str, Any]]:
        """Extract model metadata from YAML content."""
        models = []
        
        if "models" in yaml_content:
            for model in yaml_content["models"]:
                if "meta" in model:
                    models.append({
                        "name": model.get("name", "unknown"),
                        "meta": model["meta"],
                        "file": file_path
                    })
        
        return models
    
    def _validate_metadata_schema(self, flattened_meta: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate metadata against standard schema (internal method for rules)."""
        return StandardMetadata.validate_metadata(flattened_meta)
    
    def validate_model(self, model: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single model's metadata."""
        model_name = model["name"]
        meta = model["meta"]
        
        # Flatten nested meta structure for validation
        flattened_meta = self._flatten_meta(meta)
        
        # Validate against standard schema
        is_valid, errors = StandardMetadata.validate_metadata(flattened_meta)
        
        # Format errors with model name
        formatted_errors = [
            f"Model '{model_name}': {error}" for error in errors
        ]
        
        return is_valid, formatted_errors
    
    def _flatten_meta(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested meta structure (e.g., data_governance.business_owner)."""
        flattened = {}
        
        for key, value in meta.items():
            if isinstance(value, dict):
                # Handle nested structure like data_governance: { business_owner: ... }
                for nested_key, nested_value in value.items():
                    flattened_key = f"{key}.{nested_key}"
                    flattened[flattened_key] = nested_value
            else:
                flattened[key] = value
        
        return flattened
    
    def validate_all(self) -> bool:
        """Validate all models in the dbt project using configured rules."""
        yaml_files = self.find_yaml_files()
        
        if not yaml_files:
            self.warnings.append({
                "message": f"No YAML files found in {self.models_path}"
            })
            return True
        
        all_valid = True
        
        for yaml_file in yaml_files:
            yaml_content = self.parse_yaml_file(yaml_file)
            
            if not yaml_content:
                continue
            
            # Extract all models from YAML
            models = yaml_content.get("models", [])
            
            # Run all enabled rules
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                # Execute rule with appropriate arguments
                try:
                    # Determine which arguments the rule function needs
                    import inspect
                    sig = inspect.signature(rule.func)
                    params = list(sig.parameters.keys())
                    
                    # Build arguments based on rule function signature
                    rule_args = {}
                    if "models" in params:
                        rule_args["models"] = models
                    if "validator" in params:
                        rule_args["validator"] = self
                    if "yaml_content" in params:
                        rule_args["yaml_content"] = yaml_content
                    if "yaml_file" in params:
                        rule_args["yaml_file"] = yaml_file
                    
                    # Execute rule
                    is_valid, rule_errors = rule.func(**rule_args)
                    
                    if not is_valid:
                        all_valid = False
                        for error in rule_errors:
                            # Try to extract model name from error message
                            model_name = "unknown"
                            for model in models:
                                model_name_in_model = model.get("name")
                                if model_name_in_model and model_name_in_model in error:
                                    model_name = model_name_in_model
                                    break
                            
                            if rule.severity == "error":
                                self.errors.append({
                                    "file": str(yaml_file),
                                    "model": model_name,
                                    "error": error,
                                    "rule": rule.name
                                })
                            else:
                                self.warnings.append({
                                    "message": f"[{rule.name}] {error}",
                                    "file": str(yaml_file),
                                    "model": model_name
                                })
                
                except Exception as e:
                    logger.warning(f"Rule '{rule.name}' failed: {str(e)}")
                    continue
        
        return all_valid
    
    def print_report(self):
        """Print validation report."""
        logger.info("\n" + "="*60)
        logger.info("DATA GOVERNANCE METADATA VALIDATION REPORT")
        logger.info("="*60)
        
        if self.errors:
            logger.error(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"  • {error['file']}")
                logger.error(f"    Model: {error['model']}")
                if 'rule' in error:
                    logger.error(f"    Rule: {error['rule']}")
                logger.error(f"    Error: {error['error']}\n")
        else:
            logger.success("\n✅ No errors found!")
        
        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"  • {warning['message']}\n")
        
        logger.info("="*60)
        
        if self.errors:
            logger.error(f"\n❌ Validation FAILED: {len(self.errors)} error(s) found")
            return False
        else:
            logger.success(f"\n✅ Validation PASSED")
            return True


def main():
    """Main entry point for validation script."""
    import argparse
    
    # Configure logger for cleaner report output
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{message}</level>",
        level="INFO"
    )
    
    parser = argparse.ArgumentParser(
        description="Validate dbt model metadata against governance standards"
    )
    parser.add_argument(
        "--dbt-project",
        type=str,
        default="transformation",
        help="Path to dbt project directory (default: transformation)"
    )
    
    args = parser.parse_args()
    
    # Resolve path relative to script location
    script_dir = Path(__file__).parent.parent.parent
    dbt_project_path = script_dir / args.dbt_project
    
    if not dbt_project_path.exists():
        logger.error(f"❌ Error: dbt project path does not exist: {dbt_project_path}")
        sys.exit(1)
    
    validator = MetadataValidator(str(dbt_project_path))
    is_valid = validator.validate_all()
    success = validator.print_report()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

