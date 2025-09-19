# Retrieval POC

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Create `.env` file with required API keys:
```
BUTLERAI_ENDPOINT=your_butlerai_endpoint
BUTLERAI_API_KEY=your_butlerai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1-mini
```

## Approaches

### Individual Retrievers
• **BM25Okapi**: Classic BM25 algorithm for text similarity matching
• **BM25L**: BM25 variant with length normalization improvements
• **BM25Plus**: BM25 variant with better term frequency handling
• **Elasticsearch**: Full-text search using Elasticsearch with Japanese text analysis
• **Protovec**: Prototype network using sentence transformers for rule classification
• **ButlerAI**: AI-powered classification using external API service (disabled due to idev instability)
• **Random**: Baseline random retrieval for comparison
• **Dense**: Dense vector embeddings using sentence transformers
• **Text2SQL**: Retrieval-Augmented Generation using SQL generation for structured reasoning

### Combination Retrievers
• **Dense+BM25**: Combines semantic understanding (Dense) with keyword matching (BM25) using reciprocal rerank fusion
• **Dense+Text2SQL**: Combines semantic understanding (Dense) with structured reasoning (Text2SQL) using reciprocal rerank fusion
• **Dense+Text2SQL+BM25**: Combines all three approaches (Dense, Text2SQL, BM25) using reciprocal rerank fusion for maximum coverage

## Datasets

### English Synthetic (`eval_en_synth.py`)
- **Rules**: 64 English expense rules from `data/eval_en.csv`
- **Queries**: 128 synthetic examples (2 per rule) from `data/eval_en_natural_language.csv`
- **Purpose**: Test retrieval on synthetic, well-structured English data

### Japanese Real Data (`eval_ja.py`)
- **Rules**: 64 Japanese expense rules from `data/eval_ja.csv`
- **Queries**: 11 real expense entries from `data/sample_category_check_request.json`
- **Ground Truth**: Manual annotations in `data/ja_labels.csv`
- **Purpose**: Test retrieval on real-world Japanese expense data

## Run Evaluation

### Run All Evaluations (Recommended)
```bash
make run-all
```
This will start Elasticsearch and run both English and Japanese evaluations with all retrievers.

### Individual Evaluations
```bash
# English synthetic data only
make run-en-synth

# Japanese real data only  
make run-ja

# Combo retrievers on English synthetic data
make run-combo-en-synth

# Combo retrievers on Japanese real data
make run-combo-ja

# All combo retriever evaluations
make run-combo-all
```

### Elasticsearch Management
```bash
# Start Elasticsearch
make es-start

# Stop Elasticsearch
make es-stop

# Check Elasticsearch status
make es-status

# View Elasticsearch logs
make es-logs

# Clean Elasticsearch data
make es-clean
```

### Check Results
```bash
make check-results
```

## Elasticsearch Setup

The Elasticsearch retriever uses Docker to run a local Elasticsearch instance. The setup includes:

- **Docker Compose**: Configured in `docker-compose.yml`
- **Japanese Text Analysis**: Uses standard analyzer with wildcard matching for Japanese text
- **Configurable Column Mapping**: Supports different dataset structures
- **Automatic Management**: Started automatically with `make run-all`

For detailed setup instructions, see `ELASTICSEARCH_SETUP.md`.

## Results

### Individual Retriever Results
- English synthetic results: `approaches/comparison_table_en_synth.md`
- Japanese real data results: `approaches/comparison_table_ja.md`

### Combination Retriever Results
- Combo retrievers on English synthetic data: `approaches/comparison_table_combo_en_synth.md`
- Combo retrievers on Japanese real data: `approaches/comparison_table_combo_ja.md`
