from haystack import Pipeline
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.retrievers.pgvector import (
    PgvectorEmbeddingRetriever,
)

from haystack.utils import Secret
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchBM25Retriever,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.generators import OpenAIGenerator
from haystack.components.embedders import SentenceTransformersTextEmbedder

import os

ELASTICSEARCH_HOSTS = os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200")
PG_CONN_STR = os.getenv("PG_CONN_STR", "postgresql://admin:admin@localhost:5432/vector_db")
GROQ_API_KEY = "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"


# components
text_embedder = SentenceTransformersTextEmbedder()
document_store = PgvectorDocumentStore(connection_string=Secret.from_token(PG_CONN_STR))
elasticsearch_document_store = ElasticsearchDocumentStore(hosts=ELASTICSEARCH_HOSTS)
pg_vector_retriever = PgvectorEmbeddingRetriever(document_store=document_store)
elasticsearch_retriever = ElasticsearchBM25Retriever(
    document_store=elasticsearch_document_store
)
from haystack.components.generators import HuggingFaceLocalGenerator

# Uncomment to use hugging face local chat generator
# generator = HuggingFaceLocalGenerator(model="microsoft/Phi-3-mini-4k-instruct")
# generator = HuggingFaceLocalGenerator(model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
generator = OpenAIGenerator(
    api_key=Secret.from_token(GROQ_API_KEY),
    api_base_url="https://api.groq.com/openai/v1",
    model="llama3-8b-8192",
    generation_kwargs={"max_tokens": 512},
)

template = """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
prompt_builder = PromptBuilder(template=template)

ranker = TransformersSimilarityRanker()

# query pipeline: add components
query_pipeline = Pipeline()
query_pipeline.add_component(
    instance=DocumentJoiner(join_mode="reciprocal_rank_fusion"), name="joiner"
)
query_pipeline.add_component(instance=text_embedder, name="text_embedder")
query_pipeline.add_component(instance=pg_vector_retriever, name="pg_vector_retriever")
query_pipeline.add_component(instance=elasticsearch_retriever, name="elasticsearch_retriever")
query_pipeline.add_component(instance=prompt_builder, name="prompt_builder")
query_pipeline.add_component(instance=generator, name="generator")
query_pipeline.add_component(instance=ranker, name="ranker")

# query pipeline: connect components
query_pipeline.connect("elasticsearch_retriever", "joiner")
query_pipeline.connect("pg_vector_retriever", "joiner")
query_pipeline.connect("text_embedder", "pg_vector_retriever.query_embedding")
query_pipeline.connect("joiner", "ranker")
query_pipeline.connect("ranker", "prompt_builder")
query_pipeline.connect("prompt_builder", "generator.prompt")


if __name__ == "__main__":
    question = "What is the fucntion of cell?"
    result = query_pipeline.run(
            data={
                "text_embedder": {"text": question},
                "prompt_builder": {"question": question},
                "pg_vector_retriever": {"top_k": 10},
                "elasticsearch_retriever": {
                    "query": question,
                    "top_k": 10,
                },
                "ranker": {"query": question, "top_k": 5},
            }
        )
    print(result)
