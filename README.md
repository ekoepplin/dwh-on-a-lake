# dwh-in-a-box

An end-to-end data pipeline demonstrating **Data Governance as Code** with automated metadata validation, standardized schemas, and compliance enforcement—powering Evidence BI dashboards from dbt marts across DuckDB (dev) and BigQuery (prod).

## 🏗️ Data Stack

This project implements an end-to-end data governance flow with four core components:

### 1. **dlt (Data Load Tool)** - Ingestion layer (NewsAPI → warehouse)

### 2. **DuckDB (dev) / BigQuery (prod)** - Storage & warehouse

### 3. **dbt (Data Build Tool)** - Transformation layer producing marts

### 4. **Evidence** - Business Intelligence as Code consuming the marts

## 📊 Data Flow

```
┌─────────────┐
│  NewsAPI    │
│   (Source)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     dlt     │
│  (Ingest)   │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────┐
│        Storage / Warehouse         │
│ ┌─────────────┐   ┌──────────────┐ │
│ │  DuckDB     │   │   BigQuery   │ │
│ │ (dev/local) │   │   (prod)     │ │
│ └──────┬──────┘   └──────┬───────┘ │
└────────┼─────────────────┼─────────┘
         ▼                 ▼
      ┌──────────────────────────┐
      │           dbt            │
      │   (Transforms → Marts)   │
      └──────────┬──────────────┘
                 ▼
         ┌─────────────┐
         │    Marts    │
         └──────┬──────┘
                ▼
         ┌─────────────┐
         │  Evidence   │
         │(BI as Code) │
         └─────────────┘
```

### Environments

- Dev: DuckDB local file (`/tmp/newsapi_articles.duckdb`) loaded via `uv run python ingestion/newsapi_pipeline.py --dev`; dbt `profiles.yml` targets DuckDB by default.
- Prod: BigQuery dataset loaded via `uv run python ingestion/newsapi_pipeline.py --prod` with `GOOGLE_APPLICATION_CREDENTIALS` set; add a BigQuery target to `transformation/profiles.yml` and run `dbt run --target prod`. Evidence should point to the same warehouse you use (DuckDB for dev, BigQuery for prod).

## 🔒 Data Governance as Code

This project implements a **minimal but complete** data governance framework where:

1. **Metadata is standardized** in dbt YAML files
2. **Validation is automated** via Python scripts
3. **Policies are version-controlled** alongside code

### Governance Components

#### 1. Standard Metadata Schema
**Location**: `data-governance-as-code/schemas/metadata_schema.py`

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
**Location**: `data-governance-as-code/validators/metadata_validator.py`

Python script that:
- Scans all dbt model YAML files
- Validates metadata against standard schema
- Reports errors and warnings
- Can be integrated into CI/CD pipelines

#### 3. dbt Macros for Standardization
**Location**: `transformation/macros/governance/standardize_metadata.sql`

Reusable dbt macros to generate standardized metadata structures.

## 🚀 Getting Started

See `GETTING_STARTED.md` for installation, environment setup (DuckDB dev, BigQuery prod), running ingestion/dbt/governance checks, Evidence configuration, and example snippets.

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
├── dashboard/                    # Evidence (BI as Code) project consuming marts
│   ├── pages/                    # Evidence pages
│   └── sources/                  # Warehouse connections (DuckDB dev, BigQuery prod)
│
└── data-governance-as-code/          # Governance framework
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
- [Data Governance as Code Best Practices](data-governance-as-code/README.md)

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

