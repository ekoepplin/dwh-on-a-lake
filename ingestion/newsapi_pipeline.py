import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import dlt
from loguru import logger  # Import Loguru
from newsapi.newsapi_client import NewsApiClient

today = datetime.now(timezone.utc).date()
earliest_date = today - timedelta(days=30)

target_schema_name: str = dlt.config[f"{Path(__file__).stem}.destination.schema_name"]


# Define a resource for fetching articles from the US
@dlt.resource(
    table_name="articles_us_en",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_us_en(api_key=dlt.secrets.value):
    logger.info("Fetching Microsoft Copilot articles from the US (English)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="en",
        q="microsoft copilot",
        from_param=earliest_date.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


@dlt.source
def run_all_articles():
    return (get_articles_us_en(),)


def run_pipeline(destination="bigquery", full_refresh=False):
    if destination == "duckdb":
        pipeline = dlt.pipeline(
            pipeline_name="newsapi_articles",
            destination=dlt.destinations.duckdb(
                "tmp/newsapi_articles.duckdb"
            ),
            dataset_name=target_schema_name,
        )
    else:
        pipeline = dlt.pipeline(
            pipeline_name="newsapi_articles",
            destination=destination,
            dataset_name=target_schema_name,
        )

    load_info = pipeline.run(
        run_all_articles(), write_disposition="replace" if full_refresh else "append"
    )

    logger.info(f"Load info: {load_info}")
    logger.success(f"All data processed and uploaded to {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    env_group = parser.add_mutually_exclusive_group()
    env_group.add_argument(
        "--dev", action="store_true", help="Use DuckDB (development mode)"
    )
    env_group.add_argument(
        "--prod", action="store_true", help="Use BigQuery (production mode)"
    )
    parser.add_argument(
        "--full-refresh", action="store_true", help="Perform a full refresh"
    )
    parser.add_argument("--log-level", default="INFO", help="Set log level")
    args = parser.parse_args()

    logger.remove()
    logger.add(
        sink=sys.stderr,
        level=args.log_level,
        format="{time} | {level} | {message}",
    )

    # Default to DuckDB; use BigQuery when --prod is specified
    destination = "bigquery" if args.prod else "duckdb"

    run_pipeline(destination=destination, full_refresh=args.full_refresh)
