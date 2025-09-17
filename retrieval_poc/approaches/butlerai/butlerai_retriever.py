import json
import os
import re
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI
from ..base_retriever import BaseRetriever


class ButlerAIRetriever(BaseRetriever):
    def __init__(self, data=None, retrieval_size=3, api_endpoint=None, 
                 api_key=None, instructions_file=None):
        super().__init__(data, retrieval_size)

        # Load environment variables
        load_dotenv()
        
        # Set up API configuration
        self.api_endpoint = api_endpoint or os.getenv('BUTLERAI_ENDPOINT')
        self.api_key = api_key or os.getenv('BUTLERAI_API_KEY')
        
        if not self.api_endpoint:
            raise ValueError(
                "ButlerAI endpoint not provided. Set BUTLERAI_ENDPOINT in .env "
                "file or pass api_endpoint parameter."
            )
        
        # Load instructions from JSON file
        self.instructions_file = instructions_file or 'data/instructions.json'
        self.instructions = self._load_instructions()
        
        # Load pre-converted natural language data if available
        self.natural_language_data = self._load_natural_language_data()
        
        # Set up Azure OpenAI client for JSON-to-natural-language conversion
        self.azure_openai_client = None
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        azure_deployment = os.getenv(
            'AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4.1-mini'
        )
        
        if azure_endpoint and azure_api_key:
            self.azure_openai_client = AzureOpenAI(
                api_key=azure_api_key,
                api_version="2024-02-15-preview",
                azure_endpoint=azure_endpoint
            )
            self.azure_deployment = azure_deployment
        
        # Set up HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })

    def _load_instructions(self) -> Dict[str, str]:
        """Load instructions from JSON file"""
        try:
            # Try to load from the specified file path
            if os.path.exists(self.instructions_file):
                with open(self.instructions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Try to load from the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, '..', '..')
            instructions_path = os.path.join(project_root, self.instructions_file)
            if os.path.exists(instructions_path):
                with open(instructions_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Try to load from the data directory relative to project root
            data_instructions_path = os.path.join(
                project_root, 'data', 'instructions.json'
            )
            if os.path.exists(data_instructions_path):
                with open(data_instructions_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback to data parameter if provided
            if self.data:
                return self._create_instructions_from_data()
            
            raise FileNotFoundError(
                f"Instructions file '{self.instructions_file}' not found"
            )
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load instructions from file: {e}")
            # Fallback to data parameter if provided
            if self.data:
                return self._create_instructions_from_data()
            return {}

    def _create_instructions_from_data(self) -> Dict[str, str]:
        """Convert the data into instructions format for ButlerAI API"""
        instructions = {}
        
        if hasattr(self.data, 'iterrows'):
            # If data is a pandas DataFrame
            for _, row in self.data.iterrows():
                if 'rule_id' in row and 'description' in row:
                    instructions[row['rule_id']] = row['description']
        elif isinstance(self.data, list):
            # If data is a list of dictionaries
            for item in self.data:
                if (isinstance(item, dict) and 'rule_id' in item 
                    and 'description' in item):
                    instructions[item['rule_id']] = item['description']
        elif isinstance(self.data, dict):
            # If data is already in instructions format
            instructions = self.data
        
        return instructions

    def _load_natural_language_data(self) -> Optional[Dict[str, str]]:
        """Load pre-converted natural language data if available"""
        try:
            import pandas as pd
            natural_lang_file = 'data/eval_en_natural_language.csv'
            
            if os.path.exists(natural_lang_file):
                df = pd.read_csv(natural_lang_file)
                # Create a mapping from original query to natural language query
                natural_lang_map = {}
                for _, row in df.iterrows():
                    if 'original_query' in row and 'query' in row:
                        natural_lang_map[row['original_query']] = row['query']
                
                print(
                    f"✅ Loaded {len(natural_lang_map)} pre-converted "
                    f"natural language examples"
                )
                return natural_lang_map
            else:
                print(
                    "ℹ️  No pre-converted natural language data found, "
                    "will use real-time conversion"
                )
                return None
                
        except Exception as e:
            print(f"Warning: Failed to load natural language data: {e}")
            return None

    def _convert_json_to_natural_language(self, query: str) -> str:
        """Convert JSON expense data to natural language description"""
        # First, check if we have pre-converted data
        if self.natural_language_data and query in self.natural_language_data:
            print("🔄 Using pre-converted natural language")
            return self.natural_language_data[query]
        
        # Check if the query contains JSON data
        json_match = re.search(
            r'```\s*json\s*\n(.*?)\n```', query, re.DOTALL
        )
        if not json_match:
            return query  # Return original query if no JSON found
        
        json_str = json_match.group(1).strip()
        
        # If Azure OpenAI is not available, return original query
        if not self.azure_openai_client:
            return query
        
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

            response = self.azure_openai_client.chat.completions.create(
                model=self.azure_deployment,
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
            print(f"🔄 Converted JSON to natural language: {natural_language}")
            return natural_language
            
        except Exception as e:
            print(f"Warning: Failed to convert JSON to natural language: {e}")
            return query  # Return original query if conversion fails

    def _create_payload(self, query: str) -> Dict[str, Any]:
        """Create the payload for ButlerAI API request"""
        payload = {
            "instructions": self.instructions,
            "conversation": [
                {
                    "content": query,
                    "origin": "USER",
                    "kind": "QUERY",
                    "created_at": datetime.now().isoformat(),
                    "streaming_status": "thread.message.delta"
                }
            ]
        }
        
        # Debug: Print the payload being sent
        print("🔍 ButlerAI Payload:")
        print(f"Query: {query}")
        print(f"Instructions count: {len(self.instructions)}")
        print("Sample instructions:")
        for i, (rule_id, desc) in enumerate(list(self.instructions.items())[:3]):
            print(f"  {rule_id}: {desc[:100]}...")
        
        return payload

    def _make_api_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request to ButlerAI endpoint"""
        try:
            # Add log_level as query parameter as shown in the curl template
            url = f"{self.api_endpoint}?log_level=INFO"
            
            print("🚀 Sending request to ButlerAI...")
            print(f"📡 URL: {url}")
            print("⏱️  Timeout: 120 seconds")
            print(
                "🔄 ButlerAI is processing your request "
                "(this may take 1-2 minutes)..."
            )
            
            response = self.session.post(
                url,
                json=payload,
                timeout=120  # 2 minutes for slow ButlerAI processing
            )
            
            print(
                f"✅ ButlerAI responded with status: {response.status_code}"
            )
            response.raise_for_status()
            
            response_data = response.json()
            print(f"📊 Response keys: {list(response_data.keys())}")
            print(
                f"📝 Response status: {response_data.get('status', 'unknown')}"
            )
            
            return response_data
        except requests.exceptions.Timeout as e:
            print(
                f"⏰ ButlerAI request timed out after 120 seconds: {e}"
            )
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error making API request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            return None

    def _process_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process ButlerAI response and convert to retrieval format"""
        print("🔍 Processing ButlerAI response...")
        results = []
        logs = response.get('logs', [])
        print(f"📋 Found {len(logs)} log entries")
        
        # Handle direct classification (status: success)
        if response.get('status') == 'success':
            classification = response.get('classification')
            if classification and classification in self.instructions:
                confidence = self._extract_confidence_from_logs(logs, classification)
                results.append({
                    'rule_id': classification,
                    'description': self.instructions[classification],
                    'confidence': confidence,
                    'source': 'butlerai',
                    'logs': logs
                })
        
        # Handle followup case (status: followup) - extract highest confidence rules
        elif response.get('status') == 'followup':
            # Extract all confidence scores from logs
            confidence_scores = self._extract_all_confidence_scores(logs)
            
            # Sort by confidence and get top rules
            sorted_rules = sorted(
            confidence_scores.items(), key=lambda x: x[1], reverse=True
        )
            
            for rule_id, confidence in sorted_rules[:self.retrieval_size]:
                if rule_id in self.instructions and confidence > 0:
                    results.append({
                        'rule_id': rule_id,
                        'description': self.instructions[rule_id],
                        'confidence': confidence,
                        'source': 'butlerai',
                        'logs': logs,
                        'note': 'Multiple rules found - API requested clarification'
                    })
        
        return results

    def _extract_confidence_from_logs(self, logs: List[str], rule_id: str) -> int:
        """Extract confidence score for a specific rule from logs"""
        for log in logs:
            if 'Confidence from agents are' in log:
                try:
                    import re
                    confidence_match = re.search(
                        f"'{rule_id}': {{'confidence': (\\d+)", log
                    )
                    if confidence_match:
                        return int(confidence_match.group(1))
                except Exception:
                    pass
        return 0

    def _extract_all_confidence_scores(self, logs: List[str]) -> Dict[str, int]:
        """Extract all confidence scores from logs"""
        confidence_scores = {}
        
        for log in logs:
            if 'Confidence from agents are' in log:
                try:
                    import re
                    # Extract all rule confidence pairs - fixed pattern
                    pattern = r"'([^']+)': \{'confidence': (\d+)"
                    matches = re.findall(pattern, log)
                    for rule_id, confidence in matches:
                        confidence_scores[rule_id] = int(confidence)
                except Exception:
                    pass
        
        return confidence_scores

    def retrieve(self, query: str) -> List[str]:
        """Retrieve relevant rules using ButlerAI API"""
        if not query or not query.strip():
            return []
        
        # Convert JSON to natural language if needed
        processed_query = self._convert_json_to_natural_language(query)
        
        # Create payload
        payload = self._create_payload(processed_query)
        
        # Make API request
        response = self._make_api_request(payload)
        
        if not response:
            return []
        
        # Process response
        results = self._process_response(response)
        
        # Extract rule IDs and limit to retrieval_size
        rule_ids = [result['rule_id'] for result in results[:self.retrieval_size]]
        print(f"🎯 Retrieved {len(rule_ids)} rules: {rule_ids}")
        return rule_ids
