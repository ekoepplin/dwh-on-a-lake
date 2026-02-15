# dwh-on-a-lake

A complete, fast, and simple data warehouse solution built with open-source tools. Get from raw data to production-ready analytics in minutes—with ingestion and transformation included out of the box.

<p align="center">
  <img src="docs/images/dwh-on-a-lake.png" alt="Data Lakehouse Architecture" width="600">
</p>

## Why This Exists

Data warehousing doesn't have to be slow, complex, or expensive. This project proves you can build a production-ready data stack that's:
- **Fast to set up**: Get running in minutes, not months
- **Simple to operate**: Everything is code—no vendor lock-in, no black boxes
- **Feature-rich**: Ingestion and transformation ready to go
- **Cost-effective**: Open-source tools that scale from laptop to cloud

## 🏗️ Complete Data Stack

- **dlt** for ingestion (NewsAPI example) → DuckLake (Parquet + ACID catalog)
- **dbt Core** for transformations → DuckDB or MotherDuck
- **DuckLake** for lake storage: ACID transactions, merge, and time travel on Parquet files

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
       │  merge (deduplicate on URL)
       ▼
┌────────────────────────────────────┐
│          DuckLake                  │
│   ACID catalog + Parquet files    │
│   (local or MotherDuck + GCS)     │
└────────┬───────────────────────────┘
         │
         │  dbt (attach / is_ducklake)
         ▼
┌────────────────────────────────────┐
│      Transformation Targets        │
│  ┌──────────────┐ ┌─────────────┐ │
│  │   DuckDB     │ │ MotherDuck  │ │
│  │   (dev)      │ │  (cloud)    │ │
│  └──────────────┘ └─────────────┘ │
└────────┬───────────────────────────┘
         │ dbt
         ▼
┌─────────────────────────────────────┐
│  Staging → Intermediate → Mart      │
│  (rename)   (enrich)     (aggregate)│
└─────────────────────────────────────┘
```

## ✨ Key Features

- **Fast ingestion** with dlt: Connect to APIs, databases, and files in minutes
- **Powerful transformations** with dbt: Build reliable, tested data models
- **DuckLake storage**: ACID transactions, merge deduplication, and time travel on Parquet
- **Multi-target support**: Same dbt code runs on DuckDB (local) and MotherDuck (cloud)
- **Zero vendor lock-in**: Everything is open source and portable

## 🚀 Getting Started

Get up and running in minutes. See `GETTING_STARTED.md` for:
- Quick installation steps
- Dev/prod setup with DuckLake
- Running the full pipeline: ingestion → transformation
- Example configurations and snippets

## 📁 Project Structure

```
dwh-on-a-lake/
├── Makefile                      # All pipeline commands (make help)
├── ingestion/                    # dlt pipelines
│   ├── newsapi_pipeline.py      # NewsAPI ingestion → DuckLake
│   ├── schemas.py               # Pydantic validation schemas
│   └── tests/                   # Python unit tests (schemas, merge dedup)
│
├── transformation/               # dbt project
│   ├── models/                   # dbt models
│   │   ├── staging/             # Raw data staging
│   │   ├── intermediate/        # Intermediate transformations
│   │   └── mart/                # Analytics-ready marts
│   ├── macros/                   # dbt macros
│   │   ├── categorization/      # Business logic macros
│   │   └── governance/          # Metadata standardization
│   ├── tests/unit/              # dbt singular SQL unit tests
│   ├── profiles.yml             # Target configurations (dev + motherduck)
│   ├── run_motherduck.sh        # MotherDuck deployment script
│   └── run_prod.sh              # Full prod pipeline script
│
└── tests/                        # End-to-end integration tests
```

## 🔗 Quick links

- Getting started: `GETTING_STARTED.md`
- dbt project: `transformation/`

## 📚 Learn More

- [dlt Documentation](https://dlthub.com/docs)
- [dbt Documentation](https://docs.getdbt.com)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [DuckLake](https://ducklake.select/)

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]
