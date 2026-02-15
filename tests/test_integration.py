"""End-to-end integration test: ingest via dlt → transform via dbt → verify output.

Proves the full pipeline works: dlt column names match what dbt expects,
DuckLake merge deduplicates, and the model chain (src → stg → int → mart) runs.
"""

import subprocess
import textwrap
from pathlib import Path

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials
import duckdb
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSFORMATION_DIR = PROJECT_ROOT / "transformation"


def _make_article(url: str, title: str, author: str = "Test Author") -> dict:
    """Build an article dict with the column names dlt produces for DuckLake."""
    return {
        "source__name": "TestSource",
        "source__id": "test",
        "author": author,
        "title": title,
        "description": "Test description",
        "url": url,
        "url_to_image": None,
        "published_at": "2025-01-15T12:00:00+00:00",
        "content": "Test content",
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
def integration_env(tmp_path):
    """Set up a temporary DuckLake + dbt profiles for integration testing."""
    catalog_path = tmp_path / "catalog.duckdb"
    data_path = tmp_path / "data"
    data_path.mkdir()

    credentials = DuckLakeCredentials(
        ducklake_name="newsapi_lake",
        catalog=f"duckdb:///{catalog_path}",
        storage=f"file://{data_path}/",
    )

    pipeline = dlt.pipeline(
        pipeline_name="test_integration",
        destination=dlt.destinations.ducklake(credentials=credentials),
        dataset_name="ingest_newsapi_v1",
        pipelines_dir=str(tmp_path / "pipelines"),
    )

    # Batch 1: initial articles
    batch_1 = [
        _make_article("https://example.com/1", "New data pipeline tool released"),
        _make_article("https://example.com/2", "AI startup raises funding"),
        _make_article("https://example.com/3", "Random news about sports"),
        _make_article("https://example.com/4", "Machine learning breakthrough"),
    ]
    info1 = pipeline.run(_test_articles(batch_1))
    assert not info1.has_failed_jobs

    # Batch 2: duplicate URL to test merge dedup
    batch_2 = [
        _make_article("https://example.com/1", "New data pipeline tool released v2"),
    ]
    info2 = pipeline.run(_test_articles(batch_2))
    assert not info2.has_failed_jobs

    # Write a temporary profiles.yml for dbt
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_yml = profiles_dir / "profiles.yml"
    profiles_yml.write_text(textwrap.dedent(f"""\
        dwh-on-a-lake-profile:
          outputs:
            dev:
              type: duckdb
              path: ":memory:"
              extensions:
                - ducklake
              attach:
                - path: {catalog_path}
                  alias: newsapi_lake
                  type: ducklake
                  is_ducklake: true
                  options:
                    data_path: {data_path}/
              schema: dbt_dev
              threads: 4
          target: dev
    """))

    return {
        "catalog_path": str(catalog_path),
        "data_path": str(data_path) + "/",
        "profiles_dir": str(profiles_dir),
    }


def _run_dbt(args: list[str], profiles_dir: str) -> subprocess.CompletedProcess:
    """Run a dbt command with the given profiles dir."""
    cmd = [
        "uv", "run", "dbt",
        *args,
        "--profiles-dir", profiles_dir,
        "--target", "dev",
    ]
    return subprocess.run(
        cmd,
        cwd=str(TRANSFORMATION_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestIntegrationPipeline:
    def test_dbt_build_succeeds(self, integration_env):
        """dbt build (run + test) should complete successfully in a single process."""
        # Use `dbt build` to run models and tests in one process.
        # This is necessary because dbt uses :memory: — tables don't
        # persist between separate dbt run and dbt test invocations.
        result = _run_dbt(
            ["build", "--exclude", "tag:unit-test"],
            integration_env["profiles_dir"],
        )
        assert result.returncode == 0, (
            f"dbt build failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )

    def test_source_data_after_merge(self, integration_env):
        """DuckLake source should have 4 unique articles after merge dedup."""
        conn = duckdb.connect()
        conn.install_extension("ducklake")
        conn.load_extension("ducklake")
        conn.execute(
            f"ATTACH '{integration_env['catalog_path']}' AS lake "
            f"(TYPE DUCKLAKE, DATA_PATH '{integration_env['data_path']}')"
        )

        # 4 unique URLs after merge (duplicate was overwritten)
        row_count = conn.execute(
            "SELECT COUNT(*) FROM lake.ingest_newsapi_v1.articles_us_en"
        ).fetchone()
        assert row_count[0] == 4, (
            f"Expected 4 rows after merge, got {row_count[0]}"
        )

        # Verify the duplicate was merged (url /1 should have v2 title)
        title = conn.execute(
            "SELECT title FROM lake.ingest_newsapi_v1.articles_us_en "
            "WHERE url = 'https://example.com/1'"
        ).fetchone()
        assert title[0] == "New data pipeline tool released v2"

        conn.close()
