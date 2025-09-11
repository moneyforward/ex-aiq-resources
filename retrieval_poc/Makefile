install:
	poetry install

run-en-synth:
	poetry run python eval_en_synth.py

run-ja:
	poetry run python eval_ja.py

run: run-en-synth

run-all:
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
