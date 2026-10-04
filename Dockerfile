# Lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install minimal system packages for downloading & SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-install CPU-only PyTorch to minimize image size and build times
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY run.py .

# Expose server port
EXPOSE 8000

# Start FastAPI application
CMD ["python", "run.py"]
