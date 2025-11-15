#!/bin/bash
# Pre-commit hook to run linting and formatting

echo "Running pre-commit checks..."

# Run linting
echo "→ Running linter..."
if command -v ruff &> /dev/null; then
    ruff check . || exit 1
elif command -v flake8 &> /dev/null; then
    flake8 . || exit 1
else
    echo "  No linter found (install ruff or flake8)"
fi

# Run formatter
echo "→ Running formatter..."
if command -v black &> /dev/null; then
    black --check . || {
        echo "  Code needs formatting. Run: black ."
        exit 1
    }
else
    echo "  No formatter found (install black)"
fi

# Run type checker
echo "→ Running type checker..."
if command -v mypy &> /dev/null; then
    mypy . || exit 1
else
    echo "  No type checker found (install mypy)"
fi

echo "✓ All pre-commit checks passed!"
