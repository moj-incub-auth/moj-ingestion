#!/bin/bash
# Build Concat Task Container

set -e

echo "🐳 Building Concat Task Container"
echo "=================================="
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
IMAGE_NAME="${IMAGE_NAME:-concat-task}"
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
echo "  2. Single directory mode (mount source and output):"
echo "     $RUNTIME run --rm -v \$(pwd)/docs:/workspace/source:ro -v \$(pwd)/output:/workspace/output $FULL_IMAGE /workspace/source -o /workspace/output/combined.md"
echo ""
echo "  3. Batch mode (process all subdirectories):"
echo "     $RUNTIME run --rm -v \$(pwd)/docs/components:/workspace/source:ro -v \$(pwd)/output:/workspace/output $FULL_IMAGE --batch --recursive"
echo ""
echo "  4. With custom environment variables:"
echo "     $RUNTIME run --rm -e MD_SOURCE_DIR=/workspace/source -e MD_OUTPUT_DIR=/workspace/output -v \$(pwd)/docs:/workspace/source:ro -v \$(pwd)/output:/workspace/output $FULL_IMAGE --batch"
echo ""
