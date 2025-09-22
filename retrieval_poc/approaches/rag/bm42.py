from ..base_retriever import BaseRetriever
import os
from llama_index.core import Document
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings
import qdrant_client

from dotenv import load_dotenv

load_dotenv()

Settings.embed_model = AzureOpenAIEmbedding(
    azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
    model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
    api_version="2024-02-01",
)

Settings.llm = AzureOpenAI(
            temperature=0.1,
            engine="gpt-4.1-mini",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2025-01-01-preview",
        )


class BM42Retriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3):
        super().__init__(data, retrieval_size)
        self.df = data
        self.client = qdrant_client.QdrantClient("http://localhost:6333")
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="llama_bm42",
            fastembed_model="Qdrant/bm42-all-minilm-l6-v2-attentions",
            enable_hybrid=True
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = self.build_vector_index()
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=self.retrieval_size
        )

    def build_vector_index(self):
        documents = []
        for i, row in self.df.iterrows():
            text_parts = []
            for column, value in row.items():
                text_parts.append(f"{column}: {value}")
            doc_text = "\n".join(text_parts)
            doc = Document(text=doc_text, id_=str(row.get("Rule", i)))
            documents.append(doc)
        return VectorStoreIndex.from_documents(
            documents,
            vector_store=self.vector_store,
            storage_context=self.storage_context
        )

    def retrieve(self, query):
        nodes_with_score = self.retriever.retrieve(query)
        results = [node.node.ref_doc_id for node in nodes_with_score]
        return results
