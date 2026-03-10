#!/usr/bin/env python3
"""
Insert Component Data into Milvus Knowledge Base

This script inserts structured component JSON data into a Milvus vector database
using Nomic-embed-text-v1.5 embeddings for semantic search.
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

# PyMilvus imports
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility
)

# Embeddings
from sentence_transformers import SentenceTransformer


class MilvusKnowledgeBase:
    """Manage component data in Milvus vector database."""

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        host: str = "localhost",
        port: str = "19530",
        embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"
    ):
        """
        Initialize Milvus connection and embedding model.

        Args:
            collection_name: Name of the Milvus collection
            host: Milvus server host
            port: Milvus server port
            embedding_model: HuggingFace model name for embeddings
        """
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.embedding_dim = 768  # Nomic-embed-text-v1.5 dimension

        print(f"🔌 Connecting to Milvus at {host}:{port}...")
        connections.connect(
            alias="default",
            host=host,
            port=port
        )
        print("✅ Connected to Milvus")

        print(f"🤖 Loading embedding model: {embedding_model}...")
        self.model = SentenceTransformer(
            embedding_model,
            trust_remote_code=True
        )
        print("✅ Embedding model loaded")

    def create_collection(self, drop_existing: bool = False):
        """
        Create the knowledge_base collection with appropriate schema.

        Args:
            drop_existing: If True, drop existing collection before creating
        """
        # Drop existing collection if requested
        if drop_existing and utility.has_collection(self.collection_name):
            print(f"🗑️  Dropping existing collection: {self.collection_name}")
            utility.drop_collection(self.collection_name)

        # Check if collection already exists
        if utility.has_collection(self.collection_name):
            print(f"✅ Collection '{self.collection_name}' already exists")
            return Collection(self.collection_name)

        print(f"📦 Creating collection: {self.collection_name}")

        # Define schema
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
                description="Primary key"
            ),
            FieldSchema(
                name="component_id",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Unique component identifier"
            ),
            FieldSchema(
                name="title",
                dtype=DataType.VARCHAR,
                max_length=512,
                description="Component title"
            ),
            FieldSchema(
                name="description",
                dtype=DataType.VARCHAR,
                max_length=4096,
                description="Component description"
            ),
            FieldSchema(
                name="url",
                dtype=DataType.VARCHAR,
                max_length=512,
                description="Component URL"
            ),
            FieldSchema(
                name="parent",
                dtype=DataType.VARCHAR,
                max_length=256,
                description="Parent design system"
            ),
            FieldSchema(
                name="accessibility",
                dtype=DataType.VARCHAR,
                max_length=64,
                description="Accessibility level (e.g., AA)"
            ),
            FieldSchema(
                name="has_research",
                dtype=DataType.BOOL,
                description="Whether component has research"
            ),
            FieldSchema(
                name="created_at",
                dtype=DataType.VARCHAR,
                max_length=128,
                description="Creation timestamp"
            ),
            FieldSchema(
                name="updated_at",
                dtype=DataType.VARCHAR,
                max_length=128,
                description="Update timestamp"
            ),
            FieldSchema(
                name="views",
                dtype=DataType.INT16,
                description="views"
            ),
            FieldSchema(
                name="content_embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.embedding_dim,
                description="Vector embedding of component content"
            ),
            FieldSchema(
                name="full_content",
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="Full markdown content (truncated if needed)"
            )
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Knowledge base for design system component"
        )

        # Create collection
        collection = Collection(
            name=self.collection_name,
            schema=schema
        )

        print("✅ Collection created successfully")
        return collection

    def create_index(self, collection: Collection):
        """
        Create index on the vector field for efficient search.

        Args:
            collection: Milvus collection
        """
        print("🔨 Creating index on content_embedding field...")

        index_params = {
            "metric_type": "COSINE",  # Use cosine similarity
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }

        collection.create_index(
            field_name="content_embedding",
            index_params=index_params
        )

        print("✅ Index created successfully")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Nomic model.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        # Add prefix for search queries (Nomic-specific)
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def prepare_component_data(self, component: Dict[str, Any], full_content: str) -> Dict[str, Any]:
        """
        Prepare component data for insertion into Milvus.

        Args:
            component: Component metadata dictionary
            full_content: Full markdown content

        Returns:
            Dictionary with all fields ready for insertion
        """
        # Create searchable text by combining key fields
        searchable_text = f"""
Title: {component['title']}
Description: {component['description']}
Parent: {component['parent']}
Content: {full_content[:65000]}
        """.strip()

        print(f"   Generating embedding for: {component['title']}")
        embedding = self.generate_embedding(searchable_text)

        # Prepare data
        data = {
            "component_id": component['url'],  # Use URL as unique ID
            "title": component['title'],
            "description": component['description'][:4096],  # Truncate if needed
            "url": component['url'],
            "parent": component['parent'],
            "accessibility": component['accessibility'],
           # "status": component.get('status', 'Unknown'),
            "has_research": component['has_research'],
            "created_at": component['created_at'],
            "updated_at": component['updated_at'],
            "views": component['views'],
            "content_embedding": embedding,
            "full_content": full_content[:65535]  # Truncate to max VARCHAR length
        }

        return data

    def insert_from_json(self, json_file: str) -> int:
        """
        Insert component data from JSON file into Milvus.

        Args:
            json_file: Path to the JSON file

        Returns:
            Number of components inserted
        """
        print(f"📄 Reading JSON file: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both 'component' (singular) and 'components' (plural) keys
        if 'component' in data:
            component = data['component']
            if not isinstance(component, dict):
                print("❌ Component data should be a dictionary")
                return 0
            components = [component]  # Convert to list for uniform handling
        elif 'components' in data:
            components = data['components']
            if not isinstance(components, list):
                print("❌ Components data should be a list")
                return 0
        else:
            print("❌ No 'component' or 'components' key found in JSON file")
            return 0

        full_content = data.get('filecontent', '')

        if not components:
            print("❌ No components found in JSON file")
            return 0

        print(f"📊 Found {len(components)} component(s) to insert")

        # Get or create collection
        collection = Collection(self.collection_name)

        # Prepare data for batch insertion
        insert_data = []
        for component in components:
            prepared_data = self.prepare_component_data(component, full_content)
            insert_data.append(prepared_data)

        print(f"✅ Prepared {len(insert_data)} component(s) for insertion")

        # Insert data using row-based format (list of dicts)
        # PyMilvus expects each row as a dictionary
        print("\n💾 Inserting data into Milvus...")
        collection.insert(insert_data)

        # Flush to ensure data is written
        collection.flush()

        print(f"✅ Successfully inserted {len(components)} component(s)")
        return len(components)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for components using semantic search.

        Args:
            query: Search query text
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        print(f"🔍 Searching for: '{query}'")

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Get collection and load it
        collection = Collection(self.collection_name)
        collection.load()

        # Search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }

        # Perform search
        results = collection.search(
            data=[query_embedding],
            anns_field="content_embedding",
            param=search_params,
            limit=limit,
            output_fields=[
                "title",
                "description",
                "url",
                "parent",
                "accessibility",
                "has_research",
                "views"
            ]
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                result = {
                    "score": hit.score,
                    "title": hit.entity.get("title"),
                    "description": hit.entity.get("description"),
                    "url": hit.entity.get("url"),
                    "parent": hit.entity.get("parent"),
                    "accessibility": hit.entity.get("accessibility"),
                    "has_research": hit.entity.get("has_research"),
                    "views": hit.entity.get("views")
                }
                formatted_results.append(result)

        return formatted_results

    def close(self):
        """Close Milvus connection."""
        connections.disconnect("default")
        print("👋 Disconnected from Milvus")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Insert component data into Milvus knowledge base"
    )

    parser.add_argument(
        "json_file",
        type=str,
        nargs="?",
        help="Path to the component JSON file"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Milvus server host (default: localhost)"
    )

    parser.add_argument(
        "--port",
        type=str,
        default="19530",
        help="Milvus server port (default: 19530)"
    )

    parser.add_argument(
        "--collection",
        type=str,
        default="knowledge_base",
        help="Collection name (default: knowledge_base)"
    )

    parser.add_argument(
        "--create",
        action="store_true",
        help="Create collection (if it doesn't exist)"
    )

    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing collection before creating"
    )

    parser.add_argument(
        "--search",
        type=str,
        help="Search query to test the knowledge base"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of search results to return (default: 5)"
    )

    args = parser.parse_args()

    # Initialize knowledge base
    kb = MilvusKnowledgeBase(
        collection_name=args.collection,
        host=args.host,
        port=args.port
    )

    try:
        # Create collection if requested
        if args.create or args.drop:
            collection = kb.create_collection(drop_existing=args.drop)
            kb.create_index(collection)

        # Insert data from JSON file
        if args.json_file:
            if not Path(args.json_file).exists():
                print(f"❌ Error: File not found: {args.json_file}")
                return

            kb.insert_from_json(args.json_file)

        # Perform search if query provided
        if args.search:
            results = kb.search(args.search, limit=args.limit)

            print(f"\n{'='*80}")
            print(f"Search Results ({len(results)} found):")
            print(f"{'='*80}\n")

            for idx, result in enumerate(results, 1):
                print(f"Result #{idx} (Similarity: {result['score']:.4f})")
                print(f"  Title: {result['title']}")
                print(f"  Description: {result['description'][:100]}...")
                print(f"  URL: {result['url']}")
                print(f"  Parent: {result['parent']}")
                print(f"  Accessibility: {result['accessibility']}")
                print(f"  Has Research: {result['has_research']}")
                print(f"  Views: {result['views']}")
                print()

        # Show collection stats
        if utility.has_collection(args.collection):
            collection = Collection(args.collection)
            collection.flush()
            print(f"\n📊 Collection Stats:")
            print(f"   Name: {args.collection}")
            print(f"   Entities: {collection.num_entities}")

    finally:
        kb.close()

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
