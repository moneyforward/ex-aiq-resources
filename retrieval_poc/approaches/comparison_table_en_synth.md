| Retriever       |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:----------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| BM25Okapi       |   1 |          1        |         1        |           1         |           1        |     1         |          1         |      1         |                0         |
| BM25Plus        |   1 |          1        |         1        |           1         |           1        |     1         |          1         |      1         |                0         |
| BM25L           |   1 |          0.96875  |         0.960938 |           0.960938  |           0.960938 |     0.960938  |          0.960938  |      0.960938  |                0         |
| dense_retriever |   1 |          0.410938 |         0.3125   |           0.3125    |           0.3125   |     0.3125    |          0.3125    |      0.3125    |                0.195312  |
| Elasticsearch   |   1 |          0.3      |         0.164062 |           0.164062  |           0.164062 |     0.164062  |          0.164062  |      0.164062  |                0.15625   |
| Random          |   1 |          0.203125 |         0.015625 |           0.015625  |           0.015625 |     0.015625  |          0.015625  |      0.015625  |                0.046875  |
| BM25Okapi       |   3 |          0.758854 |         1        |           0.333333  |           0.5      |     1         |          1         |      1         |                0.205729  |
| BM25Plus        |   3 |          0.754167 |         1        |           0.333333  |           0.5      |     1         |          1         |      1         |                0.229167  |
| BM25L           |   3 |          0.738802 |         1        |           0.333333  |           0.5      |     0.980469  |          0.960938  |      0.980469  |                0.247396  |
| dense_retriever |   3 |          0.386458 |         0.484375 |           0.161458  |           0.242188 |     0.382812  |          0.3125    |      0.382812  |                0.247396  |
| Elasticsearch   |   3 |          0.308854 |         0.3125   |           0.104167  |           0.15625  |     0.229167  |          0.164062  |      0.229167  |                0.161458  |
| Random          |   3 |          0.201302 |         0.03125  |           0.0104167 |           0.015625 |     0.0195312 |          0.0078125 |      0.0195312 |                0.0520833 |
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
