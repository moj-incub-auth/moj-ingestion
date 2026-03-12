#!/bin/bash
# Build Parse-to-JSON Task Container

set -e

echo "🐳 Building Parse-to-JSON Task Container"
echo "========================================="
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
IMAGE_NAME="${IMAGE_NAME:-parse-to-json}"
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
echo "Usage examples:"
echo ""
echo "  1. Show help:"
echo "     $RUNTIME run --rm $FULL_IMAGE"
echo ""
echo "  2. Single file mode:"
echo "     $RUNTIME run --rm -v \$(pwd)/data:/workspace/data $FULL_IMAGE /workspace/data/alert-combined.md -o /workspace/data/alert.json"
echo ""
echo "  3. Batch mode (process all *-combined.md files):"
echo "     $RUNTIME run --rm -v \$(pwd)/data:/workspace/data $FULL_IMAGE --batch"
echo ""
echo "  4. With custom environment variables:"
echo "     $RUNTIME run --rm -e MD_OUTPUT_DIR=/workspace/data -v \$(pwd)/data:/workspace/data $FULL_IMAGE --batch"
echo ""
