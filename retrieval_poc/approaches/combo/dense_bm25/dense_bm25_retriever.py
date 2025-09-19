"""
Dense + BM25 Combination Retriever

This retriever combines the strengths of Dense Retrieval (semantic understanding)
and BM25 (keyword-based matching) using LlamaIndex's QueryFusionRetriever
with reciprocal rerank fusion.
"""

from ...base_retriever import BaseRetriever
from ...dense.dense_retriever import DenseRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core import Settings
from llama_index.llms.azure_openai import AzureOpenAI
import os
import nest_asyncio

# Apply nested async to run in notebooks/environments that need it
nest_asyncio.apply()

# Set up Azure OpenAI LLM for query generation
Settings.llm = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version="2024-02-01",
)


class DenseBM25Retriever(BaseRetriever):
    """
    Combination retriever that fuses Dense Retrieval and BM25 approaches.
    
    Uses QueryFusionRetriever with reciprocal rerank fusion to combine:
    - Dense Retriever: Semantic understanding via embeddings
    - BM25 Retriever: Keyword-based matching and ranking
    
    This combination leverages the semantic understanding of Dense retrieval
    with the keyword precision of BM25, providing cross-language robustness.
    """
    
    def __init__(self, data, retrieval_size=3, num_queries=4):
        """
        Initialize the combination retriever.
        
        Args:
            data: The rule data DataFrame
            retrieval_size: Number of top results to return
            num_queries: Number of queries to generate for fusion (default: 4)
        """
        super().__init__(data, retrieval_size)
        
        # Initialize individual retrievers
        self.dense_retriever = DenseRetriever(data, retrieval_size)
        
        # Create BM25 retriever using the same index as dense retriever
        self.bm25_retriever = BM25Retriever.from_defaults(
            docstore=self.dense_retriever.index.docstore, 
            similarity_top_k=retrieval_size
        )
        
        # Create the fusion retriever
        self.fusion_retriever = QueryFusionRetriever(
            [self.dense_retriever.retriever, self.bm25_retriever],
            similarity_top_k=retrieval_size,
            num_queries=num_queries,
            mode="reciprocal_rerank",
            use_async=True,
            verbose=False,  # Set to True for debugging
        )
        
        self.retrieval_size = retrieval_size
    
    def retrieve(self, query):
        """
        Retrieve results using the fusion of Dense and BM25 approaches.
        
        Args:
            query: The input query text
            
        Returns:
            List of rule IDs (strings) for compatibility with evaluation
        """
        try:
            # Use the fusion retriever
            nodes_with_scores = self.fusion_retriever.retrieve(query)
            
            # Extract rule IDs from the nodes
            results = []
            for node in nodes_with_scores:
                if hasattr(node, 'node') and hasattr(node.node, 'ref_doc_id'):
                    results.append(node.node.ref_doc_id)
                elif hasattr(node, 'ref_doc_id'):
                    results.append(node.ref_doc_id)
            
            return results[:self.retrieval_size]
            
        except Exception as e:
            print(f"Error in DenseBM25 fusion retrieval: {e}")
            # Fallback to individual retrievers
            try:
                dense_results = self.dense_retriever.retrieve(query)
                return dense_results[:self.retrieval_size]
            except:
                return []
    
    def get_individual_results(self, query):
        """
        Get results from individual retrievers for analysis.
        
        Args:
            query: The input query text
            
        Returns:
            Dictionary with results from each individual retriever
        """
        return {
            'dense': self.dense_retriever.retrieve(query),
            'bm25': [node.node.ref_doc_id for node in self.bm25_retriever.retrieve(query)]
        }
