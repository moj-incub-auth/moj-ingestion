#!/bin/bash
# Complete Pipeline with Environment Variables
# Demonstrates using environment variables for the entire workflow

set -e

echo "🚀 Complete Pipeline with Environment Variables"
echo "================================================"
echo ""

# Set all environment variables
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components"
export MD_OUTPUT_DIR="./batch-output"
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION="moj_components"
export MILVUS_EMBEDDING_MODEL="nomic-ai/nomic-embed-text-v1.5"

echo "📋 Configuration:"
echo "   Repository: $GIT_REPO_URL"
echo "   Source: $MD_SOURCE_DIR"
echo "   Output: $MD_OUTPUT_DIR"
echo "   Milvus: $MILVUS_HOST:$MILVUS_PORT"
echo "   Collection: $MILVUS_COLLECTION"
echo "   Embedding: $MILVUS_EMBEDDING_MODEL"
echo ""

# Step 1: Download repository
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Downloading Repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python download_git_repo.py --depth 1

# Step 2: Batch concatenate markdown
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Concatenating Markdown Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python 1_concat_markdown.py --batch --recursive

# Step 3: Batch parse to JSON
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Parsing to JSON"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python 2_parse_component_to_json.py --batch

# Step 4: Create Milvus collection
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Creating Milvus Collection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python 3_insert_to_milvus.py --drop --create

# Step 5: Insert all components
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Inserting Components to Milvus"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Use batch mode to insert all JSON files at once
python 3_insert_to_milvus.py --batch

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Pipeline Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Test search:"
python 3_insert_to_milvus.py --search "alert components" --limit 3
