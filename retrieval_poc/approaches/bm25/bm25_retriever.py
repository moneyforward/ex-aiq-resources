from ..base_retriever import BaseRetriever

class BM25Retriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3):
        super().__init__(data, retrieval_size)

    def retrieve(self, query):
        # Implement BM25 retrieval logic here
        pass
