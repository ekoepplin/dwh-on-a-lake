# Validation Rules

This directory contains a simple rule-based validation system for dbt models.

## Architecture

The rule system follows a **separation of concerns** pattern:

- **`rules.py`**: Contains rule function implementations (the logic)
- **`rules_config.yml`**: Contains rule configuration (enabled/disabled, severity, descriptions)
- **`rule_loader.py`**: Loads and combines functions with configuration

This separation allows:
- ✅ Rule logic in Python (type-safe, testable)
- ✅ Rule configuration in YAML (easy to manage, version control)
- ✅ Non-developers can enable/disable rules without touching code
- ✅ Clear separation between "what to check" (functions) and "how to check" (config)

## Adding New Rules

### Step 1: Create a Rule Function

Add your validation function to `rules.py`:

```python
def detect_my_custom_issue(
    models: List[Dict[str, Any]],
    validator
) -> Tuple[bool, List[str]]:
    """Detect my custom issue."""
    errors = []
    for model in models:
        # Your validation logic here
        if some_condition:
            errors.append(f"Model '{model.get('name')}': issue description")
    return len(errors) == 0, errors

# Register the function
RULE_FUNCTIONS["detect_my_custom_issue"] = detect_my_custom_issue
```

### Step 2: Add Rule Configuration

Add the rule to `rules_config.yml`:

```yaml
rules:
  - name: "My custom validation rule"
    func: "detect_my_custom_issue"
    severity: "error"  # or "warning"
    enabled: true
    description: "Checks for my custom issue"
```

That's it! The rule will automatically be loaded and executed during validation.

## Rule Function Signature

Rule functions can accept any of these parameters (they're automatically passed):

- `models`: List of model definitions from YAML
- `validator`: The MetadataValidator instance (for accessing helper methods)
- `yaml_content`: The full YAML content
- `yaml_file`: Path to the YAML file

The function must return: `(is_valid: bool, errors: List[str])`

## Example: Adding a Rule to Check Owner Format

```python
def detect_invalid_owner_format(
    models: List[Dict[str, Any]],
    validator
) -> tuple[bool, List[str]]:
    """Check that business_owner is a valid email."""
    import re
    errors = []
    for model in models:
        if "meta" in model and model.get("meta"):
            meta = model["meta"]
            flattened = validator._flatten_meta(meta)
            owner = flattened.get("data_governance.business_owner", "")
            if owner and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', owner):
                errors.append(
                    f"Model '{model.get('name')}': "
                    f"business_owner '{owner}' is not a valid email"
                )
    return len(errors) == 0, errors

# Add to RULES:
Rule(
    func=detect_invalid_owner_format,
    name="Invalid owner email format",
    severity="error"
)
```

## Disabling Rules

You can disable a rule by editing `rules_config.yml`:

```yaml
rules:
  - name: "Models without corresponding SQL files"
    func: "detect_models_without_sql_file"
    severity: "warning"
    enabled: false  # This rule won't run
```

No code changes needed! Just update the YAML file.

## File Structure

```
validators/
├── rules.py              # Rule function implementations
├── rules_config.yml      # Rule configuration (enabled, severity, etc.)
├── rule_loader.py        # Loads rules from config
└── metadata_validator.py # Main validator that uses rules
```

## Benefits of This Approach

1. **Separation of Concerns**: Logic (Python) vs Configuration (YAML)
2. **Easy Management**: Enable/disable rules without code changes
3. **Version Control**: Config changes are clear in git diffs
4. **Non-Developer Friendly**: Business users can adjust rules
5. **Testable**: Rule functions can be unit tested independently
6. **Scalable**: Easy to add many rules without cluttering code

