# Evidence Dashboard Setup

## Current Status

✅ **Dashboard Structure Complete:**
- Dashboard page created (`pages/index.md`)
- All SQL queries created in `sources/duckdb/`
- DuckDB connection configured
- Layout component updated

⚠️ **Known Issue:**
- DuckDB serialization error when connecting via Evidence
- This is likely a version compatibility issue between DuckDB 1.4.2 (used to create DB) and Evidence's DuckDB plugin
- **Workaround:** The database file works directly with DuckDB CLI - the issue is with Evidence's connection

## Dashboard Components

### Main Dashboard (`pages/index.md`)
- **Overview Metrics:** Total articles and Copilot articles (BigValue components)
- **Time Series:** Line charts showing articles over time
- **Source Breakdown:** Bar charts showing articles by source
- **Recent Articles:** Searchable data table

### SQL Queries (`sources/duckdb/`)
1. `total_articles_summary.sql` - Sum of all articles
2. `copilot_articles_summary.sql` - Sum of Copilot articles
3. `articles_by_date.sql` - Daily aggregated metrics
4. `articles_by_source.sql` - Source-level aggregations
5. `recent_articles.sql` - Recent articles table data

## Connection Configuration

**File:** `sources/duckdb/connection.yaml`
```yaml
name: duckdb
type: duckdb
options:
  filename: newsapi_articles.duckdb
```

## Running the Dashboard

1. **Build dbt models first:**
   ```bash
   cd ../transformation
   dbt run --select mart_newsapi__articles
   ```

2. **Start Evidence:**
   ```bash
   cd ../reports
   npm run sources  # Connect to data sources
   npm run dev       # Start dev server (opens at http://localhost:3000)
   ```

## Troubleshooting

If you encounter the serialization error:
- The database file is valid (tested with DuckDB CLI)
- Try recreating the database after rebuilding the Docker image with updated dependencies
- Or manually copy the database file to `reports/sources/duckdb/` directory

