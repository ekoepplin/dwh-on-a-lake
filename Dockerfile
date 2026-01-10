FROM --platform=${TARGETPLATFORM:-linux/amd64} python:3.11.11 AS base

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    wget \
    unzip \
    git && \
    wget https://github.com/duckdb/duckdb/releases/download/v1.4.2/duckdb_cli-linux-amd64.zip && \
    unzip duckdb_cli-linux-amd64.zip -d /usr/local/bin && \
    rm duckdb_cli-linux-amd64.zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Install uv using the official installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Configure uv for Docker builds
# - Silence uv complaining about not being able to use hard links
# - Tell uv to byte-compile packages for faster application startups
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock /app/

# Set working directory
WORKDIR /app

FROM --platform=${TARGETPLATFORM:-linux/amd64} base AS development
# Install project dependencies using lockfile for reproducible builds
# Based on https://hynek.me/articles/docker-uv/
# This layer is cached until uv.lock or pyproject.toml change
# Remove any existing venv that might have been copied from host
RUN rm -rf .venv && uv sync --locked --no-dev --no-install-project

# Copy the rest of the project (excluding .venv if it exists)
COPY . /app
RUN rm -rf .venv && uv sync --locked --no-dev --no-install-project

# Add venv to PATH so we can use the installed packages
ENV PATH="/app/.venv/bin:$PATH"

# Install dbt packages
WORKDIR /app/transformation
RUN dbt deps

# Run the main application (keep container alive for dev)
WORKDIR /app
CMD ["sleep", "infinity"]

FROM --platform=${TARGETPLATFORM:-linux/amd64} base AS production
# Install project dependencies using lockfile for reproducible builds
# Based on https://hynek.me/articles/docker-uv/
# This layer is cached until uv.lock or pyproject.toml change
# Remove any existing venv that might have been copied from host
RUN rm -rf .venv && uv sync --locked --no-dev --no-install-project

# Copy the rest of the project (excluding .venv if it exists)
COPY . /app
RUN rm -rf .venv && uv sync --locked --no-dev --no-install-project

# Add venv to PATH so we can use the installed packages
ENV PATH="/app/.venv/bin:$PATH"

# Run the main application (placeholder)
WORKDIR /app
CMD ["sleep", "infinity"]