# Quickstart Guide: Example Instructions

**For**: New InstructionKit users and example repository contributors
**Last Updated**: 2025-10-24

## For New Users: Get Started in 2 Minutes

### Prerequisites

- InstructionKit installed: `pip install instructionkit`
- At least one AI coding tool: Cursor, Claude Code, Windsurf, or GitHub Copilot
- Git installed (usually already present)

### Step 1: Download the Example Repository (15 seconds)

```bash
inskit download --from https://github.com/troylar/instructionkit-examples
```

**What happens**:
- InstructionKit clones the repository to your local library (`~/.instructionkit/library/`)
- Validates the `instructionkit.yaml` format
- Makes 12 example instructions immediately available

**Expected output**:
```
🔄 Downloading repository...
   Source: https://github.com/troylar/instructionkit-examples

✓ Cloned to library: troylar-instructionkit-examples
✓ Found 12 instructions across 7 categories

📦 Repository Contents:
   • Python development (3)
   • JavaScript/TypeScript (3)
   • Testing (1)
   • API design (1)
   • Security (2)
   • Documentation (1)
   • Git workflows (1)

✨ Next: Run 'inskit install' to browse and install examples
```

---

### Step 2: Browse Examples (30 seconds)

```bash
inskit install
```

**What happens**:
- Opens interactive Terminal UI (TUI)
- Shows all instructions from all downloaded repositories
- Supports search and filtering

**TUI Navigation**:
- **Arrow keys** or **j/k**: Move up/down
- **Space**: Select/deselect instruction
- **/** (forward slash): Search by name or tag
- **Tab**: Switch between instruction list and install options
- **Enter**: Install selected instructions
- **Esc**: Cancel and exit

**Pro tip**: Search for your tech stack

Example searches:
- `/python` - Shows all Python-related instructions
- `/react` - React and JavaScript instructions
- `/testing` - Testing-related instructions
- `/security` - Security guidelines

---

### Step 3: Install Instructions to Your Project (30 seconds)

**In the TUI**:
1. Use `/python` to search for Python examples
2. Press **Space** on `python-best-practices` to select it
3. Press **Space** on `python-async-patterns` to select it
4. Verify your AI tools are checked (Cursor, Claude Code, etc.)
5. Press **Enter** or click "Install Selected"

**Confirmation screen shows**:
```
Installing 2 instructions to:
  /Users/you/projects/my-app

Files to be created:
  .cursor/rules/python-best-practices.mdc
  .cursor/rules/python-async-patterns.mdc
  .claude/rules/python-best-practices.md
  .claude/rules/python-async-patterns.md

Continue? [Y/n]
```

**Press Y to confirm**.

**What happens**:
- Instructions installed to project-specific directories
- Tracking file created: `.instructionkit/installations.json`
- Instructions immediately active in your AI coding tools

---

### Step 4: Verify Instructions Are Working (30 seconds)

Open your AI coding tool (Cursor, Claude Code, etc.) in the same project.

**Test prompt**: Ask AI to create something that should follow the installed instructions.

Example: If you installed `python-best-practices` and `python-async-patterns`:

**Prompt**: *"Create an async function to fetch user data from a database"*

**Expected AI output** (following instructions):
```python
from typing import Optional

async def fetch_user_by_id(user_id: int) -> Optional[dict]:
    """
    Fetch user data from database by user ID.

    Args:
        user_id: The unique identifier of the user

    Returns:
        User data dictionary if found, None otherwise

    Raises:
        DatabaseError: If database connection fails
    """
    try:
        async with get_db_connection() as conn:
            user = await conn.fetchone(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            return user
    except DatabaseError as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise
```

**Notice**:
- ✅ Type hints (`user_id: int`, `-> Optional[dict]`)
- ✅ Async/await pattern
- ✅ Docstring with Args, Returns, Raises
- ✅ Error handling with specific exception
- ✅ Descriptive naming

**Without instructions**, AI might generate:
```python
def get_user(id):
    user = db.get(id)
    return user
```

---

## Updating Examples (When New Versions Are Released)

```bash
inskit update --all
```

or update specific repository:

```bash
inskit update troylar-instructionkit-examples
```

**What happens**:
- Pulls latest changes from GitHub
- Reports new/updated instructions
- Already-installed instructions are NOT automatically updated (you control when)

**To get new instructions**: Run `inskit install` again and select new examples.

---

## Common Workflows

### Workflow 1: Python FastAPI Project

```bash
# Download examples (one-time)
inskit download --from https://github.com/troylar/instructionkit-examples

# Install Python + API instructions
inskit install
# In TUI: Select python-best-practices, python-async-patterns, api-design-principles, pytest-testing-guide

# Result: AI generates FastAPI code with type hints, async patterns, RESTful design, and testable structure
```

### Workflow 2: React Frontend Project

```bash
# Download examples (if not already done)
inskit download --from https://github.com/troylar/instructionkit-examples

# Install JavaScript + React instructions
inskit install
# In TUI: Select javascript-modern-patterns, react-component-guide, typescript-best-practices

# Result: AI generates modern React functional components with hooks, TypeScript types, and best practices
```

### Workflow 3: Security-Focused Development

```bash
# Install security instructions across project types
inskit install
# In TUI: Select security-guidelines, security-owasp-checklist, plus language-specific instructions

# Result: AI includes input validation, secure authentication patterns, and OWASP compliance in all generated code
```

---

## For Instruction Authors: Creating Quality Examples

If you want to create instructions similar to these examples or contribute improvements:

### Effective Instruction Structure

**Length**: 400-600 words (range: 300-800 acceptable)

**Format**:
```markdown
# [Instruction Title]

[1-2 sentence overview]

## Core Guidelines

### 1. [Specific, Actionable Rule]

[2-3 sentences explaining why and how]

**Example**:
\`\`\`python
# Good
[code showing correct pattern]

# Avoid
[code showing anti-pattern]
\`\`\`

[... 3-7 total guidelines]

## Quick Reference

- [ ] [Checklist item]
[... up to 7 items]
```

### Writing Tips

**Be Specific, Not Generic**:
- ❌ "Write clean code"
- ✅ "Use type hints for all function parameters and return values"

**Use Measurable Criteria**:
- ❌ "Keep functions short"
- ✅ "Limit functions to 50 lines or fewer"

**Show, Don't Tell**:
- Include code examples for every guideline
- Show good and bad patterns
- Use syntax highlighting with language tags

**Be Imperative**:
- ❌ "You should consider using async"
- ✅ "Use async/await for all I/O operations"

**Stay Tool-Agnostic**:
- No references to specific AI tools (Cursor, Claude, etc.)
- Focus on code patterns AI can recognize
- Should work equally well with Cursor, Claude Code, Windsurf, and Copilot

### Testing Your Instruction

**Goal**: 80% guideline adherence when tested with AI tools

1. **Extract testable guidelines** from your instruction (5-10 specific rules)
2. **Create test prompts** that exercise different guidelines
3. **Test with AI tool**: Install instruction, run prompts
4. **Calculate adherence**: Count how many guidelines AI followed
5. **Refine if < 80%**: Make guidelines more explicit, add examples
6. **Document results**: Record which AI tools tested and pass/fail

Example test log:
```
Instruction: python-best-practices
Guidelines: 7 total
Prompts tested: 8

Results:
- Cursor: 6.8/7 = 97% ✅
- Claude Code: 6.5/7 = 93% ✅
- Windsurf: 5.9/7 = 84% ✅
- Copilot: 5.6/7 = 80% ✅

Status: PASS
```

### Contributing Improvements

See `CONTRIBUTING.md` in the example repository for:
- How to submit instruction improvements
- Code review process
- Testing requirements
- Style guidelines

---

## Troubleshooting

### Issue: "Repository not found" when downloading

**Solution**: Check the URL is correct:
```bash
inskit download --from https://github.com/troylar/instructionkit-examples
```

Note: `https://` is required, repository name is case-sensitive.

---

### Issue: "No instructions appear in TUI"

**Possible causes**:
1. Repository download failed - check `inskit list library` to verify repository exists
2. instructionkit.yaml is malformed - check repository was cloned correctly
3. TUI crashed - restart with `inskit install`

**Solution**:
```bash
# Verify repository is in library
inskit list library

# Should show: troylar-instructionkit-examples

# If missing, re-download
inskit download --from https://github.com/troylar/instructionkit-examples
```

---

### Issue: "AI not following instructions"

**Possible causes**:
1. Instructions not installed to current project
2. Installed to wrong project directory
3. AI tool not detecting instruction files

**Solution**:
```bash
# Verify current directory
pwd

# Check if .cursor/rules/ or .claude/rules/ exists
ls -la .cursor/rules/  # or .claude/rules/

# Verify installation tracking
cat .instructionkit/installations.json

# If files missing, reinstall
inskit install
# Select instructions again and ensure correct project path
```

**Pro tip**: Instructions are project-specific. If you change directories, you need to install instructions to that new project.

---

### Issue: "Update shows no new content"

**Expected behavior**: If no changes were made to the example repository since you last downloaded, `inskit update` will report "Already up to date."

**To force re-download**:
```bash
# Remove from library
inskit remove troylar-instructionkit-examples

# Re-download
inskit download --from https://github.com/troylar/instructionkit-examples
```

---

## Next Steps

**After installing examples**:
1. **Commit to Git**: Add `.cursor/`, `.claude/`, `.instructionkit/` to version control so team members get same instructions
2. **Customize**: Edit installed instructions in your project to add company-specific rules
3. **Create your own**: Use examples as templates to create project-specific instructions
4. **Share**: If you create great instructions, consider contributing back to the example repository

**Learn more**:
- InstructionKit documentation: https://github.com/instructionkit/instructionkit
- Example repository: https://github.com/troylar/instructionkit-examples
- Report issues: https://github.com/instructionkit/instructionkit/issues

---

**Time to value**: You've gone from zero to AI-assisted coding with quality guidelines in under 2 minutes. Welcome to InstructionKit! 🎉
