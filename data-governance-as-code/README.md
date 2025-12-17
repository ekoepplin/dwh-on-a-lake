# Data Governance as Code

This directory contains governance standards and validation scripts for the dwh-in-a-box project.

## Structure

```
data-governance-as-code/
├── schemas/
│   └── metadata_schema.py      # Standard metadata schema definitions
├── validators/
│   └── metadata_validator.py   # Validates dbt models against standards
└── README.md
```

## Usage

### Validate Metadata

Run the validator to check all dbt models against governance standards:

```bash
# From project root
python data-governance-as-code/validators/metadata_validator.py --dbt-project transformation
```

Or use the Makefile command:

```bash
make validate-governance
```

### Standard Metadata Schema

All dbt models must include the following required metadata fields:

- `data_governance.business_owner` (string): Email or name of business owner
- `data_governance.team_owner` (string): Team responsible for the model
- `data_governance.data_classification` (enum): PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
- `data_governance.data_lifecycle` (enum): DEVELOPMENT, STAGING, PRODUCTION, DEPRECATED

Optional fields:
- `data_governance.has_pii` (bool): Whether model contains PII
- `data_governance.pii_retention_days` (int): Required if has_pii is true
- `data_governance.can_be_referenced` (bool): Whether other models can reference this
- `data_governance.update_schedule` (string): Update frequency
- `data_governance.sla` (string): Service level agreement

## Example

See `transformation/models/mart/newsapi/mart_newsapi__daily_articles.yml` for an example of standardized metadata.

For PII examples, see `transformation/models/mart/newsapi/mart_newsapi__users_example.yml`.

## dbt Macros

The project includes dbt macros in `transformation/macros/governance/standardize_metadata.sql` that can help generate standardized metadata structures.

