install:
	poetry install

# Elasticsearch setup and management
es-start:
	docker compose up -d elasticsearch
	@echo "Waiting for Elasticsearch to be ready..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then \
			echo "✅ Elasticsearch is ready at http://localhost:9200"; \
			exit 0; \
		fi; \
		echo "Waiting... ($$i/30)"; \
		sleep 2; \
	done; \
	echo "❌ Elasticsearch failed to start within 60 seconds"

es-stop:
	docker-compose down

es-restart:
	docker-compose restart elasticsearch
	@echo "Waiting for Elasticsearch to be ready..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then \
			echo "✅ Elasticsearch restarted and ready"; \
			exit 0; \
		fi; \
		echo "Waiting... ($$i/30)"; \
		sleep 2; \
	done; \
	echo "❌ Elasticsearch failed to restart within 60 seconds"

es-status:
	@echo "Elasticsearch cluster health:"
	@curl -s http://localhost:9200/_cluster/health | poetry run python -m json.tool 2>/dev/null || curl -s http://localhost:9200/_cluster/health

es-logs:
	docker-compose logs -f elasticsearch

es-clean:
	docker-compose down -v
	@echo "✅ Elasticsearch data volumes cleaned"

# Temporary container for testing (creates fresh container each time)
es-temp:
	docker run --rm -d --name temp-elasticsearch \
		-p 9200:9200 -p 9300:9300 \
		-e "discovery.type=single-node" \
		-e "xpack.security.enabled=false" \
		-e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
		docker.elastic.co/elasticsearch/elasticsearch:8.11.0
	@echo "Waiting for temporary Elasticsearch to be ready..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then \
			echo "✅ Temporary Elasticsearch is ready at http://localhost:9200"; \
			echo "💡 Run 'docker stop temp-elasticsearch' to stop it"; \
			exit 0; \
		fi; \
		echo "Waiting... ($$i/30)"; \
		sleep 2; \
	done; \
	echo "❌ Temporary Elasticsearch failed to start within 60 seconds"

test-es:
	@echo "Testing Elasticsearch retriever..."
	poetry run python test_elasticsearch.py

run-en-synth:
	poetry run python eval_en_synth.py

run-ja:
	poetry run python eval_ja.py

run-all: es-start
	@echo "=========================================="
	@echo "Running English synthetic evaluation..."
	@echo "=========================================="
	poetry run python eval_en_synth.py
	@echo "\n=========================================="
	@echo "Running Japanese real data evaluation..."
	@echo "=========================================="
	poetry run python eval_ja.py
	@echo "\n=========================================="
	@echo "Both evaluations completed!"
	@echo "=========================================="

format:
	poetry run black .

lint:
	poetry run flake8 .

check-results:
	@echo "English synthetic results:"
	@cat approaches/comparison_table_en_synth.md
	@echo "\nJapanese real data results:"
	@cat approaches/comparison_table_ja.md
