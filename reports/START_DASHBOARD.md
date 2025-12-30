# How to Start the Evidence Dashboard

## Prerequisites

1. **Ensure data is loaded:**
   ```bash
   cd ../ingestion
   uv run python newsapi_pipeline.py --dev
   ```

2. **Build dbt models:**
   ```bash
   cd ../transformation
   dbt run --select mart_newsapi__articles
   ```

## Starting the Dashboard

### Step 1: Navigate to reports directory
```bash
cd /workspaces/dwh-in-a-box/reports
```

### Step 2: Install dependencies (if not already done)
```bash
npm install
```

### Step 3: Connect to data sources
```bash
npm run sources
```
This connects Evidence to your DuckDB database.

### Step 4: Start the development server
```bash
npm run dev
```

The dashboard will:
- Start on `http://localhost:3000` (or next available port)
- Automatically open in your browser
- Hot-reload when you make changes to markdown files

## Available Commands

- `npm run dev` - Start development server
- `npm run build` - Build static site for production
- `npm run sources` - Reconnect to data sources
- `npm run preview` - Preview production build

## Troubleshooting

**If you see connection errors:**
1. Verify the database exists: `ls -la reports/sources/duckdb/newsapi_articles.duckdb`
2. Verify dbt models are built: `cd ../transformation && dbt list`
3. Check the symlink: `ls -la reports/sources/duckdb/newsapi_articles.duckdb`

**If port is already in use:**
- Evidence will automatically try the next available port
- Check the terminal output for the actual URL


