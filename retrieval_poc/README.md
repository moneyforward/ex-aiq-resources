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

• **BM25Okapi**: Classic BM25 algorithm for text similarity matching
• **BM25L**: BM25 variant with length normalization improvements
• **BM25Plus**: BM25 variant with better term frequency handling
• **ButlerAI**: AI-powered classification using external API service (disabled due to idev instability)
• **Random**: Baseline random retrieval for comparison
• **Dense**: Dense vector embeddings (not implemented)
• **RAG**: Retrieval-Augmented Generation (not implemented)

## Run Evaluation

```bash
make run
```

## Results

Results are saved to `approaches/comparison_table.md`
