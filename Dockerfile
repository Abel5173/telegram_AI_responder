# Use the latest Python 3.12 slim image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed for Telethon, SQLite, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY userbot.py ai.py db.py config.py ./

# Copy .env if present (for local dev; in production, use --env-file or secrets)
# COPY .env .

# Expose no ports (userbot is not a web server)

# Default command
CMD ["python", "userbot.py"] 