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

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
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

Run formatters before committing:
```bash
black .
ruff check . --fix
```

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Reference issue numbers when applicable

## Code of Conduct

Please be respectful and inclusive in all interactions. We want this to be a welcoming environment for everyone.

## Questions?

Feel free to open an issue for any questions about contributing.