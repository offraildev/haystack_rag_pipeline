# Biology Text RAG System

A Retrieval Augmented Generation (RAG) system built with Haystack to process and query biology textbook content. The system supports both vector (Pgvector) and keyword (Elasticsearch) search capabilities.

Caveats:
- The system is designed to work with a single large biology textbook PDF.
- Downloaded from [here](https://openstax.org/details/books/concepts-biology)

## Features

- PDF text extraction and processing
- Dual document stores:
  - Pgvector for vector similarity search
  - Elasticsearch for keyword-based search
- Reciprocal Rank Fusion for combining search results
- Support for multiple LLM options:
  - Groq (default)
  - Local models (optional)
- Contextual document splitting (optional)

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Required Python packages (install via `pip`):
  - haystack-ai
  - PyPDF2
  - sentence-transformers
  - haystack-integrations[pgvector]
  - haystack-integrations[elasticsearch]

## Installation

1. Start the required services using Docker Compose:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector extension (port 5432)
- pgAdmin web interface (port 5050)
- Elasticsearch (port 9200)

2. Access pgAdmin (optional):
- URL: http://localhost:5050
- Email: admin@example.com
- Password: admin

## Configuration

1. Set up environment variables:
```bash
ELASTICSEARCH_HOSTS="http://localhost:9200"
PG_CONN_STR="postgresql://admin:admin@localhost:5432/vector_db"
GROQ_API_KEY="your_groq_api_key" # Add your Groq API key here or use "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"
```

2. Optional Components:
- Local LLM support:
  - Uncomment relevant sections marked with `# Uncomment to use hugging face local chat generator`
  - Supported models include:
    - TinyLlama/TinyLlama-1.1B-Chat-v1.0

- Contextual Document Splitting:
  - Uncomment sections marked with `# Uncomment to use contextual splitter`
  - Provides enhanced context awareness during document splitting

## Usage

1. Extract PDF pages:
```python
IN_PATH = Path("./biology_text_book.pdf")
DATA_IN_PATH = extract_pages(IN_PATH, start_page=19, end_page=68)
```

2. Run ingestion pipeline:
```python
ingestion.run(data={"pdf_converter": {"sources": [DATA_IN_PATH]}})
```

3. Query the system:
```python
question = "Your question here?"
result = query.run(
    data={
        "text_embedder": {"text": question},
        "prompt_builder": {"question": question},
        "pg_vector_retriever": {"top_k": 10},
        "elasticsearch_retriever": {
            "query": generator.run(
                f"Extract key search terms from this text as a comma-separated list:{question}"
            )["replies"][0],
            "top_k": 10,
        },
        "ranker": {"query": question, "top_k": 5},
    }
)
```


The `docker-compose.yml` file includes:

### PostgreSQL with pgvector
- Image: `pgvector/pgvector:pg17`
- Credentials:
  - User: admin
  - Password: admin
  - Database: vector_db
- Port: 5432

### pgAdmin
- Image: `dpage/pgadmin4`
- Credentials:
  - Email: admin@example.com
  - Password: admin
- Port: 5050

### Elasticsearch
- Image: `elasticsearch:8.11.1`
- Configuration:
  - Single node setup
  - Security disabled
  - JVM heap: 1GB
- Port: 9200

## Architecture

The system uses a dual-retrieval approach:
1. Vector similarity search via Pgvector
2. Keyword search via Elasticsearch
3. Results are combined using Reciprocal Rank Fusion
4. Top results are ranked and used to generate contextual responses