# Contributing to Basement Cowboy

Thank you for your interest in contributing to Basement Cowboy! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all skill levels.

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- A code editor (VS Code recommended)

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/basement-cowboy.git
   cd basement-cowboy
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Run the setup wizard:
   ```bash
   python scripts/setup_wizard.py
   ```

## Development Workflow

### Creating a Branch

Create a branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Make your changes
2. Write or update tests
3. Run tests locally:
   ```bash
   pytest
   ```
4. Check code style:
   ```bash
   flake8 app/ scraper/ tests/
   black --check app/ scraper/ tests/
   ```

### Committing

Write clear commit messages:

```
feat: Add article deduplication service

- Implement fuzzy title matching
- Add URL normalization
- Include unit tests
```

Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting changes
- `chore:` Maintenance tasks

### Submitting a Pull Request

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template

4. Wait for review

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names

```python
# Good
def calculate_article_score(article: Article, weights: RankingWeights) -> float:
    """Calculate the ranking score for an article."""
    total_score = 0.0
    # ...
    return total_score

# Bad
def calc(a, w):
    s = 0
    # ...
    return s
```

### Documentation

- Use docstrings for all public functions and classes
- Follow Google style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When something is wrong.
    """
```

### Tests

- Write tests for new features
- Maintain test coverage above 70%
- Use descriptive test names:

```python
class TestArticleService:
    def test_create_article_with_valid_data(self):
        """Test creating an article with valid data."""
        pass

    def test_create_article_raises_error_on_invalid_url(self):
        """Test that creating article with invalid URL raises error."""
        pass
```

## Project Structure

```
basement-cowboy/
├── app/
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   ├── utils/        # Utilities
│   ├── templates/    # HTML templates
│   └── static/       # CSS, JS, images
├── scraper/          # Scraping modules
├── scripts/          # CLI tools
├── tests/            # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/             # Documentation
└── config/           # Configuration files
```

## Areas for Contribution

### High Priority

- [ ] Test coverage improvements
- [ ] Documentation improvements
- [ ] Bug fixes
- [ ] Performance optimizations

### Feature Ideas

- Additional news source parsers
- New ranking criteria
- Export formats (RSS, Atom)
- Email notifications
- Scheduled scraping
- Multi-language support

### Good First Issues

Look for issues labeled `good first issue` on GitHub.

## Review Process

1. A maintainer will review your PR
2. They may request changes
3. Make requested changes and push
4. Once approved, your PR will be merged

## Getting Help

- Open an issue for questions
- Join discussions on GitHub
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for contributing to Basement Cowboy! 🤠
