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
pip install -r requirements-milvus.txt

# Or install individually
pip install pymilvus sentence-transformers numpy einops
```

* Start Milvus

```sh
docker-compose up -d
```

* Stop Milvus

```sh
docker-compose down
```

# Kubernetes Milvus


# Ingestion & Validation

## Concatenate all files for a component

```bash
python 1_cconcat_markdown.py /<PATH-TO>/moj-frontend/docs/components/alert -o alert-combined.md  --exclude README.md LICENSE.md
```

For more option see [README-CONCAT_MARKDOWN.md](docs/README-CONCAT_MARKDOWN.md)

## Parse to JSON Format

```bash
python parse_component_to_json.py date-picker-combined.md -o date-picker-component.json  --pretty
```

For more option see [README_PARSE_COMPONENT_TO_JSON.md](docs/README_PARSE_COMPONENT_TO_JSON.md)


## Insert to Milvus & Search

1. First time, create the `knowledge_base` collection with the proper schema:

```bash
python 3_insert_to_milvus.py --create
```

2. To drop and recreate an existing collection:

```bash
python 3_insert_to_milvus.py --drop --create
```

3. Insert your parsed component JSON into the collection:

```bash
python 3_insert_to_milvus.py alert-component.json
```

4. Perform similarity check

```bash
python insert_to_milvus.py --search "Do you have a component which can help with dates?"
```

```bash
python insert_to_milvus.py --search "Show me components that have research done"
```