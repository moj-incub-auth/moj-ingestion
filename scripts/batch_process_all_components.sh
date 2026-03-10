#!/bin/bash
# Batch Process All Components
# This script demonstrates using batch mode to process all components at once

set -e  # Exit on error

echo "🚀 Batch Component Processing"
echo "=============================="
echo ""

# Configuration
REPO_URL="${GIT_REPO_URL:-https://github.com/ministryofjustice/moj-frontend.git}"
REPO_DIR="${GIT_TARGET_DIR:-./repos/moj-frontend}"
COMPONENTS_DIR="$REPO_DIR/docs/components"
OUTPUT_DIR="${MD_OUTPUT_DIR:-./batch-output}"

echo "📋 Configuration:"
echo "   Repository: $REPO_URL"
echo "   Components Directory: $COMPONENTS_DIR"
echo "   Output Directory: $OUTPUT_DIR"
echo ""

# Step 1: Download Repository (if not already downloaded)
if [ ! -d "$REPO_DIR" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 1: Downloading Repository"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    export GIT_REPO_URL="$REPO_URL"
    export GIT_TARGET_DIR="$REPO_DIR"

    python download_git_repo.py --depth 1 --quiet

    echo "✅ Repository downloaded"
    echo ""
else
    echo "ℹ️  Repository already exists at: $REPO_DIR"
    echo "   Skipping download..."
    echo ""
fi

# Step 2: Batch Process All Components
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Batch Processing All Components"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -d "$COMPONENTS_DIR" ]; then
    echo "❌ Error: Components directory not found: $COMPONENTS_DIR"
    exit 1
fi

# Count components
component_count=$(find "$COMPONENTS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "📊 Found $component_count component(s) to process"
echo ""

# Run batch concatenation
python 1_concat_markdown.py "$COMPONENTS_DIR" \
    --batch \
    --output-dir "$OUTPUT_DIR" \
    --recursive

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Parsing to JSON (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask if user wants to continue with JSON parsing
read -p "Parse concatenated files to JSON? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Parsing to JSON..."
    echo ""

    # Use batch mode to parse all markdown files at once
    export MD_OUTPUT_DIR="$OUTPUT_DIR"
    python 2_parse_component_to_json.py --batch

    echo ""
    echo "✅ JSON files generated"
    echo ""

    # Ask if user wants to insert to Milvus
    read -p "Insert to Milvus knowledge base? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Step 4: Inserting to Milvus"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        # Use batch mode to insert all JSON files at once
        export MD_OUTPUT_DIR="$OUTPUT_DIR"
        python 3_insert_to_milvus.py --batch

        echo ""
        echo "✅ All components inserted to Milvus"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Batch Processing Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Output Location: $OUTPUT_DIR"
echo ""
echo "📊 Summary:"
find "$OUTPUT_DIR" -name "*.md" | wc -l | xargs echo "   Markdown files:"
find "$OUTPUT_DIR" -name "*.json" 2>/dev/null | wc -l | xargs echo "   JSON files:"
echo ""
echo "🔍 Test the knowledge base:"
echo "   python 3_insert_to_milvus.py --search \"your query\" --limit 5"
echo ""
