"""Tests for Pydantic schemas used in dlt ingestion pipelines."""

import pytest
from pydantic import ValidationError

from schemas import Article, ArticleSource


@pytest.fixture
def valid_article_dict():
    """A valid article dict matching the NewsAPI response format."""
    return {
        "source": {"id": "techcrunch", "name": "TechCrunch"},
        "author": "John Doe",
        "title": "New data pipeline tool released",
        "description": "A new tool for building data pipelines.",
        "url": "https://example.com/article-1",
        "urlToImage": "https://example.com/image.jpg",
        "publishedAt": "2025-01-15T12:00:00Z",
        "content": "Full article content here.",
    }


class TestArticleValidation:
    def test_valid_article(self, valid_article_dict):
        article = Article.model_validate(valid_article_dict)
        assert article.title == "New data pipeline tool released"
        assert article.author == "John Doe"
        assert str(article.url) == "https://example.com/article-1"

    def test_missing_required_title(self, valid_article_dict):
        del valid_article_dict["title"]
        with pytest.raises(ValidationError) as exc_info:
            Article.model_validate(valid_article_dict)
        assert "title" in str(exc_info.value)

    def test_empty_title_rejected(self, valid_article_dict):
        valid_article_dict["title"] = "   "
        with pytest.raises(ValidationError) as exc_info:
            Article.model_validate(valid_article_dict)
        assert "title cannot be empty" in str(exc_info.value)

    def test_invalid_url_rejected(self, valid_article_dict):
        valid_article_dict["url"] = "not-a-url"
        with pytest.raises(ValidationError) as exc_info:
            Article.model_validate(valid_article_dict)
        assert "url" in str(exc_info.value)

    def test_optional_fields_nullable(self, valid_article_dict):
        valid_article_dict["author"] = None
        valid_article_dict["description"] = None
        valid_article_dict["content"] = None
        valid_article_dict["urlToImage"] = None
        article = Article.model_validate(valid_article_dict)
        assert article.author is None
        assert article.description is None
        assert article.content is None
        assert article.url_to_image is None

    def test_extra_fields_ignored(self, valid_article_dict):
        valid_article_dict["unknown_field"] = "some_value"
        valid_article_dict["another_extra"] = 42
        article = Article.model_validate(valid_article_dict)
        assert article.title == "New data pipeline tool released"
        assert not hasattr(article, "unknown_field")

    def test_published_at_z_timezone(self, valid_article_dict):
        valid_article_dict["publishedAt"] = "2025-01-15T12:00:00Z"
        article = Article.model_validate(valid_article_dict)
        assert article.published_at.year == 2025
        assert article.published_at.month == 1
        assert article.published_at.hour == 12

    def test_field_aliases(self, valid_article_dict):
        article = Article.model_validate(valid_article_dict)
        assert article.published_at is not None
        assert article.url_to_image is not None
        assert str(article.url_to_image) == "https://example.com/image.jpg"

    def test_article_source_validation(self):
        source = ArticleSource(id=None, name="BBC News")
        assert source.name == "BBC News"
        assert source.id is None
