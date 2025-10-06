# Azure AI Search POC Makefile

.PHONY: help install index evaluate clean health-check

help: ## Show this help message
	@echo "Azure AI Search POC - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Azure Search dependencies
	poetry install


index: ## Index documents to Azure AI Search (using analyzers) - Japanese dataset
	poetry run python src/index_documents.py --dataset ja

index-embeddings: ## Index documents using Azure AI Search integrated vectorization (no separate API keys needed) - Japanese dataset
	poetry run python src/index_documents.py --dataset ja --use-embeddings

index-hybrid: ## Index documents using hybrid search (text + vector with RRF ranking) - Japanese dataset
	poetry run python src/index_documents.py --dataset ja --use-hybrid

index-en: ## Index documents to Azure AI Search (using analyzers) - English synthetic dataset
	poetry run python src/index_documents.py --dataset en

index-en-embeddings: ## Index documents using Azure AI Search integrated vectorization - English synthetic dataset
	poetry run python src/index_documents.py --dataset en --use-embeddings

index-en-hybrid: ## Index documents using hybrid search - English synthetic dataset
	poetry run python src/index_documents.py --dataset en --use-hybrid

index-both-hybrid: ## Index both Japanese and English datasets using hybrid search
	poetry run python src/index_documents.py --dataset ja --use-hybrid && poetry run python src/index_documents.py --dataset en --use-hybrid

evaluate: ## Run evaluation on Azure AI Search (Japanese dataset)
	poetry run python eval_azure_search.py --dataset ja

evaluate-en: ## Run evaluation on Azure AI Search (English synthetic dataset)
	poetry run python eval_azure_search.py --dataset en_synth

evaluate-both: ## Run evaluation on both Japanese and English synthetic datasets
	poetry run python eval_azure_search.py --dataset both

health-check: ## Check Azure Search service health
	poetry run python -c "from src.azure_retriever import AzureSearchRetriever; import pandas as pd; df = pd.read_csv('../retrieval_poc/data/eval_ja.csv'); retriever = AzureSearchRetriever(df, 1); print(retriever.get_index_stats())"

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.md" -not -name "README.md" -delete

setup-env: ## Copy environment template
	cp env.example .env
	@echo "Please edit .env file with your Azure credentials"

full-pipeline: install index evaluate ## Run the complete pipeline: install, index, and evaluate (Japanese)
	@echo "Full pipeline completed!"

full-pipeline-en: install index evaluate-en ## Run the complete pipeline: install, index, and evaluate (English synthetic)
	@echo "Full pipeline (English) completed!"

full-pipeline-both: install index evaluate-both ## Run the complete pipeline: install, index, and evaluate (both datasets)
	@echo "Full pipeline (both datasets) completed!"

full-pipeline-embeddings: install index-embeddings evaluate ## Run the complete pipeline with embeddings: install, index with embeddings, and evaluate
	@echo "Full pipeline (with embeddings) completed!"

full-pipeline-hybrid: install index-hybrid evaluate ## Run the complete pipeline with hybrid search: install, index with hybrid search, and evaluate
	@echo "Full pipeline (with hybrid search) completed!"

full-pipeline-both-hybrid: install index-both-hybrid evaluate-both ## Run the complete pipeline with hybrid search for both datasets
	@echo "Full pipeline (both datasets with hybrid search) completed!"

test-connection: ## Test connection to Azure AI Search
	poetry run python -c "import os; from azure.search.documents import SearchClient; from azure.core.credentials import AzureKeyCredential; from dotenv import load_dotenv; load_dotenv(); client = SearchClient('https://aibi-aai-stg-verification-30vc.search.windows.net', 'aiq-expense-rules', AzureKeyCredential(os.getenv('AZURE_SEARCH_ADMIN_KEY'))); print('Connection successful!')"
