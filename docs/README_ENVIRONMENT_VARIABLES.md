# Environment Variables Guide

This guide documents all environment variables supported across the MOJ component ingestion pipeline scripts.

## Overview

All scripts in the pipeline support environment variables for easier automation and batch processing. Command-line arguments always take precedence over environment variables.

## Supported Environment Variables

### Git Repository Download (`download_git_repo.py`)

| Variable | Description | Example |
|----------|-------------|---------|
| `GIT_REPO_URL` | Repository URL to clone | `https://github.com/ministryofjustice/moj-frontend.git` |
| `GIT_TARGET_DIR` | Target directory for cloning | `./repos/moj-frontend` |

**Priority**: `--url` flag > `GIT_REPO_URL` env var
**Priority**: `--target` flag > `GIT_TARGET_DIR` env var > auto-generated name

### Markdown Concatenation (`1_concat_markdown.py`)

| Variable | Description | Example |
|----------|-------------|---------|
| `MD_SOURCE_DIR` | Directory containing markdown files (single mode) or parent directory (batch mode) | `./docs/components/alert` or `./docs/components` |
| `MD_OUTPUT_FILE` | Output file path (single mode only) | `alert-combined.md` |
| `MD_OUTPUT_DIR` | Output directory (batch mode only) | `./batch-output` |

**Single Mode Priority**: positional arg > `MD_SOURCE_DIR` env var
**Single Mode Priority**: `--output` flag > `MD_OUTPUT_FILE` env var > `concatenated.md` (default)
**Batch Mode Priority**: positional arg > `MD_SOURCE_DIR` env var
**Batch Mode Priority**: `--output-dir` flag > `MD_OUTPUT_DIR` env var > `./output` (default)

### JSON Parsing (`2_parse_component_to_json.py`)

| Variable | Description | Example |
|----------|-------------|---------|
| `MD_OUTPUT_DIR` | Directory containing markdown files to parse (batch mode) | `./batch-output` |

**Single Mode Priority**: positional arg (required)
**Batch Mode Priority**: `--input-dir` flag > `MD_OUTPUT_DIR` env var

Currently uses command-line arguments only. No environment variables supported.

### Milvus Insertion (`3_insert_to_milvus.py`)

No environment variables for file paths, but connection details can be customized:
- `--host` for Milvus server host (default: localhost)
- `--port` for Milvus server port (default: 19530)
- `--collection` for collection name (default: knowledge_base)

## Usage Examples

### Example 1: Simple Single Component

Process a single component using environment variables:

```bash
# Set all variables
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components/alert"
export MD_OUTPUT_FILE="alert-combined.md"

# Run the pipeline
python download_git_repo.py --depth 1
python 1_concat_markdown.py --recursive
python 2_parse_component_to_json.py alert-combined.md -o alert-component.json --pretty
python 3_insert_to_milvus.py alert-component.json
```

### Example 2: Batch Processing Multiple Components

Process multiple components in a loop:

```bash
#!/bin/bash

# Clone repository once
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
python download_git_repo.py --depth 1

# Process each component
for component in alert button filter search; do
    echo "Processing $component..."

    # Set component-specific variables
    export MD_SOURCE_DIR="./repos/moj-frontend/docs/components/$component"
    export MD_OUTPUT_FILE="${component}-combined.md"

    # Run pipeline steps
    python 1_concat_markdown.py --recursive
    python 2_parse_component_to_json.py "$MD_OUTPUT_FILE" -o "${component}-component.json" --pretty
    python 3_insert_to_milvus.py "${component}-component.json"
done
```

### Example 3: Batch Mode - Process All Components at Once

Use batch mode to process all components in one command:

```bash
#!/bin/bash

# Clone repository
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
python download_git_repo.py --depth 1

# Batch process all components
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components"
export MD_OUTPUT_DIR="./batch-output"
python 1_concat_markdown.py --batch --recursive

# Process each generated file
for md_file in ./batch-output/*/*.md; do
    component=$(basename "$(dirname "$md_file")")
    python 2_parse_component_to_json.py "$md_file" \
        -o "./batch-output/$component/${component}.json" --pretty
    python 3_insert_to_milvus.py "./batch-output/$component/${component}.json"
done
```

Or use the automated batch script:

```bash
./batch_process_all_components.sh
```

### Example 4: Using Complete Pipeline Script

The included `complete_pipeline_example.sh` demonstrates the full workflow for a single component:

```bash
# Process the alert component (default)
./complete_pipeline_example.sh

# Process a different component
./complete_pipeline_example.sh button

# Process filter component
./complete_pipeline_example.sh filter
```

### Example 5: CI/CD Integration

GitHub Actions example:

```yaml
name: Ingest Components

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-milvus.txt

      - name: Download repository
        env:
          GIT_REPO_URL: https://github.com/ministryofjustice/moj-frontend.git
          GIT_TARGET_DIR: ./moj-frontend
        run: python download_git_repo.py --depth 1

      - name: Process components
        env:
          MILVUS_HOST: ${{ secrets.MILVUS_HOST }}
        run: |
          for component in alert button filter; do
            export MD_SOURCE_DIR="./moj-frontend/docs/components/$component"
            export MD_OUTPUT_FILE="${component}-combined.md"

            python 1_concat_markdown.py --recursive
            python 2_parse_component_to_json.py "$MD_OUTPUT_FILE" -o "${component}.json" --pretty
            python 3_insert_to_milvus.py "${component}.json" --host "$MILVUS_HOST"
          done
```

### Example 5: Docker Integration

Dockerfile using environment variables:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app
COPY *.py requirements-milvus.txt ./
RUN pip install -r requirements-milvus.txt

# Set default environment variables
ENV GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
ENV GIT_TARGET_DIR="/app/repos/moj-frontend"
ENV MD_SOURCE_DIR="/app/repos/moj-frontend/docs/components/alert"
ENV MD_OUTPUT_FILE="/app/data/alert-combined.md"

# Run pipeline
RUN python download_git_repo.py --depth 1 && \
    python 1_concat_markdown.py --recursive && \
    python 2_parse_component_to_json.py "$MD_OUTPUT_FILE" -o /app/data/alert.json
```

### Example 6: Kubernetes ConfigMap

Use ConfigMaps to configure the pipeline:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ingestion-config
data:
  GIT_REPO_URL: "https://github.com/ministryofjustice/moj-frontend.git"
  GIT_TARGET_DIR: "/data/repos/moj-frontend"
  MD_SOURCE_DIR: "/data/repos/moj-frontend/docs/components/alert"
  MD_OUTPUT_FILE: "/data/output/alert-combined.md"

---
apiVersion: batch/v1
kind: Job
metadata:
  name: component-ingestion
spec:
  template:
    spec:
      containers:
      - name: ingestion
        image: moj-ingestion:latest
        envFrom:
        - configMapRef:
            name: ingestion-config
        command: ["./complete_pipeline_example.sh"]
```

## Best Practices

### 1. Use Environment Variables for Automation

```bash
# Good: Easy to automate
export MD_SOURCE_DIR="./docs"
python 1_concat_markdown.py

# Less ideal for scripts: Harder to automate
python 1_concat_markdown.py ./docs
```

### 2. Override with Arguments When Needed

```bash
# Use env vars for defaults
export MD_SOURCE_DIR="./default-docs"

# Override for specific case
python 1_concat_markdown.py ./special-docs
```

### 3. Document Your Variables

Create a `.env.example` file:

```bash
# .env.example
GIT_REPO_URL=https://github.com/ministryofjustice/moj-frontend.git
GIT_TARGET_DIR=./repos/moj-frontend
MD_SOURCE_DIR=./repos/moj-frontend/docs/components/alert
MD_OUTPUT_FILE=alert-combined.md
```

### 4. Use .env Files (with direnv or similar)

```bash
# .envrc (for direnv)
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"
export MD_SOURCE_DIR="./repos/moj-frontend/docs/components/alert"
export MD_OUTPUT_FILE="alert-combined.md"

# Allow with: direnv allow
```

### 5. Validate Before Running

```bash
#!/bin/bash

# Check required variables
if [ -z "$GIT_REPO_URL" ]; then
    echo "Error: GIT_REPO_URL not set"
    exit 1
fi

# Run pipeline
python download_git_repo.py
```

## Variable Precedence

Understanding the precedence order helps avoid confusion:

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Default values** (lowest priority)

Example:

```bash
export GIT_TARGET_DIR="./from-env"

# Uses ./from-cli (argument overrides env var)
python download_git_repo.py --url https://github.com/user/repo.git --target ./from-cli

# Uses ./from-env (no argument, uses env var)
python download_git_repo.py --url https://github.com/user/repo.git

# Uses ./repo (no argument, no env var, auto-generated)
unset GIT_TARGET_DIR
python download_git_repo.py --url https://github.com/user/repo.git
```

## Debugging

### Check Active Variables

```bash
# Show all relevant environment variables
env | grep -E "^(GIT_|MD_)"

# Or specifically
echo "GIT_REPO_URL: $GIT_REPO_URL"
echo "MD_SOURCE_DIR: $MD_SOURCE_DIR"
```

### Clear Variables

```bash
# Unset individual variables
unset GIT_REPO_URL
unset GIT_TARGET_DIR
unset MD_SOURCE_DIR
unset MD_OUTPUT_FILE

# Or in one line
unset GIT_REPO_URL GIT_TARGET_DIR MD_SOURCE_DIR MD_OUTPUT_FILE
```

### Test Variables

```bash
# Test if variable is set
if [ -n "$GIT_REPO_URL" ]; then
    echo "GIT_REPO_URL is set to: $GIT_REPO_URL"
else
    echo "GIT_REPO_URL is not set"
fi
```

## Common Patterns

### Pattern 1: Process All Components

```bash
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"

python download_git_repo.py --depth 1

for component_dir in ./repos/moj-frontend/docs/components/*/; do
    component=$(basename "$component_dir")
    export MD_SOURCE_DIR="$component_dir"
    export MD_OUTPUT_FILE="${component}-combined.md"

    python 1_concat_markdown.py --recursive
    python 2_parse_component_to_json.py "$MD_OUTPUT_FILE" -o "${component}.json" --pretty
    python 3_insert_to_milvus.py "${component}.json"
done
```

### Pattern 2: Different Repos, Same Structure

```bash
process_repo() {
    local repo_url=$1
    local repo_name=$(basename "$repo_url" .git)

    export GIT_REPO_URL="$repo_url"
    export GIT_TARGET_DIR="./repos/$repo_name"

    python download_git_repo.py --depth 1
}

process_repo "https://github.com/ministryofjustice/moj-frontend.git"
process_repo "https://github.com/alphagov/govuk-frontend.git"
process_repo "https://github.com/nhsuk/nhsuk-frontend.git"
```

## Security Considerations

### Don't Commit .env Files

```bash
# .gitignore
.env
.envrc
```

### Use Secrets for Sensitive Data

```bash
# Good: Use secret management
export MILVUS_PASSWORD=$(cat /run/secrets/milvus_password)

# Bad: Hardcoded passwords
export MILVUS_PASSWORD="mypassword123"
```

### Validate URLs

```bash
# Validate repo URL before using
if [[ "$GIT_REPO_URL" =~ ^https://github\.com/ ]]; then
    python download_git_repo.py
else
    echo "Error: Invalid repository URL"
fi
```

## Summary

Environment variables provide a flexible way to configure the ingestion pipeline:

✅ **Easier automation** - Script-friendly configuration
✅ **Consistent interface** - Same pattern across all scripts
✅ **Override capability** - Command-line args when needed
✅ **CI/CD ready** - Perfect for pipelines and containers

Start with the `complete_pipeline_example.sh` script to see all variables in action!

### Milvus Insertion (`3_insert_to_milvus.py`)

| Variable | Description | Example |
|----------|-------------|---------|
| `MILVUS_HOST` | Milvus server hostname | `localhost` |
| `MILVUS_PORT` | Milvus server port | `19530` |
| `MILVUS_COLLECTION` | Collection name | `knowledge_base` |
| `MILVUS_EMBEDDING_MODEL` | Embedding model name | `nomic-ai/nomic-embed-text-v1.5` |

**Priority**: CLI flags > environment variables > defaults

