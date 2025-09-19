"""
Prototype Network-style Rule Classifier

This implementation uses sentence transformers to create prototype vectors
for each rule based on training examples, then classifies new requests
by finding the most similar prototype.
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import os
from tqdm import tqdm
from llama_index.core import Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from dotenv import load_dotenv
from ..base_retriever import BaseRetriever

load_dotenv()


class ProtovecRetriever(BaseRetriever):
    """
    Prototype network-style retriever that learns rule prototypes
    from training examples and classifies new requests by similarity.
    """
    
    def __init__(self, data, retrieval_size=3, model_name=None, 
                 training_data_path=None):
        """
        Initialize the prototype retriever.
        
        Args:
            data: The rule data (same format as other retrievers)
            retrieval_size: Number of top rules to return
            model_name: Deprecated - kept for compatibility but not used
            training_data_path: Path to synthetic training data JSON file
        """
        super().__init__(data, retrieval_size)
        self.model_name = "azure-openai"  # Use Azure OpenAI embeddings
        
        # Initialize Azure OpenAI embedding model (same as dense retriever)
        self.embed_model = AzureOpenAIEmbedding(
            azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
            api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
            azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
            api_version="2024-02-01",
        )
        
        self.prototypes = {}
        self.rule_examples = {}
        
        # Load or generate training data
        if training_data_path and os.path.exists(training_data_path):
            self.load_training_data(training_data_path)
        else:
            # Generate synthetic data if not provided
            self.generate_synthetic_data()
            
        # Build prototypes
        self.build_prototypes()
    
    def generate_synthetic_data(self):
        """Generate synthetic training data from CSV files."""
        # Check if we have English or Japanese data by looking at the data structure
        if self.data is not None and not self.data.empty:
            first_rule = self.data.iloc[0]
            # Check if it has English columns (Example 1, Example 2) or Japanese columns
            if 'Example 1' in first_rule or 'Expense item name' in first_rule:
                # English data
                self._generate_english_synthetic_data()
            elif '経費科目名称' in first_rule or '勘定科目' in first_rule:
                # Japanese data
                self._generate_japanese_synthetic_data()
            else:
                # Fallback to English
                self._generate_english_synthetic_data()
        else:
            # Fallback to English
            self._generate_english_synthetic_data()
    
    def _generate_english_synthetic_data(self):
        """Generate synthetic training data from the provided data."""
        from .synthetic_data_generator import SyntheticDataGenerator
        
        # Use the data passed to the retriever instead of reading from file
        # This prevents data leakage by ensuring we don't use test examples
        if self.data is None or self.data.empty:
            raise ValueError("No data provided for synthetic data generation")
            
        # Create a temporary CSV file from the provided data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.data.to_csv(f.name, index=False)
            temp_csv_path = f.name
        
        try:
            generator = SyntheticDataGenerator(temp_csv_path)
            training_data = generator.generate_training_data()
            
            # Store training data
            self.rule_examples = {}
            for item in training_data:
                rule_id = item['rule_id']
                if rule_id not in self.rule_examples:
                    self.rule_examples[rule_id] = []
                self.rule_examples[rule_id].append(item['text'])
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_path)
    
    def _generate_japanese_synthetic_data(self):
        """Generate synthetic training data from the provided data."""
        from .japanese_synthetic_data_generator import JapaneseSyntheticDataGenerator
        
        # Use the data passed to the retriever instead of reading from file
        # This prevents data leakage by ensuring we don't use test examples
        if self.data is None or self.data.empty:
            raise ValueError("No data provided for synthetic data generation")
            
        # Create a temporary CSV file from the provided data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.data.to_csv(f.name, index=False)
            temp_csv_path = f.name
        
        try:
            generator = JapaneseSyntheticDataGenerator(temp_csv_path)
            training_data = generator.generate_training_data()
            
            # Store training data
            self.rule_examples = {}
            for item in training_data:
                rule_id = item['rule_id']
                if rule_id not in self.rule_examples:
                    self.rule_examples[rule_id] = []
                self.rule_examples[rule_id].append(item['text'])
        finally:
            # Clean up temporary file
            os.unlink(temp_csv_path)
    
    def load_training_data(self, training_data_path: str):
        """Load training data from JSON file."""
        with open(training_data_path, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
            
        # Group examples by rule_id
        self.rule_examples = {}
        for item in training_data:
            rule_id = item['rule_id']
            if rule_id not in self.rule_examples:
                self.rule_examples[rule_id] = []
            self.rule_examples[rule_id].append(item['text'])
    
    def build_prototypes(self, min_examples_per_rule: int = 2):
        """Build prototype vectors for each rule."""
        print(f"Building prototypes for {len(self.rule_examples)} rules...")
        
        # Validate that all rules have sufficient examples
        insufficient_rules = []
        for rule_id, examples in self.rule_examples.items():
            if len(examples) < min_examples_per_rule:
                insufficient_rules.append((rule_id, len(examples)))
        
        if insufficient_rules:
            print(f"\nWarning: {len(insufficient_rules)} rules have insufficient examples:")
            for rule_id, count in insufficient_rules:
                print(f"  {rule_id}: {count} examples (minimum: {min_examples_per_rule})")
        
        for rule_id, examples in tqdm(self.rule_examples.items(), desc="Building prototypes"):
            if not examples:
                print(f"Warning: Skipping {rule_id} - no examples")
                continue
                
            # Encode all examples for this rule using Azure OpenAI
            embeddings = []
            for example in examples:
                embedding = self.embed_model.get_text_embedding(example)
                embeddings.append(embedding)
            
            # Convert to numpy array and compute mean prototype vector
            embeddings_array = np.array(embeddings)
            prototype = np.mean(embeddings_array, axis=0)
            self.prototypes[rule_id] = prototype
            
        print(f"Built {len(self.prototypes)} prototypes")
        
        # Report statistics
        example_counts = [len(examples) for examples in self.rule_examples.values()]
        if example_counts:
            print(f"Examples per rule - Min: {min(example_counts)}, Max: {max(example_counts)}, Avg: {sum(example_counts)/len(example_counts):.1f}")
    
    def add_new_rule(self, rule_id: str, examples: List[str]):
        """
        Add a new rule with examples (no retraining required).
        
        Args:
            rule_id: The rule identifier
            examples: List of example texts for this rule
        """
        if not examples:
            return
            
        # Encode examples and compute prototype using Azure OpenAI
        embeddings = []
        for example in examples:
            embedding = self.embed_model.get_text_embedding(example)
            embeddings.append(embedding)
        
        # Convert to numpy array and compute mean prototype
        embeddings_array = np.array(embeddings)
        prototype = np.mean(embeddings_array, axis=0)
        
        # Store prototype and examples
        self.prototypes[rule_id] = prototype
        self.rule_examples[rule_id] = examples
        
        print(f"Added new rule {rule_id} with {len(examples)} examples")
    
    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve the most similar rules for a query.
        
        Args:
            query: The input query text
            
        Returns:
            List of rule IDs (strings) for compatibility with evaluation
        """
        if not self.prototypes:
            return []
            
        # Extract JSON from markdown code block if present
        processed_query = self._extract_json_from_markdown(query)
        
        # Encode query using Azure OpenAI
        query_embedding = np.array([self.embed_model.get_text_embedding(processed_query)])
        
        # Compute similarities with all prototypes
        similarities = []
        for rule_id, prototype in self.prototypes.items():
            similarity = cosine_similarity(query_embedding, [prototype])[0][0]
            similarities.append((rule_id, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results - return just the rule IDs for evaluation compatibility
        top_results = similarities[:self.retrieval_size]
        return [rule_id for rule_id, _ in top_results]
    
    def _extract_json_from_markdown(self, query: str) -> str:
        """Extract JSON from markdown code block if present."""
        import json
        import re
        
        # Check if query looks like JSON in markdown
        if query.strip().startswith('``` json') or query.strip().startswith('```'):
            try:
                # Extract JSON from markdown code block
                json_match = re.search(r'```\s*json\s*\n(.*?)\n```', query, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to extract JSON directly
                    json_str = query.strip()
                    if json_str.startswith('```'):
                        json_str = json_str.split('\n', 1)[1]
                    if json_str.endswith('```'):
                        json_str = json_str.rsplit('\n', 1)[0]
                
                # Parse and re-serialize JSON to normalize format
                data = json.loads(json_str)
                return json.dumps(data, sort_keys=True)
                    
            except (json.JSONDecodeError, KeyError, ValueError):
                # If JSON parsing fails, return original query
                pass
        
        # Return original query if not JSON or parsing failed
        return query
    
    def get_rule_examples(self, rule_id: str) -> List[str]:
        """Get examples for a specific rule."""
        return self.rule_examples.get(rule_id, [])
    
    def get_prototype_stats(self) -> Dict[str, Any]:
        """Get statistics about the prototypes."""
        stats = {
            'total_rules': len(self.prototypes),
            'total_examples': sum(len(examples) for examples in self.rule_examples.values()),
            'examples_per_rule': {
                rule_id: len(examples) 
                for rule_id, examples in self.rule_examples.items()
            }
        }
        return stats
    
    def save_prototypes(self, filepath: str):
        """Save prototypes to file for later loading."""
        data = {
            'model_name': self.model_name,
            'prototypes': {rule_id: prototype.tolist() for rule_id, prototype in self.prototypes.items()},
            'rule_examples': self.rule_examples
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_prototypes(self, filepath: str):
        """Load prototypes from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.model_name = data['model_name']
        
        # Initialize Azure OpenAI embedding model (same as dense retriever)
        self.embed_model = AzureOpenAIEmbedding(
            azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
            api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
            azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
            api_version="2024-02-01",
        )
        
        # Convert prototype lists back to numpy arrays
        self.prototypes = {
            rule_id: np.array(prototype) 
            for rule_id, prototype in data['prototypes'].items()
        }
        
        self.rule_examples = data['rule_examples']
        
        print(f"Loaded {len(self.prototypes)} prototypes from {filepath}")


def create_protovec_retriever(data, retrieval_size=3, training_data_path=None):
    """
    Factory function to create a ProtovecRetriever.
    
    Args:
        data: Rule data
        retrieval_size: Number of results to return
        training_data_path: Optional path to training data JSON
        
    Returns:
        ProtovecRetriever instance
    """
    return ProtovecRetriever(
        data=data,
        retrieval_size=retrieval_size,
        training_data_path=training_data_path
    )


