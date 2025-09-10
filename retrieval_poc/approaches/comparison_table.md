| Retriever   |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| BM25Okapi   |   1 |          0.979167 |        1         |           1         |          1         |     1         |          1         |      1         |                0.208333  |
| BM25Plus    |   1 |          0.976823 |        1         |           1         |          1         |     1         |          1         |      1         |                0.231771  |
| BM25L       |   1 |          0.941667 |        0.960938  |           0.960938  |          0.960938  |     0.980469  |          0.960938  |      0.980469  |                0.251302  |
| Random      |   1 |          0.104036 |        0.0078125 |           0.0078125 |          0.0078125 |     0.0247396 |          0.0078125 |      0.0247396 |                0.046875  |
| BM25Okapi   |   3 |          0.745833 |        1         |           0.333333  |          0.5       |     1         |          1         |      1         |                0.208333  |
| BM25Plus    |   3 |          0.74349  |        1         |           0.333333  |          0.5       |     1         |          1         |      1         |                0.231771  |
| BM25L       |   3 |          0.727865 |        1         |           0.333333  |          0.5       |     0.980469  |          0.960938  |      0.980469  |                0.251302  |
| Random      |   3 |          0.109245 |        0.046875  |           0.015625  |          0.0234375 |     0.0221354 |          0         |      0.0221354 |                0.0546875 |
<br>

## Composite Score Calculation

The composite score is calculated using the following formula:

$$ \text{{Composite Score}} = \frac{{(R \times W_R + P \times W_P + F1 \times W_{F1} + MRR \times W_{MRR} + HR \times W_{HR} + nDCG \times W_{nDCG} + (1 - CR) \times W_{CR})}}{{\sum W}} $$

### Legend

- **R**: Average Recall (Weight: 0.05)
- **P**: Average Precision (Weight: 0.05)
- **F1**: Average F1 Score (Weight: 0.4)
- **MRR**: Average Mean Reciprocal Rank (Weight: 0.05)
- **HR**: Average Hit Rate (Weight: 0.3)
- **nDCG**: Average Normalized Discounted Cumulative Gain (Weight: 0.05)
- **1 - CR**: Inverted Average Confusion Rate (Weight: 0.1)
- We divide everything by the sum of the weights to normalize the score.

### Explanation of Components

- **Average Recall**:
  The proportion of relevant items that were retrieved.
- **Average Precision**:
  The proportion of retrieved items that are relevant.
- **Average F1 Score**:
  The harmonic mean of precision and recall.
- **Average MRR (Mean Reciprocal Rank)**:
  The average of the reciprocal ranks of the first relevant item.
- **Average Hit Rate**:
  The proportion of queries for which the first retrieved
  item is relevant.
- **Average nDCG (Normalized Discounted Cumulative Gain)**:
  A measure of ranking quality.
- **Inverted Average Confusion Rate**:
  The proportion of retrieved items that are not distractors,
  positively weighted.
