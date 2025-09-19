| Retriever           |   k |   Composite Score |   Average Recall |   Average Precision |   Average F1 Score |   Average MRR |   Average Hit Rate |   Average nDCG |   Average Confusion Rate |
|:--------------------|----:|------------------:|-----------------:|--------------------:|-------------------:|--------------:|-------------------:|---------------:|-------------------------:|
| Dense+Text2SQL+BM25 |   1 |          0.525    |         0.460938 |            0.460938 |           0.460938 |      0.460938 |           0.460938 |       0.460938 |                 0.21875  |
| Dense+BM25          |   1 |          0.492188 |         0.421875 |            0.421875 |           0.421875 |      0.421875 |           0.421875 |       0.421875 |                 0.226562 |
| Dense+Text2SQL      |   1 |          0.478125 |         0.398438 |            0.398438 |           0.398438 |      0.398438 |           0.398438 |       0.398438 |                 0.203125 |
| Dense+Text2SQL+BM25 |   3 |          0.521094 |         0.679688 |            0.226562 |           0.339844 |      0.550781 |           0.679688 |       0.550781 |                 0.304688 |
| Dense+BM25          |   3 |          0.507292 |         0.65625  |            0.21875  |           0.328125 |      0.520833 |           0.65625  |       0.520833 |                 0.296875 |
| Dense+Text2SQL      |   3 |          0.492969 |         0.632812 |            0.210938 |           0.316406 |      0.498698 |           0.632812 |       0.498698 |                 0.299479 |
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
