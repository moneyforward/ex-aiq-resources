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
        """Convert JSON data to natural language text."""
        text_parts = []
        
        # Key fields to emphasize
        key_fields = [
            'transport_mode', 'origin', 'destination', 'trip_start_date', 
            'trip_end_date', 'fare_amount', 'accommodation_name', 'accommodation_amount',
            'taxi_reason', 'taxi_destination', 'conference_name', 'meeting_name',
            'participant_names', 'participant_companies', 'meal_costs',
            'gift_type', 'recipient_name', 'recipient_company', 'gift_amount',
            'item_name', 'equipment_name', 'equipment_cost', 'service_type',
            'provider_name', 'amount', 'overseas_flag'
        ]
        
        # Build descriptive text
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
                    
        return " ".join(text_parts) if text_parts else "expense request"
    
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
        """Create a synthetic example based on rule description."""
        # Common patterns for different rule types
        if "train" in rule_description.lower() or "bus" in rule_description.lower():
            variations = [
                f"Local train travel from station A to station B for {500 + variation * 100} yen",
                f"Bus ride from city A to city B costing {300 + variation * 50} yen",
                f"Public transport from location A to location B for {400 + variation * 75} yen"
            ]
        elif "shinkansen" in rule_description.lower() or "flight" in rule_description.lower():
            variations = [
                f"Shinkansen travel from Tokyo to Osaka for {15000 + variation * 2000} yen",
                f"Flight from Tokyo to Fukuoka costing {25000 + variation * 3000} yen",
                f"High-speed transport from city A to city B for {20000 + variation * 2500} yen"
            ]
        elif "taxi" in rule_description.lower():
            variations = [
                f"Taxi ride for business meeting costing {3000 + variation * 500} yen",
                f"Taxi for emergency transport for {2500 + variation * 400} yen",
                f"Taxi service for client visit for {3500 + variation * 600} yen"
            ]
        elif "conference" in rule_description.lower() or "meeting" in rule_description.lower():
            variations = [
                f"Conference attendance fee for {50000 + variation * 10000} yen",
                f"Meeting expenses for {30000 + variation * 5000} yen",
                f"Seminar participation cost of {40000 + variation * 7500} yen"
            ]
        elif "meal" in rule_description.lower() or "dining" in rule_description.lower():
            variations = [
                f"Business meal with clients for {8000 + variation * 1000} yen",
                f"Client dining expense of {12000 + variation * 1500} yen",
                f"Business dinner for {6000 + variation * 800} yen"
            ]
        else:
            # Generic expense
            variations = [
                f"Business expense for {5000 + variation * 1000} yen",
                f"Work-related cost of {8000 + variation * 1500} yen",
                f"Business activity expense for {6000 + variation * 1200} yen"
            ]
        
        return variations[variation % len(variations)]
    
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


