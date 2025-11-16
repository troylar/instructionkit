# Code Quality Guidelines

## Principles

Follow these code quality principles when writing code:

1. **Readability First**: Code is read more often than it's written
2. **DRY (Don't Repeat Yourself)**: Extract common patterns into reusable functions
3. **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones
4. **YAGNI (You Ain't Gonna Need It)**: Don't add functionality until it's needed

## Best Practices

### Naming Conventions
- Use descriptive variable names that explain intent
- Functions should be verbs (e.g., `calculate_total`, `fetch_data`)
- Classes should be nouns (e.g., `UserAccount`, `DataProcessor`)
- Constants should be UPPER_CASE

### Code Organization
- Keep functions small and focused (single responsibility)
- Limit function parameters (max 3-4 recommended)
- Use early returns to reduce nesting
- Group related functionality together

### Error Handling
- Handle errors explicitly, don't swallow exceptions
- Provide meaningful error messages
- Fail fast and fail loudly
- Use custom exceptions for domain-specific errors

### Comments and Documentation
- Write self-documenting code first
- Add comments for "why" not "what"
- Document public APIs with docstrings
- Keep comments up-to-date with code changes

## Code Review Checklist

When reviewing code, check for:
- [ ] Code follows project style guide
- [ ] All functions have appropriate tests
- [ ] No hardcoded values (use configuration)
- [ ] Error cases are handled
- [ ] Code is properly documented
- [ ] Performance implications considered
- [ ] Security vulnerabilities addressed
