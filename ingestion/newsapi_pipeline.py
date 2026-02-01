import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import dlt
from loguru import logger
from newsapi.newsapi_client import NewsApiClient
from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from schemas import Article

# Configuration constants - easily adjustable
DAYS_LOOKBACK = 30
DEFAULT_QUERY = "Data Engineering"
DEFAULT_PAGE_SIZE = 100
MAX_RETRY_ATTEMPTS = 3
RETRY_WAIT_MIN = 1
RETRY_WAIT_MAX = 10

today = datetime.now(timezone.utc).date()
earliest_date = today - timedelta(days=DAYS_LOOKBACK)

target_schema_name: str = dlt.config[f"{Path(__file__).stem}.destination.schema_name"]


class NewsAPIError(Exception):
    """Custom exception for NewsAPI errors."""

    pass


@retry(
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying API call (attempt {retry_state.attempt_number}/{MAX_RETRY_ATTEMPTS})..."
    ),
)
def fetch_articles_from_api(newsapi: NewsApiClient, query: str, page_size: int):
    """Fetch articles from NewsAPI with retry logic."""
    response = newsapi.get_everything(
        language="en",
        q=query,
        from_param=earliest_date.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
        page_size=page_size,
    )

    if response.get("status") == "error":
        error_msg = response.get("message", "Unknown API error")
        raise NewsAPIError(f"NewsAPI returned error: {error_msg}")

    return response


@dlt.resource(
    table_name="articles_us_en",
    write_disposition="merge",
    primary_key="url",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_us_en(
    api_key=dlt.secrets.value,
    query: str = DEFAULT_QUERY,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    """Fetch and validate articles from NewsAPI.

    Args:
        api_key: NewsAPI key (from dlt secrets)
        query: Search query for articles
        page_size: Maximum number of articles to fetch per request
    """
    logger.info(f"Fetching '{query}' articles from the US (English)")
    newsapi = NewsApiClient(api_key=api_key)

    try:
        response = fetch_articles_from_api(newsapi, query, page_size)
    except NewsAPIError as e:
        logger.error(f"API error: {e}")
        return
    except Exception as e:
        logger.error(
            f"Failed to fetch articles after {MAX_RETRY_ATTEMPTS} retries: {e}"
        )
        return

    # Batch-level quality check
    article_list = response.get("articles", [])
    if not article_list:
        logger.warning("NewsAPI returned 0 articles - potential upstream issue")
        return

    logger.info(f"Received {len(article_list)} articles from NewsAPI")

    # Record-level validation
    valid_count = 0
    invalid_count = 0
    for article in article_list:
        try:
            validated = Article.model_validate(article)
            valid_count += 1
            yield validated.model_dump(mode="json")
        except ValidationError as e:
            invalid_count += 1
            logger.warning(f"Skipping invalid article: {e.errors()[0]['msg']}")

    logger.info(f"Batch complete: {valid_count} valid, {invalid_count} invalid")


@dlt.source
def run_all_articles(query: str = DEFAULT_QUERY, page_size: int = DEFAULT_PAGE_SIZE):
    """Source that yields all article resources.

    Args:
        query: Search query for articles
        page_size: Maximum number of articles to fetch per request
    """
    return (get_articles_us_en(query=query, page_size=page_size),)


def run_pipeline(
    destination: str = "bigquery",
    full_refresh: bool = False,
    query: str = DEFAULT_QUERY,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    """Run the NewsAPI ingestion pipeline.

    Args:
        destination: Target destination ('duckdb', 'bigquery', or 'filesystem')
        full_refresh: Whether to replace all data or merge
        query: Search query for articles
        page_size: Maximum number of articles to fetch per request
    """
    if destination == "duckdb":
        pipeline = dlt.pipeline(
            pipeline_name="newsapi_articles",
            destination=dlt.destinations.duckdb("/tmp/newsapi_articles.duckdb"),
            dataset_name=target_schema_name,
        )
    elif destination == "filesystem":
        pipeline = dlt.pipeline(
            pipeline_name="newsapi_articles",
            destination="filesystem",
            dataset_name=target_schema_name,
        )
    else:
        pipeline = dlt.pipeline(
            pipeline_name="newsapi_articles",
            destination=destination,
            dataset_name=target_schema_name,
        )

    # Filesystem doesn't support merge - use append and deduplicate in dbt
    # For DuckDB/BigQuery, use merge for deduplication at ingestion time
    if full_refresh:
        write_disposition = "replace"
    elif destination == "filesystem":
        write_disposition = "append"
    else:
        write_disposition = None  # Use resource's default (merge)
    load_info = pipeline.run(
        run_all_articles(query=query, page_size=page_size),
        write_disposition=write_disposition,
        loader_file_format="parquet" if destination == "filesystem" else None,
    )

    # Observability: detailed load metrics
    logger.info(f"Load IDs: {load_info.loads_ids}")
    logger.info(f"Destination: {load_info.destination_name}")
    logger.info(f"Load packages: {len(load_info.load_packages)}")
    logger.debug(f"Full load info: {load_info}")

    if load_info.has_failed_jobs:
        logger.error("Some jobs failed during load")
        raise RuntimeError("Pipeline load failed - check logs for details")

    logger.success(f"All data processed and uploaded to {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NewsAPI ingestion pipeline")
    env_group = parser.add_mutually_exclusive_group()
    env_group.add_argument(
        "--dev", action="store_true", help="Use DuckDB (development mode)"
    )
    env_group.add_argument(
        "--prod", action="store_true", help="Use BigQuery (production mode)"
    )
    env_group.add_argument(
        "--gcs",
        action="store_true",
        help="Use GCS filesystem (Parquet files to gs://dwh-on-a-lake-prod)",
    )
    parser.add_argument(
        "--full-refresh", action="store_true", help="Perform a full refresh"
    )
    parser.add_argument("--log-level", default="INFO", help="Set log level")
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help=f"Search query for articles (default: {DEFAULT_QUERY})",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Max articles per request (default: {DEFAULT_PAGE_SIZE})",
    )
    args = parser.parse_args()

    logger.remove()
    logger.add(
        sink=sys.stderr,
        level=args.log_level,
        format="{time} | {level} | {message}",
    )

    # Determine destination: --prod=BigQuery, --gcs=GCS filesystem, default=DuckDB
    if args.prod:
        destination = "bigquery"
    elif args.gcs:
        destination = "filesystem"
    else:
        destination = "duckdb"

    run_pipeline(
        destination=destination,
        full_refresh=args.full_refresh,
        query=args.query,
        page_size=args.page_size,
    )
