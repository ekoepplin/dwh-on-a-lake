# dwh-in-a-box

An end-to-end data pipeline demonstrating **Data Governance as Code** with automated metadata validation, standardized schemas, and compliance enforcement.

## 🏗️ Data Stack

This project implements an end-to-end data governance flow with three core components:

### 1. **dlt (Data Load Tool)** - Ingestion Layer

### 2. **dbt (Data Build Tool)** - Transformation Layer

### 3. **DuckDB** - Analytics Database

## 📊 Data Flow

```
┌─────────────┐
│  NewsAPI    │
│   (Source)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│     dlt     │─────▶│   DuckDB     │
│  (Ingestion)│      │  (Storage)   │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                    ┌─────────────┐
                    │     dbt     │
                    │(Transform)  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Marts     │
                    │(Analytics)  │
                    └─────────────┘
```

## 🔒 Data Governance as Code

This project implements a **minimal but complete** data governance framework where:

1. **Metadata is standardized** in dbt YAML files
2. **Validation is automated** via Python scripts
3. **Policies are version-controlled** alongside code

### Governance Components

#### 1. Standard Metadata Schema
**Location**: `governance-as-code/schemas/metadata_schema.py`

Defines required and optional metadata fields for all dbt models:

**Required Fields:**
- `data_governance.business_owner` - Business owner email/name
- `data_governance.team_owner` - Team responsible for the model
- `data_governance.data_classification` - PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
- `data_governance.data_lifecycle` - DEVELOPMENT, STAGING, PRODUCTION, DEPRECATED

**Optional Fields:**
- `data_governance.has_pii` - Boolean flag for PII data
- `data_governance.pii_retention_days` - Retention period (required if has_pii=true)
- `data_governance.can_be_referenced` - Whether other models can reference this
- `data_governance.update_schedule` - Update frequency
- `data_governance.sla` - Service level agreement

#### 2. Automated Validation
**Location**: `governance-as-code/validators/metadata_validator.py`

Python script that:
- Scans all dbt model YAML files
- Validates metadata against standard schema
- Reports errors and warnings
- Can be integrated into CI/CD pipelines

#### 3. dbt Macros for Standardization
**Location**: `transformation/macros/governance/standardize_metadata.sql`

Reusable dbt macros to generate standardized metadata structures.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- DuckDB (installed automatically via dependencies)
- NewsAPI key (for ingestion)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd dwh-in-a-box

# Install dependencies
uv sync

# Configure credentials (see credentials/ directory)
cp credentials/dlt-newsapi-secrets.toml.example credentials/dlt-newsapi-secrets.toml
# Add your NewsAPI key to the secrets file
```

### Running the Pipeline

```bash
# 1. Ingest data from NewsAPI to DuckDB
cd ingestion
uv run python newsapi_pipeline.py --dev

# 2. Transform data with dbt
cd ../transformation
dbt run

# 3. Validate governance metadata
cd ..
make validate-governance
```

## 📝 Usage Examples

### Adding Metadata to a dbt Model

```yaml
# transformation/models/mart/example_model.yml
version: 2

models:
  - name: example_model
    description: "Example model with governance metadata"
    meta:
      data_governance:
        business_owner: "alice@company.com"
        team_owner: "data-team"
        data_classification: "PUBLIC"
        data_lifecycle: "PRODUCTION"
        has_pii: false
        can_be_referenced: true
        update_schedule: "daily"
        sla: "daily"
```

### Validating Governance Metadata

```bash
# Validate all models
make validate-governance

# Or directly
uv run python governance-as-code/validators/metadata_validator.py \
  --dbt-project transformation
```

### Example Output

```
============================================================
DATA GOVERNANCE METADATA VALIDATION REPORT
============================================================

✅ No errors found!
============================================================

✅ Validation PASSED
```

## 📁 Project Structure

```
dwh-in-a-box/
├── ingestion/                    # dlt pipelines
│   └── newsapi_pipeline.py      # NewsAPI ingestion
│
├── transformation/               # dbt project
│   ├── models/                   # dbt models
│   │   ├── staging/             # Raw data staging
│   │   ├── intermediate/        # Intermediate transformations
│   │   └── mart/                # Analytics-ready marts
│   ├── macros/                   # dbt macros
│   │   └── governance/          # Governance macros
│   └── tests/                   # Data quality tests
│
└── governance-as-code/          # Governance framework
    ├── schemas/                 # Metadata schema definitions
    └── validators/              # Validation scripts
```

## 🛠️ Available Commands

```bash
# Data ingestion
make run              # Run ingestion pipeline
make test             # Run in test mode (DuckDB)

# dbt transformations
cd transformation
dbt run               # Run all models
dbt test              # Run all tests
dbt docs generate     # Generate documentation

# Governance validation
make validate-governance

# Code quality
make lint             # Check code style
make fix              # Auto-fix code style
```

## 🔍 Key Features

### 1. Standardized Metadata
All dbt models follow a consistent metadata schema, enabling:
- Automated compliance checking
- Data lineage tracking
- Access control policies
- PII identification and retention management

### 2. Automated Validation
Governance rules are enforced automatically:
- Pre-commit hooks (can be added)
- CI/CD integration ready
- Clear error reporting

### 3. Extensible Framework
The governance framework can be extended with:
- Custom validation rules
- PII retention policies
- Access control rules
- Compliance reporting

## 🎯 Next Steps

- [ ] Add CI/CD integration (GitHub Actions)
- [ ] Add PII retention enforcement
- [ ] Extend to multiple dbt projects

## 📚 Learn More

- [dlt Documentation](https://dlthub.com/docs)
- [dbt Documentation](https://docs.getdbt.com)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Data Governance as Code Best Practices](governance-as-code/README.md)

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

