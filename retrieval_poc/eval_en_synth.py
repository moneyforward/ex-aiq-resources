import pandas as pd
import os
from approaches.random.random_retriever import RandomRetriever
from approaches.bm25.bm25_retriever import BM25Retriever
from approaches.elasticsearch.elasticsearch_retriever import ElasticsearchRetriever
from approaches.dense.dense_retriever import DenseRetriever
from approaches.rag.text_to_sql import TextToSQLRetriever
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
retriever_data = data.drop(
    columns=['Example 1', 'Example 2', 'Distractor Rules'])

# Load natural language data for ButlerAI
natural_lang_file = 'data/eval_en_natural_language.csv'
if os.path.exists(natural_lang_file):
    natural_lang_data = pd.read_csv(natural_lang_file)
    print(f"Natural language data shape: {natural_lang_data.shape}")
else:
    print("Warning: Natural language data not found, ButlerAI will use original data")
    natural_lang_data = data

# Set pandas display options to show all columns
pd.set_option('display.max_columns', None)

# Define retriever configurations
retriever_configs = {
    'BM25Okapi': {'version': 'BM25Okapi', 'k1': 1.2, 'b': 0.75},
    'BM25L': {'version': 'BM25L', 'k1': 1.2, 'b': 0.75},
    'BM25Plus': {'version': 'BM25Plus', 'k1': 1.2, 'b': 0.75},
    'Elasticsearch': {'es_host': 'localhost', 'es_port': 9200,
                      'index_name': 'expense_rules_en'},
    'Random': {},
    'dense_retriever': {'version': 'dense_retriever'},
    'text2sql': {},
}

# Define evaluation metrics

def recall_at_k(retrieved, relevant, k):
    return sum(1 for r in relevant if r in retrieved[:k]) / len(relevant)


def precision_at_k(retrieved, relevant, k):
    return sum(1 for r in retrieved[:k] if r in relevant) / k


def mean_reciprocal_rank_at_k(retrieved, relevant, k):
    for rank, item in enumerate(retrieved[:k], start=1):
        if item in relevant:
            return 1 / rank
    return 0


def ndcg_at_k(retrieved, relevant, k):
    # Calculate DCG: sum of relevance scores divided by log2(rank + 1)
    dcg = 0
    for i, r in enumerate(retrieved[:k]):
        if r in relevant:
            dcg += 1 / (i + 1)  # relevance score of 1 for relevant items

    # Calculate IDCG: ideal DCG for the best possible ranking
    # For a single relevant item, IDCG = 1 (at rank 1)
    # For multiple relevant items, IDCG = sum of 1/log2(i+1) for i in
    # range(min(len(relevant), k))
    idcg = sum(1 / (i + 1) for i in range(min(len(relevant), k)))

    # Cap nDCG at 1.0 to prevent values above 1
    ndcg = dcg / idcg if idcg > 0 else 0
    return min(ndcg, 1.0)


def hit_rate(retrieved, relevant):
    # return 1 if retrieved and retrieved[0] in relevant else 0
    # Corrected to check within top-k retrieved items, not just the first item
    return 1 if any(item in relevant for item in retrieved[:k]) else 0


def confusion_rate(retrieved, relevant, distractors):
    if not retrieved:
        return 0
    return sum(1 for r in retrieved if r in distractors) / len(retrieved)


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
    for name, config in retriever_configs.items():
        print(f'Evaluating {name} Retriever')
        for k in k_values:
            # Initialize retriever with correct size for this k value
            if name == 'Random':
                retriever = RandomRetriever(retriever_data, k)
            elif name == 'dense_retriever':
                retriever = DenseRetriever(retriever_data, k)
            elif name == 'text2sql':
                retriever = TextToSQLRetriever(retriever_data, k)
            elif name == 'Elasticsearch':
                retriever = ElasticsearchRetriever(
                    retriever_data, k,
                    rule_column='Rule',
                    description_column='Expense item name\n'
                    '(Name registered in Cloud Expenses)',
                    category_column='Account',
                    rule_id_column='Rule',
                    es_host=config['es_host'],
                    es_port=config['es_port'],
                    index_name=config['index_name']
                )
            else:
                retriever = BM25Retriever(
                    retriever_data, k,
                    version=config['version'],
                    k1=config['k1'],
                    b=config['b']
                )
            # Initialize lists to store metrics
            recall_list = []
            precision_list = []
            mrr_list = []
            hit_rate_list = []
            ndcg_list = []
            confusion_list = []
            f1_list = []

            # Use appropriate data source for each retriever
            eval_data = natural_lang_data if name == 'ButlerAI' else data

            for index, row in eval_data.iterrows():
                rule = row['Rule']

                # For ButlerAI, use the converted natural language queries
                if name == 'ButlerAI':
                    # Use the converted natural language query
                    positive_examples = [row['query']]
                else:
                    # Use original JSON queries
                    positive_examples = [row['Example 1'], row['Example 2']]

                distractor_rules = eval(row['Distractor Rules'])

                # Use appropriate queries for each retriever
                for query in positive_examples:
                    # Retrieve results
                    retrieved = retriever.retrieve(query)

                    # Calculate metrics
                    recall = recall_at_k(retrieved, [rule], k)
                    precision = precision_at_k(retrieved, [rule], k)
                    mrr = mean_reciprocal_rank_at_k(retrieved, [rule], k)
                    hit_rate_value = hit_rate(retrieved, [rule])
                    ndcg_value = ndcg_at_k(retrieved, [rule], k)
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
                    print(f'MRR@{k}: {mrr}')
                    print(f'Hit Rate: {hit_rate_value}')
                    print(f'nDCG@{k}: {ndcg_value}')
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
            new_row = pd.DataFrame({
                'Retriever': [name],
                'k': [k],
                'Average Recall': [avg_recall],
                'Average Precision': [avg_precision],
                'Average F1 Score': [avg_f1],
                'Average MRR': [avg_mrr],
                'Average Hit Rate': [avg_hit_rate],
                'Average nDCG': [avg_ndcg],
                'Average Confusion Rate': [avg_confusion],
            })
            results_df = pd.concat([results_df, new_row], ignore_index=True)

    # Invert the Confusion Rate
    results_df['Inverted Confusion Rate'] = 1 - results_df['Average Confusion Rate']

    # Define weights for each metric, excluding Recall and Precision
    weights = {
        'Average F1 Score': 0.4,  # Increase to reflect its importance
        'Average MRR': 0.1,
        'Average Hit Rate': 0.2,
        'Average nDCG': 0.1,
        'Inverted Confusion Rate': 0.2
    }

    # Calculate the weighted sum of metrics
    composite_score = (
        results_df['Average F1 Score'] * weights['Average F1 Score'] +
        results_df['Average MRR'] * weights['Average MRR'] +
        results_df['Average Hit Rate'] * weights['Average Hit Rate'] +
        results_df['Average nDCG'] * weights['Average nDCG'] +
        results_df['Inverted Confusion Rate'] * weights['Inverted Confusion Rate']
    )

    # Normalize by the sum of the weights
    total_weight = sum(weights.values())
    results_df['Composite Score'] = composite_score / total_weight

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
    results_df.to_markdown('approaches/comparison_table_en_synth.md', index=False)

    # Call the function to add explanation of the composite score
    write_composite_score_explanation('approaches/comparison_table_en_synth.md')

# Inform the user where the results are saved
print(
    "The comparison table has been saved as a markdown file at "
    "'approaches/comparison_table_en_synth.md'."
)
