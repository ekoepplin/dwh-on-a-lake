# dwh-on-a-lake

A complete, fast, and simple data warehouse solution built with open-source tools. Get from raw data to production-ready analytics in minutes—with ingestion and transformation included out of the box.

## Why This Exists

Data warehousing doesn't have to be slow, complex, or expensive. This project proves you can build a production-ready data stack that's:
- **Fast to set up**: Get running in minutes, not months
- **Simple to operate**: Everything is code—no vendor lock-in, no black boxes
- **Feature-rich**: Ingestion and transformation ready to go
- **Cost-effective**: Open-source tools that scale from laptop to cloud

## 🏗️ Complete Data Stack

- **dlt** for ingestion (NewsAPI example) → DuckDB (dev/prod)
- **dbt Core** for transformations → analytics-ready marts

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
         │  (Ready for │
         │  Analytics) │
         └─────────────┘
```

## ✨ Key Features

- **Fast ingestion** with dlt: Connect to APIs, databases, and files in minutes
- **Powerful transformations** with dbt: Build reliable, tested data models
- **Dev/prod parity**: Same code runs on DuckDB locally and in production
- **Zero vendor lock-in**: Everything is open source and portable

## 🚀 Getting Started

Get up and running in minutes. See `GETTING_STARTED.md` for:
- Quick installation steps
- Dev/prod setup with DuckDB
- Running the full pipeline: ingestion → transformation
- Example configurations and snippets

## 📁 Project Structure

```
dwh-on-a-lake/
├── ingestion/                    # dlt pipelines
│   └── newsapi_pipeline.py      # NewsAPI ingestion
│
└── transformation/               # dbt project
    ├── models/                   # dbt models
    │   ├── staging/             # Raw data staging
    │   ├── intermediate/        # Intermediate transformations
    │   └── mart/                # Analytics-ready marts
    ├── macros/                   # dbt macros
    └── tests/                   # Data quality tests
```

## 🔗 Quick links

- Getting started: `GETTING_STARTED.md`
- dbt project: `transformation/`

## 📚 Learn More

- [dlt Documentation](https://dlthub.com/docs)
- [dbt Documentation](https://docs.getdbt.com)
- [DuckDB Documentation](https://duckdb.org/docs/)

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

