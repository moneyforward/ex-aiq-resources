| Retriever     |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:--------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| Elasticsearch |   1 |          0.3      |        0.164062  |           0.164062  |          0.164062  |     0.164062  |          0.164062  |      0.164062  |                0.15625   |
| Protovec      |   1 |          0.225    |        0.0703125 |           0.0703125 |          0.0703125 |     0.0703125 |          0.0703125 |      0.0703125 |                0.15625   |
| Random        |   1 |          0.203125 |        0.015625  |           0.015625  |          0.015625  |     0.015625  |          0.015625  |      0.015625  |                0.046875  |
| BM25Okapi     |   1 |          0.198438 |        0.03125   |           0.03125   |          0.03125   |     0.03125   |          0.03125   |      0.03125   |                0.132812  |
| BM25L         |   1 |          0.198438 |        0.03125   |           0.03125   |          0.03125   |     0.03125   |          0.03125   |      0.03125   |                0.132812  |
| BM25Plus      |   1 |          0.198438 |        0.03125   |           0.03125   |          0.03125   |     0.03125   |          0.03125   |      0.03125   |                0.132812  |
| Elasticsearch |   3 |          0.308854 |        0.3125    |           0.104167  |          0.15625   |     0.229167  |          0.164062  |      0.229167  |                0.161458  |
| Protovec      |   3 |          0.224479 |        0.132812  |           0.0442708 |          0.0664062 |     0.0989583 |          0.0703125 |      0.0989583 |                0.179687  |
| BM25Okapi     |   3 |          0.209635 |        0.078125  |           0.0260417 |          0.0390625 |     0.0533854 |          0.03125   |      0.0533854 |                0.114583  |
| BM25L         |   3 |          0.209635 |        0.078125  |           0.0260417 |          0.0390625 |     0.0533854 |          0.03125   |      0.0533854 |                0.114583  |
| BM25Plus      |   3 |          0.209635 |        0.078125  |           0.0260417 |          0.0390625 |     0.0533854 |          0.03125   |      0.0533854 |                0.114583  |
| Random        |   3 |          0.201302 |        0.03125   |           0.0104167 |          0.015625  |     0.0195312 |          0.0078125 |      0.0195312 |                0.0520833 |
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
