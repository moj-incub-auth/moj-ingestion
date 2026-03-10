# MOJ Component Search API

REST API for semantic search of MOJ design system components using Milvus vector database.

## Overview

The Search API provides a simple REST interface to query the MOJ component knowledge base using natural language. It uses the same search functionality from `3_insert_to_milvus.py` and returns results in a standardized JSON format.

## Features

- 🔍 **Natural Language Search**: Query using plain English
- 🚀 **Fast Semantic Search**: Powered by Milvus vector database
- 📊 **Structured Results**: Returns component metadata in JSON format
- 🌐 **CORS Enabled**: Can be called from web applications
- 💪 **Production Ready**: Health checks and error handling

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

Or install individually:

```bash
pip install Flask flask-cors pymilvus sentence-transformers
```

### 2. Ensure Milvus is Running

```bash
docker-compose ps
# If not running:
docker-compose up -d
```

### 3. Ensure Components are Loaded

```bash
# Check if collection has data
python 3_insert_to_milvus.py --search "test" --limit 1
```

## Quick Start

### Start the API Server

```bash
python api_search.py
```

The server will start on `http://0.0.0.0:5000`

### Test with curl

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I show error messages?"}'
```

## API Endpoints

### Root - GET /

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "MOJ Component Search API",
  "version": "1.0.0",
  "endpoints": {
    "search": {...},
    "health": {...}
  }
}
```

### Health Check - GET /health

Check API and database health.

**Response:**
```json
{
  "status": "healthy",
  "collection": "knowledge_base",
  "entities": 25
}
```

### Search - POST /search

Search for components using natural language.

**Request Body:**
```json
{
  "message": "Example natural language query for the AI",
  "limit": 5
}
```

**Parameters:**
- `message` (required): Natural language search query
- `limit` (optional): Number of results to return (1-50, default: 5)

**Response:**
```json
{
  "components": [
    {
      "title": "Alert",
      "url": "https://design-patterns.service.justice.gov.uk/components/alert/",
      "description": "The alert component presents 1 of 4 types of alerts to a user...",
      "parent": "MOJ Design System",
      "accessibility": "AA",
      "created_at": "2026-03-09 14:53:43",
      "updated_at": "2026-03-09 14:53:43",
      "has_research": false,
      "views": 0
    },
    {
      "title": "Filter",
      "url": "https://design-patterns.service.justice.gov.uk/components/filter/",
      "description": "Use the filter component to help users filter...",
      "parent": "MOJ Design System",
      "accessibility": "AA",
      "created_at": "2026-03-09 14:53:43",
      "updated_at": "2026-03-09 14:53:43",
      "has_research": true,
      "views": 0
    }
  ]
}
```

## Usage Examples

### Using curl

```bash
# Basic search
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I show alerts?"}'

# Search with limit
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"message": "components for date selection", "limit": 3}'

# Health check
curl http://localhost:5000/health
```

### Using Python

```python
import requests

# Search for components
response = requests.post(
    'http://localhost:5000/search',
    json={'message': 'How do I show error messages?', 'limit': 5}
)

results = response.json()
for component in results['components']:
    print(f"{component['title']}: {component['description']}")
```

### Using JavaScript/Fetch

```javascript
fetch('http://localhost:5000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'How do I show alerts?',
    limit: 5
  })
})
.then(response => response.json())
.then(data => {
  data.components.forEach(component => {
    console.log(`${component.title}: ${component.url}`);
  });
});
```

### Using Test Client

We provide a Python test client:

```bash
# Single query
python test_api_client.py --query "How do I show alerts?"

# Interactive mode
python test_api_client.py

# Custom API URL
python test_api_client.py --url http://api.example.com:8080
```

### Using Test Script

Run comprehensive tests:

```bash
./test_api.sh
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MILVUS_HOST` | Milvus server host | localhost |
| `MILVUS_PORT` | Milvus server port | 19530 |
| `MILVUS_COLLECTION` | Collection name | knowledge_base |
| `MILVUS_EMBEDDING_MODEL` | Embedding model | nomic-ai/nomic-embed-text-v1.5 |

### Command-Line Options

```bash
python api_search.py --help
```

Options:
- `--host HOST` - Host to bind to (default: 0.0.0.0)
- `--port PORT` - Port to bind to (default: 5000)
- `--debug` - Enable debug mode

### Example with Custom Configuration

```bash
export MILVUS_HOST="milvus.example.com"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION="my_components"

python api_search.py --host 0.0.0.0 --port 8080
```

## Example Queries

### Finding Components by Functionality

```json
{"message": "How do I show error messages to users?"}
{"message": "component for selecting dates"}
{"message": "filter and search components"}
{"message": "dismissible notification"}
```

### Finding Components by Type

```json
{"message": "navigation components"}
{"message": "form input components"}
{"message": "alert and warning components"}
```

### Finding Components by Accessibility

```json
{"message": "accessible date picker"}
{"message": "screen reader friendly components"}
```

### Finding Components with Research

```json
{"message": "components with user research"}
{"message": "tested components"}
```

## Response Format

All successful search responses follow this structure:

```json
{
  "components": [
    {
      "title": "string",
      "url": "string",
      "description": "string",
      "parent": "string",
      "accessibility": "string",
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "updated_at": "YYYY-MM-DD HH:MM:SS",
      "has_research": boolean,
      "views": integer
    }
  ]
}
```

## Error Handling

### Missing Message Field

**Request:**
```json
{"query": "wrong field"}
```

**Response (400):**
```json
{
  "error": "Missing \"message\" field in request body",
  "example": {"message": "Example natural language query"}
}
```

### Search Failure

**Response (500):**
```json
{
  "error": "Search failed",
  "detail": "Connection refused..."
}
```

### Unhealthy Service

**Response (503):**
```json
{
  "status": "unhealthy",
  "error": "Collection not found..."
}
```

## Deployment

### Development

```bash
python api_search.py --debug
```

### Production with Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 api_search:app
```

### Production with Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

COPY api_search.py .
COPY 3_insert_to_milvus.py .

ENV MILVUS_HOST=milvus
ENV MILVUS_PORT=19530

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_search:app"]
```

Build and run:

```bash
docker build -t moj-search-api .
docker run -p 5000:5000 \
  -e MILVUS_HOST=localhost \
  -e MILVUS_COLLECTION=knowledge_base \
  moj-search-api
```

### Docker Compose

Add to `docker-compose.yml`:

```yaml
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MILVUS_HOST=milvus-standalone
      - MILVUS_PORT=19530
      - MILVUS_COLLECTION=knowledge_base
    depends_on:
      - milvus-standalone
```

## Performance

### Response Times

- Health check: < 50ms
- Search query: 100-500ms (depends on collection size)
- Cold start: 2-5s (loading embedding model)

### Optimization Tips

1. **Keep Model Loaded**: The embedding model stays in memory after first request
2. **Use Connection Pooling**: Milvus connections are reused
3. **Limit Results**: Request only what you need (limit parameter)
4. **Cache Results**: Consider caching common queries

## Monitoring

### Health Checks

```bash
# Simple check
curl http://localhost:5000/health

# With monitoring
while true; do
  curl -s http://localhost:5000/health | jq '.status'
  sleep 60
done
```

### Logging

Enable debug mode for detailed logging:

```bash
python api_search.py --debug
```

## Security Considerations

### Production Deployment

1. **CORS Configuration**: Update `CORS(app)` to restrict origins
2. **API Authentication**: Add API key or OAuth
3. **Rate Limiting**: Implement rate limiting
4. **HTTPS**: Use SSL/TLS in production
5. **Input Validation**: Already validates message field

### Example with API Key

```python
from functools import wraps
from flask import request

API_KEY = os.environ.get('API_KEY', 'your-secret-key')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/search', methods=['POST'])
@require_api_key
def search():
    # ... existing code
```

## Troubleshooting

### API Won't Start

```
Error: Could not initialize knowledge base
```

**Solution**: Check Milvus is running and collection exists:
```bash
docker-compose ps
python 3_insert_to_milvus.py --search "test" --limit 1
```

### Connection Refused

```
Connection refused: localhost:19530
```

**Solution**: Update MILVUS_HOST environment variable:
```bash
export MILVUS_HOST=your-milvus-host
python api_search.py
```

### Empty Results

**Solution**: Ensure components are loaded:
```bash
python 3_insert_to_milvus.py --batch
```

## Next Steps

1. **Add Authentication**: Implement API keys or OAuth
2. **Add Caching**: Cache frequent queries with Redis
3. **Add Rate Limiting**: Prevent abuse with flask-limiter
4. **Add Metrics**: Track usage with Prometheus
5. **Build UI**: Create web interface for searching

## Support

- Test the API: `./test_api.sh`
- Interactive client: `python test_api_client.py`
- Check health: `curl http://localhost:5000/health`
