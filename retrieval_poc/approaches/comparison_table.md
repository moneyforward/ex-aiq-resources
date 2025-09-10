| Retriever   |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| BM25Okapi   |   1 |       0.780303    |        1         |           1         |          1         |     1         |          1         |      1         |                0.208333  |
| BM25Plus    |   1 |       0.776042    |        1         |           1         |          1         |     1         |          1         |      1         |                0.231771  |
| BM25L       |   1 |       0.742306    |        0.960938  |           0.960938  |          0.960938  |     0.980469  |          0.960938  |      0.980469  |                0.251302  |
| Random      |   1 |      -0.000591856 |        0.0078125 |           0.0078125 |          0.0078125 |     0.0247396 |          0.0078125 |      0.0247396 |                0.046875  |
| BM25Okapi   |   3 |       0.522727    |        1         |           0.333333  |          0.5       |     1         |          1         |      1         |                0.208333  |
| BM25Plus    |   3 |       0.518466    |        1         |           0.333333  |          0.5       |     1         |          1         |      1         |                0.231771  |
| BM25L       |   3 |       0.506037    |        1         |           0.333333  |          0.5       |     0.980469  |          0.960938  |      0.980469  |                0.251302  |
| Random      |   3 |       0.00556345  |        0.046875  |           0.015625  |          0.0234375 |     0.0221354 |          0         |      0.0221354 |                0.0546875 |
<br>

## Composite Score Calculation

The composite score is calculated using the following formula:

$$ \text{{Composite Score}} = \frac{{(R \times W_R + P \times W_P + F1 \times W_{F1} + MRR \times W_{MRR} + HR \times W_{HR} + nDCG \times W_{nDCG} + CR \times W_{CR})}}{{\sum W}} $$

### Legend

- **R**: Average Recall (Weight: 0.5)
- **P**: Average Precision (Weight: 0.5)
- **F1**: Average F1 Score (Weight: 5.0)
- **MRR**: Average Mean Reciprocal Rank (Weight: 0.5)
- **HR**: Average Hit Rate (Weight: 2.0)
- **nDCG**: Average Normalized Discounted Cumulative Gain (Weight: 0.5)
- **CR**: Average Confusion Rate (Weight: -2.0)
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
- **Average Confusion Rate**:
  The proportion of retrieved items that are distractors,
  negatively weighted.
