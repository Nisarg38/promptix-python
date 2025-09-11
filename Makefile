# Promptix Development Makefile
# ================================
# This Makefile provides convenient commands for development tasks

.PHONY: help install install-dev test test-all test-coverage lint format type-check security-audit clean build docs docs-serve pre-commit setup-dev ci-check release

# Default target
help: ## Show this help message
	@echo "Promptix Development Commands:"
	@echo "============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install package in current environment
	pip install -e .

install-dev: ## Install package with development dependencies
	pip install -e ".[dev]"
	pip install -r requirements-test.txt

setup-dev: install-dev ## Set up complete development environment
	pre-commit install
	@echo "Development environment setup complete!"

# Testing targets
test: ## Run tests with pytest
	pytest

test-all: ## Run all tests including slow tests
	pytest -m ""

test-coverage: ## Run tests with coverage report
	pytest --cov=promptix --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	pytest-watch --runner "pytest --cov=promptix --cov-report=term-missing"

# Code quality targets
lint: ## Run all linting tools
	@echo "Running flake8..."
	flake8 src/ tests/
	@echo "Running pydocstyle..."
	pydocstyle src/
	@echo "Running isort check..."
	isort --check-only src/ tests/
	@echo "Running black check..."
	black --check src/ tests/

format: ## Format code with black and isort
	@echo "Formatting with black..."
	black src/ tests/
	@echo "Sorting imports with isort..."
	isort src/ tests/

type-check: ## Run type checking with mypy
	mypy src/

# Security and audit targets
security-audit: ## Run security audit tools
	@echo "Running bandit security check..."
	bandit -r src/
	@echo "Running safety check..."
	safety check
	@echo "Checking for known vulnerabilities..."
	pip-audit

# Pre-commit and CI targets
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

ci-check: lint type-check test-coverage security-audit ## Run all CI checks locally
	@echo "All CI checks passed!"

# Documentation targets
docs: ## Generate documentation with Sphinx
	@echo "Building documentation..."
	sphinx-build -b html docs/ docs/_build/html

docs-serve: docs ## Build and serve documentation locally
	@echo "Serving documentation at http://localhost:8000"
	cd docs/_build/html && python -m http.server 8000

docs-clean: ## Clean documentation build files
	rm -rf docs/_build/

# Build and release targets
clean: ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean ## Build package distributions
	python -m build

release-test: build ## Upload to Test PyPI
	twine upload --repository testpypi dist/*

release: build ## Upload to PyPI
	twine upload dist/*

# Development helpers
shell: ## Start IPython shell with package loaded
	ipython -c "import promptix; print('Promptix loaded successfully')"

studio: ## Launch Promptix Studio
	promptix studio

version: ## Show current version
	python -c "import promptix; print(f'Promptix version: {promptix.__version__}')"

# Database/migration helpers (if applicable)
migrate: ## Run any database migrations (future use)
	@echo "No migrations to run currently"

# Performance and profiling
profile: ## Run performance profiling
	python -m cProfile -o profile.stats -m pytest tests/test_performance.py
	@echo "Profile saved to profile.stats"

benchmark: ## Run benchmark tests
	pytest tests/test_performance.py -v

# Environment management
freeze: ## Freeze current dependencies
	pip freeze > requirements-frozen.txt

update-deps: ## Update all dependencies to latest versions
update-deps: ## Update all dependencies to latest versions
	pip list --outdated
	@echo "To update, run: pip install --upgrade [package-name]"

# Git helpers
git-clean: ## Clean up git repository
	git clean -fdx
	git reset --hard HEAD

# Docker targets (for future use)
docker-build: ## Build Docker image
	@echo "Docker support not implemented yet"

docker-run: ## Run Docker container
	@echo "Docker support not implemented yet"

# Advanced development targets
complexity: ## Check code complexity
	@echo "Checking code complexity..."
	radon cc src/ -a

dead-code: ## Find dead code
	@echo "Finding dead code..."
	vulture src/

deps-check: ## Check for dependency issues
	@echo "Checking dependencies..."
	pipdeptree --warn fail

# Quick development cycle
dev-cycle: format lint type-check test ## Quick development cycle: format, lint, type-check, test

# Full quality check
quality: format lint type-check test-coverage security-audit docs ## Run full quality check

# Environment info
env-info: ## Show environment information
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Virtual environment: $(VIRTUAL_ENV)"
	@echo "Current directory: $(PWD)"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repository')"

# Config targets
show-config: ## Show current project configuration
	@echo "=== pyproject.toml ==="
	@cat pyproject.toml | head -30
	@echo "\n=== Pre-commit config ==="
	@cat .pre-commit-config.yaml

# Utilities
lines: ## Count lines of code
	@echo "Lines of code in src/:"
	@find src/ -name "*.py" -exec wc -l {} + | tail -1
	@echo "Lines of code in tests/:"
	@find tests/ -name "*.py" -exec wc -l {} + | tail -1

todo: ## Find TODO comments in code
	@echo "TODO items in codebase:"
	@grep -rn "TODO\|FIXME\|XXX\|HACK" src/ tests/ --include="*.py" || echo "No TODO items found"

# Debug targets
debug-test: ## Run specific test with debugging
	pytest -xvs --pdb

debug-install: ## Debug installation issues
	pip install -e . -v

# Documentation helpers
docstring-check: ## Check docstring coverage
	@echo "Checking docstring coverage..."
	interrogate src/ -v

spelling-check: ## Check spelling in documentation
	@echo "Spell checking not configured yet"

# Performance monitoring
memory-profile: ## Profile memory usage
	python -m memory_profiler tests/test_performance.py

# Legacy support cleanup
legacy-clean: ## Clean up legacy files and patterns
	@echo "Checking for legacy patterns..."
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
