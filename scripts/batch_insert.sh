#!/bin/bash
# Batch process and insert component markdown files into Milvus

set -e  # Exit on error

echo "🚀 MOJ Component Batch Ingestion"
echo "================================="
echo ""

# Configuration
MILVUS_HOST="${MILVUS_HOST:-localhost}"
MILVUS_PORT="${MILVUS_PORT:-19530}"
COLLECTION_NAME="${COLLECTION_NAME:-knowledge_base}"
DROP_EXISTING="${DROP_EXISTING:-false}"

# Check if any markdown files exist
if ! ls *-combined.md 1> /dev/null 2>&1; then
    echo "❌ No *-combined.md files found in current directory"
    echo "   Please run 1_concat_markdown.py first to create combined files"
    exit 1
fi

# Create/reset collection
echo "📦 Setting up Milvus collection: $COLLECTION_NAME"
if [ "$DROP_EXISTING" = "true" ]; then
    echo "   Dropping existing collection..."
    python 3_insert_to_milvus.py --drop --create \
        --host "$MILVUS_HOST" \
        --port "$MILVUS_PORT" \
        --collection "$COLLECTION_NAME"
else
    python 3_insert_to_milvus.py --create \
        --host "$MILVUS_HOST" \
        --port "$MILVUS_PORT" \
        --collection "$COLLECTION_NAME"
fi

echo ""
echo "📄 Processing markdown files..."
echo "================================="

# Counter
total_files=0
successful=0
failed=0

# Process each markdown file
for md_file in *-combined.md; do
    component_name="${md_file%-combined.md}"
    json_file="${component_name}-component.json"

    echo ""
    echo "Processing: $component_name"
    echo "-----------------------------------"

    total_files=$((total_files + 1))

    # Step 1: Parse markdown to JSON
    echo "  [1/2] Parsing markdown..."
    if python 2_parse_component_to_json.py "$md_file" -o "$json_file" --pretty; then
        # Step 2: Insert into Milvus
        echo "  [2/2] Inserting into Milvus..."
        if python 3_insert_to_milvus.py "$json_file" \
            --host "$MILVUS_HOST" \
            --port "$MILVUS_PORT" \
            --collection "$COLLECTION_NAME"; then
            successful=$((successful + 1))
            echo "  ✅ Success!"
        else
            failed=$((failed + 1))
            echo "  ❌ Failed to insert into Milvus"
        fi
    else
        failed=$((failed + 1))
        echo "  ❌ Failed to parse markdown"
    fi
done

# Summary
echo ""
echo "================================="
echo "📊 Summary"
echo "================================="
echo "Total files processed: $total_files"
echo "Successful: $successful"
echo "Failed: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "🎉 All components successfully inserted!"
    echo ""
    echo "Try searching:"
    echo "  python 3_insert_to_milvus.py --search \"your query\" --collection $COLLECTION_NAME"
    exit 0
else
    echo "⚠️  Some components failed to insert"
    exit 1
fi
