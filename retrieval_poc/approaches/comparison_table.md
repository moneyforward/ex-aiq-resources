| Retriever   |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| BM25Okapi   |   1 |          0.958333 |        1         |           1         |          1         |     1         |          1         |      1         |                0.208333  |
| BM25Plus    |   1 |          0.953646 |        1         |           1         |          1         |     1         |          1         |      1         |                0.231771  |
| BM25L       |   1 |          0.91849  |        0.960938  |           0.960938  |          0.960938  |     0.960938  |          0.960938  |      0.960938  |                0.251302  |
| Random      |   1 |          0.196875 |        0.0078125 |           0.0078125 |          0.0078125 |     0.0078125 |          0.0078125 |      0.0078125 |                0.046875  |
| BM25Okapi   |   3 |          0.758333 |        1         |           0.333333  |          0.5       |     1         |          1         |      1         |                0.208333  |
| BM25Plus    |   3 |          0.753646 |        1         |           0.333333  |          0.5       |     1         |          1         |      1         |                0.231771  |
| BM25L       |   3 |          0.738021 |        1         |           0.333333  |          0.5       |     0.980469  |          0.960938  |      0.980469  |                0.251302  |
| Random      |   3 |          0.202865 |        0.046875  |           0.015625  |          0.0234375 |     0.0221354 |          0         |      0.0221354 |                0.0546875 |
<br>

## Composite Score Calculation

The composite score is calculated using the following formula:

$$ \text{{Composite Score}} = \frac{{(F1 \times W_{F1}+ MRR \times W_{MRR} + HR \times W_{HR} + nDCG \times W_{nDCG} + (1 - CR) \times W_{CR})}}{{\sum W}} $$

### Legend

- **F1**: Average F1 Score (Weight: 0.4)
- **MRR@k**: Average Mean Reciprocal Rank at cutoff k (Weight: 0.1)
- **HR**: Average Hit Rate (Weight: 0.2)
- **nDCG@k**: Average Normalized Discounted Cumulative Gain at cutoff k
  (Weight: 0.1)
- **1 - CR**: Inverted Average Confusion Rate (Weight: 0.2)
- We divide everything by the sum of the weights to normalize the score.

### Explanation of Components

- **Average F1 Score**:
  The harmonic mean of precision and recall.
- **Average MRR@k (Mean Reciprocal Rank at cutoff k)**:
  The average of the reciprocal ranks of the first relevant item within
  the top k results.
- **Average Hit Rate**:
  The proportion of queries for which the first retrieved
  item is relevant.
- **Average nDCG@k (Normalized Discounted Cumulative Gain at cutoff k)**:
  A measure of ranking quality within the top k results.
- **Inverted Average Confusion Rate**:
  The proportion of retrieved items that are not distractors,
  positively weighted.
