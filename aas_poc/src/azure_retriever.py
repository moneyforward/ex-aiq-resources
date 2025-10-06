"""
Azure AI Search Retriever for AIQ investigation
Adapts the existing retrieval_poc framework to use Azure AI Search as the managed service
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, VectorizableTextQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('azure_retriever.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the retrieval_poc approaches directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../retrieval_poc/approaches'))
from base_retriever import BaseRetriever


class AzureSearchRetriever(BaseRetriever):
    """
    Azure AI Search retriever that inherits from BaseRetriever
    Uses the same interface as other retrievers in retrieval_poc
    """
    
    def __init__(self, data, retrieval_size=3, index_name="aiq-expense-rules", use_embeddings=False, use_hybrid=True):
        """
        Initialize Azure Search retriever
        
        Args:
            data: DataFrame with expense rules (same format as other retrievers)
            retrieval_size: Number of results to retrieve
            index_name: Azure Search index name
            use_embeddings: Whether to use vector search with embeddings
            use_hybrid: Whether to use hybrid search (combines text + vector)
        """
        super().__init__(data, retrieval_size)
        self.index_name = index_name
        self.endpoint = "https://aibi-aai-stg-verification-30vc.search.windows.net"
        self.use_embeddings = use_embeddings
        self.use_hybrid = use_hybrid
        
        logger.info(f"Initializing AzureSearchRetriever with index: {index_name}")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Retrieval size: {retrieval_size}")
        logger.info(f"Use embeddings: {use_embeddings}")
        logger.info(f"Use hybrid search: {use_hybrid}")
        
        if use_hybrid:
            logger.info("Using hybrid search (text + vector with RRF ranking)")
        elif use_embeddings:
            logger.info("Using Azure AI Search integrated vectorization")
        else:
            logger.info("Using traditional text search")
        
        # Initialize Azure Search client
        self.search_client = self._get_search_client()
        
        # Ensure index exists and is populated
        self._ensure_index_populated()
    
    def _get_search_client(self) -> SearchClient:
        """Get Azure Search client with appropriate credentials"""
        # Use admin key for authentication (simpler and more reliable)
        admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        if admin_key:
            logger.info("Using Azure Key Credential for authentication")
            credential = AzureKeyCredential(admin_key)
        else:
            logger.error("AZURE_SEARCH_ADMIN_KEY not found in environment variables")
            raise ValueError("AZURE_SEARCH_ADMIN_KEY is required")

        logger.info(f"Creating SearchClient for index: {self.index_name}")
        return SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=credential
        )
    
    def _ensure_index_populated(self):
        """Ensure the Azure Search index exists and is populated with data"""
        try:
            logger.info(f"Checking if index '{self.index_name}' exists and is populated...")
            # Try a simple search to check if index exists and has data
            results = self.search_client.search(
                search_text="*",
                top=1
            )
            # If we get here, index exists
            result_list = list(results)  # Consume the iterator
            logger.info(f"✅ Index '{self.index_name}' exists and is accessible")
        except Exception as e:
            logger.error(f"❌ Index '{self.index_name}' not found or empty. Please run the indexing script first.")
            logger.error(f"Error: {e}")
            raise
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query text using Azure integrated vectorization"""
        if not self.use_embeddings:
            return []
        
        # For Azure integrated vectorization, we use the search client's built-in vectorization
        # This requires the index to be configured with integrated vectorization
        logger.info("Using Azure integrated vectorization for query")
        # Note: For integrated vectorization, we don't need to generate embeddings manually
        # Azure will handle vectorization automatically when we pass the query text
        return []  # Azure will handle vectorization automatically

    def _extract_search_terms(self, query: str) -> str:
        """
        Extract search terms from JSON expense object or natural language query
        Dynamically extract meaningful text fields from JSON for better search results
        
        Args:
            query: JSON expense object as string or natural language query
            
        Returns:
            Search terms as string (extracted from JSON or natural language)
        """
        try:
            # Try to parse as JSON first to validate it's valid JSON
            json_data = json.loads(query)
            
            # If it's valid JSON, extract meaningful search terms
            logger.info("Query is valid JSON, extracting meaningful search terms")
            
            # Dynamically extract all text content from JSON
            search_terms = self._extract_text_from_json(json_data)
            
            if search_terms:
                extracted_text = ' '.join(search_terms)
                logger.info(f"Extracted search terms: {extracted_text[:100]}{'...' if len(extracted_text) > 100 else ''}")
                return extracted_text
            else:
                # Fallback to original query if no meaningful terms found
                logger.warning("No meaningful search terms extracted from JSON, using original query")
                return query
            
        except json.JSONDecodeError:
            # If not JSON, treat as natural language query
            logger.info("Query is not JSON, using as natural language")
            return query
        except Exception as e:
            logger.warning(f"Error processing query: {e}")
            # Fallback to original query
            return query
    
    def _extract_text_from_json(self, data, max_depth=3, current_depth=0):
        """
        Recursively extract all text content from JSON data
        Completely dynamic approach - no hardcoded field names
        
        Args:
            data: JSON data (dict, list, or primitive)
            max_depth: Maximum recursion depth to prevent infinite loops
            current_depth: Current recursion depth
            
        Returns:
            List of text strings found in the JSON
        """
        if current_depth >= max_depth:
            return []
        
        text_terms = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                # Skip fields that are clearly non-text based on common patterns
                if self._is_likely_non_text_field(key, value):
                    continue
                
                # For nested structures, continue recursion
                if isinstance(value, (dict, list)):
                    nested_terms = self._extract_text_from_json(value, max_depth, current_depth + 1)
                    text_terms.extend(nested_terms)
                elif isinstance(value, str) and value.strip():
                    # Include all text fields
                    text_terms.append(value.strip())
                
        elif isinstance(data, list):
            for item in data:
                nested_terms = self._extract_text_from_json(item, max_depth, current_depth + 1)
                text_terms.extend(nested_terms)
                
        elif isinstance(data, str):
            # Clean and validate the string
            cleaned_text = data.strip()
            if cleaned_text and cleaned_text.lower() not in ['null', 'none', '']:
                text_terms.append(cleaned_text)
        
        return text_terms
    
    def _is_likely_non_text_field(self, key, value):
        """
        Determine if a field is likely not useful for text search
        Based on common patterns, not hardcoded lists
        """
        key_lower = key.lower()
        
        # Skip fields that are clearly numeric/ID patterns
        if any(pattern in key_lower for pattern in ['_id', '_number', '_amount', '_count', '_size', '_length']):
            return True
        
        # Skip fields that are clearly date/time patterns
        if any(pattern in key_lower for pattern in ['_date', '_time', '_at', '_timestamp', '_created', '_updated']):
            return True
        
        # Skip if value is clearly not text (numeric, boolean, etc.)
        if isinstance(value, (int, float, bool)):
            return True
        
        # Skip if value looks like an ID or number
        if isinstance(value, str) and (value.isdigit() or value.replace('.', '').isdigit()):
            return True
        
        return False

    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve relevant rules using Azure AI Search
        
        Args:
            query: JSON expense object as string or natural language query
            
        Returns:
            List of rule IDs in order of relevance
        """
        try:
            # Check if query is JSON and extract meaningful search terms
            search_text = self._extract_search_terms(query)
            
            logger.info(f"🔍 Searching for: '{search_text[:100]}{'...' if len(search_text) > 100 else ''}'")
            
            if self.use_hybrid:
                # Use hybrid search (text + vector with RRF ranking) - NO FALLBACKS
                logger.info("Using hybrid search (text + vector)...")
                
                # Find the correct vector field
                vector_field_candidates = ["key_content_vector", "content_vector", "text_vector", "embedding"]
                vector_query = None
                vector_field_used = None
                
                for field_name in vector_field_candidates:
                    try:
                        vector_query = VectorizableTextQuery(
                            text=search_text,  # Text to be vectorized by Azure
                            k_nearest_neighbors=self.retrieval_size,
                            fields=field_name
                        )
                        vector_field_used = field_name
                        logger.info(f"Using vector field: {field_name}")
                        break
                    except Exception as e:
                        logger.debug(f"Vector field {field_name} not available: {e}")
                        continue
                
                if not vector_query:
                    raise ValueError("No vector fields found in the index. Hybrid search requires vector fields.")
                
                # Always use hybrid search with both text and vector
                results = self.search_client.search(
                    search_text=search_text,
                    vector_queries=[vector_query],
                    top=self.retrieval_size,
                    search_mode="any",  # More permissive for better recall
                    query_type=QueryType.simple,
                    include_total_count=True
                )
            elif self.use_embeddings:
                # Use Azure integrated vectorization - no need to generate embeddings manually
                logger.info("Using Azure integrated vectorization...")
                
                # For pure vector search, we need to provide the vector query
                vector_query = VectorizableTextQuery(
                    text=search_text,  # Text to be vectorized by Azure
                    k_nearest_neighbors=self.retrieval_size,
                    fields="key_content_vector"  # This matches the field name in the index
                )
                
                results = self.search_client.search(
                    search_text="",  # Empty for pure vector search
                    vector_queries=[vector_query],
                    top=self.retrieval_size,
                    include_total_count=True
                )
            else:
                # Traditional text search
                return self._text_search(search_text)
            
            # Extract rule IDs from results
            retrieved_rules = []
            for i, result in enumerate(results):
                rule_id = result.get('rule_id', '')
                score = result.get('@search.score', 0.0)
                if rule_id:
                    retrieved_rules.append(rule_id)
                    logger.info(f"  Result {i+1}: {rule_id} (score: {score:.3f})")
            
            logger.info(f"✅ Retrieved {len(retrieved_rules)} rules: {retrieved_rules}")
            return retrieved_rules
            
        except Exception as e:
            logger.error(f"❌ Error during retrieval: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _text_search(self, query: str) -> List[str]:
        """Perform traditional text search"""
        logger.info("Using traditional text search...")
        
        logger.info(f"Search options: top={self.retrieval_size}, search_mode=any, query_type=simple")
        
        # Perform search with direct parameters
        results = self.search_client.search(
            search_text=query,
            top=self.retrieval_size,
            search_mode="all",  # All terms must match (more precise)
            query_type=QueryType.simple,
            scoring_profile="expense_relevance",  # Use our custom scoring profile
            include_total_count=True,
            minimum_coverage=100.0
        )
        
        # Extract rule IDs from results
        retrieved_rules = []
        for i, result in enumerate(results):
            rule_id = result.get('rule_id', '')
            score = result.get('@search.score', 0.0)
            if rule_id:
                retrieved_rules.append(rule_id)
                logger.info(f"  Result {i+1}: {rule_id} (score: {score:.3f})")
        
        return retrieved_rules
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Azure Search index"""
        try:
            logger.info("Getting index statistics...")
            # Get total document count
            results = self.search_client.search(
                search_text="*",
                top=0,
                include_total_count=True
            )
            total_count = results.get_count()
            
            stats = {
                "index_name": self.index_name,
                "endpoint": self.endpoint,
                "total_documents": total_count,
                "retrieval_size": self.retrieval_size
            }
            
            logger.info(f"Index stats: {total_count} documents in '{self.index_name}'")
            return stats
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}
