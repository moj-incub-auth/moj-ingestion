# Milvus Knowledge Base Integration

Insert and search MOJ Design System component data using Milvus vector database with Nomic-embed-text-v1.5 embeddings.

## Overview

This script enables semantic search over design system components by:
1. Creating a Milvus collection with a structured schema
2. Generating vector embeddings using Nomic-embed-text-v1.5 (768 dimensions)
3. Inserting component metadata and content
4. Providing semantic search capabilities

## Prerequisites

### 1. Install Dependencies

```bash
uv sync
```

### 2. Run Milvus Server

#### Option A: Docker (Recommended)

```bash
# Download and start Milvus standalone
wget https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml -O docker-compose.yml
docker-compose up -d

# Check status
docker-compose ps
```

#### Option B: Kubernetes

```bash
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm install milvus milvus/milvus
```

#### Option C: Milvus Lite (Development)

```bash
uv tool install milvus
uv run milvus-server
# Runs embedded Milvus - no separate server needed
```

## Usage

### Step 1: Create Collection

First, create the `knowledge_base` collection with the proper schema:

```bash
uv run 3_insert_to_milvus.py --create
```

To drop and recreate an existing collection:

```bash
uv run 3_insert_to_milvus.py --drop --create
```

### Step 2: Insert Component Data

Insert your parsed component JSON into the collection:

```bash
uv run 3_insert_to_milvus.py alert-component.json
```

### Step 3: Search the Knowledge Base

Search for components using natural language queries:

```bash
uv run 3_insert_to_milvus.py --search "alert component for errors" --limit 3
```

### Complete Workflow Example

```bash
# 1. Parse markdown to JSON
uv run 2_parse_component_to_json.py alert-combined.md -o alert-component.json --pretty

# 2. Create Milvus collection
uv run 3_insert_to_milvus.py --create

# 3. Insert data
uv run 3_insert_to_milvus.py alert-component.json

# 4. Search
uv run 3_insert_to_milvus.py --search "How do I show success messages?"
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `json_file` | Path to component JSON file | None |
| `--host` | Milvus server hostname | localhost |
| `--port` | Milvus server port | 19530 |
| `--collection` | Collection name | knowledge_base |
| `--create` | Create collection if it doesn't exist | False |
| `--drop` | Drop existing collection before creating | False |
| `--search` | Search query string | None |
| `--limit` | Number of search results | 5 |

## Collection Schema

The `knowledge_base` collection includes the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | INT64 | Auto-generated primary key |
| `component_id` | VARCHAR(256) | Unique component identifier (URL) |
| `title` | VARCHAR(512) | Component title |
| `description` | VARCHAR(2048) | Component description |
| `url` | VARCHAR(512) | Component documentation URL |
| `parent` | VARCHAR(256) | Parent design system name |
| `accessibility` | VARCHAR(64) | WCAG level (e.g., AA) |
| `status` | VARCHAR(128) | Component status (Official, Beta, etc.) |
| `has_research` | BOOL | Whether component has research |
| `created_at` | VARCHAR(128) | Creation timestamp |
| `updated_at` | VARCHAR(128) | Last update timestamp |
| `content_embedding` | FLOAT_VECTOR(768) | Nomic embedding vector |
| `full_content` | VARCHAR(65535) | Full markdown content |

## Batch Processing Multiple Components

Process and insert multiple components:

```bash
# Parse all components
for file in *.md; do
    uv run 2_parse_component_to_json.py "$file" -o "${file%.md}.json" --pretty
done

# Create collection once
uv run 3_insert_to_milvus.py --create

# Insert all components
for json_file in *-component.json; do
    uv run 3_insert_to_milvus.py "$json_file"
done
```

Or use a simple batch script:

```bash
#!/bin/bash
# batch_insert.sh

# Create collection
uv run 3_insert_to_milvus.py --drop --create

# Process and insert all component files
for md_file in *-combined.md; do
    component_name="${md_file%-combined.md}"
    echo "Processing $component_name..."

    # Parse to JSON
    uv run 2_parse_component_to_json.py "$md_file" -o "${component_name}.json" --pretty

    # Insert to Milvus
    uv run 3_insert_to_milvus.py "${component_name}.json"
done

echo "All components inserted!"
```

## Search Examples

### Basic Search

```bash
uv run 3_insert_to_milvus.py --search "error alert"
```

### Specific Use Case

```bash
uv run 3_insert_to_milvus.py --search "How do I show a warning to users?"
```

### Multiple Results

```bash
uv run 3_insert_to_milvus.py --search "dismissible notification" --limit 10
```

## Advanced Usage

### Connecting to Remote Milvus

```bash
uv run 3_insert_to_milvus.py alert-component.json \
    --host milvus.example.com \
    --port 19530 \
    --collection production_kb
```

### Using Custom Collection Name

```bash
uv run 3_insert_to_milvus.py --create --collection moj_components
uv run 3_insert_to_milvus.py alert-component.json --collection moj_components
```

## Python API Usage

You can also use the `MilvusKnowledgeBase` class programmatically:

```python
from insert_to_milvus import MilvusKnowledgeBase

# Initialize
kb = MilvusKnowledgeBase(
    collection_name="knowledge_base",
    host="localhost",
    port="19530"
)

# Create collection
collection = kb.create_collection()
kb.create_index(collection)

# Insert data
kb.insert_from_json("alert-component.json")

# Search
results = kb.search("error messages", limit=5)

for result in results:
    print(f"{result['title']}: {result['score']:.4f}")

# Close connection
kb.close()
```

## Embeddings

The script uses **Nomic-embed-text-v1.5**, which:
- Produces 768-dimensional vectors
- Optimized for semantic search
- Supports long context (up to 8192 tokens)
- State-of-the-art retrieval performance

The embedding combines:
- Component title
- Description
- Parent system
- First 5000 characters of content

## Performance Tips

### Indexing

The script uses `IVF_FLAT` index with cosine similarity:
- Good balance of speed and accuracy
- Suitable for datasets up to millions of vectors
- For larger datasets, consider `IVF_PQ` or `HNSW`

### Batch Insertion

For large-scale insertion, consider batching:

```python
# Process in batches of 100
batch_size = 100
for i in range(0, len(json_files), batch_size):
    batch = json_files[i:i+batch_size]
    for json_file in batch:
        kb.insert_from_json(json_file)
```

## Troubleshooting

### Connection Refused

```
Error: Connection refused
```

**Solution**: Ensure Milvus server is running:
```bash
docker-compose ps
# or
docker ps | grep milvus
```

### Model Download Issues

```
Error downloading nomic-ai/nomic-embed-text-v1.5
```

**Solution**: The first run downloads the model (~1GB). Ensure internet connection and sufficient disk space.

### Dimension Mismatch

```
Error: vector dimension mismatch
```

**Solution**: Drop and recreate the collection:
```bash
uv run 3_insert_to_milvus.py --drop --create
```

### Out of Memory

```
Error: Out of memory
```

**Solution**:
- Reduce batch size
- Increase Docker memory limits
- Use a machine with more RAM

## Monitoring

### Check Collection Stats

```bash
uv run 3_insert_to_milvus.py --search "test" --limit 1
# Shows entity count at the end
```

### Using Attu (Milvus GUI)

```bash
docker run -p 8000:3000 -e MILVUS_URL=milvus:19530 zilliz/attu:latest
# Open http://localhost:8000
```

## Next Steps

1. **Integrate with RAG**: Use the search results with an LLM for question answering
2. **Add filtering**: Filter by `parent`, `status`, or `has_research`
3. **Hybrid search**: Combine vector search with metadata filtering
4. **Update mechanism**: Add functionality to update existing components

## Example Output

```bash
$ uv run 3_insert_to_milvus.py --search "How to show warnings?"

🔍 Searching for: 'How to show warnings?'
================================================================================
Search Results (3 found):
================================================================================

Result #1 (Similarity: 0.8542)
  Title: Alert
  Description: The alert component presents 1 of 4 types of alerts to a user. It can stay on th...
  URL: https://design-patterns.service.justice.gov.uk/components/alert/
  Parent: MOJ Design System
  Status: Official

Result #2 (Similarity: 0.7234)
  Title: Warning Text
  Description: Use the warning text component when you need to warn users about something...
  URL: https://design-patterns.service.justice.gov.uk/components/warning-text/
  Parent: GOV.UK Design System
  Status: Official

Result #3 (Similarity: 0.6891)
  Title: Notification Banner
  Description: Use notification banner to tell the user about something they need to know...
  URL: https://design-patterns.service.justice.gov.uk/components/notification-banner/
  Parent: GOV.UK Design System
  Status: Official
```

## License

MIT License - Feel free to use and modify as needed.
