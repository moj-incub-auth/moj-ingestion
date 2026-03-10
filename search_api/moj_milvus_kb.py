#!/usr/bin/env python3
"""
MOJ Milvus Knowledge Base Module

Reusable module for managing component data in Milvus vector database.
"""

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

    def process_batch(self, input_dir: Path) -> int:
        """
        Process all JSON files in a directory and insert into Milvus.

        Args:
            input_dir: Directory containing JSON files to insert

        Returns:
            Number of successfully inserted files
        """
        print(f"🔄 Batch mode: Processing JSON files in {input_dir}")
        print()

        # Find all .json files recursively
        json_files = list(input_dir.rglob("*.json"))

        if not json_files:
            print(f"❌ No JSON files found in: {input_dir}")
            return 0

        print(f"📊 Found {len(json_files)} JSON file(s) to insert")
        print()

        successful = 0
        failed = 0
        total_components = 0

        for json_file in sorted(json_files):
            component_name = json_file.stem.replace('-component', '')

            print(f"Processing: {component_name}")
            print(f"   File: {json_file.relative_to(input_dir)}")

            try:
                # Insert from JSON file
                count = self.insert_from_json(str(json_file))
                if count > 0:
                    successful += 1
                    total_components += count
                    print(f"   ✅ Success! ({count} component(s) inserted)")
                else:
                    failed += 1
                    print(f"   ❌ Failed!")
            except Exception as e:
                failed += 1
                print(f"   ❌ Error: {e}")

            print()

        # Summary
        print(f"{'='*60}")
        print(f"Batch Processing Summary")
        print(f"{'='*60}")
        print(f"Total files: {len(json_files)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total components inserted: {total_components}")
        print()

        return successful

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
