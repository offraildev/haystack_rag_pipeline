from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import shutil
from typing import Dict
from pydantic import BaseModel
from ingestion import ingestion_pipeline
from query import query_pipeline
import os

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Update connection strings to use Docker service names
ELASTICSEARCH_HOSTS = os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200")
PG_CONN_STR = os.getenv("PG_CONN_STR", "postgresql://admin:admin@localhost:5432/vector_db")

class Question(BaseModel):
    text: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle PDF upload and ingestion"""
    try:
        # Save uploaded file
        temp_path = UPLOAD_DIR / file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run ingestion pipeline
        result = ingestion_pipeline.run(
            data={"pdf_converter": {"sources": [temp_path]}}
        )
        
        return {
            "status": "success",
            "documents_written": {
                "pgvector": result["pg_vector_writer"]["documents_written"],
                "elasticsearch": result["elasticsearch_writer"]["documents_written"]
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/query")
async def query(question: Question):
    """Handle RAG queries"""
    try:
        result = query_pipeline.run(
            data={
                "text_embedder": {"text": question.text},
                "prompt_builder": {"question": question.text},
                "pg_vector_retriever": {"top_k": 10},
                "elasticsearch_retriever": {
                    "query": question.text,
                    "top_k": 10,
                },
                "ranker": {"query": question.text, "top_k": 5},
            }
        )
        print(result)
        
        return {
            "answer": result["generator"]["replies"][0],
            "usage": result["generator"]["meta"][0]["usage"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}