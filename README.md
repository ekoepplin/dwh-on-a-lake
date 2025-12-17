# dwh-in-a-box

An end-to-end data pipeline demonstrating **Data Governance as Code** with automated metadata validation, standardized schemas, and compliance enforcement—powering Evidence BI dashboards from dbt marts across DuckDB (dev) and BigQuery (prod).

## 🏗️ Data Stack

- **dlt** ingestion (NewsAPI) → DuckDB (dev) or BigQuery (prod)
- **dbt** transforms → governed marts
- **Evidence** (BI as Code) on top of marts
- **Data Governance as Code** baked into dbt metadata and validators

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

## 🔒 Data Governance (snapshot)

- Standardized dbt metadata + validators + macros.
- Governed marts power Evidence dashboards.
- Details and how-to: `GETTING_STARTED.md` and `data-governance-as-code/README.md`.

## 🚀 Getting Started

See `GETTING_STARTED.md` for install, dev/prod setup, running ingestion + dbt + governance, Evidence configuration, and example snippets.

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

## 🔗 Quick links

- Getting started: `GETTING_STARTED.md`
- Governance reference: `data-governance-as-code/README.md`
- Evidence project: `dashboard/`
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

