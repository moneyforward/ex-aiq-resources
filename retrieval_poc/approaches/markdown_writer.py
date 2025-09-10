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
            "$$ \\text{{Composite Score}} = \\frac{{(R \\times W_R + P \\times W_P "
            "+ F1 \\times W_{F1} + MRR \\times W_{MRR} + HR \\times W_{HR} "
            "+ nDCG \\times W_{nDCG} + (1 - CR) \\times W_{CR})}}{{\\sum W}} $$\n"
        )

        f.write(dedent(
            """
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
            """
        ))
