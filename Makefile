# Django i18n No-Prefix Development Makefile

.PHONY: help
help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

.PHONY: install
install:  ## Install development dependencies
	pip install -e ".[dev]"

.PHONY: test
test:  ## Run all tests
	pytest tests/ -v

.PHONY: test-fast
test-fast:  ## Run tests in parallel (faster)
	pytest tests/ -n auto

.PHONY: coverage
coverage:  ## Run tests with coverage report
	pytest tests/ --cov=django_i18n_noprefix --cov-report=html --cov-report=term

.PHONY: format
format:  ## Format code with black
	black .
	ruff check . --fix

.PHONY: lint
lint:  ## Check code style
	black --check .
	ruff check .

.PHONY: typecheck
typecheck:  ## Run type checking with mypy
	mypy django_i18n_noprefix

.PHONY: clean
clean:  ## Clean build artifacts
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.PHONY: run-example
run-example:  ## Run the example project
	cd example_project && python manage.py runserver

.PHONY: migrations
migrations:  ## Make and run migrations for example project
	cd example_project && python manage.py makemigrations
	cd example_project && python manage.py migrate

.PHONY: messages
messages:  ## Update translation messages
	cd example_project && python manage.py makemessages -l ko -l ja
	cd example_project && python manage.py compilemessages

.PHONY: docs
docs:  ## Build documentation
	@echo "Documentation building not yet configured"

.PHONY: build
build:  ## Build distribution packages
	python -m build

.PHONY: publish-test
publish-test:  ## Publish to TestPyPI
	twine upload --repository testpypi dist/*

.PHONY: publish
publish:  ## Publish to PyPI
	twine upload dist/*

.PHONY: pre-commit
pre-commit:  ## Run pre-commit on all files
	pre-commit run --all-files

.PHONY: pre-commit-install
pre-commit-install:  ## Install pre-commit hooks
	pre-commit install
	@echo "Pre-commit hooks installed! They will run automatically on git commit."

.PHONY: pre-commit-update
pre-commit-update:  ## Update pre-commit hooks to latest versions
	pre-commit autoupdate

.PHONY: quality
quality:  ## Run all quality checks (lint, typecheck, pre-commit)
	@echo "Running code quality checks..."
	@make lint
	@make typecheck
	@make pre-commit
