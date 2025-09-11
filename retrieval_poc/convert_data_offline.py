#!/usr/bin/env python3
"""
Offline conversion of JSON evaluation data to natural language
"""

import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

def convert_json_to_natural_language(json_str, azure_client, deployment_name):
    """Convert JSON expense data to natural language using Azure OpenAI"""
    try:
        # Parse JSON to extract key information
        expense_data = json.loads(json_str)
        
        # Create a natural language description using Azure OpenAI
        prompt = (
            f"Convert this expense JSON data into a natural language "
            f"description that would help classify it into the appropriate "
            f"expense rule:\n\nJSON Data:\n{json.dumps(expense_data, indent=2)}\n\n"
            f"Please create a clear, concise natural language description "
            f"that captures:\n1. What type of expense this is\n"
            f"2. Key details like amounts, dates, locations, participants\n"
            f"3. The purpose or context of the expense\n\n"
            f"Focus on the most important details that would help determine "
            f"the correct expense rule from a rulebook. Keep it under 100 words."
        )

        response = azure_client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert at converting structured expense data "
                        "into natural language descriptions for expense "
                        "classification."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        natural_language = response.choices[0].message.content.strip()
        return natural_language
        
    except Exception as e:
        print(f"Warning: Failed to convert JSON to natural language: {e}")
        return json_str  # Return original JSON if conversion fails

def main():
    """Convert all evaluation data offline"""
    print("🔄 Starting offline conversion of evaluation data")
    print("=" * 60)
    
    # Set up Azure OpenAI client
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
    azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4.1-mini')
    
    if not azure_endpoint or not azure_api_key:
        print("❌ Azure OpenAI credentials not found in .env file")
        return
    
    azure_client = AzureOpenAI(
        api_key=azure_api_key,
        api_version="2024-02-15-preview",
        azure_endpoint=azure_endpoint
    )
    
    # Load evaluation data
    eval_file = 'data/eval_en.csv'
    if not os.path.exists(eval_file):
        print(f"❌ Evaluation file not found: {eval_file}")
        return
    
    print(f"📊 Loading evaluation data from {eval_file}")
    df = pd.read_csv(eval_file)
    print(f"Found {len(df)} examples to convert")
    
    # Convert each example
    converted_data = []
    
    for idx, row in df.iterrows():
        print(f"Converting {idx + 1}/{len(df)}: {row['rule_id']}")
        
        # Extract JSON from the query
        query = row['query']
        json_match = None
        
        # Try to find JSON in the query
        import re
        json_match = re.search(r'```\s*json\s*\n(.*?)\n```', query, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).strip()
            # Convert to natural language
            natural_language = convert_json_to_natural_language(
                json_str, azure_client, azure_deployment
            )
            
            # Create new row with converted query
            new_row = row.copy()
            new_row['query'] = natural_language
            new_row['original_query'] = query  # Keep original for reference
            converted_data.append(new_row)
            
            print(f"  ✅ Converted: {natural_language[:80]}...")
        else:
            # No JSON found, keep original
            new_row = row.copy()
            new_row['original_query'] = query
            converted_data.append(new_row)
            print("  ⚠️  No JSON found, keeping original")
    
    # Save converted data
    converted_df = pd.DataFrame(converted_data)
    output_file = 'data/eval_en_natural_language.csv'
    converted_df.to_csv(output_file, index=False)
    
    print("\n✅ Conversion complete!")
    print(f"📁 Saved {len(converted_data)} examples to {output_file}")
    print("📊 Original queries preserved in 'original_query' column")
    
    # Show sample conversions
    print("\n📋 Sample conversions:")
    for i in range(min(3, len(converted_data))):
        row = converted_data[i]
        print(f"\nExample {i+1} ({row['rule_id']}):")
        print(f"Original: {row['original_query'][:100]}...")
        print(f"Converted: {row['query'][:100]}...")

if __name__ == "__main__":
    main()
