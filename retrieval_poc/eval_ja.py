import pandas as pd
import json
from approaches.random.random_retriever import RandomRetriever
from approaches.bm25.bm25_retriever import BM25Retriever
from approaches.elasticsearch.elasticsearch_retriever import ElasticsearchRetriever
import random
import numpy as np
from approaches.markdown_writer import write_composite_score_explanation

# Set a random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Load the JSON evaluation data
json_file_path = 'data/sample_category_check_request.json'
ground_truth_file = 'data/ja_labels.csv'

# Load the full rule space from eval_ja.csv (Japanese rules)
rule_space_file = 'data/eval_ja.csv'
rule_space_data = pd.read_csv(rule_space_file)
print(f"Rule space: {len(rule_space_data)} rules from eval_ja.csv")

# Load JSON data
with open(json_file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Load ground truth mapping
ground_truth_df = pd.read_csv(ground_truth_file)
print(f"JSON data: {len(json_data['expenses'])} expenses")
print(f"Ground truth: {len(ground_truth_df)} mappings")

# Convert JSON data to DataFrame format compatible with existing retrievers
def json_to_dataframe(json_data, ground_truth_df, rule_space_data):
    """Convert JSON expense data to DataFrame format for evaluation"""
    rows = []
    
    # Get all available rules from the rule space (64 rules from eval_en.csv)
    all_available_rules = rule_space_data['Rule'].unique()
    print(f"Available rules for search space: {len(all_available_rules)}")
    
    for idx, expense in enumerate(json_data['expenses']):
        # Get the ground truth rule for this expense
        ground_truth_row = ground_truth_df[ground_truth_df['index'] == idx]
        if ground_truth_row.empty:
            print(f"Warning: No ground truth found for expense {idx}")
            continue
            
        rule_id = ground_truth_row.iloc[0]['rule_id']
        
        # Create a natural language description of the expense
        description = expense.get('description', '')
        amount = expense.get('amount', 0)
        date = expense.get('date', '')
        category = expense.get('category', '')
        
        # Create a comprehensive query that includes all relevant information
        query = (f"Expense: {description}, Amount: {amount} yen, "
                f"Date: {date}, Category: {category}")
        
        # Get distractor rules from the rule space data for this specific rule
        rule_row = rule_space_data[rule_space_data['Rule'] == rule_id]
        if not rule_row.empty:
            distractor_rules_str = rule_row.iloc[0]['Distractor Rules']
            # Parse the string representation of the list
            distractor_rules = eval(distractor_rules_str)
        else:
            # Fallback: use all other rules if not found
            distractor_rules = [r for r in all_available_rules if r != rule_id]
        
        rows.append({
            'Rule': rule_id,
            'query': query,
            'description': description,
            'amount': amount,
            'date': date,
            'category': category,
            'Distractor Rules': distractor_rules,
            'Example 1': query,  # For compatibility with existing retrievers
            'Example 2': query   # For compatibility with existing retrievers
        })
    
    return pd.DataFrame(rows)

# Convert JSON data to DataFrame
data = json_to_dataframe(json_data, ground_truth_df, rule_space_data)
print(f"Converted data shape: {data.shape}")

# Set pandas display options to show all columns
pd.set_option('display.max_columns', None)

# Define retriever configurations
retriever_configs = {
    'BM25Okapi': {'version': 'BM25Okapi', 'k1': 1.2, 'b': 0.75},
    'BM25L': {'version': 'BM25L', 'k1': 1.2, 'b': 0.75},
    'BM25Plus': {'version': 'BM25Plus', 'k1': 1.2, 'b': 0.75},
    'Elasticsearch': {'es_host': 'localhost', 'es_port': 9200, 'index_name': 'expense_rules_ja'},
    'Random': {}
}

# Define evaluation metrics (same as original eval.py)
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
    return 1 if retrieved and retrieved[0] in relevant else 0

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
    print("=" * 60)
    print("EVALUATING RETRIEVERS ON JSON EXPENSE DATASET")
    print("=" * 60)
    
    # Define k values to evaluate
    k_values = [1, 3]

    # Initialize a DataFrame to store the results
    results_df = pd.DataFrame(columns=[
        'Retriever', 'k', 'Average Recall', 'Average Precision', 'Average F1 Score',
        'Average MRR', 'Average Hit Rate', 'Average nDCG', 'Average Confusion Rate'
    ])

    # Iterate through each retriever and evaluate
    for name, config in retriever_configs.items():
        print(f'\nEvaluating {name} Retriever on JSON dataset')
        print("-" * 40)
        
        for k in k_values:
            print(f'\nEvaluating at k={k}')
            
            # Initialize retriever with correct size for this k value
            # Use the full rule space (64 rules) for retrieval, not just the JSON data
            if name == 'Random':
                retriever = RandomRetriever(rule_space_data, k)
            elif name == 'Elasticsearch':
                retriever = ElasticsearchRetriever(
                    rule_space_data, k,
                    rule_column='Rule',
                    description_column='経費科目名称\n（クラウド経費に登録されている名称）',
                    category_column='勘定科目',
                    rule_id_column='Rule',
                    es_host=config['es_host'],
                    es_port=config['es_port'],
                    index_name=config['index_name']
                )
            else:
                retriever = BM25Retriever(
                    rule_space_data, k, 
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

            # Evaluate each expense
            for index, row in data.iterrows():
                rule = row['Rule']
                query = row['query']
                distractor_rules = row['Distractor Rules']

                # Retrieve results
                retrieved = retriever.retrieve(query)

                # Calculate metrics
                recall = recall_at_k(retrieved, [rule], k)
                precision = precision_at_k(retrieved, [rule], k)
                mrr = mean_reciprocal_rank_at_k(retrieved, [rule], k)
                hit_rate_value = hit_rate(retrieved, [rule])
                ndcg_value = ndcg_at_k(retrieved, [rule], k)
                confusion = confusion_rate(retrieved, [rule], distractor_rules)
                f1 = f1_score(recall, precision)

                # Append metrics to lists
                recall_list.append(recall)
                precision_list.append(precision)
                mrr_list.append(mrr)
                hit_rate_list.append(hit_rate_value)
                ndcg_list.append(ndcg_value)
                confusion_list.append(confusion)
                f1_list.append(f1)

                # Print results for each expense
                print(f'Expense {index}: {row["description"][:50]}...')
                print(f'  Rule: {rule}')
                print(f'  Retrieved: {retrieved}')
                print(f'  Recall@{k}: {recall:.3f}')
                print(f'  Precision@{k}: {precision:.3f}')
                print(f'  F1 Score: {f1:.3f}')
                print(f'  MRR@{k}: {mrr:.3f}')
                print(f'  Hit Rate: {hit_rate_value:.3f}')
                print(f'  nDCG@{k}: {ndcg_value:.3f}')
                print(f'  Confusion Rate: {confusion:.3f}')
                print('  ---')

            # Calculate and print average metrics
            avg_recall = sum(recall_list) / len(recall_list)
            avg_precision = sum(precision_list) / len(precision_list)
            avg_mrr = sum(mrr_list) / len(mrr_list)
            avg_hit_rate = sum(hit_rate_list) / len(hit_rate_list)
            avg_ndcg = sum(ndcg_list) / len(ndcg_list)
            avg_confusion = sum(confusion_list) / len(confusion_list)
            avg_f1 = sum(f1_list) / len(f1_list)

            print(f'\n{name} @ k={k} - Average Metrics:')
            print(f'  Average Recall@{k}: {avg_recall:.3f}')
            print(f'  Average Precision@{k}: {avg_precision:.3f}')
            print(f'  Average F1 Score: {avg_f1:.3f}')
            print(f'  Average MRR: {avg_mrr:.3f}')
            print(f'  Average Hit Rate: {avg_hit_rate:.3f}')
            print(f'  Average nDCG: {avg_ndcg:.3f}')
            print(f'  Average Confusion Rate: {avg_confusion:.3f}')
            print('=' * 50)

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
        'Average F1 Score': 0.4,
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

    # Save the comparison table as a markdown file
    output_file = 'approaches/comparison_table_ja.md'
    results_df.to_markdown(output_file, index=False)

    # Call the function to add explanation of the composite score
    write_composite_score_explanation(output_file)

    print(f"\nThe Japanese dataset comparison table has been saved as "
          f"'{output_file}'")
    print(f"Dataset summary: {len(data)} expenses, "
          f"{len(ground_truth_df['rule_id'].unique())} unique rules")
