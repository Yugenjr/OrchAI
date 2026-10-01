FROM python:3.13-slim

# Set deterministic working directory
WORKDIR /app

# Ensure unbuffered output and deterministic environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r orchai && useradd -r -g orchai orchai

# Install dependencies in a separate layer
COPY pyproject.toml /app/
RUN pip install --no-cache-dir .

# Copy application code
COPY src/ /app/src/

# Create runtime directories with appropriate permissions
RUN mkdir -p /app/workspace /app/.orchai/tasks /app/.orchai/memory /app/.orchai/logs \
    && chown -R orchai:orchai /app

# Switch to non-root user
USER orchai

# Explicitly set the workspace directory
WORKDIR /app/workspace

# Set entrypoint to orchai CLI
ENTRYPOINT ["python", "-m", "orchai"]
CMD ["--help"]
