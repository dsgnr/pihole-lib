.PHONY: help install test test-cov lint format type-check clean build publish pre-commit check docker-up docker-down docker-logs docs docs-clean docs-apidoc

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	poetry install

test: ## Run all tests
	poetry run pytest -v

test-cov: ## Run tests with coverage
	poetry run pytest --cov=pihole_lib --cov-report=html --cov-report=term-missing

lint: ## Run linting
	poetry run ruff check .

format: ## Format code
	poetry run ruff format .

format-check: ## Format code
	poetry run ruff format . --check

type-check: ## Run type checking
	poetry run mypy pihole_lib/

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ docs/_build/ docs/lib/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete."

build: clean ## Build package
	poetry build

publish: build ## Publish to PyPI
	poetry publish

pre-commit: ## Install pre-commit hooks
	poetry run pre-commit install

check: lint type-check test ## Run all checks

docker-up: ## Start Pi-hole test container
	docker-compose -f tests/docker-compose.test.yml up -d

docker-down: ## Stop Pi-hole test container
	docker-compose -f tests/docker-compose.test.yml down

docker-logs: ## Show Pi-hole container logs
	docker-compose -f tests/docker-compose.test.yml logs -f pihole

docs-apidoc: ## Generate API documentation
	poetry run sphinx-apidoc -o docs/lib pihole_lib

docs: docs-apidoc ## Build documentation
	poetry run sphinx-build -b html docs docs/_build/html

docs-clean: ## Clean documentation build artifacts
	rm -rf docs/_build docs/lib
