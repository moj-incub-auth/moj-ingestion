
## 🌐 Search API

### Start API Server
```bash
# Quick start
./start_api.sh

# Or manually
python api_search.py

# With custom port
python api_search.py --port 8080 --debug
```

### API Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Search (POST)
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I show alerts?", "limit": 5}'
```

### Test API
```bash
# Run all tests
./test_api.sh

# Interactive client
python test_api_client.py

# Single query
python test_api_client.py --query "alert component"
```

### Request Format
```json
{
  "message": "Natural language query",
  "limit": 5
}
```

### Response Format
```json
{
  "components": [{
    "title": "Component Title",
    "url": "https://...",
    "description": "...",
    "parent": "MOJ Design System",
    "accessibility": "AA",
    "created_at": "2026-03-09 14:53:43",
    "updated_at": "2026-03-09 14:53:43",
    "has_research": false,
    "views": 0
  }]
}
```
