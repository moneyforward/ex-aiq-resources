#!/usr/bin/env python3
"""
Convert instructions to natural language format for ButlerAI
"""

import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

def convert_rule_to_natural_language(
    rule_id, rule_description, azure_client, deployment_name
):
    """Convert a rule description to natural language format"""
    try:
        prompt = (
            f"Convert this expense rule description into a natural language "
            f"format that would help classify expense descriptions:\n\n"
            f"Rule ID: {rule_id}\nRule Description: {rule_description}\n\n"
            f"Please create a clear, concise natural language description "
            f"that captures:\n1. What type of expense this rule covers\n"
            f"2. Key characteristics and requirements\n"
            f"3. Specific conditions or limitations\n\n"
            f"Focus on the most important details that would help determine "
            f"if an expense matches this rule. Keep it under 100 words."
        )


        response = azure_client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert at converting expense rules into "
                        "natural language descriptions for expense classification."
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
        print(f"Warning: Failed to convert rule {rule_id} to natural language: {e}")
        return rule_description  # Return original if conversion fails

def main():
    """Convert all instructions to natural language format"""
    print("🔄 Converting instructions to natural language format")
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
    
    # Load original instructions
    instructions_file = 'data/instructions.json'
    if not os.path.exists(instructions_file):
        print(f"❌ Instructions file not found: {instructions_file}")
        return
    
    with open(instructions_file, 'r') as f:
        original_instructions = json.load(f)
    
    print(f"📊 Loaded {len(original_instructions)} original instructions")
    
    # Convert each instruction to natural language
    natural_language_instructions = {}
    
    for rule_id, rule_description in original_instructions.items():
        print(f"Converting {rule_id}...")
        
        # Convert to natural language
        natural_language = convert_rule_to_natural_language(
            rule_id, rule_description, azure_client, azure_deployment
        )
        natural_language_instructions[rule_id] = natural_language
        
        print(f"  ✅ Converted: {natural_language[:80]}...")
    
    # Save converted instructions
    output_file = 'data/instructions_natural_language.json'
    with open(output_file, 'w') as f:
        json.dump(natural_language_instructions, f, indent=2)
    
    print("\n✅ Conversion complete!")
    print(
        f"📁 Saved {len(natural_language_instructions)} natural language "
        f"instructions to {output_file}"
    )
    
    # Show sample conversions
    print("\n📋 Sample conversions:")
    for i, (rule_id, description) in enumerate(
        list(natural_language_instructions.items())[:3]
    ):
        print(f"\nExample {i+1} ({rule_id}):")
        print(f"Original: {original_instructions[rule_id][:100]}...")
        print(f"Converted: {description[:100]}...")

if __name__ == "__main__":
    main()
