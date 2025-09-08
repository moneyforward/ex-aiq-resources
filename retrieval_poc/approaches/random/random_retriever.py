import random
from ..base_retriever import BaseRetriever

class RandomRetriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3):
        super().__init__(data)
        self.retrieval_size = retrieval_size

    def retrieve(self, query):
        # Randomly select rules from the dataset
        rules = self.data['Rule'].tolist()
        return random.sample(rules, min(self.retrieval_size, len(rules)))
