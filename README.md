# dwh-in-a-box

A complete, fast, and simple data warehouse solution built with open-source tools. Get from raw data to production-ready analytics in minutes—with ingestion, transformation, BI dashboards, and **data governance** all included out of the box.

## Why This Exists

Data warehousing doesn't have to be slow, complex, or expensive. This project proves you can build a production-ready data stack that's:
- **Fast to set up**: Get running in minutes, not months
- **Simple to operate**: Everything is code—no vendor lock-in, no black boxes
- **Feature-rich**: Ingestion, transformation, BI, and governance all included
- **Cost-effective**: Open-source tools that scale from laptop to cloud

## 🏗️ Complete Data Stack

- **dlt** for ingestion (NewsAPI example) → DuckDB (dev/prod)
- **dbt Core** for transformations → analytics-ready marts
- **Jupyter Notebooks** for Exploratory Data Analysis (EDA): Quickly explore your ingested data, prototype transformations before formalizing them in dbt, and accelerate your analytics workflow
- **Evidence** for BI dashboards (BI as Code)
- **Data Governance as Code** with automated metadata validation and compliance enforcement

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
│ ┌─────────────┐                    │
│ │  DuckDB     │                    │
│ │ (dev/prod)  │                    │
│ └──────┬──────┘                    │
└────────┼───────────────────────────┘
         ▼
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

## ✨ Key Features

- **Fast ingestion** with dlt: Connect to APIs, databases, and files in minutes
- **Powerful transformations** with dbt: Build reliable, tested data models
- **Beautiful dashboards** with Evidence: BI as Code—versioned, reviewable, deployable
- **Data governance built-in**: Automated metadata validation, standardized schemas, compliance enforcement
- **Dev/prod parity**: Same code runs on DuckDB locally and in production
- **Zero vendor lock-in**: Everything is open source and portable

## 🔒 Data Governance

Data governance is baked in, not bolted on:
- Standardized dbt metadata schemas
- Automated validation scripts
- Compliance enforcement at build time
- Details and how-to: `GETTING_STARTED.md` and `data-governance-as-code/README.md`.

## 🚀 Getting Started

Get up and running in minutes. See `GETTING_STARTED.md` for:
- Quick installation steps
- Dev/prod setup with DuckDB
- Running the full pipeline: ingestion → transformation → governance → dashboards
- Example configurations and snippets

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
├── reports/                      # Evidence (BI as Code) project consuming marts
│   ├── pages/                    # Evidence pages
│   └── sources/                  # Warehouse connections (DuckDB)
│
└── data-governance-as-code/          # Governance framework
    ├── schemas/                 # Metadata schema definitions
    └── validators/              # Validation scripts
```

## 🔗 Quick links

- Getting started: `GETTING_STARTED.md`
- Governance reference: `data-governance-as-code/README.md`
- Evidence project: `reports/`
- dbt project: `transformation/`

## 📚 Learn More

- [dlt Documentation](https://dlthub.com/docs)
- [dbt Documentation](https://docs.getdbt.com)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Data Governance as Code Best Practices](data-governance-as-code/README.md)

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

