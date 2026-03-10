# Quick Start Guide - MOJ Component Knowledge Base

Complete workflow for ingesting MOJ component documentation into Milvus vector database.

## Prerequisites

### 1. Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements-milvus.txt

# Or install individually
pip install pymilvus sentence-transformers numpy einops
```

### 2. Start Milvus Server

```bash
# Using Docker (recommended)
wget https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml -O docker-compose.yml
docker-compose up -d

# Verify it's running
docker-compose ps
```

## Workflow

### Step 1: Concatenate Markdown Files

If you have multiple markdown files for a component in separate directories:

```bash
# Concatenate all .md files from a component directory
python concat_markdown.py /path/to/component/docs -o alert-combined.md --recursive
```

Example:
```bash
python concat_markdown.py \
    /home/stkousso/Stelios/Projects/2026/0018-MoJ/customer-resources/data/moj-frontend/docs/components/alert \
    -o alert-combined.md \
    --recursive
```

### Step 2: Parse to JSON

Convert the concatenated markdown to structured JSON:

```bash
python parse_component_to_json.py alert-combined.md -o alert-component.json --pretty
```

This creates a JSON file with:
- Component metadata (title, description, URL, etc.)
- Full file content
- Structured information ready for Milvus

### Step 3: Create Milvus Collection

Create the `knowledge_base` collection (only needed once):

```bash
python insert_to_milvus.py --create
```

Or drop existing and recreate:

```bash
python insert_to_milvus.py --drop --create
```

### Step 4: Insert Data

Insert your component into the knowledge base:

```bash
python insert_to_milvus.py alert-component.json
```

### Step 5: Search

Search the knowledge base using natural language:

```bash
python insert_to_milvus.py --search "How do I show error messages?"
```

## Complete Example

```bash
# 1. Concatenate component docs
python concat_markdown.py ./docs/components/alert -o alert-combined.md --recursive

# 2. Parse to JSON
python parse_component_to_json.py alert-combined.md -o alert-component.json --pretty

# 3. Create collection (first time only)
python insert_to_milvus.py --create

# 4. Insert component
python insert_to_milvus.py alert-component.json

# 5. Search
python insert_to_milvus.py --search "dismissible alerts"
```

## Batch Processing

For multiple components, use the batch script:

```bash
# First, create all *-combined.md files
# Then run batch insert
./batch_insert.sh
```

Or set environment variables:

```bash
export DROP_EXISTING=true
export COLLECTION_NAME=moj_components
./batch_insert.sh
```

## Current Collection Schema

Based on your customizations, the collection has:

| Field | Type | Description |
|-------|------|-------------|
| id | INT64 | Auto-generated primary key |
| component_id | VARCHAR(256) | Component URL (unique ID) |
| title | VARCHAR(512) | Component title |
| description | VARCHAR(4096) | Component description |
| url | VARCHAR(512) | Documentation URL |
| parent | VARCHAR(256) | Parent design system |
| accessibility | VARCHAR(64) | WCAG level |
| has_research | BOOL | Has research/examples |
| created_at | VARCHAR(128) | Creation timestamp |
| updated_at | VARCHAR(128) | Update timestamp |
| views | INT16 | View count |
| content_embedding | FLOAT_VECTOR(768) | Nomic embedding |
| full_content | VARCHAR(65535) | Full markdown |

## Testing Your Setup

After inserting data, verify it works:

```bash
# Search for something specific
python insert_to_milvus.py --search "warning messages" --limit 3

# You should see results with similarity scores
```

Expected output:
```
🔍 Searching for: 'warning messages'
================================================================================
Search Results (3 found):
================================================================================

Result #1 (Similarity: 0.8542)
  Title: Alert
  Description: The alert component presents 1 of 4 types of alerts...
  URL: https://design-patterns.service.justice.gov.uk/components/alert/
  Parent: MOJ Design System
```

## Troubleshooting

### Cannot connect to Milvus
```bash
# Check if Milvus is running
docker-compose ps

# Restart if needed
docker-compose restart

# Check logs
docker-compose logs milvus-standalone
```

### Model download fails
The first run downloads Nomic-embed-text-v1.5 (~1GB). Ensure:
- Internet connection is available
- Sufficient disk space
- HuggingFace is accessible

### Schema mismatch
If you modified the schema and get errors:
```bash
# Drop and recreate collection
python insert_to_milvus.py --drop --create
```

## Next Steps

1. **Process more components**: Repeat steps 1-4 for other components
2. **Build a search API**: Use the search functionality in a web service
3. **RAG integration**: Combine search results with an LLM for Q&A
4. **Monitoring**: Use Attu (Milvus GUI) to visualize your data

## Example Queries

```bash
# Use case questions
python insert_to_milvus.py --search "When should I use this component?"

# Specific features
python insert_to_milvus.py --search "dismissible notifications"

# Accessibility
python insert_to_milvus.py --search "screen reader support"

# Examples
python insert_to_milvus.py --search "show me examples"
```

## Files Overview

- `concat_markdown.py` - Combines multiple .md files
- `parse_component_to_json.py` - Extracts structured JSON
- `insert_to_milvus.py` - Main Milvus integration script
- `batch_insert.sh` - Batch process multiple components
- `requirements-milvus.txt` - Python dependencies

## Support

For issues or questions:
- Check the README files in this directory
- Review Milvus logs: `docker-compose logs`
- Verify JSON structure matches expected format

Happy searching! 🚀
