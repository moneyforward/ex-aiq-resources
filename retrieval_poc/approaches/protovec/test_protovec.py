"""
Test script for the ProtovecRetriever implementation.
"""

import os
import sys
import json
import pandas as pd

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import with absolute paths
from approaches.protovec.protovec_retriever import ProtovecRetriever
from approaches.protovec.synthetic_data_generator import SyntheticDataGenerator


def load_eval_data():
    """Load evaluation data from CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/eval_en.csv")
    df = pd.read_csv(csv_path)
    
    # Convert to list of dicts (same format as other retrievers)
    data = []
    for _, row in df.iterrows():
        data.append(row.to_dict())
    
    return data


def test_synthetic_data_generation():
    """Test the synthetic data generator."""
    print("Testing Synthetic Data Generation")
    print("=" * 40)
    
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/eval_en.csv")
    print(f"📁 Loading data from: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        return []
    
    generator = SyntheticDataGenerator(csv_path)
    print(f"📊 Loaded {len(generator.df)} rules from CSV")
    
    # Generate training data
    print("🔄 Generating training data...")
    training_data = generator.generate_training_data()
    
    print(f"✅ Generated {len(training_data)} training examples")
    
    # Show some examples
    print("\n📝 Sample training examples:")
    for i, example in enumerate(training_data[:5]):
        print(f"  {i+1}. Rule: {example['rule_id']}")
        print(f"     Text: {example['text']}")
        print()
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), "synthetic_training_data.json")
    print(f"💾 Saving training data to: {output_path}")
    generator.save_training_data(output_path)
    
    return training_data


def test_protovec_retriever():
    """Test the ProtovecRetriever."""
    print("Testing ProtovecRetriever")
    print("=" * 30)
    
    # Load data
    print("📁 Loading evaluation data...")
    data = load_eval_data()
    print(f"✅ Loaded {len(data)} rules from eval_en.csv")
    
    # Create retriever
    print("🔄 Creating ProtovecRetriever...")
    retriever = ProtovecRetriever(data, retrieval_size=3)
    print("✅ ProtovecRetriever created successfully!")
    
    # Print statistics
    stats = retriever.get_prototype_stats()
    print(f"\n📊 Prototype Statistics:")
    print(f"  Total rules: {stats['total_rules']}")
    print(f"  Total examples: {stats['total_examples']}")
    print(f"  Average examples per rule: {stats['total_examples'] / stats['total_rules']:.1f}")
    
    # Test queries
    test_queries = [
        "Train from Tokyo to Shinjuku, 500 yen",
        "Shinkansen from Tokyo to Osaka with hotel accommodation",
        "Taxi ride for emergency to hospital",
        "Conference fee for Tech Summit 2025",
        "Dinner with clients at expensive restaurant over 10000 yen",
        "Equipment purchase laptop 150000 yen",
        "Communication costs SaaS subscription",
        "Overseas travel Seoul to Busan subway"
    ]
    
    print(f"\nTesting {len(test_queries)} queries:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        results = retriever.retrieve(query)
        
        for j, result in enumerate(results, 1):
            rule_data = result['rule_data']
            rule_name = rule_data.get('Expense item name', 'N/A')
            print(f"   {j}. {result['rule_id']} (similarity: {result['similarity']:.3f})")
            print(f"      {rule_name}")
    
    return retriever


def test_rule_examples():
    """Test getting examples for specific rules."""
    print("\nTesting Rule Examples")
    print("=" * 25)
    
    data = load_eval_data()
    retriever = ProtovecRetriever(data, retrieval_size=3)
    
    # Test a few rules
    test_rules = ['RULE_001', 'RULE_002', 'RULE_005']
    
    for rule_id in test_rules:
        examples = retriever.get_rule_examples(rule_id)
        print(f"\n{rule_id} examples ({len(examples)}):")
        for i, example in enumerate(examples[:3], 1):  # Show first 3
            print(f"  {i}. {example}")
        if len(examples) > 3:
            print(f"  ... and {len(examples) - 3} more")


def test_add_new_rule():
    """Test adding a new rule dynamically."""
    print("\nTesting Add New Rule")
    print("=" * 25)
    
    data = load_eval_data()
    retriever = ProtovecRetriever(data, retrieval_size=3)
    
    # Add a new rule
    new_rule_id = "RULE_TEST"
    new_examples = [
        "Test expense for new rule",
        "Another test example for the new rule",
        "Third example for testing purposes"
    ]
    
    print(f"Adding new rule {new_rule_id} with {len(new_examples)} examples")
    retriever.add_new_rule(new_rule_id, new_examples)
    
    # Test querying the new rule
    test_query = "Test expense for new rule"
    results = retriever.retrieve(test_query)
    
    print(f"\nQuery: {test_query}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['rule_id']} (similarity: {result['similarity']:.3f})")
    
    # Verify the new rule is in results
    new_rule_found = any(result['rule_id'] == new_rule_id for result in results)
    print(f"\nNew rule found in results: {new_rule_found}")


def main():
    """Run all tests."""
    print("Prototype Network Rule Classifier - Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Synthetic data generation
        print("\n🔍 Starting Test 1: Synthetic Data Generation")
        training_data = test_synthetic_data_generation()
        
        # Test 2: ProtovecRetriever
        print("\n🔍 Starting Test 2: ProtovecRetriever")
        retriever = test_protovec_retriever()
        
        # Test 3: Rule examples
        print("\n🔍 Starting Test 3: Rule Examples")
        test_rule_examples()
        
        # Test 4: Add new rule
        print("\n🔍 Starting Test 4: Add New Rule")
        test_add_new_rule()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
