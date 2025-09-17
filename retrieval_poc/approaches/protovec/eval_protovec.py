"""
Evaluation script for ProtovecRetriever that integrates with the existing evaluation framework.
"""

import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from protovec_retriever import ProtovecRetriever


def load_eval_data():
    """Load evaluation data from CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/eval_en.csv")
    df = pd.read_csv(csv_path)
    
    # Convert to list of dicts (same format as other retrievers)
    data = []
    for _, row in df.iterrows():
        data.append(row.to_dict())
    
    return data


def create_test_queries() -> List[Dict[str, Any]]:
    """Create test queries based on the rule examples."""
    data = load_eval_data()
    
    test_queries = []
    
    # Create queries based on rule examples
    for rule in data:
        rule_id = rule['Rule']
        
        # Extract examples and create queries
        examples = []
        for col in ['Example 1', 'Example 2']:
            if col in rule and pd.notna(rule[col]):
                example_text = str(rule[col])
                # Extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```\s*json\s*\n(.*?)\n```', example_text, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                        examples.append(json_data)
                    except json.JSONDecodeError:
                        continue
        
        # Create queries from examples
        for i, example in enumerate(examples[:2]):  # Use first 2 examples
            query_text = json_to_query_text(example)
            if query_text:
                test_queries.append({
                    'query': query_text,
                    'expected_rule': rule_id,
                    'rule_name': rule.get('Expense item name', 'N/A')
                })
    
    return test_queries


def json_to_query_text(json_data: Dict[str, Any]) -> str:
    """Convert JSON data to a natural language query."""
    text_parts = []
    
    # Build query text
    if 'transport_mode' in json_data:
        transport = json_data['transport_mode']
        if transport in ['Train', 'Bus', 'Subway']:
            text_parts.append(f"Local {transport.lower()} travel")
        elif transport == 'Shinkansen':
            text_parts.append("Shinkansen bullet train travel")
        elif transport == 'Flight':
            text_parts.append("Airplane flight")
        elif transport == 'Taxi':
            text_parts.append("Taxi ride")
            
    if 'origin' in json_data and 'destination' in json_data:
        text_parts.append(f"from {json_data['origin']} to {json_data['destination']}")
        
    if 'overseas_flag' in json_data and json_data.get('overseas_flag'):
        text_parts.append("overseas travel")
        
    if 'trip_start_date' in json_data:
        text_parts.append(f"on {json_data['trip_start_date']}")
        
    if 'fare_amount' in json_data and json_data['fare_amount'] != 'not applicable':
        text_parts.append(f"costing {json_data['fare_amount']} yen")
        
    if 'accommodation_name' in json_data and json_data['accommodation_name']:
        text_parts.append(f"staying at {json_data['accommodation_name']}")
        
    if 'taxi_reason' in json_data:
        text_parts.append(f"for {json_data['taxi_reason']}")
        
    if 'conference_name' in json_data:
        text_parts.append(f"conference: {json_data['conference_name']}")
        
    if 'meeting_name' in json_data:
        text_parts.append(f"meeting: {json_data['meeting_name']}")
        
    if 'participant_companies' in json_data:
        text_parts.append(f"with {json_data['participant_companies']}")
        
    if 'gift_type' in json_data:
        text_parts.append(f"{json_data['gift_type']} for {json_data.get('recipient_name', 'client')}")
        
    if 'item_name' in json_data:
        text_parts.append(f"purchase of {json_data['item_name']}")
        
    if 'service_type' in json_data:
        text_parts.append(f"{json_data['service_type']} service")
        
    if 'provider_name' in json_data:
        text_parts.append(f"from {json_data['provider_name']}")
        
    # Add amount if available
    amount_fields = ['amount', 'fare_amount', 'accommodation_amount', 'gift_amount', 'equipment_cost']
    for field in amount_fields:
        if field in json_data and json_data[field] and json_data[field] != 'not applicable':
            try:
                amount = int(json_data[field])
                if amount > 0:
                    text_parts.append(f"amount: {amount} yen")
                    break
            except (ValueError, TypeError):
                continue
                
    return " ".join(text_parts) if text_parts else None


def evaluate_protovec(retrieval_size=3) -> Dict[str, Any]:
    """Evaluate the ProtovecRetriever."""
    print("Evaluating ProtovecRetriever")
    print("=" * 40)
    
    # Load data
    data = load_eval_data()
    print(f"Loaded {len(data)} rules")
    
    # Create retriever
    retriever = ProtovecRetriever(data, retrieval_size=retrieval_size)
    
    # Create test queries
    test_queries = create_test_queries()
    print(f"Created {len(test_queries)} test queries")
    
    # Evaluate
    correct_top1 = 0
    correct_top3 = 0
    total_queries = len(test_queries)
    
    results = []
    
    for i, test_query in enumerate(test_queries):
        query = test_query['query']
        expected_rule = test_query['expected_rule']
        
        # Get results
        retrieved_results = retriever.retrieve(query)
        retrieved_rules = [result['rule_id'] for result in retrieved_results]
        
        # Check accuracy
        top1_correct = retrieved_rules[0] == expected_rule if retrieved_rules else False
        top3_correct = expected_rule in retrieved_rules
        
        if top1_correct:
            correct_top1 += 1
        if top3_correct:
            correct_top3 += 1
        
        results.append({
            'query': query,
            'expected_rule': expected_rule,
            'retrieved_rules': retrieved_rules,
            'top1_correct': top1_correct,
            'top3_correct': top3_correct,
            'similarities': [result['similarity'] for result in retrieved_results]
        })
        
        if i < 5:  # Show first 5 results
            print(f"\nQuery {i+1}: {query}")
            print(f"Expected: {expected_rule}")
            print(f"Retrieved: {retrieved_rules}")
            print(f"Top-1 correct: {top1_correct}, Top-3 correct: {top3_correct}")
    
    # Calculate metrics
    top1_accuracy = correct_top1 / total_queries
    top3_accuracy = correct_top3 / total_queries
    
    print(f"\nEvaluation Results:")
    print(f"Total queries: {total_queries}")
    print(f"Top-1 accuracy: {top1_accuracy:.3f} ({correct_top1}/{total_queries})")
    print(f"Top-3 accuracy: {top3_accuracy:.3f} ({correct_top3}/{total_queries})")
    
    # Prototype statistics
    stats = retriever.get_prototype_stats()
    print(f"\nPrototype Statistics:")
    print(f"Total rules with prototypes: {stats['total_rules']}")
    print(f"Total training examples: {stats['total_examples']}")
    print(f"Average examples per rule: {stats['total_examples'] / stats['total_rules']:.1f}")
    
    return {
        'top1_accuracy': top1_accuracy,
        'top3_accuracy': top3_accuracy,
        'total_queries': total_queries,
        'correct_top1': correct_top1,
        'correct_top3': correct_top3,
        'prototype_stats': stats,
        'results': results
    }


def main():
    """Run evaluation."""
    results = evaluate_protovec(retrieval_size=3)
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "protovec_evaluation_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to {output_path}")
