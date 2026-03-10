#!/bin/bash
# Build MOJ Search API Container

set -e

echo "🐳 Building MOJ Search API Container"
echo "======================================"
echo ""

# Detect container runtime
if command -v podman &> /dev/null; then
    RUNTIME="podman"
    echo "Using Podman"
elif command -v docker &> /dev/null; then
    RUNTIME="docker"
    echo "Using Docker"
else
    echo "❌ Error: Neither Docker nor Podman found"
    echo "   Please install Docker or Podman first"
    exit 1
fi

echo ""

# Configuration
IMAGE_NAME="${IMAGE_NAME:-moj-search-api}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "Configuration:"
echo "  Image: $FULL_IMAGE"
echo "  Runtime: $RUNTIME"
echo ""

# Build the image
echo "Building container image..."
echo ""

$RUNTIME build \
    -f Containerfile \
    -t "$FULL_IMAGE" \
    .

echo ""
echo "✅ Container built successfully!"
echo ""
echo "Image: $FULL_IMAGE"
echo ""
echo "Next steps:"
echo "  1. Run with Docker Compose:"
echo "     docker-compose up -d"
echo ""
echo "  2. Run standalone (requires Milvus):"
echo "     $RUNTIME run -d -p 5000:5000 \\"
echo "       -e MILVUS_HOST=localhost \\"
echo "       -e MILVUS_COLLECTION=knowledge_base \\"
echo "       $FULL_IMAGE"
echo ""
echo "  3. Test the API:"
echo "     curl http://localhost:5000/health"
echo ""
