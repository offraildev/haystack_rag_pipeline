import os
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter

# Uncomment to use contextual splitter
# from contextual_splitter import ContextualDocumentSplitter
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack.components.generators.chat import HuggingFaceLocalChatGenerator


# Update connection strings to use Docker service names
ELASTICSEARCH_HOSTS = os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200")
PG_CONN_STR = os.getenv("PG_CONN_STR", "postgresql://admin:admin@localhost:5432/vector_db")
GROQ_API_KEY = "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"


# ingestion pipeline components
pdf_converter = PyPDFToDocument()
document_cleaner = DocumentCleaner(remove_repeated_substrings=True)

chunk_size = 512
chunk_overlap = int(0.1 * chunk_size)
split_threshold = 0.35 * chunk_size

# Uncomment to use contextual splitter
# document_splitter = ContextualDocumentSplitter(
#     split_by="word",
#     split_length=chunk_size,
#     split_overlap=chunk_overlap,
#     split_threshold=split_threshold,
#     model="llama3-8b-8192",
# )
document_splitter = DocumentSplitter(
    split_by="word",
    split_length=chunk_size,
    split_overlap=chunk_overlap,
    split_threshold=split_threshold,
)
doc_embedder = SentenceTransformersDocumentEmbedder()

document_store = PgvectorDocumentStore(connection_string=Secret.from_token(PG_CONN_STR))
elasticsearch_document_store = ElasticsearchDocumentStore(hosts=ELASTICSEARCH_HOSTS)

elasticsearch_writer = DocumentWriter(
    elasticsearch_document_store, policy=DuplicatePolicy.SKIP
)
pg_vector_writer = DocumentWriter(document_store, policy=DuplicatePolicy.SKIP)


# ingestion pipeline: add components
ingestion_pipeline = Pipeline()
ingestion_pipeline.add_component(instance=pdf_converter, name="pdf_converter")
ingestion_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
ingestion_pipeline.add_component(instance=document_splitter, name="document_splitter")
ingestion_pipeline.add_component(instance=doc_embedder, name="document_embedder")
ingestion_pipeline.add_component(instance=pg_vector_writer, name="pg_vector_writer")
ingestion_pipeline.add_component(instance=elasticsearch_writer, name="elasticsearch_writer")

# ingestion pipeline: connect components
ingestion_pipeline.connect("pdf_converter", "document_cleaner")
ingestion_pipeline.connect("document_cleaner", "document_splitter")
ingestion_pipeline.connect("document_splitter", "document_embedder")
ingestion_pipeline.connect("document_embedder", "pg_vector_writer")
ingestion_pipeline.connect("document_embedder", "elasticsearch_writer")


if __name__ == "__main__":
    result = ingestion_pipeline.run(
        data={"pdf_converter": {"sources": ["./biology_text_book_pages_19_to_68.pdf"]}}
    )
    print(result)