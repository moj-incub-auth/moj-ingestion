# Quick Reference - MOJ Component Ingestion Pipeline

One-page reference for common tasks.

## 🚀 Quick Start

### Single Component

```bash
# Download → Concatenate → Parse → Insert
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components/alert"
export MD_OUTPUT_FILE="alert-combined.md"

python download_git_repo.py --depth 1
python 1_concat_markdown.py --recursive
python 2_parse_component_to_json.py alert-combined.md -o alert.json --pretty
python 3_insert_to_milvus.py alert.json
```

### All Components (Batch Mode)

```bash
# Download → Batch Process → Parse All → Insert All
./batch_process_all_components.sh
```

## 📋 Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `GIT_REPO_URL` | download_git_repo.py | Repository URL |
| `GIT_TARGET_DIR` | download_git_repo.py | Clone destination |
| `MD_SOURCE_DIR` | 1_concat_markdown.py | Source directory |
| `MD_OUTPUT_FILE` | 1_concat_markdown.py | Output file (single mode) |
| `MD_OUTPUT_DIR` | 1_concat_markdown.py | Output directory (batch mode) |

## 🛠️ Common Commands

### Download Repository

```bash
# Basic
python download_git_repo.py --url https://github.com/user/repo.git

# With environment variable
export GIT_REPO_URL="https://github.com/user/repo.git"
python download_git_repo.py

# Shallow clone (faster)
python download_git_repo.py --url https://github.com/user/repo.git --depth 1

# Specific branch
python download_git_repo.py --url https://github.com/user/repo.git --branch develop
```

### Concatenate Markdown

```bash
# Single directory
python 1_concat_markdown.py ./docs/components/alert -o alert-combined.md

# Recursive search
python 1_concat_markdown.py ./docs/components/alert -o alert-combined.md --recursive

# Batch mode (all subdirectories)
python 1_concat_markdown.py ./docs/components --batch --output-dir ./output

# With environment variables
export MD_SOURCE_DIR="./docs/components/alert"
export MD_OUTPUT_FILE="alert-combined.md"
python 1_concat_markdown.py --recursive
```

### Parse to JSON

```bash
# Basic
python 2_parse_component_to_json.py alert-combined.md -o alert.json

# Pretty print
python 2_parse_component_to_json.py alert-combined.md -o alert.json --pretty
```

### Insert to Milvus

```bash
# Create collection (first time only)
python 3_insert_to_milvus.py --create

# Insert component
python 3_insert_to_milvus.py alert.json

# Search
python 3_insert_to_milvus.py --search "How do I use alerts?" --limit 5

# Drop and recreate
python 3_insert_to_milvus.py --drop --create
```

## 📁 File Structure

### Input Structure
```
repos/moj-frontend/docs/components/
├── alert/
│   ├── overview.md
│   ├── usage.md
│   └── examples.md
└── button/
    ├── overview.md
    └── variants.md
```

### Output Structure (Batch Mode)
```
batch-output/
├── alert/
│   ├── alert-combined.md
│   └── alert-component.json
└── button/
    ├── button-combined.md
    └── button-component.json
```

## 🔁 Common Workflows

### Workflow 1: Process One Component

```bash
# 1. Set variables
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components/alert"
export MD_OUTPUT_FILE="alert-combined.md"

# 2. Download
python download_git_repo.py --depth 1

# 3. Concatenate
python 1_concat_markdown.py --recursive

# 4. Parse
python 2_parse_component_to_json.py alert-combined.md -o alert.json --pretty

# 5. Insert
python 3_insert_to_milvus.py --create  # First time only
python 3_insert_to_milvus.py alert.json

# 6. Search
python 3_insert_to_milvus.py --search "alert component"
```

### Workflow 2: Process All Components

```bash
# Option A: Use automated script
./batch_process_all_components.sh

# Option B: Manual steps
python download_git_repo.py --url https://github.com/ministryofjustice/moj-frontend.git --depth 1 --target ./repos/moj-frontend
python 1_concat_markdown.py ./repos/moj-frontend/docs/components --batch --output-dir ./output --recursive

for md in ./output/*/*.md; do
    dir=$(dirname "$md")
    name=$(basename "$dir")
    python 2_parse_component_to_json.py "$md" -o "$dir/${name}.json" --pretty
    python 3_insert_to_milvus.py "$dir/${name}.json"
done
```

### Workflow 3: Update Existing Components

```bash
# 1. Pull latest changes
python download_git_repo.py --pull ./repos/moj-frontend

# 2. Reprocess components
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components"
export MD_OUTPUT_DIR="./output"
python 1_concat_markdown.py --batch --recursive

# 3. Drop and recreate Milvus collection
python 3_insert_to_milvus.py --drop --create

# 4. Reinsert all
for json in ./output/*/*.json; do
    python 3_insert_to_milvus.py "$json"
done
```

## 🎯 Flags Quick Reference

### download_git_repo.py
- `--url URL` - Repository URL
- `--target DIR` - Target directory
- `--branch NAME` - Specific branch
- `--depth N` - Shallow clone
- `--pull DIR` - Update existing repo
- `--quiet` - Suppress output

### 1_concat_markdown.py
- `-o, --output FILE` - Output file (single mode)
- `-r, --recursive` - Search recursively
- `--batch` - Batch mode
- `--output-dir DIR` - Output directory (batch mode)
- `--no-separators` - No separators
- `--no-filenames` - No filename headers
- `--exclude FILE...` - Exclude files

### 2_parse_component_to_json.py
- `-o, --output FILE` - Output JSON file
- `--pretty` - Pretty-print JSON
- `--indent N` - Indentation level

### 3_insert_to_milvus.py
- `--create` - Create collection
- `--drop` - Drop existing collection
- `--search QUERY` - Search query
- `--limit N` - Number of results
- `--host HOST` - Milvus host
- `--port PORT` - Milvus port
- `--collection NAME` - Collection name

## 🐛 Troubleshooting

### Git Clone Fails
```bash
# Check git installation
git --version

# Try with SSH instead of HTTPS
export GIT_REPO_URL="git@github.com:user/repo.git"
```

### No Markdown Files Found
```bash
# Check directory exists
ls -la ./docs/components/alert

# Try recursive search
python 1_concat_markdown.py ./docs/components/alert -o output.md --recursive
```

### Milvus Connection Failed
```bash
# Check Milvus is running
docker-compose ps

# Restart Milvus
docker-compose restart
```

### Collection Already Exists
```bash
# Drop and recreate
python 3_insert_to_milvus.py --drop --create
```

## 💡 Pro Tips

1. **Use shallow clones** for faster downloads: `--depth 1`
2. **Use batch mode** to process all components at once
3. **Set environment variables** in `.envrc` or `.env` for convenience
4. **Pretty-print JSON** during development for easier debugging
5. **Use `--quiet`** flag in scripts to reduce noise

## 📚 Full Documentation

- [Git Download](README_GIT_DOWNLOAD.md)
- [Batch Mode](README_BATCH_MODE.md)
- [Environment Variables](README_ENVIRONMENT_VARIABLES.md)
- [Milvus Integration](README_MILVUS.md)
- [Quick Start](QUICKSTART.md)

## 🔗 Useful Commands

```bash
# Show all environment variables
env | grep -E "^(GIT_|MD_)"

# Count components
find ./repos/moj-frontend/docs/components -mindepth 1 -maxdepth 1 -type d | wc -l

# List all concatenated files
find ./output -name "*-combined.md"

# Check Milvus collection stats
python 3_insert_to_milvus.py --search "test" --limit 1

# Verify JSON files
find ./output -name "*.json" -exec jq '.components[0].title' {} \;
```

## ⚡ One-Liners

```bash
# Quick test single component
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git" && python download_git_repo.py --depth 1 --target /tmp/test && python 1_concat_markdown.py /tmp/test/docs/components/alert -o /tmp/alert.md --recursive

# Batch process and search
python 1_concat_markdown.py ./repos/moj-frontend/docs/components --batch --output-dir ./output --recursive && python 3_insert_to_milvus.py --search "components"

# Count markdown files in all components
find ./repos/moj-frontend/docs/components -name "*.md" | wc -l
```
