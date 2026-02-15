FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory and sandbox temp directory
RUN mkdir -p /data /tmp/shellguard_sandbox

# Create non-root user for security
RUN useradd -m -u 1000 shellguard && \
    chown -R shellguard:shellguard /app /data /tmp/shellguard_sandbox

# Switch to non-root user
USER shellguard

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
