from textwrap import dedent

def write_composite_score_explanation(file_path):
    with open(file_path, 'a') as f:
        f.write(dedent(
            """
            <br>
            ## Composite Score Calculation

            The composite score is calculated using the following formula:

            $$
            \\text{Composite Score} =
            (R \\times W_R + P \\times W_P + F1 \\times W_{F1} \\\\
            + MRR \\times W_{MRR} + HR \\times W_{HR} \\\\
            + nDCG \\times W_{nDCG} + CR \\times W_{CR})
            $$

            ### Legend

            - **R**: Average Recall
            - **P**: Average Precision
            - **F1**: Average F1 Score
            - **MRR**: Average Mean Reciprocal Rank
            - **HR**: Average Hit Rate
            - **nDCG**: Average Normalized Discounted Cumulative Gain
            - **CR**: Average Confusion Rate
            - **W**: Weight of the respective metric

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
            """
        ))
