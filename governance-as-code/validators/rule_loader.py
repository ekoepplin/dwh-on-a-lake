"""Load and configure validation rules from config file."""
import yaml
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from validators.rules import RULE_FUNCTIONS


@dataclass
class Rule:
    """A validation rule for dbt models."""
    func: callable
    name: str
    severity: str = "error"  # "error" or "warning"
    enabled: bool = True
    description: str = ""
    
    def __call__(self, *args, **kwargs):
        """Execute the rule function."""
        if not self.enabled:
            return True, []
        return self.func(*args, **kwargs)


def load_rules(config_path: Path = None) -> List[Rule]:
    """
    Load rules from configuration file.
    
    Args:
        config_path: Path to rules_config.yml. If None, uses default location.
    
    Returns:
        List of Rule objects configured from the config file.
    """
    if config_path is None:
        # Default to rules_config.yml in the same directory as this file
        config_path = Path(__file__).parent / "rules_config.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Rules config file not found: {config_path}. "
            f"Please create it or specify a different path."
        )
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    rules = []
    for rule_config in config.get("rules", []):
        func_name = rule_config.get("func")
        if func_name not in RULE_FUNCTIONS:
            raise ValueError(
                f"Rule function '{func_name}' not found in RULE_FUNCTIONS. "
                f"Available functions: {list(RULE_FUNCTIONS.keys())}"
            )
        
        rule = Rule(
            func=RULE_FUNCTIONS[func_name],
            name=rule_config.get("name", func_name),
            severity=rule_config.get("severity", "error"),
            enabled=rule_config.get("enabled", True),
            description=rule_config.get("description", "")
        )
        rules.append(rule)
    
    return rules


# Default rules loaded from config
def get_default_rules() -> List[Rule]:
    """Get default rules from config file."""
    try:
        return load_rules()
    except FileNotFoundError:
        # Fallback: return empty list if config doesn't exist
        return []

