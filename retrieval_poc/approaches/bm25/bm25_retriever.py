from ..base_retriever import BaseRetriever
from rank_bm25 import BM25Okapi, BM25L, BM25Plus

class BM25Retriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3, version='BM25Okapi', k1=1.5, b=0.75):
        super().__init__(data, retrieval_size)
        # Concatenate relevant columns to form a single document per row
        self.tokenized_corpus = [
            ' '.join(map(str, row)) for _, row in data.iterrows()
        ]
        self.tokenized_corpus = [doc.split() for doc in self.tokenized_corpus]
        self.version = version
        if version == 'BM25Okapi':
            self.bm25 = BM25Okapi(self.tokenized_corpus, k1=k1, b=b)
        elif version == 'BM25L':
            self.bm25 = BM25L(self.tokenized_corpus, k1=k1, b=b)
        elif version == 'BM25Plus':
            # Fix line length issue
            self.bm25 = BM25Plus(
                self.tokenized_corpus, k1=k1, b=b
            )
        else:
            raise ValueError(f"Unsupported BM25 version: {version}")

    def retrieve(self, query):
        tokenized_query = query.split()
        doc_scores = self.bm25.get_scores(tokenized_query)
        top_n_indices = sorted(
            range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True
        )[:self.retrieval_size]
        return [self.data.iloc[i]['Rule'] for i in top_n_indices]

    def sample_tokenized_corpus(self, sample_size=5):
        """Print a sample of the tokenized corpus for analysis."""
        for i, doc in enumerate(self.tokenized_corpus[:sample_size]):
            print(f"Document {i+1}: {doc}")
