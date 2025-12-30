# Contributing to Quantis

Thank you for considering contributing to Quantis! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guide](#code-style-guide)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Updates](#documentation-updates)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Accept responsibility for mistakes and learn from them

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.9 or higher
- Node.js 16 or higher
- Git for version control
- Basic understanding of FastAPI, React, and ML concepts
- Familiarity with async/await patterns

### Finding Issues to Work On

- Browse [GitHub Issues](https://github.com/abrar2030/Quantis/issues)
- Look for `good-first-issue` label for beginner-friendly tasks
- Check `help-wanted` label for issues needing contributors
- Comment on an issue to express interest before starting work

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Quantis.git
cd Quantis

# Add upstream remote
git remote add upstream https://github.com/abrar2030/Quantis.git
```

### 2. Create Development Environment

```bash
# Run automated setup
./scripts/setup_quantis_env.sh

# Or manual setup:
cd code/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dev dependencies
cd ../..

# Frontend setup
cd web-frontend
npm install
cd ..
```

### 3. Create Feature Branch

```bash
# Always create a new branch for your work
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/bug-description
```

### 4. Start Development Services

```bash
# Start all services
./scripts/run_quantis.sh dev

# Or start individually:
# Terminal 1 - Backend
cd code && uvicorn api.app:app --reload

# Terminal 2 - Frontend
cd web-frontend && npm start
```

---

## How to Contribute

### Types of Contributions

1. **Bug Fixes**: Fix existing issues
2. **New Features**: Add new functionality
3. **Documentation**: Improve or add documentation
4. **Tests**: Increase test coverage
5. **Performance**: Optimize code for better performance
6. **Refactoring**: Improve code quality without changing behavior

### Contribution Workflow

1. **Discuss first** (for major changes):
   - Open an issue to discuss your idea
   - Get feedback from maintainers
   - Align on implementation approach

2. **Make changes**:
   - Write clean, well-documented code
   - Follow the code style guide
   - Add tests for new functionality
   - Update documentation

3. **Test thoroughly**:
   - Run test suite: `./scripts/test_quantis.sh`
   - Test manually in development environment
   - Ensure no regressions

4. **Submit Pull Request**:
   - Follow PR template
   - Reference related issues
   - Provide clear description

---

## Code Style Guide

### Python Style (PEP 8)

```python
# Use 4 spaces for indentation
# Maximum line length: 88 characters (Black formatter)

# Good
def calculate_npv(rate: float, cash_flows: List[float]) -> float:
    """
    Calculate Net Present Value.

    Args:
        rate: Discount rate
        cash_flows: List of cash flow values

    Returns:
        Net present value
    """
    npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
    return npv

# Use type hints
from typing import List, Optional, Dict, Any

# Use descriptive variable names
user_email = "user@example.com"  # Good
x = "user@example.com"           # Bad

# Document complex logic
# Calculate moving average with 7-day window
rolling_mean = df['price'].rolling(window=7).mean()
```

### JavaScript/TypeScript Style

```typescript
// Use 2 spaces for indentation
// Prefer const over let, avoid var

// Good
const fetchModels = async (): Promise<Model[]> => {
  const response = await api.get('/models');
  return response.data;
};

// Use meaningful names
const isUserAuthenticated = true; // Good
const flag = true; // Bad

// Use arrow functions
const double = (x: number) => x * 2;

// Document complex components
/**
 * ModelTrainingForm component
 * Handles model training configuration and submission
 */
const ModelTrainingForm: React.FC<Props> = ({ model }) => {
  // Component implementation
};
```

### Code Formatting

Use automated formatters:

```bash
# Python: Black + isort
black code/
isort code/

# JavaScript/TypeScript: Prettier
npm run format

# Or use pre-commit hooks
pre-commit install
```

### Linting

```bash
# Python
pylint code/api/
flake8 code/api/
mypy code/api/

# JavaScript/TypeScript
npm run lint

# Run all linters
./scripts/linting.sh
```

---

## Testing Guidelines

### Writing Tests

```python
# Unit test example
import pytest
from api.endpoints.models import create_model

def test_create_model_success():
    """Test successful model creation."""
    model_data = {
        "name": "Test Model",
        "model_type": "lstm",
        "hyperparameters": {"hidden_size": 64}
    }
    result = create_model(model_data)
    assert result["name"] == "Test Model"
    assert result["model_type"] == "lstm"

def test_create_model_invalid_type():
    """Test model creation with invalid type."""
    model_data = {
        "name": "Test Model",
        "model_type": "invalid_type"
    }
    with pytest.raises(ValueError):
        create_model(model_data)
```

### Test Structure

```
tests/
├── unit/               # Unit tests (fast, isolated)
│   ├── test_models.py
│   ├── test_auth.py
│   └── test_data.py
├── integration/        # Integration tests (slower, multiple components)
│   ├── test_api.py
│   └── test_database.py
└── e2e/               # End-to-end tests (full workflow)
    └── test_prediction_workflow.py
```

### Running Tests

```bash
# All tests
./scripts/test_quantis.sh

# Unit tests only
pytest tests/unit/

# Specific test file
pytest tests/unit/test_models.py

# Specific test function
pytest tests/unit/test_models.py::test_create_model_success

# With coverage
pytest --cov=api --cov-report=html tests/
```

### Test Coverage Requirements

- New code must have **>80% coverage**
- Critical paths (auth, payments) require **>95% coverage**
- Add tests for:
  - Happy paths
  - Error conditions
  - Edge cases
  - Boundary conditions

---

## Documentation Updates

### When to Update Documentation

Update docs when you:

- Add new features or APIs
- Change existing behavior
- Fix bugs that affect usage
- Improve performance significantly
- Add new configuration options

### Documentation Files to Update

| Change Type              | Files to Update                            |
| ------------------------ | ------------------------------------------ |
| New API endpoint         | `docs/API.md`                              |
| New CLI command          | `docs/CLI.md`                              |
| New feature              | `docs/FEATURE_MATRIX.md`, `docs/README.md` |
| Configuration change     | `docs/CONFIGURATION.md`                    |
| New troubleshooting item | `docs/TROUBLESHOOTING.md`                  |
| Architecture change      | `docs/ARCHITECTURE.md`                     |

### Documentation Style

- Use clear, concise language
- Include code examples
- Provide before/after comparisons
- Add diagrams where helpful
- Use tables for structured information
- Test all code examples before committing

### Example Documentation

````markdown
## New Feature: Batch Predictions

The API now supports batch predictions for improved performance.

**Endpoint**: `POST /predict/batch`

**Request:**
\```json
{
"model_id": 1,
"input_data_list": [
[0.1, 0.2, 0.3],
[0.4, 0.5, 0.6]
]
}
\```

**Response:**
\```json
{
"predictions": [...],
"total_predictions": 2,
"successful_predictions": 2
}
\```

**Example Usage:**
\```python
import requests

response = requests.post(
"http://localhost:8000/predict/batch",
json={"model_id": 1, "input_data_list": [[0.1, 0.2], [0.3, 0.4]]}
)
\```
````

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No merge conflicts with main branch
- [ ] Commit messages are clear and descriptive

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues

Fixes #123

## Testing

Describe testing performed

## Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed by self
```

### PR Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address any requested changes
4. **Approval**: PR approved by maintainer
5. **Merge**: Maintainer merges PR into main

### Commit Message Guidelines

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Code style changes (formatting)
refactor: Code refactoring
test: Test additions or changes
chore: Build/tool changes

# Examples:
feat(api): add batch prediction endpoint
fix(auth): resolve JWT token expiration bug
docs(readme): update installation instructions
test(models): add LSTM training tests
```

---

## Issue Guidelines

### Reporting Bugs

Use this template:

```markdown
## Bug Description

Clear description of the bug

## Steps to Reproduce

1. Step one
2. Step two
3. See error

## Expected Behavior

What should happen

## Actual Behavior

What actually happens

## Environment

- OS: Ubuntu 22.04
- Python: 3.11
- Quantis Version: 1.0.0

## Logs/Screenshots

Include relevant logs or screenshots
```

### Feature Requests

```markdown
## Feature Description

What feature would you like?

## Use Case

Why is this feature useful?

## Proposed Solution

How might this be implemented?

## Alternatives Considered

Other approaches considered
```

---

## Development Best Practices

### 1. Keep Changes Focused

- One feature/fix per PR
- Avoid mixing refactoring with features
- Split large changes into smaller PRs

### 2. Write Clear Commit Messages

```bash
# Good
feat(prediction): add confidence score calculation

# Bad
update files
```

### 3. Test Edge Cases

```python
# Test edge cases
def test_npv_with_zero_rate():
    """Test NPV calculation with zero discount rate."""
    result = calculate_npv(0.0, [100, 200])
    assert result == 300  # Sum of cash flows

def test_npv_with_empty_list():
    """Test NPV calculation with empty cash flows."""
    result = calculate_npv(0.1, [])
    assert result == 0
```

### 4. Use Type Hints

```python
# Good - with type hints
def train_model(
    data_path: str,
    epochs: int = 100,
    batch_size: int = 32
) -> dict:
    pass

# Bad - no type hints
def train_model(data_path, epochs=100, batch_size=32):
    pass
```

### 5. Handle Errors Gracefully

```python
# Good
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.exception("Unexpected error")
    raise HTTPException(status_code=500, detail="Internal error")

# Bad
result = risky_operation()  # No error handling
```

---

## Code Review Checklist

For reviewers:

- [ ] Code follows style guide
- [ ] Logic is clear and well-documented
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Error handling is appropriate

---

## License

By contributing to Quantis, you agree that your contributions will be licensed under the MIT License.

---
