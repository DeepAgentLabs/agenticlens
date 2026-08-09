.DEFAULT_GOAL := help

.PHONY: help install lint format format-check typecheck test test-cov clean build docs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (dev extras)
	uv sync --extra dev --extra docs

lint: ## Run ruff linter
	uv run ruff check .

format: ## Auto-format code
	uv run ruff format .

format-check: ## Check formatting without changes
	uv run ruff format --check .

typecheck: ## Run mypy type checking
	uv run mypy

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov --cov-report=term-missing

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info src/*.egg-info .mypy_cache .pytest_cache .ruff_cache site/

build: ## Build package distributions
	uv run python -m build

docs: ## Build documentation
	uv run mkdocs build

docs-serve: ## Serve docs locally
	uv run mkdocs serve

check: lint format-check typecheck test ## Run all quality gates
