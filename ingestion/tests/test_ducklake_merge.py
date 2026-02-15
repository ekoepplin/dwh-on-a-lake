"""Integration test proving DuckLake merge deduplicates on URL.

This test does NOT call the NewsAPI — it feeds data directly into a dlt
pipeline targeting a temporary DuckLake catalog, then verifies that
duplicate URLs are merged (not appended).
"""

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials
import duckdb
import pytest


def _make_article(url: str, title: str, author: str = "Author") -> dict:
    """Helper to build a minimal article dict for dlt ingestion."""
    return {
        "source__name": "TestSource",
        "source__id": "test",
        "author": author,
        "title": title,
        "description": "desc",
        "url": url,
        "url_to_image": None,
        "published_at": "2025-01-15T12:00:00+00:00",
        "content": "content",
    }


@dlt.resource(
    table_name="articles_us_en",
    write_disposition="merge",
    primary_key="url",
    columns={
        "source__id": {"data_type": "text"},
        "url_to_image": {"data_type": "text", "nullable": True},
    },
)
def _test_articles(data):
    yield from data


@pytest.fixture
def ducklake_pipeline(tmp_path):
    """Create a dlt pipeline pointing to a temp DuckLake catalog."""
    catalog_path = str(tmp_path / "catalog.duckdb")
    data_path = str(tmp_path / "data") + "/"

    pipeline = dlt.pipeline(
        pipeline_name="test_merge_dedup",
        destination=dlt.destinations.ducklake(
            credentials=DuckLakeCredentials(
                ducklake_name="testlake",
                catalog=f"duckdb:///{catalog_path}",
                storage=f"file://{data_path}",
            )
        ),
        dataset_name="test_schema",
        pipelines_dir=str(tmp_path / "pipelines"),
    )
    return pipeline, catalog_path, data_path


class TestDuckLakeMergeDedup:
    def test_duplicate_urls_are_merged(self, ducklake_pipeline):
        """Two pipeline runs with overlapping URLs should not produce duplicates."""
        pipeline, catalog_path, data_path = ducklake_pipeline

        # Batch 1: 3 articles
        batch_1 = [
            _make_article("https://example.com/1", "Article One v1"),
            _make_article("https://example.com/2", "Article Two v1"),
            _make_article("https://example.com/3", "Article Three v1"),
        ]

        # Batch 2: 2 new + 1 overlap (url /2 with updated title)
        batch_2 = [
            _make_article("https://example.com/2", "Article Two v2"),
            _make_article("https://example.com/4", "Article Four v1"),
            _make_article("https://example.com/5", "Article Five v1"),
        ]

        # Run pipeline twice
        info1 = pipeline.run(_test_articles(batch_1))
        assert not info1.has_failed_jobs

        info2 = pipeline.run(_test_articles(batch_2))
        assert not info2.has_failed_jobs

        # Query DuckLake directly
        conn = duckdb.connect()
        conn.install_extension("ducklake")
        conn.load_extension("ducklake")
        conn.execute(
            f"ATTACH '{catalog_path}' AS lake "
            f"(TYPE DUCKLAKE, DATA_PATH '{data_path}')"
        )

        # Check total rows = 5 unique URLs (no duplicates)
        result = conn.execute(
            "SELECT COUNT(*) FROM lake.test_schema.articles_us_en"
        ).fetchone()
        assert result[0] == 5, f"Expected 5 rows, got {result[0]}"

        # Check no duplicate URLs
        dup_count = conn.execute(
            "SELECT COUNT(*) FROM ("
            "  SELECT url, COUNT(*) as cnt"
            "  FROM lake.test_schema.articles_us_en"
            "  GROUP BY url HAVING cnt > 1"
            ")"
        ).fetchone()
        assert dup_count[0] == 0, "Found duplicate URLs after merge"

        # Check the overlapping URL has the updated (v2) title
        title = conn.execute(
            "SELECT title FROM lake.test_schema.articles_us_en "
            "WHERE url = 'https://example.com/2'"
        ).fetchone()
        assert title[0] == "Article Two v2", (
            f"Expected updated title, got '{title[0]}'"
        )

        conn.close()
