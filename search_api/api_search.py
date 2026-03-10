#!/usr/bin/env python3
"""
Milvus Search API

REST API that exposes semantic search functionality for MOJ design components.
Accepts natural language queries and returns matching components.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the MilvusKnowledgeBase class from the module
sys.path.insert(0, str(Path(__file__).parent))
from moj_milvus_kb import MilvusKnowledgeBase


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global knowledge base instance
kb = None


def get_kb():
    """Get or create the knowledge base instance."""
    global kb
    if kb is None:
        # Get configuration from environment variables
        host = os.environ.get('MILVUS_HOST', 'localhost')
        port = os.environ.get('MILVUS_PORT', '19530')
        collection = os.environ.get('MILVUS_COLLECTION', 'knowledge_base')
        embedding_model = os.environ.get(
            'MILVUS_EMBEDDING_MODEL',
            'nomic-ai/nomic-embed-text-v1.5'
        )

        print(f"Initializing Milvus connection to {host}:{port}")
        print(f"Collection: {collection}")
        print(f"Embedding model: {embedding_model}")

        kb = MilvusKnowledgeBase(
            collection_name=collection,
            host=host,
            port=port,
            embedding_model=embedding_model
        )

    return kb


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        knowledge_base = get_kb()
        from pymilvus import Collection
        collection = Collection(knowledge_base.collection_name)
        collection.flush()

        return jsonify({
            'status': 'healthy',
            'collection': knowledge_base.collection_name,
            'entities': collection.num_entities
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/search', methods=['POST'])
def search():
    """
    Search for components using natural language query.

    Request body:
    {
        "message": "Example natural language query for the AI"
    }

    Response:
    {
        "components": [
            {
                "title": "Component Title",
                "url": "https://...",
                "description": "...",
                "parent": "MOJ Design System",
                "accessibility": "AA",
                "created_at": "2026-03-09 14:53:43",
                "updated_at": "2026-03-09 14:53:43",
                "has_research": false,
                "views": 0
            },
            ...
        ]
    }
    """
    try:
        # Parse request body
        if not request.json:
            return jsonify({
                'error': 'Request body must be JSON',
                'example': {'message': 'Example natural language query'}
            }), 400

        message = request.json.get('message')
        if not message:
            return jsonify({
                'error': 'Missing "message" field in request body',
                'example': {'message': 'Example natural language query'}
            }), 400

        # Optional: get limit from request, default to 5
        limit = request.json.get('limit', 5)
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            limit = 5

        # Get knowledge base and perform search
        knowledge_base = get_kb()
        results = knowledge_base.search(message, limit=limit)

        # Format results to match the specified output format
        components = []
        for result in results:
            component = {
                'title': result['title'],
                'url': result['url'],
                'description': result['description'],
                'parent': result['parent'],
                'accessibility': result['accessibility'],
                'created_at': result.get('created_at', ''),
                'updated_at': result.get('updated_at', ''),
                'has_research': result['has_research'],
                'views': result['views']
            }
            components.append(component)

        return jsonify({
            'components': components
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Search failed',
            'detail': str(e)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'name': 'MOJ Component Search API',
        'version': '1.0.0',
        'endpoints': {
            'search': {
                'method': 'POST',
                'path': '/search',
                'body': {
                    'message': 'Your natural language query',
                    'limit': 5
                }
            },
            'health': {
                'method': 'GET',
                'path': '/health'
            }
        },
        'example_request': {
            'url': '/search',
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'message': 'How do I show error messages to users?',
                'limit': 5
            }
        }
    }), 200


def main():
    """Run the API server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="MOJ Component Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  MILVUS_HOST            Milvus server host (default: localhost)
  MILVUS_PORT            Milvus server port (default: 19530)
  MILVUS_COLLECTION      Collection name (default: knowledge_base)
  MILVUS_EMBEDDING_MODEL Embedding model (default: nomic-ai/nomic-embed-text-v1.5)

Examples:
  # Start API server
  python api_search.py

  # Start with custom host and port
  python api_search.py --host 0.0.0.0 --port 8080

  # Start in debug mode
  python api_search.py --debug

  # Test the API
  curl -X POST http://localhost:5000/search \\
    -H "Content-Type: application/json" \\
    -d '{"message": "How do I show alerts?"}'
        """
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    print(f"""
╔════════════════════════════════════════════════════════╗
║  MOJ Component Search API                              ║
╠════════════════════════════════════════════════════════╣
║  Server:     http://{args.host}:{args.port:<5}                      ║
║  Health:     http://{args.host}:{args.port}/health               ║
║  Search:     POST http://{args.host}:{args.port}/search          ║
╠════════════════════════════════════════════════════════╣
║  Example Request:                                      ║
║  curl -X POST http://{args.host}:{args.port}/search \\      ║
║    -H "Content-Type: application/json" \\                ║
║    -d '{{"message": "How do I show alerts?"}}'           ║
╚════════════════════════════════════════════════════════╝
    """)

    # Initialize knowledge base on startup
    try:
        get_kb()
        print("✅ Knowledge base initialized successfully\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize knowledge base: {e}")
        print("   API will attempt to connect on first request\n")

    # Run Flask app
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
