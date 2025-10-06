# Azure AI Search POC

Hybrid search (text + vector) for expense rule retrieval.

## Data Flow

```mermaid
sequenceDiagram
    participant EN as English Data
    participant JA as Japanese Data
    participant Indexer as Document Indexer
    participant Azure as Azure AI Search
    participant Retriever as Hybrid Retriever
    participant Eval as Evaluation

    EN->>Indexer: 64 rules (eval_en.csv)
    JA->>Indexer: 64 rules (eval_ja.csv)
    Indexer->>Azure: Index documents with vectors
    
    EN->>Eval: 128 synthetic JSON queries
    JA->>Eval: 11 real JSON queries
    
    Eval->>Retriever: JSON query
    Retriever->>Azure: Hybrid search (text + vector)
    Azure-->>Retriever: Ranked results
    Retriever-->>Eval: Retrieved rules
    Eval-->>EN: English metrics
    Eval-->>JA: Japanese metrics
```

### Dataset Differences

**English (en_synth)**:
- 64 unique expense rules
- 128 synthetic test queries (2 per rule)
- Index: `aiq-expense-rules-en`

**Japanese (ja)**:
- 64 unique expense rules  
- 11 real test queries
- Index: `aiq-expense-rules-ja`

## Setup

1. Copy `env.example` to `.env` and fill in Azure credentials
2. `poetry install`

## Usage

```bash
# Index documents
poetry run python src/index_documents.py --use-hybrid --dataset en
poetry run python src/index_documents.py --use-hybrid --dataset ja

# Run evaluation
poetry run python eval_azure_search.py --dataset en_synth
poetry run python eval_azure_search.py --dataset ja
```

## Results

- **English**: 34.4% recall@3, 28.0% nDCG, 15.5% confusion
- **Japanese**: 100.0% recall@3, 95.5% nDCG, 24.2% confusion

Results saved to `azure_search_results_*.md`.