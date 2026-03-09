# Markdown Vectorizer with Docling and LangChain

A Python script that ingests markdown files using Docling, vectorizes the content using LangChain, and provides semantic search capabilities.

## Features

- ✅ Ingest markdown files using Docling
- ✅ Vectorize content using sentence transformers
- ✅ Store vectors in FAISS vector database
- ✅ Perform semantic similarity search
- ✅ Interactive query mode
- ✅ Save/load vector stores for reuse

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install docling langchain langchain-community faiss-cpu sentence-transformers
```

### 2. Make Script Executable (Optional)

```bash
chmod +x markdown_vectorizer.py
```

## Usage

### Basic Usage

Ingest a markdown file and query it:

```bash
python markdown_vectorizer.py sample.md --query "What is machine learning?"
```

### With Custom Parameters

```bash
python markdown_vectorizer.py sample.md \
    --query "Tell me about NLP" \
    --num-results 5 \
    --chunk-size 500 \
    --chunk-overlap 100
```

### Save Vector Store for Reuse

```bash
# Create and save vector store
python markdown_vectorizer.py sample.md \
    --query "What are embeddings?" \
    --save ./vector_db

# Load previously saved vector store
python markdown_vectorizer.py sample.md \
    --load ./vector_db \
    --query "What is supervised learning?"
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `markdown_file` | Path to the markdown file to ingest | *Required* |
| `--query`, `-q` | Initial query to search for | "What is this document about?" |
| `--num-results`, `-k` | Number of results to return | 3 |
| `--chunk-size` | Size of text chunks for vectorization | 1000 |
| `--chunk-overlap` | Overlap between text chunks | 200 |
| `--save` | Path to save the vector store | None |
| `--load` | Path to load a saved vector store | None |

## Example Session

```bash
$ python markdown_vectorizer.py sample.md --query "What is reinforcement learning?"

📄 Ingesting markdown file: sample.md
✅ Successfully ingested 2847 characters
🔄 Splitting text into chunks (size=1000, overlap=200)
📊 Created 4 document chunks
🔮 Initializing embeddings model...
💾 Creating vector store...
✅ Vector store created successfully

🔍 Searching for: 'What is reinforcement learning?'
📊 Returning top 3 results

================================================================================
Result #1 (Similarity Score: 0.8234)
--------------------------------------------------------------------------------
#### Reinforcement Learning
Reinforcement learning involves an agent learning to make decisions by
interacting with an environment. The agent receives rewards or penalties
based on its actions and learns to maximize cumulative rewards.

================================================================================
💬 Interactive Query Mode (press Ctrl+C to exit)
================================================================================

Enter your query: What are vector embeddings used for?
...
```

## How It Works

1. **Document Ingestion**: Docling parses and normalizes the markdown file
2. **Text Splitting**: Content is split into overlapping chunks for better context
3. **Vectorization**: Each chunk is converted to a vector embedding using sentence-transformers
4. **Vector Storage**: Embeddings are stored in FAISS for efficient similarity search
5. **Query**: User queries are vectorized and matched against stored vectors
6. **Results**: Most similar chunks are returned with similarity scores

  ✨ Key Features

  - Docling integration: Normalizes and parses markdown files
  - LangChain components: Text splitting, embeddings, vector stores
  - FAISS vector database: Fast similarity search
  - Interactive mode: Keep querying after initial search
  - Persistence: Save and reload vector stores
  - Configurable: Adjust chunk size, overlap, and number of results

  The script returns the most relevant text chunks with similarity scores, making it easy to find specific information in your markdown documents!

## Advanced Usage

### Using Different Embedding Models

Edit the script to use a different embedding model:

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

### Integrating with LangChain Chains

The vector store can be used as a retriever in LangChain:

```python
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=retriever
)

result = qa_chain.run("What is machine learning?")
```

## Troubleshooting

### Import Errors

If you get import errors, ensure all dependencies are installed:
```bash
pip install --upgrade docling langchain langchain-community faiss-cpu sentence-transformers
```

### FAISS Installation Issues

If `faiss-cpu` fails to install, try:
```bash
# On Linux/Mac
conda install -c pytorch faiss-cpu

# Or use GPU version
pip install faiss-gpu
```

### Memory Issues with Large Files

For large markdown files, reduce chunk size or process in batches:
```bash
python markdown_vectorizer.py large_file.md --chunk-size 500
```

## License

MIT License - Feel free to use and modify as needed.
