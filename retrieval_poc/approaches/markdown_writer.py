from textwrap import dedent

def write_composite_score_explanation(file_path):
    with open(file_path, 'a') as f:
        f.write(dedent(
            """
            <br>

            ## Composite Score Calculation

            The composite score is calculated using the following formula:
            
            """
        ))

        f.write(
            "$$ \\text{{Composite Score}} = \\frac{{(F1 \\times W_{F1}"
            "+ MRR \\times W_{MRR} + HR \\times W_{HR} "
            "+ nDCG \\times W_{nDCG} + (1 - CR) \\times W_{CR})}}{{\\sum W}} $$\n"
        )

        f.write(dedent(
            """
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
            """
        ))
