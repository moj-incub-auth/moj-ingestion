# Concat Task Container

Container for concatenating markdown files from directories - designed for Tekton/Kubernetes pipeline tasks.

## What It Does

This container runs the `concat-task.py` script which:
- Concatenates multiple markdown files into a single file
- Supports batch processing of multiple subdirectories
- Adds filename headers and separators (optional)
- Works in both single-file and batch modes

## Building

```bash
# Build the container
./build.sh

# Or manually
docker build -f Containerfile -t concat-task:latest .
podman build -f Containerfile -t concat-task:latest .
```

## Usage

### Single Directory Mode

Concatenate all markdown files from a single directory:

```bash
# Using volume mounts
docker run --rm \
  -v $(pwd)/docs:/workspace/source:ro \
  -v $(pwd)/output:/workspace/output \
  concat-task:latest \
  /workspace/source -o /workspace/output/combined.md

# With recursive search
docker run --rm \
  -v $(pwd)/docs:/workspace/source:ro \
  -v $(pwd)/output:/workspace/output \
  concat-task:latest \
  /workspace/source -o /workspace/output/combined.md --recursive
```

### Batch Mode

Process all subdirectories as separate components:

```bash
# Batch mode (each subdirectory becomes a separate output file)
docker run --rm \
  -v $(pwd)/docs/components:/workspace/source:ro \
  -v $(pwd)/output:/workspace/output \
  concat-task:latest \
  --batch --recursive

# With environment variables
docker run --rm \
  -e MD_SOURCE_DIR=/workspace/source \
  -e MD_OUTPUT_DIR=/workspace/output \
  -v $(pwd)/docs/components:/workspace/source:ro \
  -v $(pwd)/output:/workspace/output \
  concat-task:latest \
  --batch --recursive
```

### Options

```bash
# Show help
docker run --rm concat-task:latest --help

# No separators or filenames
docker run --rm \
  -v $(pwd)/docs:/workspace/source:ro \
  -v $(pwd)/output:/workspace/output \
  concat-task:latest \
  /workspace/source -o /workspace/output/combined.md \
  --no-separators --no-filenames

# Exclude files
docker run --rm \
  -v $(pwd)/docs:/workspace/source:ro \
  -v $(pwd)/output:/workspace/output \
  concat-task:latest \
  /workspace/source -o /workspace/output/combined.md \
  --exclude README.md CHANGELOG.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MD_SOURCE_DIR` | Source directory with markdown files | `/workspace/source` |
| `MD_OUTPUT_DIR` | Output directory for batch mode | `/workspace/output` |

## Volume Mounts

| Path | Purpose | Mode |
|------|---------|------|
| `/workspace/source` | Source markdown files | `ro` (read-only) |
| `/workspace/output` | Output concatenated files | `rw` (read-write) |

## Tekton Task Example

```yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: concat-markdown
spec:
  params:
    - name: source-dir
      description: Source directory containing markdown files
      default: "docs/components"
    - name: output-dir
      description: Output directory for concatenated files
      default: "combined-output"
    - name: recursive
      description: Search subdirectories recursively
      default: "true"
  workspaces:
    - name: source
      description: Workspace with source files
  steps:
    - name: concat
      image: concat-task:latest
      workingDir: $(workspaces.source.path)
      env:
        - name: MD_SOURCE_DIR
          value: "$(workspaces.source.path)/$(params.source-dir)"
        - name: MD_OUTPUT_DIR
          value: "$(workspaces.source.path)/$(params.output-dir)"
      script: |
        #!/bin/bash
        set -e

        echo "Concatenating markdown files..."
        echo "Source: $MD_SOURCE_DIR"
        echo "Output: $MD_OUTPUT_DIR"

        if [ "$(params.recursive)" = "true" ]; then
          python concat-task.py --batch --recursive
        else
          python concat-task.py --batch
        fi
```

## Kubernetes Job Example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: concat-markdown-job
spec:
  template:
    spec:
      containers:
      - name: concat
        image: concat-task:latest
        env:
        - name: MD_SOURCE_DIR
          value: "/data/source"
        - name: MD_OUTPUT_DIR
          value: "/data/output"
        command: ["python", "concat-task.py"]
        args: ["--batch", "--recursive"]
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: markdown-data
      restartPolicy: OnFailure
```

## Testing Locally

```bash
# Create test directories
mkdir -p test/source/component1 test/source/component2 test/output

# Add some test markdown files
echo "# Test 1" > test/source/component1/file1.md
echo "# Test 2" > test/source/component1/file2.md
echo "# Test 3" > test/source/component2/file1.md

# Run in batch mode
docker run --rm \
  -v $(pwd)/test/source:/workspace/source:ro \
  -v $(pwd)/test/output:/workspace/output \
  concat-task:latest \
  --batch

# Check output
ls -la test/output/
cat test/output/component1-combined.md
cat test/output/component2-combined.md
```

## Exit Codes

- `0` - Success
- `1` - Error (no files found, invalid directory, etc.)

## Notes

- Source volumes should be mounted as read-only (`:ro`) for safety
- Output directory will be created automatically if it doesn't exist
- The script automatically excludes the output file if it's in the source directory
- In batch mode, each subdirectory produces a separate `{name}-combined.md` file
