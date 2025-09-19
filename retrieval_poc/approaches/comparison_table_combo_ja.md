| Retriever           |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:--------------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| Dense+Text2SQL      |   1 |          1        |         1        |            1        |           1        |      1        |           1        |       1        |                 0        |
| Dense+Text2SQL+BM25 |   1 |          0.727273 |         0.727273 |            0.727273 |           0.727273 |      0.727273 |           0.727273 |       0.727273 |                 0.272727 |
| Dense+BM25          |   1 |          0.636364 |         0.636364 |            0.636364 |           0.636364 |      0.636364 |           0.636364 |       0.636364 |                 0.363636 |
| Dense+Text2SQL+BM25 |   3 |          0.706061 |         1        |            0.333333 |           0.5      |      0.863636 |           1        |       0.863636 |                 0.333333 |
| Dense+BM25          |   3 |          0.684848 |         1        |            0.333333 |           0.5      |      0.818182 |           1        |       0.818182 |                 0.393939 |
| Dense+Text2SQL      |   3 |          0.684848 |         1        |            0.333333 |           0.5      |      1        |           1        |       1        |                 0.575758 |
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
