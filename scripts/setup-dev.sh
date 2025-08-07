#!/bin/bash

# Django i18n No-Prefix Development Environment Setup Script
# This script sets up a complete development environment for contributors

set -e  # Exit on error

# Color definitions for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR=".venv"
MIN_PYTHON_VERSION="3.8"
LOG_FILE="$PROJECT_ROOT/setup.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    log "INFO: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

print_step() {
    echo -e "\n${CYAN}▶ $1${NC}"
    log "STEP: $1"
}

# Header
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Django i18n No-Prefix Development Setup Script      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Initialize log file
echo "=== Setup started at $(date) ===" > "$LOG_FILE"
print_info "Log file: $LOG_FILE"

# Change to project root
cd "$PROJECT_ROOT"

# Step 1: Check operating system
print_step "Detecting operating system..."
case "$(uname -s)" in
    Linux*)     OS="Linux";;
    Darwin*)    OS="Mac";;
    CYGWIN*|MINGW*|MSYS*) OS="Windows";;
    *)          OS="Unknown";;
esac
print_success "Operating System: $OS"

# Step 2: Check Python installation
print_step "Checking Python installation..."

# Find Python command
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [ "$(printf '%s\n' "$MIN_PYTHON_VERSION" "$version" | sort -V | head -n1)" = "$MIN_PYTHON_VERSION" ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python $MIN_PYTHON_VERSION or higher is required but not found."
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "Found $PYTHON_VERSION"

# Step 3: Check for package managers
print_step "Checking package managers..."

USE_UV=false
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1)
    print_success "Found uv: $UV_VERSION"
    USE_UV=true
else
    print_info "uv not found, will use pip"
    print_info "Consider installing uv for faster dependency installation:"
    print_info "  curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Step 4: Create virtual environment
print_step "Setting up virtual environment..."

if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists at $VENV_DIR"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        print_info "Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    if [ "$USE_UV" = true ]; then
        print_info "Creating virtual environment with uv..."
        uv venv "$VENV_DIR"
    else
        print_info "Creating virtual environment with venv..."
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi
    print_success "Virtual environment created"
fi

# Step 5: Activate virtual environment
print_step "Activating virtual environment..."

# Determine activation script based on OS
if [ "$OS" = "Windows" ]; then
    ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
fi

if [ -f "$ACTIVATE_SCRIPT" ]; then
    source "$ACTIVATE_SCRIPT"
    print_success "Virtual environment activated"
else
    print_error "Could not find activation script at $ACTIVATE_SCRIPT"
    exit 1
fi

# Step 6: Upgrade pip
print_step "Upgrading pip..."
if [ "$USE_UV" = true ]; then
    uv pip install --upgrade pip
else
    pip install --upgrade pip
fi
print_success "pip upgraded"

# Step 7: Install dependencies
print_step "Installing project dependencies..."

if [ "$USE_UV" = true ]; then
    print_info "Installing with uv (fast mode)..."
    uv pip install -e ".[dev]"
else
    print_info "Installing with pip..."
    pip install -e ".[dev]"
fi
print_success "Dependencies installed"

# Step 8: Install pre-commit hooks
print_step "Setting up pre-commit hooks..."

if [ -f ".pre-commit-config.yaml" ]; then
    print_info "Installing pre-commit hooks..."

    # Check if pre-commit is installed
    if ! command -v pre-commit &> /dev/null; then
        print_info "Installing pre-commit..."
        if [ "$USE_UV" = true ]; then
            uv pip install pre-commit
        else
            pip install pre-commit
        fi
    fi

    # Install the git hooks
    pre-commit install
    print_success "Pre-commit hooks installed"

    # Run on all files to check current status
    print_info "Checking code with pre-commit..."
    if pre-commit run --all-files; then
        print_success "All pre-commit checks passed!"
    else
        print_warning "Some pre-commit checks failed. Run 'make pre-commit' to see details."
        print_info "Many issues can be auto-fixed by running the hooks again."
    fi
else
    print_warning "No .pre-commit-config.yaml found, skipping pre-commit setup"
    print_info "Run 'make pre-commit-install' to set up pre-commit hooks later"
fi

# Step 9: Run initial tests
print_step "Running tests to verify installation..."

if pytest tests/ -v --tb=short -q; then
    print_success "All tests passed! Environment is ready."
else
    print_warning "Some tests failed, but environment is set up."
    print_info "Run 'pytest tests/ -v' for detailed test output."
fi

# Step 10: Create useful shortcuts
print_step "Creating development shortcuts..."

# Create a Makefile if it doesn't exist
if [ ! -f "Makefile" ]; then
    print_info "Creating Makefile with common commands..."
    cat > Makefile << 'EOF'
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
EOF
    print_success "Makefile created"
fi

# Create development documentation
print_step "Creating development documentation..."

mkdir -p docs
if [ ! -f "docs/development.md" ]; then
    cat > docs/development.md << 'EOF'
# Development Guide

## Quick Start

After running `scripts/setup-dev.sh`, your development environment is ready!

### Activate Virtual Environment

```bash
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### Common Commands

We provide a Makefile with common development commands:

- `make help` - Show all available commands
- `make test` - Run all tests
- `make coverage` - Run tests with coverage report
- `make format` - Format code with black and ruff
- `make lint` - Check code style
- `make typecheck` - Run mypy type checking
- `make clean` - Clean build artifacts
- `make run-example` - Run the example Django project

### Manual Commands

If you prefer not to use Make:

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=django_i18n_noprefix --cov-report=html

# Format code
black .
ruff check . --fix

# Type checking
mypy django_i18n_noprefix

# Run example project
cd example_project && python manage.py runserver
```

### Project Structure

```
django-i18n-noprefix/
├── django_i18n_noprefix/     # Main package
│   ├── middleware.py         # Core middleware
│   ├── views.py             # Language switching views
│   ├── utils.py             # Utility functions
│   └── templatetags/        # Template tags
├── tests/                   # Test suite
├── example_project/         # Demo Django project
├── scripts/                 # Development scripts
└── docs/                    # Documentation
```

### Testing

Run the full test suite:
```bash
make test
```

Run specific tests:
```bash
pytest tests/test_middleware.py -v
pytest tests/test_middleware.py::TestClass::test_method
```

Generate coverage report:
```bash
make coverage
# Open htmlcov/index.html in browser
```

### Code Quality

Before committing:
1. Format your code: `make format`
2. Check linting: `make lint`
3. Run tests: `make test`
4. Check types: `make typecheck`

### Troubleshooting

#### Virtual Environment Issues
- Ensure you're in the project root directory
- Check Python version: `python --version` (needs 3.8+)
- Recreate venv: `rm -rf .venv && scripts/setup-dev.sh`

#### Import Errors
- Ensure virtual environment is activated
- Reinstall in development mode: `pip install -e ".[dev]"`

#### Test Failures
- Check Django version: `pip show django`
- Update dependencies: `pip install -e ".[dev]" --upgrade`

### IDE Setup

#### VS Code
Recommended extensions:
- Python
- Pylance
- Black Formatter
- Ruff

Settings (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm
1. Mark `django_i18n_noprefix` as Sources Root
2. Set Python interpreter to `.venv/bin/python`
3. Enable Django support with `example_project` as Django project root

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.
EOF
    print_success "Development documentation created"
fi

# Final summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 Development Environment Ready! 🎉          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
print_info "Next steps:"
echo "  1. Activate virtual environment:"
echo "     ${CYAN}source $ACTIVATE_SCRIPT${NC}"
echo ""
echo "  2. Run tests:"
echo "     ${CYAN}make test${NC} or ${CYAN}pytest tests/${NC}"
echo ""
echo "  3. Start the example project:"
echo "     ${CYAN}make run-example${NC}"
echo ""
echo "  4. See all available commands:"
echo "     ${CYAN}make help${NC}"
echo ""
print_info "Documentation: ${BLUE}docs/development.md${NC}"
print_info "Need help? Check the troubleshooting section or open an issue."
echo ""

# Save environment info
cat > .env.development << EOF
# Development Environment Information
# Generated by setup-dev.sh on $(date)
PYTHON_VERSION=$PYTHON_VERSION
VENV_PATH=$PROJECT_ROOT/$VENV_DIR
OS=$OS
USE_UV=$USE_UV
SETUP_DATE=$(date -Iseconds)
EOF

print_success "Environment configuration saved to .env.development"

# Reminder about activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo ""
    print_warning "Don't forget to activate the virtual environment!"
    echo "     ${CYAN}source $ACTIVATE_SCRIPT${NC}"
fi

log "=== Setup completed successfully at $(date) ==="
