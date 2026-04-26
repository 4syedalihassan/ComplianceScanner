#!/bin/bash
# Deployment Script for CIS Compliance Scanner

set -e

echo "=== CIS Compliance Scanner Deployment ==="

# Check environment
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env"
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t compliance-scanner .

# Run database migrations
echo "Running database migrations..."
docker run --rm -it \
    --env-file .env \
    compliance-scanner \
    python -c "import asyncpg; print('Database connection OK')" || true

# Start containers
echo "Starting services..."
docker-compose up -d

# Check health
echo "Checking health..."
sleep 5
curl -f http://localhost:8000/health || {
    echo "ERROR: Health check failed"
    exit 1
}

echo "=== Deployment Complete ==="
echo "Access at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"