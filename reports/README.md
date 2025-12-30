# Evidence Dashboard

This Evidence dashboard visualizes Microsoft Copilot news articles from the dbt mart models.

## Setup

1. Ensure the DuckDB database exists at `reports/sources/duckdb/newsapi_articles.duckdb`
2. Run dbt to build the mart models:
   ```bash
   cd ../transformation
   dbt run --select mart_newsapi__articles
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Connect to data sources:
   ```bash
   npm run sources
   ```
5. Start the dev server:
   ```bash
   npm run dev
   ```

## Data Source

The dashboard connects to DuckDB at `reports/sources/duckdb/newsapi_articles.duckdb` and queries the `ingest_newsapi_v1.mart_newsapi__articles` table.

## Dashboard Pages

- `pages/index.md` - Main dashboard with overview metrics, time series, and source breakdowns

## Queries

All SQL queries are in `sources/duckdb/`:
- `total_articles_summary.sql` - Total article count
- `copilot_articles_summary.sql` - Copilot article count  
- `articles_by_date.sql` - Time series data
- `articles_by_source.sql` - Source breakdown
- `recent_articles.sql` - Recent articles table

