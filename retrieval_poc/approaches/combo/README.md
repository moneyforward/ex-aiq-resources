# Combo Retrievers

This module contains combination retrievers that fuse multiple retrieval approaches using LlamaIndex's `QueryFusionRetriever` with reciprocal rerank fusion, as described in the [LlamaIndex documentation](https://developers.llamaindex.ai/python/examples/retrievers/reciprocal_rerank_fusion/).

## Available Combinations

### 1. DenseText2SQLRetriever
**Combines:** Dense Retrieval + Text2SQL
- **Dense Retrieval**: Semantic understanding via embeddings
- **Text2SQL**: Structured reasoning via SQL generation
- **Expected Benefits**: High recall from Dense + precision from Text2SQL

### 2. DenseBM25Retriever  
**Combines:** Dense Retrieval + BM25
- **Dense Retrieval**: Semantic understanding via embeddings
- **BM25**: Keyword-based matching and ranking
- **Expected Benefits**: Cross-language robustness, semantic + keyword matching

### 3. DenseText2SQLBM25Retriever
**Combines:** Dense Retrieval + Text2SQL + BM25
- **All three approaches** combined for maximum coverage
- **Expected Benefits**: Best of all worlds - recall, precision, and keyword robustness

## How It Works

Each combo retriever uses LlamaIndex's `QueryFusionRetriever` which:

1. **Generates multiple queries** from the original query (default: 4 queries)
2. **Runs each query** through all individual retrievers
3. **Applies reciprocal rerank fusion** to combine and re-rank results
4. **Returns top-k results** based on the fusion scores

## Usage

```python
from approaches.combo import (
    DenseText2SQLRetriever,
    DenseBM25Retriever,
    DenseText2SQLBM25Retriever
)

# Initialize with your data
retriever = DenseText2SQLRetriever(data, retrieval_size=3)

# Retrieve results
results = retriever.retrieve(query)

# Get individual results for analysis
individual_results = retriever.get_individual_results(query)
```

## Performance Expectations

Based on the analysis of individual retrievers:

| Combination | Expected English k=3 | Expected Japanese k=3 | Key Benefits |
|-------------|---------------------|----------------------|--------------|
| Dense + Text2SQL | 0.45-0.50 | 0.70-0.75 | Precision + Recall |
| Dense + BM25 | 0.40-0.45 | 0.75-0.80 | Cross-language robustness |
| All Three | 0.50-0.55 | 0.80-0.85 | Maximum coverage |

## Configuration

- **num_queries**: Number of queries to generate (default: 4)
- **retrieval_size**: Number of results to return (default: 3)
- **mode**: Fusion mode (default: "reciprocal_rerank")
- **use_async**: Whether to use async processing (default: True)

## Dependencies

- `llama-index-retrievers-bm25`: For BM25 retrieval
- `llama-index-core`: For QueryFusionRetriever
- Azure OpenAI: For LLM-based query generation
