class BaseRetriever:
    def __init__(self, data, retrieval_size=3):
        self.data = data
        self.retrieval_size = retrieval_size

    def retrieve(self, query):
        raise NotImplementedError("This method should be overridden by subclasses.")
