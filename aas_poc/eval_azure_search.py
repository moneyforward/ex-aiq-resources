"""
Azure AI Search Evaluation Script
Uses the existing retrieval_poc evaluation framework with Azure AI Search as the retriever
"""

import os
import sys
import pandas as pd
import json
import random
import numpy as np
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('evaluation.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the retrieval_poc approaches directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../retrieval_poc/approaches'))

# Import the Azure Search retriever
from src.azure_retriever import AzureSearchRetriever

# Import evaluation functions from the existing framework
try:
    from approaches.markdown_writer import write_composite_score_explanation
except ImportError:
    # Fallback if markdown_writer is not available
    def write_composite_score_explanation(*args, **kwargs):
        pass

# Set random seeds for reproducibility
random.seed(42)
np.random.seed(42)


def load_evaluation_data(dataset_type="ja"):
    """Load evaluation data from retrieval_poc
    
    Args:
        dataset_type: "ja" for Japanese or "en_synth" for English synthetic
    """
    logger.info(f"Loading {dataset_type} evaluation data from retrieval_poc...")
    
    if dataset_type == "ja":
        # Japanese dataset
        json_file_path = '../retrieval_poc/data/sample_category_check_request.json'
        ground_truth_file = '../retrieval_poc/data/ja_labels.csv'
        rule_space_file = '../retrieval_poc/data/eval_ja.csv'
        index_name = "aiq-expense-rules-ja"
    elif dataset_type == "en_synth":
        # English synthetic dataset
        json_file_path = None  # English uses CSV directly
        ground_truth_file = None  # English has ground truth in the same file
        rule_space_file = '../retrieval_poc/data/eval_en.csv'
        index_name = "aiq-expense-rules-en"
    else:
        raise ValueError(f"Unknown dataset_type: {dataset_type}. Use 'ja' or 'en_synth'")
    
    # Load the full rule space
    logger.info(f"Loading rule space from: {rule_space_file}")
    rule_space_data_full = pd.read_csv(rule_space_file)
    logger.info(f"✅ Rule space: {len(rule_space_data_full)} rules from {rule_space_file}")
    
    # Create filtered data for retrievers (exclude Distractor Rules to prevent data leakage)
    rule_space_data = rule_space_data_full.drop(columns=['Distractor Rules'])
    logger.info(f"✅ Filtered rule space shape (excluding Distractor Rules): {rule_space_data.shape}")
    
    if dataset_type == "ja":
        # Load JSON data for Japanese
        logger.info(f"Loading JSON data from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Load ground truth mapping
        logger.info(f"Loading ground truth from: {ground_truth_file}")
        ground_truth_df = pd.read_csv(ground_truth_file)
        logger.info(f"✅ JSON data: {len(json_data['expenses'])} expenses")
        logger.info(f"✅ Ground truth: {len(ground_truth_df)} mappings")
        
        return json_data, ground_truth_df, rule_space_data_full, rule_space_data, index_name
    else:
        # For English synthetic, the data is already in the CSV
        logger.info(f"✅ English synthetic data: {len(rule_space_data_full)} rules")
        return None, None, rule_space_data_full, rule_space_data, index_name


def prepare_evaluation_data(dataset_type, json_data, ground_truth_df, rule_space_data_full):
    """Prepare evaluation data in DataFrame format
    
    Args:
        dataset_type: "ja" or "en_synth"
        json_data: JSON data for Japanese (None for English)
        ground_truth_df: Ground truth for Japanese (None for English)
        rule_space_data_full: Full rule space data
    """
    if dataset_type == "ja":
        return json_to_dataframe(json_data, ground_truth_df, rule_space_data_full)
    else:
        return csv_to_dataframe(rule_space_data_full)


def json_to_dataframe(json_data, ground_truth_df, rule_space_data_full):
    """Convert JSON expense data to DataFrame format for evaluation (Japanese)"""
    rows = []
    
    # Get all available rules from the rule space (64 rules from eval_ja.csv)
    all_available_rules = rule_space_data_full['Rule'].unique()
    logger.info(f"Available rules for search space: {len(all_available_rules)}")
    
    for idx, expense in enumerate(json_data['expenses']):
        # Get the ground truth rule for this expense
        ground_truth_row = ground_truth_df[ground_truth_df['index'] == idx]
        if ground_truth_row.empty:
            logger.warning(f"Warning: No ground truth found for expense {idx}")
            continue
        
        rule_id = ground_truth_row.iloc[0]['rule_id']
        
        # Use the full JSON expense object as the query instead of extracting natural language
        # This matches the real input format that the system will receive
        query = json.dumps(expense, ensure_ascii=False, indent=2)
        
        # Get distractor rules from the full rule space data for this specific rule
        rule_row = rule_space_data_full[rule_space_data_full['Rule'] == rule_id]
        if not rule_row.empty:
            distractor_rules_str = rule_row.iloc[0]['Distractor Rules']
            # Parse the string representation of the list
            distractor_rules = eval(distractor_rules_str)
        else:
            # Fallback: use all other rules if not found
            distractor_rules = [r for r in all_available_rules if r != rule_id]
        
        rows.append({
            'Rule': rule_id,
            'query': query,  # Full JSON expense object
            'description': expense.get('description', ''),
            'amount': expense.get('amount', 0),
            'date': expense.get('date', ''),
            'category': expense.get('category', ''),
            'Distractor Rules': distractor_rules,
            'Example 1': query,  # For compatibility with existing retrievers
            'Example 2': query   # For compatibility with existing retrievers
        })
    
    return pd.DataFrame(rows)


def csv_to_dataframe(rule_space_data_full):
    """Convert CSV data to DataFrame format for evaluation (English synthetic)"""
    logger.info("Preparing English synthetic data for evaluation...")
    
    # Create 2 queries per rule using Example 1 and Example 2
    rows = []
    
    for _, row in rule_space_data_full.iterrows():
        rule = row['Rule']
        
        # Parse distractor rules
        distractor_rules = eval(row['Distractor Rules']) if pd.notna(row['Distractor Rules']) else []
        
        # Parse JSON from Example 1 and Example 2 columns
        # These contain markdown-formatted JSON objects with backticks
        if pd.notna(row['Example 1']):
            try:
                # Strip markdown formatting (``` json ... ```)
                example1_text = str(row['Example 1']).strip()
                if example1_text.startswith('``` json'):
                    # Remove markdown formatting - handle newlines properly
                    example1_text = example1_text[7:]  # Remove '``` json'
                    if example1_text.startswith('\n'):
                        example1_text = example1_text[1:]  # Remove leading newline
                    elif example1_text.startswith('n'):  # Handle escaped newline
                        example1_text = example1_text[1:]  # Remove leading 'n'
                    if example1_text.endswith('```'):
                        example1_text = example1_text[:-3]  # Remove trailing '```'
                    example1_text = example1_text.strip()
                
                # Parse the JSON from Example 1
                example1_json = json.loads(example1_text)
                query1 = json.dumps(example1_json, ensure_ascii=False, indent=2)
                rows.append({
                    'query': query1,
                    'Rule': rule,
                    'Distractor Rules': distractor_rules,
                    'example_type': 'Example 1'
                })
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Example 1 JSON for rule {rule}: {e}")
                # Fallback to using the raw text if JSON parsing fails
                rows.append({
                    'query': row['Example 1'],
                    'Rule': rule,
                    'Distractor Rules': distractor_rules,
                    'example_type': 'Example 1'
                })
        
        # Create query from Example 2
        if pd.notna(row['Example 2']):
            try:
                # Strip markdown formatting (``` json ... ```)
                example2_text = str(row['Example 2']).strip()
                if example2_text.startswith('``` json'):
                    # Remove markdown formatting - handle newlines properly
                    example2_text = example2_text[7:]  # Remove '``` json'
                    if example2_text.startswith('\n'):
                        example2_text = example2_text[1:]  # Remove leading newline
                    elif example2_text.startswith('n'):  # Handle escaped newline
                        example2_text = example2_text[1:]  # Remove leading 'n'
                    if example2_text.endswith('```'):
                        example2_text = example2_text[:-3]  # Remove trailing '```'
                    example2_text = example2_text.strip()
                
                # Parse the JSON from Example 2
                example2_json = json.loads(example2_text)
                query2 = json.dumps(example2_json, ensure_ascii=False, indent=2)
                rows.append({
                    'query': query2,
                    'Rule': rule,
                    'Distractor Rules': distractor_rules,
                    'example_type': 'Example 2'
                })
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Example 2 JSON for rule {rule}: {e}")
                # Fallback to using the raw text if JSON parsing fails
                rows.append({
                    'query': row['Example 2'],
                    'Rule': rule,
                    'Distractor Rules': distractor_rules,
                    'example_type': 'Example 2'
                })
    
    data = pd.DataFrame(rows)
    logger.info(f"✅ Prepared {len(data)} English synthetic queries (64 rules × 2 examples)")
    return data


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


def evaluate_azure_search(dataset_type="ja"):
    """Main evaluation function for Azure AI Search
    
    Args:
        dataset_type: "ja" for Japanese or "en_synth" for English synthetic
    """
    logger.info("=" * 60)
    logger.info(f"EVALUATING AZURE AI SEARCH ON {dataset_type.upper()} DATASET")
    logger.info("=" * 60)
    
    # Load evaluation data
    json_data, ground_truth_df, rule_space_data_full, rule_space_data, index_name = load_evaluation_data(dataset_type)
    
    # Prepare evaluation data
    logger.info(f"Preparing {dataset_type} data for evaluation...")
    data = prepare_evaluation_data(dataset_type, json_data, ground_truth_df, rule_space_data_full)
    logger.info(f"✅ Prepared data shape: {data.shape}")
    
    # Define k values to evaluate
    k_values = [1, 3]
    logger.info(f"Evaluating at k values: {k_values}")
    
    # Initialize a DataFrame to store the results
    results_df = pd.DataFrame(columns=[
        'Retriever', 'k', 'Average Recall', 'Average Precision', 'Average F1 Score',
        'Average MRR', 'Average Hit Rate', 'Average nDCG', 'Average Confusion Rate'
    ])
    
    # Evaluate Azure AI Search
    retriever_name = 'Azure AI Search'
    logger.info(f'\n🔍 Evaluating {retriever_name} Retriever on JSON dataset')
    logger.info("-" * 40)
    
    for k in k_values:
        logger.info(f'\n📊 Evaluating at k={k}')
        
        # Initialize Azure Search retriever
        # Use the full rule space for retrieval, not just the evaluation data
        logger.info(f"Initializing Azure Search retriever for {dataset_type} dataset...")
        retriever = AzureSearchRetriever(rule_space_data, k, index_name=index_name, use_hybrid=True) # Enable hybrid search!
        
        # Get index stats
        stats = retriever.get_index_stats()
        logger.info(f"Index stats: {stats}")
        
        # Initialize lists to store metrics
        recall_list = []
        precision_list = []
        mrr_list = []
        hit_rate_list = []
        ndcg_list = []
        confusion_list = []
        f1_list = []
        
        # Evaluate each query
        logger.info(f"Evaluating {len(data)} queries...")
        for index, row in data.iterrows():
            rule = row['Rule']
            query = row['query']
            distractor_rules = row['Distractor Rules']
            
            # Show different info based on dataset type
            if dataset_type == "ja":
                description = row.get('description', '')
                logger.info(f"Expense {index + 1}/{len(data)}: {description[:50]}...")
            else:
                logger.info(f"Query {index + 1}/{len(data)}: {query[:50]}...")
            
            # Retrieve using Azure AI Search
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
            
            # Log results for each expense
            logger.info(f'  Rule: {rule}')
            logger.info(f'  Retrieved: {retrieved}')
            logger.info(f'  Recall@{k}: {recall:.3f}')
            logger.info(f'  Precision@{k}: {precision:.3f}')
            logger.info(f'  F1 Score: {f1:.3f}')
            logger.info(f'  MRR@{k}: {mrr:.3f}')
            logger.info(f'  Hit Rate: {hit_rate_value:.3f}')
            logger.info(f'  nDCG@{k}: {ndcg_value:.3f}')
            logger.info(f'  Confusion Rate: {confusion:.3f}')
            logger.info('  ---')
        
        # Calculate and print average metrics
        avg_recall = sum(recall_list) / len(recall_list)
        avg_precision = sum(precision_list) / len(precision_list)
        avg_mrr = sum(mrr_list) / len(mrr_list)
        avg_hit_rate = sum(hit_rate_list) / len(hit_rate_list)
        avg_ndcg = sum(ndcg_list) / len(ndcg_list)
        avg_confusion = sum(confusion_list) / len(confusion_list)
        avg_f1 = sum(f1_list) / len(f1_list)
        
        logger.info(f'\n📈 {retriever_name} @ k={k} - Average Metrics:')
        logger.info(f'  Average Recall@{k}: {avg_recall:.3f}')
        logger.info(f'  Average Precision@{k}: {avg_precision:.3f}')
        logger.info(f'  Average F1 Score: {avg_f1:.3f}')
        logger.info(f'  Average MRR: {avg_mrr:.3f}')
        logger.info(f'  Average Hit Rate: {avg_hit_rate:.3f}')
        logger.info(f'  Average nDCG: {avg_ndcg:.3f}')
        logger.info(f'  Average Confusion Rate: {avg_confusion:.3f}')
        logger.info('=' * 50)
        
        # Append results to the DataFrame
        new_row = pd.DataFrame({
            'Retriever': [retriever_name],
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
    output_file = f'azure_search_results_{dataset_type}.md'
    results_df.to_markdown(output_file, index=False)
    
    # Call the function to add explanation of the composite score
    write_composite_score_explanation(output_file)
    
    logger.info(f"\n💾 The Azure AI Search evaluation results have been saved as '{output_file}'")
    if dataset_type == "ja":
        logger.info(f"Dataset summary: {len(data)} expenses, "
                    f"{len(ground_truth_df['rule_id'].unique())} unique rules")
    else:
        logger.info(f"Dataset summary: {len(data)} queries, "
                    f"{len(data['Rule'].unique())} unique rules")
    
    return results_df


def main():
    """Main function to run evaluations for both datasets"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate Azure AI Search on expense datasets')
    parser.add_argument('--dataset', choices=['ja', 'en_synth', 'both'], default='ja',
                       help='Dataset to evaluate: ja (Japanese), en_synth (English synthetic), or both')
    
    args = parser.parse_args()
    
    if args.dataset == 'both':
        logger.info("🚀 Running evaluation on both Japanese and English synthetic datasets")
        
        # Evaluate Japanese dataset
        logger.info("\n" + "="*80)
        logger.info("JAPANESE DATASET EVALUATION")
        logger.info("="*80)
        results_ja = evaluate_azure_search("ja")
        
        # Evaluate English synthetic dataset
        logger.info("\n" + "="*80)
        logger.info("ENGLISH SYNTHETIC DATASET EVALUATION")
        logger.info("="*80)
        results_en = evaluate_azure_search("en_synth")
        
        logger.info("🎉 Both evaluations completed!")
        return results_ja, results_en
    else:
        return evaluate_azure_search(args.dataset)


if __name__ == '__main__':
    results = main()
