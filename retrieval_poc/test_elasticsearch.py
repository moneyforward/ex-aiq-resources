#!/usr/bin/env python3
"""
Simple test script to verify Elasticsearch retriever implementation.
Run this after starting Elasticsearch with: make es-start
"""

import pandas as pd
from approaches.elasticsearch.elasticsearch_retriever import ElasticsearchRetriever

def test_elasticsearch_retriever():
    """Test the Elasticsearch retriever with sample data"""
    
    # Create sample data similar to the evaluation datasets
    sample_data = pd.DataFrame({
        'rule_id': ['rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5'],
        'Rule': [
            'Travel expenses for business meetings',
            'Office supplies and stationery',
            'Client entertainment and meals',
            'Transportation and parking fees',
            'Software licenses and subscriptions'
        ],
        'Description': [
            'Covers travel costs for business meetings and conferences',
            'Office supplies, paper, pens, and other stationery items',
            'Meals and entertainment expenses for client meetings',
            'Parking fees, tolls, and local transportation costs',
            'Software licenses, cloud services, and digital subscriptions'
        ],
        'Category': [
            'Travel',
            'Office',
            'Entertainment',
            'Transportation',
            'Software'
        ]
    })
    
    print("🧪 Testing Elasticsearch Retriever")
    print("=" * 50)
    
    try:
        # Initialize retriever with a unique index name to avoid conflicts
        import time
        unique_index = f'test_expense_rules_{int(time.time())}'
        print("📝 Initializing Elasticsearch retriever...")
        retriever = ElasticsearchRetriever(
            sample_data, 
            retrieval_size=3,
            index_name=unique_index
        )
        
        # Test queries
        test_queries = [
            "business travel meeting",
            "office supplies",
            "client dinner",
            "parking fees",
            "software license"
        ]
        
        print("\n🔍 Testing search queries:")
        print("-" * 30)
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = retriever.retrieve(query)
            print(f"Results: {results}")
            
            # Show details of retrieved rules
            for i, rule_id in enumerate(results, 1):
                rule_data = sample_data[sample_data['rule_id'] == rule_id]
                if not rule_data.empty:
                    rule = rule_data.iloc[0]
                    print(f"  {i}. {rule['Rule']} ({rule['Category']})")
        
        # Test stats
        print(f"\n📊 Index statistics:")
        stats = retriever.get_search_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Elasticsearch retriever test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\n💡 Make sure Elasticsearch is running:")
        print("   make es-start")
        return False
    
    return True

if __name__ == "__main__":
    success = test_elasticsearch_retriever()
    exit(0 if success else 1)
