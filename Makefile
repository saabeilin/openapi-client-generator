.PHONY: clean lint format test unittest coverage

# Python settings
PYTHON = python3
PYTEST = pytest
PYTEST_ARGS = --verbose --color=yes
COVERAGE_ARGS = --cov=openapi_client_generator --cov-report=term --cov-report=html

# Directories
SRC_DIR = openapi_client_generator
TEST_DIR = tests

clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	@echo "Linting code..."
	ruff check $(SRC_DIR) $(TEST_DIR)

format:
	@echo "Formatting code..."
	ruff format $(SRC_DIR) $(TEST_DIR)

test:
	@echo "Running tests..."
	$(PYTEST) $(PYTEST_ARGS) $(TEST_DIR)

unittest: test

coverage:
	@echo "Running tests with coverage..."
	$(PYTEST) $(PYTEST_ARGS) $(COVERAGE_ARGS) $(TEST_DIR)

all: clean lint format test
