# Git Repository Download Script

A Python script to clone git repositories using a URL from an environment variable or command line argument.

## Features

- ✅ Clone repositories via environment variable or CLI argument
- ✅ Support for specific branches
- ✅ Shallow clones (save bandwidth and disk space)
- ✅ Pull updates to existing repositories
- ✅ Automatic directory naming from repository URL
- ✅ Safe handling of existing directories
- ✅ Works with HTTPS, SSH, and git protocols

## Prerequisites

- Python 3.6+
- Git installed and available in PATH

```bash
# Verify git is installed
git --version
```

## Usage

### Method 1: Using Environment Variable (Recommended)

```bash
# Set the repository URL
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"

# Clone the repository
python 0_download_git_repo.py

# The repo will be cloned to ./moj-frontend/
```

### Method 1b: Using Environment Variables for URL and Target

```bash
# Set both URL and target directory
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
export GIT_TARGET_DIR="./repos/moj-frontend"

# Clone the repository
python 0_download_git_repo.py
```

### Method 2: Using Command Line Argument

```bash
# Clone directly with --url flag
python 0_download_git_repo.py --url https://github.com/ministryofjustice/moj-frontend.git
```

### Method 3: Custom Environment Variable

```bash
# Use a different environment variable name
export MY_REPO="https://github.com/user/repo.git"
python 0_download_git_repo.py --env-var MY_REPO
```

## Options

| Option | Description | Example |
|--------|-------------|---------|
| `--url URL` | Repository URL (overrides env var) | `--url https://github.com/user/repo.git` |
| `--target DIR` | Target directory | `--target ./my-repo` |
| `--branch NAME` | Clone specific branch | `--branch main` |
| `--depth N` | Shallow clone (only N commits) | `--depth 1` |
| `--pull DIR` | Pull updates in existing repo | `--pull ./my-repo` |
| `--quiet`, `-q` | Suppress git output | `--quiet` |
| `--env-var NAME` | Custom env var name | `--env-var MY_REPO_URL` |

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GIT_REPO_URL` | Repository URL to clone | `export GIT_REPO_URL="https://github.com/user/repo.git"` |
| `GIT_TARGET_DIR` | Target directory for cloning | `export GIT_TARGET_DIR="./repos/my-repo"` |

Note: Command line arguments (--url, --target) override environment variables.

## Examples

### Clone to Specific Directory

```bash
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
python 0_download_git_repo.py --target /path/to/destination
```

### Clone Specific Branch

```bash
python 0_download_git_repo.py \
    --url https://github.com/ministryofjustice/moj-frontend.git \
    --branch develop
```

### Shallow Clone (Faster, Less Disk Space)

Perfect for CI/CD or when you only need the latest code:

```bash
python 0_download_git_repo.py \
    --url https://github.com/ministryofjustice/moj-frontend.git \
    --depth 1
```

This downloads only the latest commit, saving bandwidth and time.

### Clone Private Repository (SSH)

```bash
export GIT_REPO_URL="git@github.com:ministryofjustice/private-repo.git"
python 0_download_git_repo.py
```

Make sure your SSH keys are configured correctly.

### Update Existing Repository

```bash
# Pull latest changes
python 0_download_git_repo.py --pull ./moj-frontend
```

### Quiet Mode

```bash
python 0_download_git_repo.py \
    --url https://github.com/ministryofjustice/moj-frontend.git \
    --quiet
```

## Integration Examples

### In a Shell Script

```bash
#!/bin/bash
# download_repos.sh

# Download multiple repositories
export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"
python 0_download_git_repo.py --target ./repos/moj-frontend

export GIT_REPO_URL="https://github.com/alphagov/govuk-frontend.git"
python 0_download_git_repo.py --target ./repos/govuk-frontend

echo "All repositories downloaded!"
```

### In Another Python Script

```python
import os
import subprocess

# Set environment variable
os.environ['GIT_REPO_URL'] = 'https://github.com/ministryofjustice/moj-frontend.git'

# Run the download script
result = subprocess.run(
    ['python', '0_download_git_repo.py', '--target', './data/moj-frontend'],
    check=True
)

if result.returncode == 0:
    print("Repository downloaded successfully!")
```

### Docker/CI Integration

```dockerfile
# Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

COPY 0_download_git_repo.py /app/

ENV GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"

RUN python /app/0_download_git_repo.py --target /app/repo
```

### GitHub Actions

```yaml
# .github/workflows/download.yml
name: Download Repository

on: [push]

jobs:
  download:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Download repository
        env:
          GIT_REPO_URL: https://github.com/ministryofjustice/moj-frontend.git
        run: |
          python 0_download_git_repo.py --target ./external-repo
```

## Error Handling

### Directory Already Exists

If the target directory exists and is not empty, the script will prompt:

```
⚠️  Warning: Directory './moj-frontend' already exists and is not empty
Do you want to remove it and re-clone? (y/N):
```

- Type `y` to remove and re-clone
- Type `n` or press Enter to abort

### No Git Installed

```
❌ Error: 'git' command not found. Please install git first.
```

Install git:
- Ubuntu/Debian: `sudo apt-get install git`
- macOS: `brew install git`
- Windows: Download from https://git-scm.com/

### Invalid URL

```
❌ Error: Invalid git URL: not-a-url
   URL should start with http://, https://, git@, or ssh://
```

### Authentication Required

For private repositories, ensure:
- HTTPS: Git credential helper is configured
- SSH: SSH keys are set up correctly

## Advanced Usage

### Clone Multiple Repositories in Parallel

```bash
#!/bin/bash
# parallel_clone.sh

clone_repo() {
    python 0_download_git_repo.py --url "$1" --target "$2" &
}

clone_repo "https://github.com/ministryofjustice/moj-frontend.git" "./repos/moj-frontend"
clone_repo "https://github.com/alphagov/govuk-frontend.git" "./repos/govuk-frontend"
clone_repo "https://github.com/nhsuk/nhsuk-frontend.git" "./repos/nhsuk-frontend"

# Wait for all background jobs to complete
wait

echo "All repositories downloaded!"
```

### Clone and Process

```bash
#!/bin/bash
# clone_and_process.sh

export GIT_REPO_URL="https://github.com/ministryofjustice/moj-frontend.git"

# Clone the repository
if python 0_download_git_repo.py --target ./moj-frontend --depth 1; then
    echo "✅ Repository cloned successfully"

    # Process the downloaded repository
    cd moj-frontend

    # Find all component documentation
    find ./docs/components -name "*.md" -type f

    echo "Processing complete!"
else
    echo "❌ Failed to clone repository"
    exit 1
fi
```

## Return Codes

- `0`: Success
- `1`: Error (clone failed, invalid URL, etc.)

## Troubleshooting

### Permission Denied (SSH)

```bash
# Test SSH connection
ssh -T git@github.com

# If it fails, add your SSH key
ssh-add ~/.ssh/id_rsa
```

### Large Repository Timeout

Use shallow clone to reduce download size:

```bash
python 0_download_git_repo.py --url https://github.com/large/repo.git --depth 1
```

### Proxy Issues

Configure git proxy if needed:

```bash
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy https://proxy.example.com:8080
```

## Use Cases

1. **CI/CD Pipelines**: Download dependencies or external repositories
2. **Data Ingestion**: Clone repositories for documentation processing
3. **Automated Testing**: Clone repos to test against
4. **Backup/Mirroring**: Create local copies of important repositories
5. **Batch Processing**: Download multiple repos for analysis

## License

MIT License - Feel free to use and modify as needed.
