# ============================================================================
# dwh-on-a-lake Makefile
# Modern Data Lakehouse: dlt + dbt + DuckLake (DuckDB/MotherDuck)
# ============================================================================

.PHONY: help install
.PHONY: ingest-dev ingest-prod ingest-dev-full ingest-prod-full
.PHONY: build-dev transform-motherduck
.PHONY: test-motherduck
.PHONY: pipeline-dev pipeline-motherduck
.PHONY: docs docs-serve query-dev
.PHONY: lint fix clean clean-all

# ============================================================================
# Configuration
# ============================================================================

INGESTION_DIR = ingestion
TRANSFORM_DIR = transformation
DUCKLAKE_CATALOG = /tmp/newsapi_ducklake_catalog.duckdb
DUCKLAKE_DATA = /tmp/newsapi_ducklake_data

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
	@echo "$(GREEN)📥 INGESTION (dlt → DuckLake)$(RESET)"
	@echo "  make ingest-dev           Ingest data to local DuckLake"
	@echo "  make ingest-prod          Ingest data to MotherDuck DuckLake"
	@echo "  make ingest-dev-full      Full refresh to local DuckLake"
	@echo "  make ingest-prod-full     Full refresh to MotherDuck DuckLake"
	@echo ""
	@echo "$(GREEN)🔄 TRANSFORMATION (dbt)$(RESET)"
	@echo "  make build-dev            Build + test dbt models on local DuckLake"
	@echo "  make transform-motherduck Run dbt models on MotherDuck"
	@echo ""
	@echo "$(GREEN)✅ TESTING$(RESET)"
	@echo "  make test-motherduck      Run dbt tests on MotherDuck"
	@echo ""
	@echo "$(GREEN)🚀 FULL PIPELINES (Ingest + Transform + Test)$(RESET)"
	@echo "  make pipeline-dev         Full dev pipeline (local DuckLake)"
	@echo "  make pipeline-motherduck  Full prod pipeline (MotherDuck DuckLake)"
	@echo ""
	@echo "$(GREEN)📊 UTILITIES$(RESET)"
	@echo "  make query-dev            Open DuckDB CLI to query local DuckLake"
	@echo "  make docs                 Generate dbt documentation"
	@echo "  make docs-serve           Generate and serve dbt docs (localhost:8080)"
	@echo "  make lineage MODEL=name   Show upstream/downstream dependencies"
	@echo ""
	@echo "$(GREEN)🧹 CODE QUALITY$(RESET)"
	@echo "  make lint                 Check Python code style"
	@echo "  make fix                  Auto-fix Python code style"
	@echo "  make clean                Clean temporary files"
	@echo "  make clean-all            Clean everything including DuckLake"
	@echo ""
	@echo "$(YELLOW)Environment Variables:$(RESET)"
	@echo "  MOTHERDUCK_TOKEN                - MotherDuck authentication token"
	@echo ""

# ============================================================================
# Setup
# ============================================================================

install:
	@echo "$(CYAN)Installing dependencies...$(RESET)"
	uv sync
	cd $(TRANSFORM_DIR) && dbt deps --profiles-dir .

# ============================================================================
# Ingestion (dlt)
# ============================================================================

ingest-dev:
	@echo "$(CYAN)Ingesting data to local DuckLake...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --dev

ingest-prod:
	@echo "$(CYAN)Ingesting data to MotherDuck DuckLake...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --prod

ingest-dev-full:
	@echo "$(CYAN)Full refresh to local DuckLake...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --dev --full-refresh

ingest-prod-full:
	@echo "$(CYAN)Full refresh to MotherDuck DuckLake...$(RESET)"
	cd $(INGESTION_DIR) && uv run python newsapi_pipeline.py --prod --full-refresh

# ============================================================================
# Transformation (dbt)
# ============================================================================

build-dev:
	@echo "$(CYAN)Building dbt models + tests on local DuckLake...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt build --profiles-dir . --target dev

transform-motherduck:
	@echo "$(CYAN)Running dbt models on MotherDuck...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt run --profiles-dir . --target motherduck

# ============================================================================
# Testing
# ============================================================================

test-motherduck:
	@echo "$(CYAN)Running dbt tests on MotherDuck...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt test --profiles-dir . --target motherduck

# ============================================================================
# Full Pipelines
# ============================================================================

pipeline-dev: ingest-dev build-dev
	@echo "$(GREEN)✓ Dev pipeline complete (local DuckLake)$(RESET)"

pipeline-motherduck: ingest-prod transform-motherduck test-motherduck
	@echo "$(GREEN)✓ MotherDuck DuckLake pipeline complete$(RESET)"

# ============================================================================
# Documentation & Utilities
# ============================================================================

docs:
	@echo "$(CYAN)Generating dbt documentation...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt docs generate --profiles-dir . --target dev

docs-serve: docs
	@echo "$(CYAN)Serving dbt docs at http://localhost:8080...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt docs serve --profiles-dir . --port 8080

query-dev:
	@echo "$(CYAN)Opening DuckDB CLI with DuckLake catalog...$(RESET)"
	@echo "$(YELLOW)Hint: Try 'ATTACH \"$(DUCKLAKE_CATALOG)\" AS lake (TYPE DUCKLAKE); USE lake; SHOW TABLES;'$(RESET)"
	duckdb

lineage:
ifndef MODEL
	@echo "$(YELLOW)Usage: make lineage MODEL=mart_newsapi__articles$(RESET)"
else
	@echo "$(CYAN)Upstream dependencies:$(RESET)"
	cd $(TRANSFORM_DIR) && dbt ls --profiles-dir . --select +$(MODEL)
	@echo ""
	@echo "$(CYAN)Downstream dependencies:$(RESET)"
	cd $(TRANSFORM_DIR) && dbt ls --profiles-dir . --select $(MODEL)+
endif

# Compile dbt models without running (useful for debugging)
compile:
	@echo "$(CYAN)Compiling dbt models...$(RESET)"
	cd $(TRANSFORM_DIR) && dbt compile --profiles-dir . --target dev

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
	@echo "$(CYAN)Cleaning DuckLake catalog and data...$(RESET)"
	rm -f $(DUCKLAKE_CATALOG)
	rm -rf $(DUCKLAKE_DATA)
	@echo "$(GREEN)✓ All cleaned$(RESET)"

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
