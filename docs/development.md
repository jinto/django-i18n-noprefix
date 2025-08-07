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

## Project Structure

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

## Testing

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

## Code Quality

Before committing:
1. Format your code: `make format`
2. Check linting: `make lint`
3. Run tests: `make test`
4. Check types: `make typecheck`

## Troubleshooting

### Virtual Environment Issues
- Ensure you're in the project root directory
- Check Python version: `python --version` (needs 3.8+)
- Recreate venv: `rm -rf .venv && scripts/setup-dev.sh`

### Import Errors
- Ensure virtual environment is activated
- Reinstall in development mode: `pip install -e ".[dev]"`

### Test Failures
- Check Django version: `pip show django`
- Update dependencies: `pip install -e ".[dev]" --upgrade`

## IDE Setup

### VS Code
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

### PyCharm
1. Mark `django_i18n_noprefix` as Sources Root
2. Set Python interpreter to `.venv/bin/python`
3. Enable Django support with `example_project` as Django project root

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.