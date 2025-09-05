.PHONY: validate build run demo docker-build docker-run clean install

# Default target
all: install demo

# Install dependencies
install:
	poetry install

# Validation
validate:
	poetry run python validate_rulebook.py --schema expense_rulebook.schema.json --rulebook expense_rulebook.json

# Build demo (placeholder for now - will be React build later)
demo:
	@echo "Demo page ready at static/index.html"
	@echo "Run 'make run' to start server"

# Development
build: install

run:
	poetry run ruler-server

# Docker
docker-build:
	docker build -t ruler-demo .

docker-run:
	docker run --name ruler-demo-container -p 8810:8810 ruler-demo

# Cleanup
clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	poetry env remove --all
	docker container prune -f
