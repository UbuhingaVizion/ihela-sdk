# Contributing to ihela-sdk

## Setup

```bash
git clone git@github.com:UbuhingaVizion/ihela-sdk.git
cd ihela-sdk

# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

## Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=ihela_sdk

# Specific test file
uv run pytest tests/test_merchant_client.py

# Via tox (all environments)
uv run tox
```

## Linting

```bash
# Format and lint
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Type Checking

```bash
uv run mypy src/
```

## Building

```bash
uv build
```

## Pull Requests

1. Fork the repository
2. Create a feature branch from `develop`
3. Make your changes
4. Ensure tests pass and lint is clean
5. Submit a PR to `develop`

## Code Style

- Follow existing code conventions
- Use type hints for all public methods
- Keep HTTP calls with explicit `timeout=` parameters
- Add tests for new functionality
