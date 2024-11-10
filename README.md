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
- Streamlit web interface for document upload and querying
- FastAPI backend service

## Prerequisites

- Docker and Docker Compose

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/offraildev/haystack_rag_pipeline.git
cd haystack_rag_pipeline
```

2. Start the services using Docker Compose:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector (port 5432)
- pgAdmin web interface (port 5050)
- Elasticsearch (port 9200)
- FastAPI backend (port 8000)
- Streamlit frontend (port 8501)

## Accessing the Services

- Streamlit Interface: http://localhost:8501
- FastAPI Swagger UI: http://localhost:8000/docs
- pgAdmin (optional):
  - URL: http://localhost:5050
  - Email: admin@example.com
  - Password: admin


## Configuration

1. Set up environment variables:
```bash
GROQ_API_KEY="your_groq_api_key" # Add your Groq API key here or use "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"
```

2. Optional Components:
- Local LLM support:
  - Uncomment relevant sections marked with `# Uncomment to use hugging face local chat generator`
  
- Contextual Document Splitting:
  - Uncomment sections marked with `# Uncomment to use contextual splitter`
  - Provides enhanced context awareness during document splitting

## Usage

1. Extract PDF pages:
```python
IN_PATH = Path("./biology_text_book.pdf")
DATA_IN_PATH = extract_pages(IN_PATH, start_page=19, end_page=68)
```

2. Open the Streamlit interface at http://localhost:8501

3. Upload Documents:
   - Use the sidebar's file uploader to select a PDF file
   - Click "Process Document" to ingest the content
   - Wait for the confirmation message

4. Query the System:
   - Use the chat interface to ask questions about the uploaded content
   - View token usage details in the expandable section below each response


## Architecture

The system consists of several Docker containers working together:

### Frontend (Streamlit)
- Provides a user-friendly interface for document upload and querying
- Communicates with the FastAPI backend

### Backend (FastAPI)
- Handles document ingestion and query processing
- Manages communication with document stores and LLM

### Document Stores
- PostgreSQL with pgvector for vector embeddings
- Elasticsearch for keyword-based search

### Query Processing
1. Vector similarity search via Pgvector
2. Keyword search via Elasticsearch
3. Results combined using Reciprocal Rank Fusion
4. Top results ranked and used for response generation

## Environment Variables

The system uses the following environment variables (pre-configured in docker-compose.yml):

```
ELASTICSEARCH_HOSTS=http://elasticsearch:9200
PG_CONN_STR=postgresql://admin:admin@db:5432/vector_db
```

## Service Details

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