# Complete Batch Mode - All Scripts

All scripts in the pipeline now support batch mode for processing multiple components at once.

## 🎯 Overview

The entire MOJ component ingestion pipeline can now be run in batch mode, processing all components in a single workflow.

## 📊 Batch Mode Support

| Script | Batch Flag | Environment Variable | What It Processes |
|--------|-----------|---------------------|-------------------|
| `download_git_repo.py` | N/A | `GIT_REPO_URL`, `GIT_TARGET_DIR` | Downloads repository |
| `1_concat_markdown.py` | `--batch` | `MD_SOURCE_DIR`, `MD_OUTPUT_DIR` | All subdirectories as components |
| `2_parse_component_to_json.py` | `--batch` | `MD_OUTPUT_DIR` | All `*-combined.md` files |
| `3_insert_to_milvus.py` | `--batch` | `MD_OUTPUT_DIR`, `MILVUS_*` | All `*.json` files |

## 🚀 Quick Start - Complete Batch Workflow

### Using Environment Variables (Recommended)

```bash
# Set all configuration
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components"
export MD_OUTPUT_DIR="./batch-output"
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION="moj_components"

# Run entire pipeline
python download_git_repo.py --depth 1
python 1_concat_markdown.py --batch --recursive
python 2_parse_component_to_json.py --batch
python 3_insert_to_milvus.py --drop --create
python 3_insert_to_milvus.py --batch
```

### Using Automated Script

```bash
./batch_process_all_components.sh
```

Or with the full environment variables:

```bash
./example_full_pipeline_env.sh
```

## 📋 Step-by-Step Explanation

### Step 1: Download Repository

```bash
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
python download_git_repo.py --depth 1
```

**Output**: Repository cloned to `./repos/moj-frontend/`

### Step 2: Batch Concatenate Markdown Files

```bash
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components"
export MD_OUTPUT_DIR="./batch-output"
python 1_concat_markdown.py --batch --recursive
```

**What happens**:
- Finds all subdirectories in `docs/components/` (alert, button, filter, etc.)
- For each subdirectory, recursively finds all `.md` files
- Creates `batch-output/{component}/{component}-combined.md` for each

**Output structure**:
```
batch-output/
├── alert/
│   └── alert-combined.md
├── button/
│   └── button-combined.md
└── filter/
    └── filter-combined.md
```

### Step 3: Batch Parse to JSON

```bash
export MD_OUTPUT_DIR="./batch-output"
python 2_parse_component_to_json.py --batch
```

**What happens**:
- Finds all `*-combined.md` files in `batch-output/`
- Parses each one and creates JSON with same name

**Output structure**:
```
batch-output/
├── alert/
│   ├── alert-combined.md
│   └── alert-combined.json
├── button/
│   ├── button-combined.md
│   └── button-combined.json
└── filter/
    ├── filter-combined.md
    └── filter-combined.json
```

### Step 4: Create Milvus Collection

```bash
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION="moj_components"
python 3_insert_to_milvus.py --drop --create
```

**What happens**:
- Drops existing collection (if `--drop` specified)
- Creates new collection with proper schema
- Creates index for efficient searching

### Step 5: Batch Insert to Milvus

```bash
export MD_OUTPUT_DIR="./batch-output"
python 3_insert_to_milvus.py --batch
```

**What happens**:
- Finds all `*.json` files in `batch-output/`
- Generates embeddings for each component
- Inserts all components into Milvus collection
- Shows summary statistics

**Output**:
```
🔄 Batch mode: Processing JSON files in ./batch-output

📊 Found 3 JSON file(s) to insert

Processing: alert
   File: alert/alert-combined.json
   ✅ Success! (1 component(s) inserted)

Processing: button
   File: button/button-combined.json
   ✅ Success! (1 component(s) inserted)

Processing: filter
   File: filter/filter-combined.json
   ✅ Success! (1 component(s) inserted)

============================================================
Batch Processing Summary
============================================================
Total files: 3
Successful: 3
Failed: 0
Total components inserted: 3

🎉 Done! Successfully inserted 3 file(s)
```

## 🔍 Search the Knowledge Base

After insertion, search for components:

```bash
python 3_insert_to_milvus.py --search "alert component for errors" --limit 5
```

## 💡 Pro Tips

### 1. Use .env File

Create a `.env` file:

```bash
# .env
GIT_REPO_URL=https://github.com/ministryofjustice/moj-frontend.git
GIT_TARGET_DIR=./repos/moj-frontend
MD_SOURCE_DIR=./repos/moj-frontend/docs/components
MD_OUTPUT_DIR=./batch-output
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION=moj_components
MILVUS_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5
```

Then load it:

```bash
source .env
# or with direnv
direnv allow
```

### 2. Process Only New/Updated Components

```bash
# Only process components modified in last 7 days
find ./repos/moj-frontend/docs/components -type d -mtime -7 -maxdepth 1
```

### 3. Parallel Processing for Large Repositories

For very large repositories with many components, consider processing in parallel (advanced):

```bash
# Use GNU parallel (if installed)
find ./batch-output -name "*.json" | parallel -j 4 python 3_insert_to_milvus.py {}
```

### 4. Monitor Progress

```bash
# Count components before and after
echo "Before: $(python 3_insert_to_milvus.py --search 'test' --limit 1 2>&1 | grep 'Entities:')"

# Run batch insert
python 3_insert_to_milvus.py --batch

echo "After: $(python 3_insert_to_milvus.py --search 'test' --limit 1 2>&1 | grep 'Entities:')"
```

## 🐛 Troubleshooting

### No Files Found

```
❌ No *-combined.md files found in: ./batch-output
```

**Solution**: Make sure you ran step 2 (concatenation) first.

### Collection Already Exists

```
✅ Collection 'knowledge_base' already exists
```

**Solution**: Use `--drop --create` to recreate the collection.

### Connection Refused

```
❌ Error: Connection refused
```

**Solution**: Ensure Milvus is running:
```bash
docker-compose ps
docker-compose restart
```

## 📊 Performance

Processing times (approximate):

| Components | Concatenate | Parse | Insert | Total |
|-----------|-------------|-------|--------|-------|
| 10 | 5s | 8s | 15s | 28s |
| 25 | 10s | 20s | 35s | 65s |
| 50 | 18s | 40s | 70s | 128s |

*Times vary based on file sizes, system performance, and embedding generation speed.*

## 🎓 Learning Path

1. **Start Simple**: Process one component manually
2. **Environment Variables**: Set up `.env` file
3. **Batch Mode**: Use `--batch` for each script
4. **Automation**: Use `batch_process_all_components.sh`
5. **CI/CD**: Integrate into automated pipelines

## 📚 Related Documentation

- [Environment Variables Guide](docs/README_ENVIRONMENT_VARIABLES.md)
- [Batch Mode Guide](docs/README_BATCH_MODE.md)
- [Milvus Integration](docs/README_MILVUS.md)
- [Quick Reference](QUICK_REFERENCE.md)

## 🎯 Next Steps

1. Process your first design system
2. Set up automated daily/weekly updates
3. Add filtering and advanced queries
4. Build a web interface for searching
5. Integrate with LLM for RAG (Retrieval-Augmented Generation)

---

**Happy batch processing!** 🚀
