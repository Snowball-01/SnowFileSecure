# Use a lightweight official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build dependencies, install Python packages, then remove build deps
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        python3-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Default command
ENTRYPOINT ["python3"]
CMD ["bot.py"]
