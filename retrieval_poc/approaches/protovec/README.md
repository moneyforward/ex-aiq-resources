# Protovec - Prototype Network Rule Classifier

Uses sentence transformers to create prototype vectors (protovecs) for each rule, then classifies queries by similarity.

## Usage

```python
from protovec_retriever import ProtovecRetriever

# Create retriever (auto-generates training data)
retriever = ProtovecRetriever(data, retrieval_size=3)

# Query (supports both JSON and natural language)
results = retriever.retrieve('{"origin": "Tokyo", "destination": "Shinjuku", "transport_mode": "Train"}')
# or
results = retriever.retrieve("Train from Tokyo to Shinjuku, 500 yen")
```

## Key Features

- **No retraining**: Add new rules with just examples
- **Auto-detection**: Works with both English and Japanese data
- **JSON Support**: Handles markdown-wrapped JSON queries automatically
- **Fast inference**: Pre-computed prototype vectors
- **Data Leakage Prevention**: Uses filtered training data (excludes test examples)

## Files

- `protovec_retriever.py` - Main implementation with JSON extraction
- `synthetic_data_generator.py` - English training data (JSON format)
- `japanese_synthetic_data_generator.py` - Japanese training data (train station codes)

## Integration

Runs automatically with `make run-all` alongside other retrievers.
