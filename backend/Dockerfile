FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

# Use environment variable for port (Render requirement)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}


