# Elasticsearch Setup Guide

This guide explains how to set up and use the Elasticsearch retriever in the retrieval evaluation system.

## Prerequisites

- Docker and Docker Compose installed
- Poetry for Python dependency management

## Quick Start

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Start Elasticsearch:**
   ```bash
   make es-start
   ```

3. **Run evaluations with Elasticsearch:**
   ```bash
   make run-with-es
   ```

## Manual Setup

### 1. Start Elasticsearch

```bash
# Start Elasticsearch container
docker-compose up -d elasticsearch

# Check if Elasticsearch is ready
curl http://localhost:9200/_cluster/health
```

### 2. Install Python Dependencies

```bash
poetry install
```

### 3. Run Evaluations

```bash
# Run English synthetic evaluation
poetry run python eval_en_synth.py

# Run Japanese real data evaluation  
poetry run python eval_ja.py
```

## Elasticsearch Management Commands

```bash
# Start Elasticsearch
make es-start

# Stop Elasticsearch
make es-stop

# Check Elasticsearch status
make es-status

# Clean Elasticsearch data (removes all indices)
make es-clean
```

## Configuration

The Elasticsearch retriever is configured in the evaluation scripts:

- **English evaluation**: `expense_rules_en` index
- **Japanese evaluation**: `expense_rules_ja` index
- **Default settings**: localhost:9200, standard analyzer

## Features

The Elasticsearch retriever includes:

- **Multi-field search**: Searches across rule, description, category, and full text
- **Field boosting**: Rules have higher weight (2x), descriptions (1.5x)
- **Fuzzy matching**: Automatic typo tolerance
- **Automatic indexing**: Creates and populates indices automatically

## Troubleshooting

### Elasticsearch not starting
```bash
# Check Docker logs
docker-compose logs elasticsearch

# Clean and restart
make es-clean
make es-start
```

### Connection errors
- Ensure Elasticsearch is running: `make es-status`
- Check if port 9200 is available: `lsof -i :9200`
- Verify Docker is running: `docker ps`

### Performance issues
- Increase memory allocation in `docker-compose.yml`
- Check available system resources: `docker stats`

## Index Management

The retriever automatically:
- Creates indices with appropriate mappings
- Indexes all rule data on initialization
- Refreshes indices for immediate searchability
- Deletes and recreates indices on each run (for clean state)

## Customization

To customize the Elasticsearch retriever:

1. **Modify search query** in `elasticsearch_retriever.py`
2. **Adjust field weights** in the multi_match query
3. **Change analyzer** for different language support
4. **Add custom mappings** for specialized fields
