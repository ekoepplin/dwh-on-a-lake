"""Pydantic schemas for data validation in dlt pipelines."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ArticleSource(BaseModel):
    """Schema for the nested source object in NewsAPI articles."""

    id: Optional[str] = None
    name: str


class Article(BaseModel):
    """Schema for validating NewsAPI article records.

    Enforces data types, required fields, and basic constraints
    at extraction time before data enters the pipeline.
    """

    source: ArticleSource
    author: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: HttpUrl
    url_to_image: Optional[HttpUrl] = Field(default=None, alias="urlToImage")
    published_at: datetime = Field(alias="publishedAt")
    content: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "ignore"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("title cannot be empty")
        return v

    @field_validator("published_at", mode="before")
    @classmethod
    def parse_published_at(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
