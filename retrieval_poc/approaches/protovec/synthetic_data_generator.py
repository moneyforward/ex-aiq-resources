"""
Synthetic data generator for prototype network training.
Creates training examples from eval_en.csv rule examples.
"""

import json
import pandas as pd
import random
from typing import List, Dict, Any
import re
from tqdm import tqdm


class SyntheticDataGenerator:
    """Generates synthetic training data from rule examples."""
    
    def __init__(self, csv_path: str):
        """Initialize with path to eval_en.csv."""
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        
    def extract_json_examples(self, row) -> List[Dict[str, Any]]:
        """Extract JSON examples from a rule row."""
        examples = []
        
        # Extract Example 1 and Example 2 columns
        for col in ['Example 1', 'Example 2']:
            if col in self.df.columns and pd.notna(row[col]):
                example_text = str(row[col])
                # Extract JSON from markdown code blocks
                json_match = re.search(r'```\s*json\s*\n(.*?)\n```', example_text, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                        examples.append(json_data)
                    except json.JSONDecodeError:
                        continue
                        
        return examples
    
    def json_to_text(self, json_data: Dict[str, Any]) -> str:
        """Convert JSON data to JSON string for direct comparison."""
        # Return the JSON as a string for direct comparison with query JSON
        return json.dumps(json_data, sort_keys=True)
    
    def generate_training_data(self, min_examples_per_rule: int = 2) -> List[Dict[str, Any]]:
        """Generate training data from all rules."""
        training_data = []
        rules_with_insufficient_examples = []
        
        print("Generating English synthetic training data...")
        for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Processing rules"):
            rule_id = row['Rule']
            examples = self.extract_json_examples(row)
            
            rule_examples = []
            for example in examples:
                text = self.json_to_text(example)
                if text and text != "expense request":  # Skip empty examples
                    rule_examples.append({
                        'text': text,
                        'rule_id': rule_id,
                        'json_data': example
                    })
            
            # Check if we have enough examples
            if len(rule_examples) < min_examples_per_rule:
                rules_with_insufficient_examples.append((rule_id, len(rule_examples)))
                # Generate additional synthetic examples
                additional_examples = self._generate_additional_examples(rule_id, row, min_examples_per_rule - len(rule_examples))
                rule_examples.extend(additional_examples)
            
            training_data.extend(rule_examples)
        
        # Report rules with insufficient examples
        if rules_with_insufficient_examples:
            print(f"\nWarning: {len(rules_with_insufficient_examples)} rules had insufficient examples:")
            for rule_id, count in rules_with_insufficient_examples:
                print(f"  {rule_id}: {count} examples (generated additional)")
                    
        return training_data
    
    def _generate_additional_examples(self, rule_id: str, row: pd.Series, num_needed: int) -> List[Dict[str, Any]]:
        """Generate additional synthetic examples for rules with insufficient examples."""
        additional_examples = []
        
        # Get rule description for context
        rule_description = row.get('Expense item name\n(Name registered in Cloud Expenses)', '')
        
        # Generate variations based on rule type
        for i in range(num_needed):
            # Create a synthetic example based on rule description
            synthetic_text = self._create_synthetic_example(rule_id, rule_description, i)
            if synthetic_text:
                additional_examples.append({
                    'text': synthetic_text,
                    'rule_id': rule_id,
                    'json_data': {}  # No original JSON data for synthetic examples
                })
        
        return additional_examples
    
    def _create_synthetic_example(self, rule_id: str, rule_description: str, variation: int) -> str:
        """Create a synthetic JSON example based on rule description."""
        import random
        
        # Generate JSON examples that match the test data format
        if "train" in rule_description.lower() or "bus" in rule_description.lower():
            examples = [
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-07",
                    "trip_end_date": "2025-09-07",
                    "origin": "Tokyo",
                    "destination": "Shinjuku",
                    "transport_mode": "Train",
                    "fare_amount": str(500 + variation * 100),
                    "receipt_number": "not applicable"
                },
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-08",
                    "trip_end_date": "2025-09-08",
                    "origin": "Osaka",
                    "destination": "Kyoto",
                    "transport_mode": "Bus",
                    "fare_amount": str(300 + variation * 50),
                    "receipt_number": "not applicable"
                }
            ]
        elif "shinkansen" in rule_description.lower() or "flight" in rule_description.lower():
            examples = [
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-07",
                    "trip_end_date": "2025-09-07",
                    "origin": "Tokyo",
                    "destination": "Osaka",
                    "transport_mode": "Shinkansen",
                    "fare_amount": str(15000 + variation * 2000),
                    "receipt_number": "not applicable"
                },
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-08",
                    "trip_end_date": "2025-09-08",
                    "origin": "Tokyo",
                    "destination": "Fukuoka",
                    "transport_mode": "Flight",
                    "fare_amount": str(25000 + variation * 3000),
                    "receipt_number": "not applicable"
                }
            ]
        elif "taxi" in rule_description.lower():
            examples = [
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-07",
                    "trip_end_date": "2025-09-07",
                    "origin": "Office",
                    "destination": "Client Office",
                    "transport_mode": "Taxi",
                    "fare_amount": str(3000 + variation * 500),
                    "receipt_number": "not applicable"
                }
            ]
        elif "conference" in rule_description.lower() or "meeting" in rule_description.lower():
            examples = [
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-07",
                    "trip_end_date": "2025-09-07",
                    "event_type": "Conference",
                    "event_name": "Business Conference",
                    "registration_fee": str(50000 + variation * 10000),
                    "receipt_number": "not applicable"
                }
            ]
        elif "meal" in rule_description.lower() or "dining" in rule_description.lower():
            examples = [
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-07",
                    "trip_end_date": "2025-09-07",
                    "meal_type": "Business Meal",
                    "participants": "Client",
                    "amount": str(8000 + variation * 1000),
                    "receipt_number": "not applicable"
                }
            ]
        else:
            # Generic business expense
            examples = [
                {
                    "employee_id": f"JP{random.randint(100, 999)}",
                    "trip_start_date": "2025-09-07",
                    "trip_end_date": "2025-09-07",
                    "expense_type": "Business Expense",
                    "description": "Work-related expense",
                    "amount": str(5000 + variation * 1000),
                    "receipt_number": "not applicable"
                }
            ]
        
        selected_example = examples[variation % len(examples)]
        return json.dumps(selected_example, sort_keys=True)
    
    def save_training_data(self, output_path: str):
        """Save training data to JSON file."""
        training_data = self.generate_training_data()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
            
        print(f"Generated {len(training_data)} training examples")
        print(f"Saved to {output_path}")
        
        # Print statistics
        rule_counts = {}
        for item in training_data:
            rule_id = item['rule_id']
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
            
        print(f"\nExamples per rule:")
        for rule_id, count in sorted(rule_counts.items()):
            print(f"  {rule_id}: {count} examples")


