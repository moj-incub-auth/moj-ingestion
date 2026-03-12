# Parse-to-JSON Task Container

Container for parsing MOJ component markdown files to structured JSON format - designed for Tekton/Kubernetes pipeline tasks.

## What It Does

This container runs the `parse_component_to_json.py` script which:
- Parses concatenated markdown files containing component documentation
- Extracts structured information (title, description, URL, etc.)
- Outputs JSON in a standardized format
- Supports both single-file and batch processing modes

## Building

```bash
# Build the container
./build.sh

# Or manually
docker build -f Containerfile -t parse-to-json:latest .
podman build -f Containerfile -t parse-to-json:latest .
```

## Usage

### Single File Mode

Parse a single markdown file to JSON:

```bash
# Parse one file
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  parse-to-json:latest \
  /workspace/data/alert-combined.md -o /workspace/data/alert.json

# Print to stdout instead of file
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  parse-to-json:latest \
  /workspace/data/alert-combined.md
```

### Batch Mode

Process all `*-combined.md` files in a directory:

```bash
# Batch mode (processes all *-combined.md files)
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  parse-to-json:latest \
  --batch

# With environment variable
docker run --rm \
  -e MD_OUTPUT_DIR=/workspace/data \
  -v $(pwd)/data:/workspace/data \
  parse-to-json:latest \
  --batch

# With custom input directory
docker run --rm \
  -v $(pwd)/combined-output:/workspace/input \
  parse-to-json:latest \
  --batch --input-dir /workspace/input
```

### Options

```bash
# Show help
docker run --rm parse-to-json:latest --help

# Compact JSON output (no pretty printing)
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  parse-to-json:latest \
  /workspace/data/alert-combined.md -o /workspace/data/alert.json \
  --no-pretty

# Custom indentation
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  parse-to-json:latest \
  /workspace/data/alert-combined.md -o /workspace/data/alert.json \
  --indent 4
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MD_OUTPUT_DIR` | Directory containing markdown files (batch mode) | `/workspace/data` |

## Volume Mounts

| Path | Purpose | Mode |
|------|---------|------|
| `/workspace/data` | Input markdown and output JSON files | `rw` (read-write) |

## Output Format

The script generates JSON in this format:

```json
{
  "filecontent": "... full markdown content ...",
  "component": {
    "title": "Alert",
    "url": "https://design-patterns.service.justice.gov.uk/components/alert/",
    "description": "The alert component presents 1 of 4 types of alerts to a user...",
    "parent": "MOJ Design System",
    "accessibility": "AA",
    "created_at": "2026-03-09 14:53:43",
    "updated_at": "2026-03-09 14:53:43",
    "has_research": false,
    "views": 0
  }
}
```

## Extraction Rules

The parser extracts information using these rules:

1. **Title**: From frontmatter `title:` field or first H1 heading
2. **Description**: From frontmatter `lede:` field or first paragraph of Overview section
3. **URL**: Generated from component path or title slug
4. **Parent**: Detected from content ("MOJ Design System" or "GOV.UK Design System")
5. **Accessibility**: WCAG level (defaults to "AA" for government services)
6. **Dates**: From frontmatter `statusDate:` or current timestamp
7. **Has Research**: Detected by presence of research-related keywords
8. **Views**: Defaults to 0 (tracked separately in production)

## Tekton Task Example

```yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: parse-to-json
spec:
  params:
    - name: input-dir
      description: Directory containing markdown files
      default: "combined-output"
  workspaces:
    - name: source
      description: Workspace with markdown files
  steps:
    - name: parse
      image: parse-to-json:latest
      workingDir: $(workspaces.source.path)
      env:
        - name: MD_OUTPUT_DIR
          value: "$(workspaces.source.path)/$(params.input-dir)"
      script: |
        #!/bin/bash
        set -e

        echo "Parsing markdown files to JSON..."
        echo "Input directory: $MD_OUTPUT_DIR"

        python parse_component_to_json.py --batch --pretty

        echo "Parsing complete!"
        echo "JSON files created:"
        find $MD_OUTPUT_DIR -name "*.json" -type f
```

## Kubernetes Job Example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parse-markdown-to-json
spec:
  template:
    spec:
      containers:
      - name: parse
        image: parse-to-json:latest
        env:
        - name: MD_OUTPUT_DIR
          value: "/data"
        command: ["python", "parse_component_to_json.py"]
        args: ["--batch", "--pretty"]
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: component-data
      restartPolicy: OnFailure
```

## Testing Locally

```bash
# Create test directory structure
mkdir -p test/data

# Create a sample concatenated markdown file
cat > test/data/alert-combined.md <<'EOF'
---
title: Alert
lede: The alert component presents alerts to users
---

# Alert Component

## Overview

The alert component presents 1 of 4 types of alerts to a user:
- Information
- Success
- Warning
- Error

Use this component when you need to notify users of important information.
EOF

# Run in single file mode
docker run --rm \
  -v $(pwd)/test/data:/workspace/data \
  parse-to-json:latest \
  /workspace/data/alert-combined.md -o /workspace/data/alert.json

# Check output
cat test/data/alert.json | jq '.component'

# Create multiple combined markdown files for batch test
cp test/data/alert-combined.md test/data/filter-combined.md

# Run in batch mode
docker run --rm \
  -v $(pwd)/test/data:/workspace/data \
  parse-to-json:latest \
  --batch

# Check outputs
ls -la test/data/*.json
```

## Dependencies

This container uses **only Python standard library** - no external dependencies required!

The script uses:
- `argparse` - Command-line argument parsing
- `json` - JSON encoding/decoding
- `os` - Operating system interfaces
- `re` - Regular expressions
- `pathlib` - Object-oriented filesystem paths
- `datetime` - Date and time handling

## Exit Codes

- `0` - Success
- `1` - Error (file not found, invalid directory, parsing error)

## Notes

- The script looks for files matching the pattern `*-combined.md` in batch mode
- Output JSON files are created in the same directory as input markdown files
- The `filecontent` field contains the full markdown content for vector embeddings
- Dates use the format `YYYY-MM-DD HH:MM:SS`
- The parser is forgiving - if specific fields can't be extracted, it uses sensible defaults

## Common Issues

### No files found in batch mode

**Issue**: "No *-combined.md files found"

**Solution**: Ensure your markdown files end with `-combined.md` suffix or use single file mode for other naming patterns.

### Parsing errors

**Issue**: "Error: ..."

**Solution**: Check that the markdown file is valid UTF-8 encoded text. The parser is designed to handle most markdown formats gracefully.

### Permission denied

**Issue**: Can't write output files

**Solution**: Ensure the volume mount has write permissions. Don't mount as read-only (`:ro`).
