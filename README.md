# moj-ingestion

# milvus schema

```
{
  "filecontent": "COMBINED MDs content",
  "component": {
    "title": "Alert",
    "url": "https://design-patterns.service.justice.gov.uk/components/alert/",
    "description": "The alert component presents 1 of 4 types of alerts to a user. It can stay on the page or be dismissed by the user.",
    "parent": "MOJ Design System",
    "accessibility": "AA",
    "created_at": "2026-03-09 14:53:43",
    "updated_at": "2026-03-09 14:53:43",
    "has_research": false,
    "views": 0
  }
}
```

# Local Milvus

* Prereqs

```bash
# Install all requirements
uv sync
```

* Start Milvus

```sh
docker-compose up -d
```

* Stop Milvus

```sh
docker-compose down
```

# Ingestion & Validation


## Prereqs

```bash
### Install all requirements
<<<<<<< HEAD
uv sync
=======
pip install -r requirements.txt
>>>>>>> dev-stelios
```

## Retrieve repository

| Variable | Description | Example |
|----------|-------------|---------|
| `GIT_REPO_URL` | Repository URL to clone | `export GIT_REPO_URL="https://github.com/user/repo.git"` |
| `GIT_TARGET_DIR` | Target directory for cloning | `export GIT_TARGET_DIR="/tmp/my-repo"` |


```bash
<<<<<<< HEAD
uv run download_git_repo.py --depth 1
=======
python download_git_repo.py --depth 1
>>>>>>> dev-stelios
```

## Concatenate all files for a component

| Variable | Description | Example |
|----------|-------------|---------|
| `MD_SOURCE_DIR` | Parent directory containing component subdirectories | `export MD_SOURCE_DIR="/tmp/moj-frontend/docs/components"` |
| `MD_OUTPUT_DIR` | Output directory for batch processing | `export MD_OUTPUT_DIR="/tmp/moj-frontend/combined-output"` |

```bash
<<<<<<< HEAD
uv run 1_concat_markdown.py --batch --recursive
=======
python 1_concat_markdown.py --batch --recursive
>>>>>>> dev-stelios
```

For more option see [README-CONCAT_MARKDOWN.md](docs/README-CONCAT_MARKDOWN.md)

## Parse to JSON Format

| Variable | Description | Example |
|----------|-------------|---------|
| `MD_OUTPUT_DIR` | Output directory for batch processing | `export MD_OUTPUT_DIR="/tmp/moj-frontend/combined-output"` |

```bash
<<<<<<< HEAD
uv run 2_parse_component_to_json.py --batch
=======
python 2_parse_component_to_json.py --batch
>>>>>>> dev-stelios
```

For more option see [README_PARSE_COMPONENT_TO_JSON.md](docs/README_PARSE_COMPONENT_TO_JSON.md)


## Insert to Milvus & Search

| Variable | Description | Default |
|----------|-------------|---------|
| `MILVUS_HOST` | Milvus server host | localhost/Route |
| `MILVUS_PORT` | Milvus server port | 19530 |
| `MILVUS_COLLECTION` | Collection name | knowledge_base |
| `MILVUS_EMBEDDING_MODEL` | Embedding model | nomic-ai/nomic-embed-text-v1.5 |


1. First time, create the `knowledge_base` collection with the proper schema:


| Milvus Location | Command | 
|----------|-------------|
<<<<<<< HEAD
| Local | `uv run 3_insert_to_milvus.py --create --collection=knowledge_base` |
| Remote | `uv run 3_insert_to_milvus.py --drop --create --host=<ROUTE> --port=19530 --collection=knowledge_base` |
=======
| Local | `python 3_insert_to_milvus.py --create --collection=knowledge_base` |
| Remote | `python 3_insert_to_milvus.py --drop --create --host=<ROUTE> --port=19530 --collection=knowledge_base` |
>>>>>>> dev-stelios

2. To drop and recreate an existing collection:

| Milvus Location | Command | 
|----------|-------------|
<<<<<<< HEAD
| Local | `uv run 3_insert_to_milvus.py --drop --create --collection=knowledge_base` |
| Remote | `uv run 3_insert_to_milvus.py --drop --create --host=<ROUTE> --port=19530 --collection=knowledge_base` |
=======
| Local | `python 3_insert_to_milvus.py --drop --create --collection=knowledge_base` |
| Remote | `python 3_insert_to_milvus.py --drop --create --host=<ROUTE> --port=19530 --collection=knowledge_base` |
>>>>>>> dev-stelios


3. Insert your parsed component JSON into the collection:


| Milvus Location | Command | 
|----------|-------------|
<<<<<<< HEAD
| Local | `uv run 3_insert_to_milvus.py --batch --collection=knowledge_base` |
| Remote | `uv run 3_insert_to_milvus.py --batch --host=<ROUTE> --port=19530 --collection=knowledge_base` |
=======
| Local | `python 3_insert_to_milvus.py --batch --collection=knowledge_base` |
| Remote | `python 3_insert_to_milvus.py --batch --host=<ROUTE> --port=19530 --collection=knowledge_base` |
>>>>>>> dev-stelios


4. Perform similarity check

```bash
uv run 3_insert_to_milvus.py --search "Do you have a component which can help with dates?"
```

```bash
<<<<<<< HEAD
uv run 3_insert_to_milvus.py --search "Show me components that have research done"
=======
python 3_insert_to_milvus.py --search "Show me components that have research done"
>>>>>>> dev-stelios
```

# Search API

`cd search_api`

## Build Image Container

`./build_container.sh`

## Run Container

```bash
podman run -d   \
  --name moj-search-api  \
  --network host  \
  -p 5000:5000   \
  -e MILVUS_HOST=0.0.0.0 [OCP Route/SVC] \
  -e MILVUS_PORT=19530 \
  -e MILVUS_COLLECTION=knowledge_base  \
  moj-search-api:latest
```

## Query

```bash
 curl -X POST http://0.0.0.0:5000/search   -H "Content-Type: application/json"   -d '{"message": "How do I show alerts?", "limit": 10}' |j
 ```

Result

```
{
  "components": [
    {
      "accessibility": "AA",
      "created_at": "",
      "description": "The notification badge component shows users that there are items in a service that need their attention.",
      "has_research": true,
      "parent": "MOJ Design System",
      "title": "Notification badge",
      "updated_at": "",
      "url": "https://design-patterns.service.justice.gov.uk/components/notification-badge/",
      "views": 0
    },
    {
      "accessibility": "AA",
      "created_at": "",
      "description": "The inset text (highlighted) component emphasises guidance to busy internal users of a service.",
      "has_research": false,
      "parent": "MOJ Design System",
      "title": "Inset text (highlighted)",
      "updated_at": "",
      "url": "https://design-patterns.service.justice.gov.uk/components/inset-text-highlighted/",
      "views": 0
    }
  ]
}
```
