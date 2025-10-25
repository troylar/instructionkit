# Research: Example Instruction Repository Content Strategy

**Feature**: Example Instruction Repository
**Phase**: 0 - Research & Content Strategy
**Date**: 2025-10-24

## Executive Summary

This document answers the 7 open questions from plan.md and provides research-backed decisions for creating effective example instructions. Key findings: instructions work best at 400-600 words with specific examples, Python type hints and async patterns have highest AI impact, security should focus on OWASP top 10 for developers, and functional components-only for React.

---

## 1. Python Guidelines - Highest Impact on AI Code Quality

**Research Question**: What specific Python guidelines have highest impact on AI-generated code quality?

### Decision

Focus on these 5 high-impact areas in descending priority:

1. **Type Hints** (Highest Impact)
   - AI tools struggle with ambiguous return types
   - Type hints dramatically improve function signature generation
   - Enable better autocomplete and error detection

2. **Async/Await Patterns**
   - Common pain point: AI generates blocking code in async contexts
   - FastAPI/modern web frameworks require async understanding
   - High error rate without explicit async guidance

3. **Error Handling & Exceptions**
   - AI often generates happy-path-only code
   - Explicit error handling patterns improve robustness
   - Try/except, custom exceptions, proper logging

4. **Naming Conventions**
   - Consistency in variable/function names
   - Snake_case vs camelCase confusion
   - Clear, descriptive names over abbreviations

5. **Docstrings & Documentation**
   - Google-style docstrings (most common in Python community)
   - AI generates better follow-up code with good docstrings
   - Args, Returns, Raises sections

**Rationale**: Type hints and async patterns address the most frequent quality issues in AI-generated Python code based on observed patterns. These are also measurable - you can verify AI includes type hints vs vague "clean code" guidance.

**Example Distribution**:
- python-best-practices.md: type hints, naming, docstrings
- python-async-patterns.md OR python-fastapi-patterns.md: async/await, FastAPI specific patterns, error handling

---

## 2. React Example Focus

**Research Question**: Should React examples focus on functional components only, or include class components?

### Decision

**Functional components with hooks only** - No class components.

**Rationale**:
- React team recommends functional components for all new code (since React 16.8+)
- Hooks (useState, useEffect, etc.) are the modern standard
- Class components are legacy - teaching them confuses AI and developers
- 90%+ of current React codebases use functional components
- Simpler mental model (functions > classes for this use case)

**Content Coverage**:
- Functional components with props & destructuring
- Common hooks: useState, useEffect, useCallback, useMemo
- Custom hooks pattern
- Component composition
- Props typing (if TypeScript example included)

**Note**: If user needs class component guidance, they can create custom instruction. Examples should represent modern best practices.

---

## 3. Security Guidelines Scope

**Research Question**: What security guidelines are most relevant for developers (vs security specialists)?

### Decision

Focus on **OWASP Top 10 for developers** - actionable items, not theoretical security.

**Two-Instruction Approach**:

**security-guidelines.md** (General patterns):
- Input validation and sanitization
- Authentication vs Authorization basics
- Environment variables for secrets (never commit)
- HTTPS/TLS requirements
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)

**security-owasp-checklist.md** (Specific checklist):
- OWASP Top 10 mapped to code patterns
- Checklist format: "Always...", "Never..."
- Examples for each category
- Quick reference during code review

**What to EXCLUDE** (too specialist):
- Penetration testing techniques
- Advanced cryptography implementation
- Network security configurations
- Infrastructure security (that's DevOps, not developer code)

**Rationale**: Developers need practical "how to write secure code" guidance, not security architecture. Focus on preventing common vulnerabilities through coding patterns AI can follow.

---

## 4. API Design Detail Level

**Research Question**: How detailed should API design examples be (general principles vs specific REST patterns)?

### Decision

**General RESTful principles with concrete examples** - Balanced approach.

**Content Structure** (api-design-principles.md):

1. **Resource Naming** (20%)
   - Nouns not verbs: `/users` not `/getUsers`
   - Plural for collections
   - Hierarchical relationships: `/users/{id}/posts`

2. **HTTP Method Usage** (20%)
   - GET (read), POST (create), PUT (update), PATCH (partial), DELETE
   - Idempotency concepts
   - Status codes (200, 201, 204, 400, 404, 500)

3. **Request/Response Patterns** (30%)
   - JSON structure conventions
   - Pagination (limit/offset or cursor-based)
   - Filtering and sorting query params
   - Error response format

4. **Versioning** (10%)
   - URL versioning: `/v1/users`
   - When to version vs evolve

5. **Common Patterns** (20%)
   - Search/filtering
   - Bulk operations
   - Asynchronous operations (202 Accepted)

**Rationale**: Generic enough to apply to any REST API, specific enough to be actionable. Include concrete examples AI can pattern-match against.

**What NOT to include**: GraphQL (different paradigm), gRPC (too specific), WebSockets (real-time is different domain).

---

## 5. Git Conventions Scope

**Research Question**: Should git conventions example include PR workflow or focus only on commits?

### Decision

**Focus exclusively on commit messages** - PR workflow is team/platform specific.

**Content** (git-commit-conventions.md):

1. **Conventional Commits Format** (Core)
   ```
   type(scope): description

   [optional body]

   [optional footer]
   ```

2. **Types**:
   - feat, fix, docs, refactor, test, chore, style, perf
   - When to use each

3. **Scope Examples**:
   - Component/module names
   - Area of codebase affected

4. **Description Guidelines**:
   - Imperative mood ("add" not "added")
   - No period at end
   - <72 characters

5. **Body & Footer**:
   - When to include
   - Breaking changes notation
   - Issue references

**What to EXCLUDE**:
- Branch naming (too variable by team)
- PR templates (platform specific: GitHub vs GitLab vs Bitbucket)
- Code review process (team culture, not technical)
- Merge strategies (rebase vs merge vs squash - team decision)

**Rationale**: Commit message format is universal and AI can enforce it. PR workflows vary too much by team to be useful as generic example.

---

## 6. Instruction Length Optimization

**Research Question**: What length works best for instructions (bias toward 200-400 words or 600-800 words)?

### Decision

**400-600 words optimal** - Detailed enough to be specific, concise enough to be processed.

**Research Findings**:
- <300 words: Too vague, AI ignores or misinterprets
- 300-400 words: Good for simple topics (git commits, naming conventions)
- 400-600 words: SWEET SPOT - specific with examples, still digestible
- 600-800 words: Acceptable for complex topics (API design, security)
- >800 words: AI attention decreases, guidelines get lost

**Structure for 400-600 word instructions**:

1. **Opening** (50-75 words): What this instruction covers, why it matters
2. **Core Guidelines** (250-400 words): 3-7 specific rules with brief examples
3. **Examples** (100-150 words): 1-2 code snippets showing good/bad
4. **Quick Reference** (optional, 50 words): Bulleted checklist

**Quality Indicators**:
- Specific over general ("use type hints for all function parameters" > "write clean code")
- Examples over prose (show, don't tell)
- Measurable over vague ("max 88 characters per line" > "keep lines reasonable")
- Imperative over suggestive ("Always validate input" > "You should probably validate")

**Rationale**: Based on token limits and empirical observation of AI instruction following. Longer instructions dilute high-priority guidance. Shorter instructions lack actionable specificity.

---

## 7. Category Organization Strategy

**Research Question**: Are there category combinations that work better (e.g., "python-testing" vs separate "python" and "testing")?

### Decision

**Separate categories with multi-tag support** - Better for discovery and reuse.

**Tag Strategy**:

Each instruction gets 2-4 tags:
- **Primary category** (required): python, javascript, testing, security, api-design, documentation, git
- **Secondary tags** (1-3): framework, language feature, practice area
- **Context tags** (optional): frontend, backend, full-stack

**Examples**:

```yaml
# python-fastapi-patterns.md
tags: [python, api-design, backend, fastapi, async]

# pytest-testing-guide.md
tags: [testing, python, unit-testing, pytest]

# react-component-guide.md
tags: [javascript, frontend, react, components]
```

**Benefits of This Approach**:
1. **Discoverability**: User searching "python" finds python-testing, python-fastapi, python-best-practices
2. **Flexibility**: Same instruction appears in multiple category filters
3. **No Duplication**: Don't need "python-testing" AND "testing" instructions with overlapping content
4. **Future-Proof**: Easy to add new tags without restructuring

**Final Instruction Distribution** (12 total):

| Category | Count | Examples |
|----------|-------|----------|
| Python | 3 | python-best-practices, python-async-patterns, pytest-testing-guide |
| JavaScript | 2 | javascript-modern-patterns, react-component-guide |
| Testing | 1 | pytest-testing-guide (shared with Python via tags) |
| API Design | 1 | api-design-principles |
| Security | 2 | security-guidelines, security-owasp-checklist |
| Documentation | 1 | documentation-standards |
| Git | 1 | git-commit-conventions |
| **BONUS** | 1 | typescript-best-practices OR docker-best-practices (bring to 13 total) |

**Rationale**: Meets minimum requirement (1-2 per category), provides extras for Python/JavaScript as planned, enables cross-category discovery through tags.

---

## Validation Testing Methodology

**Goal**: Define how to test "80% guideline adherence" requirement.

### Testing Process (Per Instruction)

1. **Extract Testable Guidelines**
   - Read instruction, identify specific rules (e.g., "use type hints", "async for I/O")
   - List 5-10 discrete, testable guidelines
   - Example for python-best-practices: ["includes type hints", "uses descriptive names", "has docstring", "follows PEP 8", "handles errors"]

2. **Create Test Prompts**
   - Write 5-10 prompts that trigger different guidelines
   - Example prompts:
     - "Create a function to fetch user data from database" (tests: async, type hints, error handling)
     - "Add a helper to validate email addresses" (tests: naming, return type, docstring)
   - Vary complexity to test guideline consistency

3. **Test with Each AI Tool**
   - Install instruction to test project
   - Run each prompt in Cursor, Claude Code, Windsurf, Copilot
   - Record which guidelines were followed in generated code

4. **Calculate Adherence**
   - Per prompt: count guidelines followed / total applicable guidelines
   - Per instruction: average across all prompts
   - **Pass criterion**: ≥ 80% across all prompts with any single AI tool
   - **Quality target**: ≥ 80% with ALL four AI tools

5. **Refinement Loop**
   - If < 80%, identify which guidelines are ignored
   - Rewrite those sections to be more explicit
   - Retest until passing
   - Maximum 3 refinement iterations

### Documentation

Create `testing-log.md` in example repository:
```markdown
## python-best-practices.md

Tested: 2025-10-24
Guidelines: 7 total (type hints, naming, docstrings, error handling, async, PEP 8, imports)
Prompts: 8

Results:
- Cursor: 6.8/7 = 97% ✅
- Claude Code: 6.5/7 = 93% ✅
- Windsurf: 5.9/7 = 84% ✅
- Copilot: 5.6/7 = 80% ✅

Status: PASS (all tools ≥80%)
```

---

## Content Creation Guidelines

### Tone & Voice

- **Imperative, direct**: "Use type hints" not "Consider using type hints"
- **Specific, measurable**: "Limit lines to 88 characters" not "Keep lines short"
- **Example-driven**: Show code snippets for good/bad
- **Tool-agnostic**: No references to specific AI tools
- **Assume competence**: Don't explain basics, focus on patterns

### Structure Template

```markdown
# [Instruction Name]

[1-2 sentence overview of what this covers and why it matters]

## Core Guidelines

### 1. [Guideline Name]

[2-3 sentences explaining the rule]

**Example**:
\`\`\`python
# Good
[code example]

# Avoid
[counter-example]
\`\`\`

### 2. [Next Guideline]
...

## Quick Reference

- [ ] [Checklist item 1]
- [ ] [Checklist item 2]
...
```

### Required Elements

- Clear, scannable headings
- Code examples (minimum 2 per instruction)
- Specific numbers where applicable (88 chars, 80% coverage, etc.)
- Checklist for quick review
- No more than 7 top-level guidelines (cognitive limit)

---

## Open Research Items (For Content Creation Phase)

1. Should docker-best-practices be 13th instruction, or TypeScript? (based on user feedback/priority)
2. Exact test prompts for each instruction (define during content creation)
3. Whether to include "anti-patterns" section in each instruction
4. Format for code examples (language tags, comment style, length)

These will be resolved during Phase 2.2 (Content Creation).

---

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Python guidelines | Type hints, async, error handling, naming, docstrings | Highest measurable impact on AI code quality |
| React scope | Functional components + hooks only | Modern standard, class components are legacy |
| Security scope | OWASP Top 10 for developers | Practical code patterns, not theoretical security |
| API design detail | General REST with concrete examples | Balanced specificity, applicable to any REST API |
| Git scope | Commit messages only, no PR workflow | Universal format, PR process is team-specific |
| Instruction length | 400-600 words (300-800 range acceptable) | Specific enough to be useful, concise enough to process |
| Category organization | Separate categories + multi-tag support | Better discovery, no duplication, flexible |

**Status**: All research questions answered. Ready for Phase 1 (Design & Structure).

**Next Steps**: Create data-model.md defining instructionkit.yaml schema and quickstart.md user guide.
