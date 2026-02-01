# ============================================================================
# dwh-on-a-lake Makefile
# Modern Data Lakehouse: dlt + dbt + DuckDB/BigQuery/MotherDuck
# ============================================================================

.PHONY: help install
.PHONY: ingest-dev ingest-prod ingest-gcs ingest-dev-full ingest-prod-full
.PHONY: transform-dev transform-bigquery transform-motherduck
.PHONY: test-dev test-bigquery test-motherduck
.PHONY: pipeline-dev pipeline-bigquery pipeline-motherduck pipeline-gcs-bigquery
.PHONY: docs docs-serve query-dev
.PHONY: lint fix clean clean-all

# ============================================================================
# Configuration
# ============================================================================

INGESTION_DIR = ingestion
TRANSFORM_DIR = transformation
DUCKDB_PATH = /tmp/newsapi_articles.duckdb

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

# ============================================================================
# Help
# ============================================================================

help:
	@echo ""
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)║           dwh-on-a-lake: Modern Data Lakehouse Commands            ║$(RESET)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(GREEN)📦 SETUP$(RESET)"
	@echo "  make install              Install all dependencies (uv sync)"
	@echo ""
	@echo "$(GREEN)📥 INGESTION (dlt → DuckDB/BigQuery/GCS)$(RESET)"
	@echo "  make ingest-dev           Ingest data to local DuckDB"
	@echo "  make ingest-prod          Ingest data to BigQuery"
	@echo "  make ingest-gcs           Ingest data to GCS as Parquet files"
	@echo "  make ingest-dev-full      Full refresh to local DuckDB"
	@echo "  make ingest-prod-full     Full refresh to BigQuery"
	@echo ""
	@echo "$(GREEN)🔄 TRANSFORMATION (dbt)$(RESET)"
	@echo "  make transform-dev        Run dbt models on local DuckDB"
	@echo "  make transform-bigquery   Run dbt models on BigQuery"
	@echo "  make transform-motherduck Run dbt models on MotherDuck"
	@echo ""
	@echo "$(GREEN)✅ TESTING$(RESET)"
	@echo "  make test-dev             Run dbt tests on local DuckDB"
	@echo "  make test-bigquery        Run dbt tests on BigQuery"
	@echo "  make test-motherduck      Run dbt tests on MotherDuck"
	@echo ""
	@echo "$(GREEN)🚀 FULL PIPELINES (Ingest + Transform + Test)$(RESET)"
	@echo "  make pipeline-dev         Full dev pipeline (DuckDB)"
	@echo "  make pipeline-bigquery    Full prod pipeline (BigQuery direct)"
	@echo "  make pipeline-motherduck  Full prod pipeline (MotherDuck)"
	@echo "  make pipeline-gcs-bigquery Full pipeline: GCS Parquet → BigQuery External"
	@echo ""
	@echo "$(GREEN)📊 UTILITIES$(RESET)"
	@echo "  make query-dev            Open DuckDB CLI to query local data"
	@echo "  make docs                 Generate dbt documentation"
	@echo "  make docs-serve           Generate and serve dbt docs (localhost:8080)"
	@echo "  make lineage MODEL=name   Show upstream/downstream dependencies"
	@echo ""
	@echo "$(GREEN)🧹 CODE QUALITY$(RESET)"
	@echo "  make lint                 Check Python code style"
	@echo "  make fix                  Auto-fix Python code style"
	@echo "  make clean                Clean temporary files"
	@echo "  make clean-all            Clean everything including DuckDB"
	@echo ""
	@echo "$(YELLOW)Environment Variables:$(RESET)"
	@echo "  GOOGLE_APPLICATION_CREDENTIALS  - Path to GCP service account key"
	@echo "  GCP_PROJECT_ID                  - GCP project ID for BigQuery"
	@echo "  MOTHERDUCK_TOKEN                - MotherDuck authentication token"
	@echo ""

# ============================================================================
# Setup
# ============================================================================

install:
	@echo "$(CYAN)Installing dependencies...$(RESET)"
	uv sync
	cd $(TRANSFORM_DIR) && dbt deps

# ============================================================================
# Ingestion (dlt)
# ============================================================================

ingest-dev:
	@echo "$(CYAN)Ingesting data to local DuckDB...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --dev

ingest-prod:
	@echo "$(CYAN)Ingesting data to BigQuery...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --prod

ingest-gcs:
	@echo "$(CYAN)Ingesting data to GCS as Parquet...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --gcs

ingest-dev-full:
	@echo "$(CYAN)Full refresh to local DuckDB...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --dev --full-refresh

ingest-prod-full:
	@echo "$(CYAN)Full refresh to BigQuery...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --prod --full-refresh

# ============================================================================
# Transformation (dbt)
# ============================================================================

transform-dev:
	@echo "$(CYAN)Running dbt models on local DuckDB...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt run --target dev

transform-bigquery:
	@echo "$(CYAN)Running dbt models on BigQuery...$(RESET)"
	cd $(TRANSFORM_DIR) && ./run_bigquery.sh

transform-motherduck:
	@echo "$(CYAN)Running dbt models on MotherDuck...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt run --target motherduck

# ============================================================================
# Testing
# ============================================================================

test-dev:
	@echo "$(CYAN)Running dbt tests on local DuckDB...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt test --target dev

test-bigquery:
	@echo "$(CYAN)Running dbt tests on BigQuery...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt test --target bigquery

test-motherduck:
	@echo "$(CYAN)Running dbt tests on MotherDuck...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt test --target motherduck

# ============================================================================
# Full Pipelines
# ============================================================================

pipeline-dev: ingest-dev transform-dev test-dev
	@echo "$(GREEN)✓ Dev pipeline complete (DuckDB)$(RESET)"

pipeline-bigquery: ingest-prod transform-bigquery test-bigquery
	@echo "$(GREEN)✓ BigQuery pipeline complete$(RESET)"

pipeline-motherduck: ingest-dev transform-motherduck test-motherduck
	@echo "$(GREEN)✓ MotherDuck pipeline complete$(RESET)"

# GCS → BigQuery External Table pipeline
pipeline-gcs-bigquery: ingest-gcs
	@echo "$(CYAN)Creating BigQuery external table from GCS...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt run-operation create_bigquery_external_table \
		--args '{table_name: ext_newsapi__articles_us_en, gcs_uri: gs://dwh-on-a-lake-prod/dlt/ingest_newsapi_v1/articles_us_en/*.parquet}' \
		--target bigquery
	cd $(TRANSFORM_DIR) && dbt run --target bigquery
	cd $(TRANSFORM_DIR) && dbt test --target bigquery
	@echo "$(GREEN)✓ GCS → BigQuery external table pipeline complete$(RESET)"

# ============================================================================
# Documentation & Utilities
# ============================================================================

docs:
	@echo "$(CYAN)Generating dbt documentation...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt docs generate --target dev

docs-serve: docs
	@echo "$(CYAN)Serving dbt docs at http://localhost:8080...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt docs serve --port 8080

query-dev:
	@echo "$(CYAN)Opening DuckDB CLI...$(RESET)"
	@echo "$(YELLOW)Hint: Try 'SHOW TABLES;' or 'SELECT * FROM ingest_newsapi_v1.articles_us_en LIMIT 10;'$(RESET)"
	duckdb $(DUCKDB_PATH)

lineage:
ifndef MODEL
	@echo "$(YELLOW)Usage: make lineage MODEL=mart_newsapi__articles$(RESET)"
else
	@echo "$(CYAN)Upstream dependencies:$(RESET)"
	cd $(TRANSFORM_DIR) && dbt ls --select +$(MODEL)
	@echo ""
	@echo "$(CYAN)Downstream dependencies:$(RESET)"
	cd $(TRANSFORM_DIR) && dbt ls --select $(MODEL)+
endif

# Compile dbt models without running (useful for debugging)
compile:
	@echo "$(CYAN)Compiling dbt models...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt compile --target dev

# ============================================================================
# Code Quality
# ============================================================================

lint:
	@echo "$(CYAN)Checking Python code style...$(RESET)"
	cd $(INGESTION_DIR) && uv run black --check .
	cd $(INGESTION_DIR) && uv run flake8 .

fix:
	@echo "$(CYAN)Fixing Python code style...$(RESET)"
	cd $(INGESTION_DIR) && uv run black .

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "$(CYAN)Cleaning temporary files...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	rm -rf $(TRANSFORM_DIR)/target
	rm -rf $(TRANSFORM_DIR)/dbt_packages
	rm -rf $(INGESTION_DIR)/.dlt/pipeline_data

clean-all: clean
	@echo "$(CYAN)Cleaning DuckDB database...$(RESET)"
	rm -f $(DUCKDB_PATH)
	@echo "$(GREEN)✓ All cleaned$(RESET)"

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
