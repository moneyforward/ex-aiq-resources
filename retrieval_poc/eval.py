import pandas as pd
from approaches.random.random_retriever import RandomRetriever

# Load the evaluation data
file_path = 'data/eval_en.csv'
data = pd.read_csv(file_path)

# Set a standard retrieval size
retrieval_size = 3

# Initialize retrievers
retrievers = {
    # 'BM25': BM25Retriever(data, retrieval_size),
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
    # Initialize lists to store metrics
    recall_list = []
    precision_list = []
    mrr_list = []
    hit_rate_list = []
    ndcg_list = []
    confusion_list = []
    f1_list = []

    # Iterate through each retriever and evaluate
    for name, retriever in retrievers.items():
        print(f'Evaluating {name} Retriever')
        for index, row in data.iterrows():
            rule = row['Rule']
            positive_examples = [row['Example 1'], row['Example 2']]
            distractor_rules = eval(row['Distractor Rules'])

            for query in positive_examples:  # Use both positive examples as queries
                # Retrieve results
                retrieved = retriever.retrieve(query)

                # Calculate metrics
                recall = recall_at_k(retrieved, positive_examples, 3)
                precision = precision_at_k(retrieved, positive_examples, 3)
                mrr = mean_reciprocal_rank(retrieved, positive_examples)
                hit_rate_value = hit_rate(retrieved, positive_examples)
                ndcg_value = ndcg(retrieved, positive_examples)
                confusion = confusion_rate(
                    retrieved, positive_examples, distractor_rules
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
                print(f'Recall@3: {recall}')
                print(f'Precision@3: {precision}')
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

        print(f'Average Recall@3: {avg_recall}')
        print(f'Average Precision@3: {avg_precision}')
        print(f'Average F1 Score: {avg_f1}')
        print(f'Average MRR: {avg_mrr}')
        print(f'Average Hit Rate: {avg_hit_rate}')
        print(f'Average nDCG: {avg_ndcg}')
        print(f'Average Confusion Rate: {avg_confusion}')
        print('===')
