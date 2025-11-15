#!/bin/bash
# Run test suite with coverage

echo "Running test suite..."

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest not found. Install with: pip install pytest pytest-cov"
    exit 1
fi

# Run tests with coverage
pytest \
    --cov \
    --cov-report=term-missing \
    --cov-report=html \
    -v \
    "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ All tests passed!"
    echo "  Coverage report: htmlcov/index.html"
else
    echo ""
    echo "✗ Tests failed with exit code: $exit_code"
fi

exit $exit_code
