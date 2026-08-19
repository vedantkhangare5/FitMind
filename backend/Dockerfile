FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install required system dependencies (e.g. for building packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project specification files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8000

# Run gunicorn with uvicorn workers
CMD ["uv", "run", "gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
