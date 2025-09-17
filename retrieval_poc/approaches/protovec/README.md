# Protovec - Prototype Network Rule Classifier

Uses sentence transformers to create prototype vectors for each rule, then classifies queries by similarity.

## Usage

```python
from protovec_retriever import ProtovecRetriever

# Create retriever (auto-generates training data)
retriever = ProtovecRetriever(data, retrieval_size=3)

# Query
results = retriever.retrieve("Train from Tokyo to Shinjuku, 500 yen")
```

## Key Features

- **No retraining**: Add new rules with just examples
- **Auto-detection**: Works with both English and Japanese data
- **Fast inference**: Pre-computed prototype vectors

## Files

- `protovec_retriever.py` - Main implementation
- `synthetic_data_generator.py` - English training data
- `japanese_synthetic_data_generator.py` - Japanese training data

## Integration

Runs automatically with `make run-all` alongside other retrievers.
