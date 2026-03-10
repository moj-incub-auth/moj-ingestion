# MOJ Search API Container

Build and run the MOJ Component Search API as a container.

## Quick Start

### Build and Run with Docker Compose (Recommended)

The easiest way to run both Milvus and the API together:

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f moj-search-api

# Test the API
curl http://localhost:5000/health
```

### Build Standalone Container

Build the container image:

```bash
# Using Docker
docker build -f Containerfile -t moj-search-api:latest .

# Using Podman
podman build -f Containerfile -t moj-search-api:latest .
```

### Run Standalone Container

Run the API container (requires a running Milvus instance):

```bash
# Using Docker
docker run -d \
  --name moj-search-api \
  --network host \
  -p 5000:5000 \
  -e MILVUS_HOST=0.0.0.0 \
  -e MILVUS_PORT=19530 \
  -e MILVUS_COLLECTION=knowledge_base \
  moj-search-api:latest

# Using Podman
podman run -d \
  --name moj-search-api \
  --network host \  
  -p 5000:5000 \
  -e MILVUS_HOST=0.0.0.0 \
  -e MILVUS_PORT=19530 \
  -e MILVUS_COLLECTION=knowledge_base \
  moj-search-api:latest
```

## Environment Variables

Configure the API using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MILVUS_HOST` | Milvus server hostname | `milvus-standalone` |
| `MILVUS_PORT` | Milvus server port | `19530` |
| `MILVUS_COLLECTION` | Collection name | `knowledge_base` |
| `MILVUS_EMBEDDING_MODEL` | HuggingFace model name | `nomic-ai/nomic-embed-text-v1.5` |

## Container Details

### What's Included

- Python 3.11 slim base image
- Flask REST API (`api_search.py`)
- Milvus knowledge base module (`moj_milvus_kb.py`)
- Gunicorn WSGI server (4 workers)
- Health check endpoint

### Ports

- `5000` - API server

### Health Check

The container includes a health check that runs every 30 seconds:

```bash
curl http://localhost:5000/health
```

## Usage Examples

### Test the API

```bash
# Health check
curl http://localhost:5000/health

# Search for components
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I show alerts?", "limit": 5}'
```

### Interactive Testing

Use the Python test client from the host:

```bash
python test_api_client.py --url http://localhost:5000
```

## Docker Compose Services

The `docker-compose.yml` file includes:

1. **etcd** - Metadata storage for Milvus
2. **minio** - Object storage for Milvus
3. **milvus-standalone** - Vector database
4. **moj-search-api** - Search API service

### Start Services

```bash
# Start all services
docker-compose up -d

# Start only specific services
docker-compose up -d milvus-standalone moj-search-api

# Scale API workers
docker-compose up -d --scale moj-search-api=3
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f moj-search-api

# Last 100 lines
docker-compose logs --tail=100 moj-search-api
```

## Production Deployment

### Using Gunicorn (Default)

The container runs with Gunicorn by default:

```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "api_search:app"]
```

### Custom Configuration

Override the command to customize Gunicorn:

```bash
docker run -d \
  --name moj-search-api \
  --network host \
  -p 5000:5000 \
  -e MILVUS_HOST=milvus \
  moj-search-api:latest \
  gunicorn -w 8 -b 0.0.0.0:5000 --timeout 180 api_search:app
```

### Environment-Specific Configs

Development:
```bash
docker run -d -p 5000:5000 \
  -e MILVUS_HOST=0.0.0.0 \
  moj-search-api:latest \
  python api_search.py --debug
```

Production:
```bash
docker run -d -p 5000:5000 \
  -e MILVUS_HOST=milvus.production.svc \
  -e MILVUS_PORT=19530 \
  moj-search-api:latest
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs moj-search-api
```

### Can't Connect to Milvus

Verify Milvus is running:
```bash
docker-compose ps milvus-standalone
```

Test connection:
```bash
docker-compose exec moj-search-api curl http://milvus-standalone:19530
```

### API Returns Unhealthy

Check the health endpoint:
```bash
curl http://localhost:5000/health
```

Enter the container to debug:
```bash
docker-compose exec moj-search-api /bin/bash
```

### Port Already in Use

Change the host port mapping:
```bash
docker run -p 8080:5000 moj-search-api:latest
```

Or in docker-compose.yml:
```yaml
ports:
  - "8080:5000"
```

## Building for Different Architectures

### Multi-Architecture Build

Build for multiple platforms:

```bash
# Using Docker Buildx
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t moj-search-api:latest \
  -f Containerfile \
  .

# Using Podman
podman build \
  --platform linux/amd64,linux/arm64 \
  -t moj-search-api:latest \
  -f Containerfile \
  .
```

### Push to Registry

```bash
# Tag for registry
docker tag moj-search-api:latest registry.example.com/moj-search-api:latest

# Push to registry
docker push registry.example.com/moj-search-api:latest

# Pull and run from registry
docker pull registry.example.com/moj-search-api:latest
docker run -d -p 5000:5000 registry.example.com/moj-search-api:latest
```

## Resource Limits

Set resource limits for the container:

```bash
docker run -d \
  --name moj-search-api \
  --network host \  
  --memory="2g" \
  --cpus="2.0" \
  -p 5000:5000 \
  moj-search-api:latest
```

Or in docker-compose.yml:
```yaml
services:
  moj-search-api:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Kubernetes Deployment

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: moj-search-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: moj-search-api
  template:
    metadata:
      labels:
        app: moj-search-api
    spec:
      containers:
      - name: api
        image: moj-search-api:latest
        ports:
        - containerPort: 5000
        env:
        - name: MILVUS_HOST
          value: "milvus-standalone"
        - name: MILVUS_PORT
          value: "19530"
        - name: MILVUS_COLLECTION
          value: "knowledge_base"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: moj-search-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 5000
  selector:
    app: moj-search-api
```

## Next Steps

1. Insert data into Milvus (see main README.md)
2. Test the API with sample queries
3. Configure authentication if needed
4. Set up monitoring and logging
5. Deploy to production environment
