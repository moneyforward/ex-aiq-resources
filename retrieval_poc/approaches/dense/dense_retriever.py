from ..base_retriever import BaseRetriever
import os
from llama_index.core import Settings
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()


Settings.embed_model = AzureOpenAIEmbedding(
    azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
    azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
    api_version="2024-02-01",
)


class DenseRetriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3):
        super().__init__(data, retrieval_size)
        self.df = data
        self.index = self.build_vector_index()
        self.retrieval_size = retrieval_size
        self.retriever = VectorIndexRetriever(
            index=self.index, similarity_top_k=self.retrieval_size
        )

    def build_vector_index(self):
        # Implement vector index building logic here
        documents = []
        for i, row in self.df.iterrows():
            text_parts = []
            for column, value in row.items():
                if column not in ["Rule", "Example 1", "Example 2", "Distractor Rules"]:
                    text_parts.append(f"{column}: {value}")
            doc_text = "\n".join(text_parts)
            doc = Document(text=doc_text, doc_id=row["Rule"])
            documents.append(doc)

        return VectorStoreIndex.from_documents(
            documents, embed_model=Settings.embed_model
        )

    def retrieve(self, query):
        # Implement dense retrieval logic here
        response = self.retriever.retrieve(query)
        results = []
        for node in response:
            # print(node.node.ref_doc_id, node)
            results.append(node.node.ref_doc_id)

        return results
