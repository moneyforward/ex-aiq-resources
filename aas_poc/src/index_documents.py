"""
Document indexing script for Azure AI Search
Indexes the expense rules from retrieval_poc data into Azure AI Search
"""

import os
import sys
import pandas as pd
import json
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import IndexingResult
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ScoringProfile,
    TextWeights,
    CorsOptions,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters
)
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
        logging.FileHandler('indexing.log')
    ]
)
logger = logging.getLogger(__name__)
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ComplexField,
    CorsOptions,
    ScoringProfile,
    TextWeights
)

# Add the retrieval_poc approaches directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../retrieval_poc/approaches'))


class AzureSearchIndexer:
    """Indexes expense rules into Azure AI Search"""
    
    def __init__(self, index_name="aiq-expense-rules", use_embeddings=False, use_hybrid=False):
        self.index_name = index_name
        self.endpoint = "https://aibi-aai-stg-verification-30vc.search.windows.net"
        self.use_embeddings = use_embeddings
        self.use_hybrid = use_hybrid
        
        logger.info(f"Initializing AzureSearchIndexer with index: {index_name}")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Use embeddings: {use_embeddings}")
        logger.info(f"Use hybrid search: {use_hybrid}")
        
        if use_hybrid:
            logger.info("Using hybrid search (text + vector with RRF ranking)")
        elif use_embeddings:
            logger.info("Using Azure AI Search integrated vectorization")
        else:
            logger.info("Using traditional text search")
        
        self.search_client = self._get_search_client()
        self.index_client = self._get_index_client()
    
    def _get_search_client(self) -> SearchClient:
        """Get Azure Search client"""
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
    
    def _get_index_client(self) -> SearchIndexClient:
        """Get Azure Search index client"""
        # Use admin key for authentication (simpler and more reliable)
        admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        if admin_key:
            logger.info("Using Azure Key Credential for authentication")
            credential = AzureKeyCredential(admin_key)
        else:
            logger.error("AZURE_SEARCH_ADMIN_KEY not found in environment variables")
            raise ValueError("AZURE_SEARCH_ADMIN_KEY is required")
        
        logger.info("Creating SearchIndexClient")
        return SearchIndexClient(
            endpoint=self.endpoint,
            credential=credential
        )
    
    def delete_index(self) -> None:
        """Delete the Azure Search index."""
        try:
            logger.info(f"Deleting index '{self.index_name}'...")
            self.index_client.delete_index(self.index_name)
            logger.info(f"✅ Index '{self.index_name}' deleted successfully")
        except HttpResponseError as e:
            if e.status_code == 404:  # Index not found
                logger.info(f"Index '{self.index_name}' not found (already deleted)")
            else:
                logger.error(f"Error deleting index: {e}")
                raise
    
    def create_index(self):
        """Create the Azure Search index with appropriate schema"""
        logger.info("Creating index schema...")
        
        # Base fields - key content for vectorization, rest as metadata
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="rule_id", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="key_content", type=SearchFieldDataType.String),  # This gets vectorized
            # All other columns as metadata fields (not searchable, just for filtering)
            SimpleField(name="expense_name", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="account", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="concat_ab", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="advance_application", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="receipt_attached", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="eligibility_number", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="memo_section", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="when_to_use", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="check_contents", type=SearchFieldDataType.String, filterable=True),
        ]
        
        if self.use_hybrid:
            # Hybrid search: main content field + vector field
            logger.info("Adding fields for hybrid search (text + vector)...")
            
            # Add vector field for hybrid search
            key_content_vector_field = SearchField(
                name="key_content_vector", 
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True
            )
            # Set vector-specific properties after creation
            key_content_vector_field.vector_search_dimensions = 3072  # text-embedding-3-large dimensions
            key_content_vector_field.vector_search_profile_name = "default-vector-profile"  # Use the vectorization profile
            fields.append(key_content_vector_field)
        elif self.use_embeddings:
            # Add vector fields for embeddings
            logger.info("Adding vector fields for embeddings...")
            
            # TODO: Add vector field once we figure out the correct configuration
            # content_vector_field = SimpleField(
            #     name="content_vector", 
            #     type=SearchFieldDataType.Collection(SearchFieldDataType.Single)
            # )
            # content_vector_field.dimensions = 1536  # Azure integrated vectorization dimensions
            # content_vector_field.vector_search_configuration = "default-vector-config"
            # fields.append(content_vector_field)
        else:
            # Use analyzers for text fields
            logger.info("Using analyzers for text fields...")
            # Content field is already added above
        
        logger.info(f"Defined {len(fields)} fields for the index")
        
        # For Azure integrated vectorization, we don't need complex vector search profiles
        # The vector fields will be automatically configured
        
        # Create scoring profile for better relevance
        logger.info("Creating scoring profile...")
        scoring_profile = ScoringProfile(
            name="expense_relevance",
            text_weights=TextWeights(
                weights={
                    "key_content": 1.0  # Only the vectorized field gets weighted
                }
            )
        )
        logger.info("Scoring profile created with custom weights")
        
        # Create vector search configuration if using hybrid or embeddings
        vector_search = None
        
        if self.use_hybrid or self.use_embeddings:
            logger.info("Creating vector search configuration...")
            
            # Create HNSW algorithm configuration
            hnsw_config = HnswAlgorithmConfiguration(
                name="default-hnsw-config"
            )
            
            # Create Azure OpenAI vectorizer parameters
            vectorizer_params = AzureOpenAIVectorizerParameters(
                resource_url=os.getenv("AZURE_EMBEDDING_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large"),
                api_key=os.getenv("AZURE_EMBEDDING_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY"),
                model_name=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large")
            )
            
            # Create Azure OpenAI vectorizer for integrated vectorization
            vectorizer = AzureOpenAIVectorizer(
                vectorizer_name="default-vectorizer",
                parameters=vectorizer_params
            )
            
            # Create vector search profile
            vector_profile = VectorSearchProfile(
                name="default-vector-profile",
                algorithm_configuration_name="default-hnsw-config",
                vectorizer_name="default-vectorizer"
            )
            
            # Create vector search configuration
            vector_search = VectorSearch(
                algorithms=[hnsw_config],
                vectorizers=[vectorizer],
                profiles=[vector_profile]
            )
        
        # Create the index
        logger.info("Creating SearchIndex object...")
        index_kwargs = {
            "name": self.index_name,
            "fields": fields,
            "scoring_profiles": [scoring_profile],
            "default_scoring_profile": "expense_relevance",
            "cors_options": CorsOptions(allowed_origins=["*"])
        }
        
        # Add vector search configuration if needed
        if vector_search:
            index_kwargs["vector_search"] = vector_search
        
        index = SearchIndex(**index_kwargs)
        
        try:
            logger.info(f"Attempting to create index '{self.index_name}'...")
            self.index_client.create_index(index)
            logger.info(f"✅ Index '{self.index_name}' created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"ℹ️  Index '{self.index_name}' already exists - deleting and recreating...")
                try:
                    self.index_client.delete_index(self.index_name)
                    logger.info(f"✅ Deleted existing index '{self.index_name}'")
                    self.index_client.create_index(index)
                    logger.info(f"✅ Recreated index '{self.index_name}' with new schema")
                except Exception as recreate_error:
                    logger.error(f"❌ Failed to recreate index: {recreate_error}")
                    raise
            else:
                logger.error(f"❌ Error creating index: {e}")
                raise
    
    def load_expense_data(self, dataset_type="ja") -> pd.DataFrame:
        """Load expense rules data from retrieval_poc"""
        if dataset_type == "ja":
            data_path = os.path.join(os.path.dirname(__file__), '../../retrieval_poc/data/eval_ja.csv')
        elif dataset_type == "en":
            data_path = os.path.join(os.path.dirname(__file__), '../../retrieval_poc/data/eval_en.csv')
        else:
            raise ValueError(f"Unknown dataset_type: {dataset_type}. Use 'ja' or 'en'")
        
        logger.info(f"Loading {dataset_type} expense data from: {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"✅ Loaded {len(df)} expense rules from {data_path}")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    
    def prepare_documents(self, df: pd.DataFrame, dataset_type="ja") -> List[Dict[str, Any]]:
        """Prepare documents for indexing - following dense retriever and text_to_sql approach"""
        logger.info("Preparing documents for indexing...")
        documents = []
        
        # Define column mappings for both Japanese and English datasets
        if dataset_type == "ja":
            col_mapping = {
                'expense_name': '経費科目名称\n（クラウド経費に登録されている名称）',
                'account': '勘定科目',
                'concat_ab': 'CONCAT A&B',  # This might not exist in JA, will handle gracefully
                'advance_application': '事前申請',
                'receipt_attached': '領収書添付',
                'eligibility_number': '適格番号',
                'memo_section': 'メモ欄（記載内容）',
                'when_to_use': 'この経費科目を使う時',
                'check_contents': '記載内容の確認・注意点・備考'
            }
        else:  # English dataset
            col_mapping = {
                'expense_name': 'Expense item name\n(Name registered in Cloud Expenses)',
                'account': 'Account',
                'concat_ab': 'CONCAT A&B',
                'advance_application': 'Advance application',
                'receipt_attached': 'Receipt attached',
                'eligibility_number': 'Eligibility number',
                'memo_section': 'Memo section (contents to be entered)',
                'when_to_use': 'When to use this expense item',
                'check_contents': 'Check the contents, notes, and remarks'
            }
        
        for idx, row in df.iterrows():
            if idx % 10 == 0:  # Log every 10th document
                logger.info(f"Processing document {idx + 1}/{len(df)}")
            
            # Create key_content field combining the most important fields for vectorization
            key_parts = []
            
            # Add expense name (highest priority)
            if 'expense_name' in col_mapping and col_mapping['expense_name'] in row:
                expense_name_val = row[col_mapping['expense_name']]
                if pd.notna(expense_name_val) and str(expense_name_val).strip():
                    key_parts.append(str(expense_name_val))
            
            # Add account category
            if 'account' in col_mapping and col_mapping['account'] in row:
                account_val = row[col_mapping['account']]
                if pd.notna(account_val) and str(account_val).strip():
                    key_parts.append(str(account_val))
            
            # Add when to use
            if 'when_to_use' in col_mapping and col_mapping['when_to_use'] in row:
                when_to_use_val = row[col_mapping['when_to_use']]
                if pd.notna(when_to_use_val) and str(when_to_use_val).strip():
                    key_parts.append(str(when_to_use_val))
            
            # Add check contents
            if 'check_contents' in col_mapping and col_mapping['check_contents'] in row:
                check_contents_val = row[col_mapping['check_contents']]
                if pd.notna(check_contents_val) and str(check_contents_val).strip():
                    key_parts.append(str(check_contents_val))
            
            key_content = " ".join(key_parts)  # Simple space separation for vectorization
            
            # Extract all metadata fields using the mapping
            document = {
                "id": str(idx),
                "rule_id": str(row.get('Rule', '')),
                "key_content": key_content  # Only this field gets vectorized
            }
            
            # Add all mapped fields
            for field_name, col_name in col_mapping.items():
                if col_name in row:
                    document[field_name] = str(row[col_name]) if pd.notna(row[col_name]) else ''
                else:
                    document[field_name] = ''  # Field doesn't exist in this dataset
            
            documents.append(document)
        
        logger.info(f"✅ Prepared {len(documents)} documents for indexing")
        return documents
    
    def _generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using Azure integrated vectorization"""
        if not self.use_embeddings:
            return []
        
        # Azure AI Search integrated vectorization - no separate API calls needed
        # The embeddings will be generated automatically during indexing
        logger.info("Using Azure AI Search integrated vectorization")
        return []  # Return empty - Azure will generate embeddings automatically
    
    def _add_embeddings_to_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to documents if using embedding or hybrid mode"""
        if not (self.use_embeddings or self.use_hybrid):
            return documents
        
        # For Azure integrated vectorization, we don't pre-generate embeddings
        # Azure will generate them automatically during indexing
        if self.use_hybrid:
            logger.info("Using hybrid search - embeddings will be generated automatically for vector fields")
        else:
            logger.info("Using Azure integrated vectorization - embeddings will be generated automatically")
        return documents
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Index documents into Azure Search"""
        try:
            # Upload documents in batches
            batch_size = 100
            total_docs = len(documents)
            logger.info(f"Starting to index {total_docs} documents in batches of {batch_size}")
            
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                batch_num = i//batch_size + 1
                logger.info(f"Uploading batch {batch_num} ({len(batch)} documents)...")
                
                result = self.search_client.upload_documents(batch)
                
                # Check for errors
                failed_docs = [doc for doc in result if not doc.succeeded]
                if failed_docs:
                    logger.error(f"❌ Failed to index {len(failed_docs)} documents in batch {batch_num}")
                    for doc in failed_docs:
                        logger.error(f"  Error: {doc.error_message}")
                else:
                    logger.info(f"✅ Successfully indexed batch {batch_num} ({len(batch)} documents)")
            
            logger.info(f"🎉 Indexing completed. Total documents: {total_docs}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during indexing: {e}")
            return False
    
    def run_full_indexing(self, dataset_type="ja"):
        """Run the complete indexing process"""
        logger.info(f"🚀 Starting Azure AI Search indexing process for {dataset_type} dataset...")
        
        # Create index
        logger.info("Step 1: Creating index...")
        self.create_index()
        
        # Load data
        logger.info("Step 2: Loading expense data...")
        df = self.load_expense_data(dataset_type)
        
        # Prepare documents
        logger.info("Step 3: Preparing documents...")
        documents = self.prepare_documents(df, dataset_type)
        
        # Add embeddings if using embedding or hybrid mode
        if self.use_embeddings or self.use_hybrid:
            logger.info("Step 3.5: Adding embeddings to documents...")
            documents = self._add_embeddings_to_documents(documents)
        
        # Index documents
        logger.info("Step 4: Indexing documents...")
        success = self.index_documents(documents)
        
        if success:
            logger.info("🎉 Indexing completed successfully!")
        else:
            logger.error("❌ Indexing failed!")
        
        return success


def main():
    """Main function to run indexing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index documents to Azure AI Search')
    parser.add_argument('--index-name', default='aiq-expense-rules', 
                       help='Name of the Azure Search index')
    parser.add_argument('--use-embeddings', action='store_true',
                       help='Use embeddings instead of analyzers')
    parser.add_argument('--use-hybrid', action='store_true',
                       help='Use hybrid search (combines text + vector with RRF ranking)')
    parser.add_argument('--dataset', choices=['ja', 'en'], default='ja',
                       help='Dataset to index: ja (Japanese) or en (English synthetic)')
    args = parser.parse_args()
    
    # Set default index name based on dataset
    if args.index_name == "aiq-expense-rules":
        args.index_name = f"aiq-expense-rules-{args.dataset}"
    
    indexer = AzureSearchIndexer(
        index_name=args.index_name,
        use_embeddings=args.use_embeddings,
        use_hybrid=args.use_hybrid
    )
    indexer.run_full_indexing(args.dataset)


if __name__ == "__main__":
    main()
