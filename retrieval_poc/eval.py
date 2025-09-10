import pandas as pd
from approaches.random.random_retriever import RandomRetriever
from approaches.bm25.bm25_retriever import BM25Retriever
import random
import numpy as np
from approaches.markdown_writer import write_composite_score_explanation

# Set a random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Load the evaluation data
file_path = 'data/eval_en.csv'
data = pd.read_csv(file_path)
print(f"Data shape: {data.shape}")  # Print the shape of the DataFrame

# Set pandas display options to show all columns
pd.set_option('display.max_columns', None)

# Set a standard retrieval size
retrieval_size = 3

# Initialize retrievers
retrievers = {
    'BM25Okapi': BM25Retriever(
        data, retrieval_size, version='BM25Okapi', k1=1.2, b=0.75
    ),
    'BM25L': BM25Retriever(
        data, retrieval_size, version='BM25L', k1=1.2, b=0.75
    ),
    'BM25Plus': BM25Retriever(
        data, retrieval_size, version='BM25Plus', k1=1.2, b=0.75
    ),
    # 'Dense': DenseRetriever(data, retrieval_size),
    # 'RAG': RAGRetriever(data, retrieval_size),
    # 'ButlerAI': ButlerAIRetriever(data, retrieval_size),
    'Random': RandomRetriever(data, retrieval_size)
}

# Define evaluation metrics

def recall_at_k(retrieved, relevant, k):
    return sum(1 for r in relevant if r in retrieved[:k]) / len(relevant)


def precision_at_k(retrieved, relevant, k):
    return sum(1 for r in retrieved[:k] if r in relevant) / k


def mean_reciprocal_rank(retrieved, relevant):
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1 / rank
    return 0


def hit_rate(retrieved, relevant):
    return 1 if retrieved[0] in relevant else 0


def ndcg(retrieved, relevant):
    dcg = sum((1 / (i + 1)) for i, r in enumerate(retrieved)
               if r in relevant)
    idcg = sum((1 / (i + 1)) for i in range(len(relevant)))
    return dcg / idcg if idcg > 0 else 0


def confusion_rate(retrieved, relevant, distractors):
    return sum(
        1 for d in distractors if d in retrieved and d not in relevant
    ) / len(distractors)


def f1_score(recall, precision):
    if recall + precision == 0:
        return 0
    return 2 * (recall * precision) / (recall + precision)

# Main evaluation loop
if __name__ == '__main__':
    # Define k values to evaluate
    k_values = [1, 3]

    # Initialize a DataFrame to store the results
    results_df = pd.DataFrame(columns=[
        'Retriever', 'k', 'Average Recall', 'Average Precision', 'Average F1 Score',
        'Average MRR', 'Average Hit Rate', 'Average nDCG', 'Average Confusion Rate'
    ])

    # Iterate through each retriever and evaluate
    for name, retriever in retrievers.items():
        print(f'Evaluating {name} Retriever')
        for k in k_values:
            # Initialize lists to store metrics
            recall_list = []
            precision_list = []
            mrr_list = []
            hit_rate_list = []
            ndcg_list = []
            confusion_list = []
            f1_list = []

            for index, row in data.iterrows():
                rule = row['Rule']
                positive_examples = [row['Example 1'], row['Example 2']]
                distractor_rules = eval(row['Distractor Rules'])

                for query in positive_examples:  # Use both positive examples as queries
                    # Retrieve results
                    retrieved = retriever.retrieve(query)

                    # Calculate metrics
                    recall = recall_at_k(retrieved, [rule], k)
                    precision = precision_at_k(retrieved, [rule], k)
                    mrr = mean_reciprocal_rank(retrieved, [rule])
                    hit_rate_value = hit_rate(retrieved, [rule])
                    ndcg_value = ndcg(retrieved, [rule])
                    confusion = confusion_rate(
                        retrieved, [rule], distractor_rules
                    )
                    f1 = f1_score(recall, precision)

                    # Append metrics to lists
                    recall_list.append(recall)
                    precision_list.append(precision)
                    mrr_list.append(mrr)
                    hit_rate_list.append(hit_rate_value)
                    ndcg_list.append(ndcg_value)
                    confusion_list.append(confusion)
                    f1_list.append(f1)

                    # Print results for each rule
                    print(f'Rule: {rule}, Query: {query}')
                    print(f'Retrieved: {retrieved}')
                    print(f'Recall@{k}: {recall}')
                    print(f'Precision@{k}: {precision}')
                    print(f'F1 Score: {f1}')
                    print(f'MRR: {mrr}')
                    print(f'Hit Rate: {hit_rate_value}')
                    print(f'nDCG: {ndcg_value}')
                    print(f'Confusion Rate: {confusion}')
                    print('---')

            # Calculate and print average metrics
            avg_recall = sum(recall_list) / len(recall_list)
            avg_precision = sum(precision_list) / len(precision_list)
            avg_mrr = sum(mrr_list) / len(mrr_list)
            avg_hit_rate = sum(hit_rate_list) / len(hit_rate_list)
            avg_ndcg = sum(ndcg_list) / len(ndcg_list)
            avg_confusion = sum(confusion_list) / len(confusion_list)
            avg_f1 = sum(f1_list) / len(f1_list)

            print(f'Average Recall@{k}: {avg_recall}')
            print(f'Average Precision@{k}: {avg_precision}')
            print(f'Average F1 Score: {avg_f1}')
            print(f'Average MRR: {avg_mrr}')
            print(f'Average Hit Rate: {avg_hit_rate}')
            print(f'Average nDCG: {avg_ndcg}')
            print(f'Average Confusion Rate: {avg_confusion}')
            print('===')

            # Append results to the DataFrame
            results_df = results_df.append({
                'Retriever': name,
                'k': k,
                'Average Recall': avg_recall,
                'Average Precision': avg_precision,
                'Average F1 Score': avg_f1,
                'Average MRR': avg_mrr,
                'Average Hit Rate': avg_hit_rate,
                'Average nDCG': avg_ndcg,
                'Average Confusion Rate': avg_confusion
            }, ignore_index=True)

    # Define weights for each metric
    weights = {
        'Average Recall': 0.5,
        'Average Precision': 0.5,
        'Average F1 Score': 2.0,  # Prioritize F1 Score
        'Average MRR': 0.5,
        'Average Hit Rate': 2.0,  # Prioritize Hit Rate
        'Average nDCG': 0.5,
        'Average Confusion Rate': -2.0  # Prioritize Confusion Rate negatively
    }

    # Fix line length issues
    results_df['Composite Score'] = (
        results_df['Average Recall'] * weights['Average Recall'] +
        results_df['Average Precision'] * weights['Average Precision'] +
        results_df['Average F1 Score'] * weights['Average F1 Score'] +
        results_df['Average MRR'] * weights['Average MRR'] +
        results_df['Average Hit Rate'] * weights['Average Hit Rate'] +
        results_df['Average nDCG'] * weights['Average nDCG'] +
        results_df['Average Confusion Rate'] * weights['Average Confusion Rate']
    )

    # Sort the table by k and composite score
    results_df.sort_values(
        by=['k', 'Composite Score'], ascending=[True, False], inplace=True
    )

    # Reorder columns to place Composite Score after k
    results_df = results_df[[
        'Retriever', 'k', 'Composite Score', 'Average Recall', 'Average Precision',
        'Average F1 Score', 'Average MRR', 'Average Hit Rate', 'Average nDCG',
        'Average Confusion Rate'
    ]]

    # Save the reordered comparison table as a markdown file
    results_df.to_markdown('approaches/comparison_table.md', index=False)

    # Call the function to add explanation of the composite score
    write_composite_score_explanation('approaches/comparison_table.md')

# Inform the user where the results are saved
print(
    "The comparison table has been saved as a markdown file at "
    "'approaches/comparison_table.md'."
)
