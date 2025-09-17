from ..base_retriever import BaseRetriever
import pandas as pd
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever

class DenseRetriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3):
        super().__init__(data, retrieval_size)
        self.data = data
        self.index = self.build_vector_index()
        self.retrieval_size = retrieval_size
        self.retriever = VectorIndexRetriever(
            index = self.index,
            similarity_top_k=self.retrieval_size)

    def build_vector_index(self):
        # Implement vector index building logic here
        df = pd.read_csv(self.data)
        documents = []
        for i, row in df.iterrows():
            text_parts = []
            for column, value in row.items():
                if column not in ['Rule', 'Example 1', 'Example 2', 'Distractor Rules']:
                    text_parts.append(f"{column}: {value}")
            doc_text = '\n'.join(text_parts)
            doc = Document(text=doc_text, doc_id=str(i))
            documents.append(doc)

        return VectorStoreIndex.from_documents(documents)

    def retrieve(self, query):
        # Implement dense retrieval logic here
        response = self.retriever.retrieve(query)
        results = []
        for node in response:
            # print(node.node.ref_doc_id, node)
            results.append(node.node.ref_doc_id)

        return results


# dretriever = DenseRetriever("../../data/eval_en.csv")
# print(dretriever.retrieve("Expense names for domestic travel?"))
