from elasticsearch import Elasticsearch
from ..base_retriever import BaseRetriever
import json
from typing import List, Dict, Any


class ElasticsearchRetriever(BaseRetriever):
    def __init__(self, data, retrieval_size=3, 
                 es_host='localhost', es_port=9200, 
                 index_name='expense_rules', 
                 analyzer='standard',
                 rule_column='Rule',
                 description_column='Description', 
                 category_column='Category',
                 rule_id_column='rule_id'):
        super().__init__(data, retrieval_size)
        
        # Initialize Elasticsearch client with timeout settings
        self.es = Elasticsearch(
            f"http://{es_host}:{es_port}",
            request_timeout=30,
            retry_on_timeout=True,
            max_retries=3
        )
        self.index_name = index_name
        self.analyzer = analyzer
        self.rule_column = rule_column
        self.description_column = description_column
        self.category_column = category_column
        self.rule_id_column = rule_id_column
        
        # Test connection
        try:
            self.es.ping()
            print(f"✅ Connected to Elasticsearch at {es_host}:{es_port}")
        except Exception as e:
            print(f"❌ Failed to connect to Elasticsearch: {e}")
            raise
        
        # Index the documents
        self._create_index()
        self._index_documents()
    
    def _create_index(self):
        """Create Elasticsearch index with appropriate mapping"""
        # Check if index already exists and delete it
        try:
            if self.es.indices.exists(index=self.index_name):
                print(f"🗑️  Deleting existing index: {self.index_name}")
                self.es.indices.delete(index=self.index_name)
                # Small delay to ensure deletion is complete
                import time
                time.sleep(1)
        except Exception as e:
            print(f"Warning: Could not delete existing index: {e}")
        
        # Simple mapping using standard analyzer for now
        mapping = {
            "mappings": {
                "properties": {
                    "rule_id": {"type": "keyword"},
                    "rule": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "category": {"type": "keyword"},
                    "full_text": {"type": "text", "analyzer": "standard"}
                }
            }
        }
        
        try:
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"✅ Created Elasticsearch index: {self.index_name}")
        except Exception as e:
            if "resource_already_exists_exception" in str(e):
                print(f"ℹ️  Index {self.index_name} already exists, using existing index")
            else:
                raise
    
    def _index_documents(self):
        """Index all documents from the data"""
        for idx, row in self.data.iterrows():
            # Create a comprehensive document for search using configurable column names
            doc = {
                "rule_id": row.get(self.rule_id_column, f"rule_{idx}"),
                "rule": str(row.get(self.rule_column, '')),
                "description": str(row.get(self.description_column, '')),
                "category": str(row.get(self.category_column, '')),
                "full_text": ' '.join([
                    str(row.get(self.rule_column, '')),
                    str(row.get(self.description_column, '')),
                    str(row.get(self.category_column, ''))
                ])
            }
            
            self.es.index(index=self.index_name, id=idx, document=doc)
        
        # Refresh index to make documents searchable
        self.es.indices.refresh(index=self.index_name)
        print(f"✅ Indexed {len(self.data)} documents into Elasticsearch")
        
    
    def _extract_expense_description(self, query: str) -> str:
        """Extract the expense description from the query format"""
        # Handle Japanese format: "Expense: [description], Amount: [amount], Date: [date]"
        if "Expense:" in query:
            # Extract the expense description part
            expense_part = query.split("Expense:")[1]
            if "," in expense_part:
                expense_desc = expense_part.split(",")[0].strip()
                return expense_desc
        
        # Handle JSON format queries
        if query.strip().startswith('{') and query.strip().endswith('}'):
            try:
                import json
                data = json.loads(query)
                # Extract key fields that are most relevant for search
                search_terms = []
                for key in ['transport_mode', 'origin', 'destination', 'campaign_name', 
                           'event_name', 'vaccine_name', 'advertising_platform', 'bank_name',
                           'organization_name', 'meeting_name', 'affiliate_name']:
                    if key in data and data[key]:
                        search_terms.append(str(data[key]))
                return ' '.join(search_terms) if search_terms else query
            except:
                # If JSON parsing fails, return original query
                return query
        
        # For other formats, return as-is
        return query
    
    def retrieve(self, query: str) -> List[str]:
        """Retrieve relevant rules using Elasticsearch search"""
        if not query or not query.strip():
            return []
        
        # Extract key terms from the query for better matching
        # The query format is: "Expense: [description], Amount: [amount], Date: [date]"
        # We want to focus on the expense description part
        processed_query = self._extract_expense_description(query)
        
        # Simple search query with multiple strategies for Japanese text
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": processed_query,
                                "fields": ["rule^2", "description^1.5", "full_text^1"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "multi_match": {
                                "query": processed_query,
                                "fields": ["rule^2", "description^1.5", "full_text^1"],
                                "type": "phrase_prefix"
                            }
                        },
                        {
                            "wildcard": {
                                "rule": {
                                    "value": f"*{processed_query}*",
                                    "boost": 1.5
                                }
                            }
                        },
                        {
                            "wildcard": {
                                "description": {
                                    "value": f"*{processed_query}*",
                                    "boost": 1.0
                                }
                            }
                        },
                        {
                            "match": {
                                "category": {
                                    "query": processed_query,
                                    "boost": 0.5
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": self.retrieval_size
        }
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            results = []
            
            for hit in response['hits']['hits']:
                rule_id = hit['_source'].get('rule_id')
                if rule_id:
                    results.append(rule_id)
            
            print(f"🔍 Elasticsearch found {len(results)} results for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            print(f"❌ Elasticsearch search error: {e}")
            return []
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about the Elasticsearch index"""
        try:
            stats = self.es.indices.stats(index=self.index_name)
            return {
                "total_documents": stats['indices'][self.index_name]['total']['docs']['count'],
                "index_size": stats['indices'][self.index_name]['total']['store']['size_in_bytes']
            }
        except Exception as e:
            print(f"Warning: Could not get Elasticsearch stats: {e}")
            return {}
