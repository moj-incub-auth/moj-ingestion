#!/usr/bin/env python3
"""
Markdown Document Ingestion and Query System using Docling and LangChain

This script demonstrates how to:
1. Ingest a markdown file using Docling
2. Vectorize the content using LangChain embeddings
3. Store vectors in a FAISS vector store
4. Query the vectorized content
"""

import argparse
from pathlib import Path
from typing import List

# Docling imports
from docling.document_converter import DocumentConverter

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


def ingest_markdown_with_docling(file_path: str) -> str:
    """
    Ingest a markdown file using Docling.

    Args:
        file_path: Path to the markdown file

    Returns:
        Extracted text content from the markdown file
    """
    print(f"📄 Ingesting markdown file: {file_path}")

    # Initialize Docling converter
    converter = DocumentConverter()

    # Convert the document
    result = converter.convert(file_path)

    # Export to markdown (Docling can parse and normalize the content)
    markdown_content = result.document.export_to_markdown()

    print(f"✅ Successfully ingested {len(markdown_content)} characters")
    return markdown_content


def create_vector_store(text_content: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Create a vector store from text content.

    Args:
        text_content: The text to vectorize
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks

    Returns:
        FAISS vector store
    """
    print(f"🔄 Splitting text into chunks (size={chunk_size}, overlap={chunk_overlap})")

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    # Create Document objects
    chunks = text_splitter.split_text(text_content)
    documents = [Document(page_content=chunk) for chunk in chunks]

    print(f"📊 Created {len(documents)} document chunks")

    # Initialize embeddings (using HuggingFace's sentence-transformers)
    print("🔮 Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create vector store
    print("💾 Creating vector store...")
    vector_store = FAISS.from_documents(documents, embeddings)

    print("✅ Vector store created successfully")
    return vector_store


def query_vector_store(vector_store, query: str, k: int = 3):
    """
    Query the vector store for relevant documents.

    Args:
        vector_store: The FAISS vector store
        query: The search query
        k: Number of results to return

    Returns:
        List of relevant documents with scores
    """
    print(f"\n🔍 Searching for: '{query}'")
    print(f"📊 Returning top {k} results\n")

    # Perform similarity search with scores
    results = vector_store.similarity_search_with_score(query, k=k)

    # Display results
    for idx, (doc, score) in enumerate(results, 1):
        print(f"{'='*80}")
        print(f"Result #{idx} (Similarity Score: {score:.4f})")
        print(f"{'-'*80}")
        print(doc.page_content)
        print()

    return results


def save_vector_store(vector_store, save_path: str):
    """Save the vector store to disk."""
    print(f"💾 Saving vector store to: {save_path}")
    vector_store.save_local(save_path)
    print("✅ Vector store saved successfully")


def load_vector_store(load_path: str):
    """Load a previously saved vector store."""
    print(f"📂 Loading vector store from: {load_path}")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    print("✅ Vector store loaded successfully")
    return vector_store


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Ingest markdown files and query using vector search"
    )
    parser.add_argument(
        "markdown_file",
        help="Path to the markdown file to ingest"
    )
    parser.add_argument(
        "--query",
        "-q",
        default="What is this document about?",
        help="Query to search for in the vectorized content"
    )
    parser.add_argument(
        "--num-results",
        "-k",
        type=int,
        default=3,
        help="Number of results to return"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks for vectorization"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between text chunks"
    )
    parser.add_argument(
        "--save",
        help="Path to save the vector store"
    )
    parser.add_argument(
        "--load",
        help="Path to load a previously saved vector store (skips ingestion)"
    )

    args = parser.parse_args()

    # Check if we should load an existing vector store
    if args.load:
        vector_store = load_vector_store(args.load)
    else:
        # Ingest markdown file
        if not Path(args.markdown_file).exists():
            print(f"❌ Error: File not found: {args.markdown_file}")
            return

        # Step 1: Ingest with Docling
        text_content = ingest_markdown_with_docling(args.markdown_file)

        # Step 2: Create vector store
        vector_store = create_vector_store(
            text_content,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )

        # Save if requested
        if args.save:
            save_vector_store(vector_store, args.save)

    # Step 3: Query the vector store
    query_vector_store(vector_store, args.query, k=args.num_results)

    # Interactive mode
    print("\n" + "="*80)
    print("💬 Interactive Query Mode (press Ctrl+C to exit)")
    print("="*80 + "\n")

    try:
        while True:
            user_query = input("Enter your query: ").strip()
            if not user_query:
                continue
            query_vector_store(vector_store, user_query, k=args.num_results)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    main()
