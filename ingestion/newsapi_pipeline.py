import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import dlt
from loguru import logger  # Import Loguru
from newsapi.newsapi_client import NewsApiClient

# Get today's date and calculate the date range for a week
today = datetime.now(timezone.utc).date()
week_ago = today - timedelta(days=7)

target_schema_name: str = dlt.config[f"{Path(__file__).stem}.destination.schema_name"]


# Define a resource for fetching articles from Germany
@dlt.resource(
    table_name="articles_de_de",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_de_de(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Germany (German)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="de",
        q="Bank AND (Finanz OR Finanzen OR Wirtschaft)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Spain
@dlt.resource(
    table_name="articles_es_es",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_es_es(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Spain (Spanish)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="es",
        q="banco AND (finanzas OR financiero OR negocio)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from France
@dlt.resource(
    table_name="articles_fr_fr",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_fr_fr(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from France (French)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="fr",
        q="banque AND (finance OR financier OR affaires)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Italy
@dlt.resource(
    table_name="articles_it_it",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_it_it(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Italy (Italian)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="it",
        q="banca AND (finanza OR finanziario OR affari)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from the UK
@dlt.resource(
    table_name="articles_uk_gb",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_uk_gb(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from the UK (English)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="en",
        q="bank AND (finance OR financial OR business)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Switzerland
@dlt.resource(
    table_name="articles_ch_de",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_ch_de(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Switzerland (German)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="de",
        q="Bank AND (Finanz OR Finanzen OR Wirtschaft)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Netherlands
@dlt.resource(
    table_name="articles_nl_nl",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_nl_nl(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Netherlands (Dutch)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="nl",
        q="bank AND (financiën OR financieel OR zaken)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Belgium
@dlt.resource(
    table_name="articles_be_fr",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_be_fr(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Belgium (French)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="fr",
        q="banque AND (finance OR financier OR affaires)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Austria
@dlt.resource(
    table_name="articles_at_de",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_at_de(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Austria (German)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="de",
        q="Bank AND (Finanz OR Finanzen OR Wirtschaft)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from Sweden
@dlt.resource(
    table_name="articles_se_sv",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_se_sv(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from Sweden (Swedish)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="sv",
        q="bank AND (finans OR finansiell OR affärer)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from the US
@dlt.resource(
    table_name="articles_us_en",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_us_en(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from the US (English)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="en",
        q="bank AND (finance OR financial OR business)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


# Define a resource for fetching articles from China
@dlt.resource(
    table_name="articles_cn_zh",
    write_disposition="append",
    columns={"source__id": {"data_type": "text"}},
)
def get_articles_cn_zh(api_key=dlt.secrets.value):
    logger.info("Fetching bank-related articles from China (Chinese)")
    newsapi = NewsApiClient(api_key=api_key)
    articles = newsapi.get_everything(
        language="zh",
        q="银行 AND (金融 OR 财经 OR 商业)",
        from_param=week_ago.isoformat(),
        to=today.isoformat(),
        sort_by="publishedAt",
    )
    for article in articles["articles"]:
        yield article


@dlt.source
def run_all_articles():
    return (
        get_articles_de_de(),
        get_articles_es_es(),
        get_articles_fr_fr(),
        get_articles_it_it(),
        get_articles_uk_gb(),
        get_articles_ch_de(),
        get_articles_nl_nl(),
        get_articles_be_fr(),
        get_articles_at_de(),
        get_articles_se_sv(),
        get_articles_us_en(),
        get_articles_cn_zh(),
    )


def run_pipeline(destination="bigquery", full_refresh=False):
    if destination == "duckdb":
        pipeline = dlt.pipeline(
            pipeline_name="newsapi_articles",
            destination=dlt.destinations.duckdb("/tmp/newsapi_articles.duckdb"),
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
