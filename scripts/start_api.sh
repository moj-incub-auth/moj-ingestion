#!/bin/bash
# Start MOJ Component Search API

set -e

echo "🚀 Starting MOJ Component Search API"
echo "====================================="
echo ""

# Check if Milvus is running
echo "Checking Milvus connection..."
if ! docker-compose ps | grep -q milvus-standalone; then
    echo "⚠️  Milvus doesn't appear to be running"
    echo "   Starting Milvus..."
    docker-compose up -d
    echo "   Waiting for Milvus to be ready..."
    sleep 5
fi

# Check if collection has data
echo "Checking collection..."
export MILVUS_COLLECTION="${MILVUS_COLLECTION:-knowledge_base}"

# Get configuration from environment or use defaults
HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-5000}"

echo ""
echo "Configuration:"
echo "  Milvus Host: ${MILVUS_HOST:-localhost}"
echo "  Milvus Port: ${MILVUS_PORT:-19530}"
echo "  Collection:  $MILVUS_COLLECTION"
echo "  API Host:    $HOST"
echo "  API Port:    $PORT"
echo ""

# Start the API
echo "Starting API server..."
echo ""

python api_search.py --host "$HOST" --port "$PORT"
