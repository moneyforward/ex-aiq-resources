"""
Test script for Japanese ProtovecRetriever implementation.
"""

import os
import sys
import pandas as pd

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import with absolute paths
from approaches.protovec.protovec_retriever import ProtovecRetriever
from approaches.protovec.japanese_synthetic_data_generator import JapaneseSyntheticDataGenerator


def load_japanese_data():
    """Load Japanese evaluation data from CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/eval_ja.csv")
    df = pd.read_csv(csv_path)
    
    # Convert to list of dicts (same format as other retrievers)
    data = []
    for _, row in df.iterrows():
        data.append(row.to_dict())
    
    return data


def test_japanese_synthetic_data_generation():
    """Test the Japanese synthetic data generator."""
    print("Testing Japanese Synthetic Data Generation")
    print("=" * 50)
    
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/eval_ja.csv")
    print(f"📁 Loading Japanese data from: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        return []
    
    generator = JapaneseSyntheticDataGenerator(csv_path)
    print(f"📊 Loaded {len(generator.df)} Japanese rules from CSV")
    
    # Generate training data
    print("🔄 Generating Japanese training data...")
    training_data = generator.generate_training_data()
    
    print(f"✅ Generated {len(training_data)} Japanese training examples")
    
    # Show some examples
    print("\n📝 Sample Japanese training examples:")
    for i, example in enumerate(training_data[:10]):
        print(f"  {i+1}. Rule: {example['rule_id']}")
        print(f"     Text: {example['text']}")
        print()
    
    return training_data


def test_japanese_protovec_retriever():
    """Test the ProtovecRetriever with Japanese data."""
    print("Testing ProtovecRetriever with Japanese Data")
    print("=" * 50)
    
    # Load Japanese data
    print("📁 Loading Japanese evaluation data...")
    data = load_japanese_data()
    print(f"✅ Loaded {len(data)} Japanese rules from eval_ja.csv")
    
    # Create retriever
    print("🔄 Creating ProtovecRetriever with Japanese data...")
    retriever = ProtovecRetriever(data, retrieval_size=3)
    print("✅ ProtovecRetriever created successfully!")
    
    # Print statistics
    stats = retriever.get_prototype_stats()
    print(f"\n📊 Prototype Statistics:")
    print(f"  Total rules: {stats['total_rules']}")
    print(f"  Total examples: {stats['total_examples']}")
    print(f"  Average examples per rule: {stats['total_examples'] / stats['total_rules']:.1f}")
    
    # Test queries in Japanese
    test_queries = [
        "東京から新宿まで電車で500円",
        "東京から大阪まで新幹線で15000円",
        "緊急で病院までタクシーで4500円",
        "会議費で50000円",
        "お客様との食事で8500円",
        "ノートPC購入で150000円",
        "Freee会計ソフトで16500円",
        "ソウルから釜山まで地下鉄で3000円"
    ]
    
    print(f"\nTesting {len(test_queries)} Japanese queries:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        results = retriever.retrieve(query)
        
        for j, result in enumerate(results, 1):
            rule_data = result['rule_data']
            rule_name = rule_data.get('経費科目名称\n（クラウド経費に登録されている名称）', 'N/A')
            print(f"   {j}. {result['rule_id']} (similarity: {result['similarity']:.3f})")
            print(f"      {rule_name}")
    
    return retriever


def main():
    """Run all Japanese tests."""
    print("Japanese Prototype Network Rule Classifier - Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Japanese synthetic data generation
        print("\n🔍 Starting Test 1: Japanese Synthetic Data Generation")
        training_data = test_japanese_synthetic_data_generation()
        
        # Test 2: Japanese ProtovecRetriever
        print("\n🔍 Starting Test 2: Japanese ProtovecRetriever")
        retriever = test_japanese_protovec_retriever()
        
        print("\n" + "=" * 70)
        print("✅ All Japanese tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
