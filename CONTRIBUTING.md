# Contributing to Django i18n No-Prefix

Thank you for your interest in contributing to django-i18n-noprefix! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

- Check if the issue already exists in the [issue tracker](https://github.com/jinto/django-i18n-noprefix/issues)
- Provide a clear description of the problem
- Include steps to reproduce the issue
- Mention your Django and Python versions

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request with a clear description

### Development Setup

1. Clone your fork:
```bash
git clone git@github.com:your-username/django-i18n-noprefix.git
cd django-i18n-noprefix
```

2. Use the setup script (recommended):
```bash
./scripts/setup-dev.sh
```

Or manually:

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_i18n_noprefix

# Run specific test file
pytest tests/test_middleware.py
```

### Code Style

- We use [Black](https://github.com/psf/black) for code formatting
- We use [Ruff](https://github.com/charliermarsh/ruff) for linting
- Maximum line length is 88 characters
- Type hints are encouraged for better code clarity

Run formatters before committing:
```bash
make format  # Or manually:
black .
ruff check . --fix
```

Pre-commit hooks will automatically check code style:
```bash
pre-commit run --all-files
```

### CI/CD Process

All pull requests are automatically tested with:

1. **Test Matrix**: Python 3.8-3.12 × Django 4.2-5.1
2. **Code Quality**: Black, Ruff, MyPy
3. **Coverage**: Minimum 70% code coverage required
4. **Pre-commit**: All hooks must pass

#### GitHub Actions Workflows

- **Tests** (`test.yml`): Runs on every push and PR
- **Code Quality** (`quality.yml`): Checks code style and linting
- **Dependabot**: Weekly dependency updates

#### Local Testing

Test against specific Python/Django versions:
```bash
# Test with specific Django version
pip install "Django~=5.0.0"
pytest

# Run the same checks as CI
make test
make lint
make typecheck
```

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Reference issue numbers when applicable

## Code of Conduct

Please be respectful and inclusive in all interactions. We want this to be a welcoming environment for everyone.

## Questions?

Feel free to open an issue for any questions about contributing.
