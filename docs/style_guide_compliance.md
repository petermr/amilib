# Style Guide Compliance

## Overview

This document records the importance of style guide compliance and lessons learned during the amilib refactoring process.

## Background

During the refactoring work, we encountered several style guide violations that needed to be corrected. This highlighted the critical importance of following established coding standards and conventions.

## Style Guide Location

The official style guide is located at:
`../pygetpapers/docs/styleguide.md`

## Key Style Rules

### Import Style

**Rule:** Use absolute imports with module prefix

**✅ CORRECT:**
```python
from amilib.util import Util
from amilib.file_lib import FileLib
from amilib.core.constants import NS_MAP
```

**❌ WRONG:**
```python
from .util import Util
from .file_lib import FileLib
from ..core.constants import NS_MAP
```

### __init__.py Files

**Rule:** All `__init__.py` files should be empty unless explicitly agreed

**✅ CORRECT:**
```python
# amilib/__init__.py
# Empty file
```

**❌ WRONG:**
```python
# amilib/__init__.py
from .core.util import Util
from .core.constants import NS_MAP
```

### No Mocks in Tests

**Rule:** Do not use mocks or patches in tests. Tests should use real implementations and real services.

**✅ CORRECT:**
```python
def test_service_connection_basic(self):
    """Test basic service connection functionality."""
    result = FileLib.check_service_connection(
        service_url="https://httpbin.org/status/200",
        service_name="HTTPBin Test",
        timeout=10
    )
    # Handle both success and failure cases
    if result['connected']:
        self.assertEqual(result['status_code'], 200)
    else:
        self.assertIsNotNone(result['error'])
```

**❌ WRONG:**
```python
@patch('amilib.file_lib.requests.get')
def test_service_connection_basic(self, mock_get):
    """Test basic service connection functionality."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    # ... test code
```

**Rationale**: Tests should verify real behavior, not mocked behavior. Mocks hide integration issues and make tests less reliable. If external services are unreliable, tests should handle both success and failure cases gracefully.

### Tests: Use assert to trap errors, not return False

**Rule:** All tests should use `assert` to trap errors, not `return False`. Do not report failures by printing an error and returning False; fail the test with a clear assertion message.

**Date added:** 2026-02-04 (system date)

**✅ CORRECT:**
```python
def test_something():
    result = do_thing()
    assert result is not None, "do_thing() returned None"
    assert result.get("ok"), f"Expected ok=True, got: {result}"
```

**❌ WRONG:**
```python
def test_something():
    result = do_thing()
    if result is None:
        print("Error: do_thing() returned None")
        return False
    if not result.get("ok"):
        print(f"Error: got {result}")
        return False
    return True
```

**Rationale**: Using `assert` ensures test runners (e.g. pytest) see a real failure with a clear message. `return False` and `print` do not cause a test failure and can be missed; assertions integrate with the test framework and CI.

### No Magic Strings

**Rule:** Do not use hardcoded string literals for values that represent constants, identifiers, or configuration. Use class constants or accessor methods instead.

**✅ CORRECT:**
```python
class AmiEncyclopedia:
    # Define constants as class attributes
    REASON_MISSING_WIKIPEDIA = "missing_wikipedia"
    REASON_GENERAL_TERM = "general_term"
    REASON_FALSE_WIKIPEDIA = "false_wikipedia"
    
    @classmethod
    def get_valid_checkbox_reasons(cls) -> list:
        """Get list of valid checkbox reason values"""
        return [
            cls.REASON_MISSING_WIKIPEDIA,
            cls.REASON_GENERAL_TERM,
            cls.REASON_FALSE_WIKIPEDIA,
        ]
    
    def _add_hide_checkbox(self, container, entry_id: str, reason: str):
        # Use constant instead of string literal
        if reason == self.REASON_MISSING_WIKIPEDIA:
            # ...
```

```python
# In tests - use constants from the class
from amilib.ami_encyclopedia import AmiEncyclopedia

def test_checkbox_reasons(self):
    valid_reasons = AmiEncyclopedia.get_valid_checkbox_reasons()
    assert AmiEncyclopedia.REASON_MISSING_WIKIPEDIA in valid_reasons
```

**❌ WRONG:**
```python
class AmiEncyclopedia:
    def _add_hide_checkbox(self, container, entry_id: str, reason: str):
        # Magic string - hard to maintain and error-prone
        if reason == "missing_wikipedia":
            # ...
```

```python
# In tests - using magic strings
def test_checkbox_reasons(self):
    assert reason in ['missing_wikipedia', 'general_term', 'false_wikipedia']
    # Hard to maintain - if constant changes, test breaks
```

**Rationale**: Magic strings (hardcoded string literals) create several problems:
- **Typos**: Easy to make mistakes with string literals
- **Maintainability**: If a value changes, must update it in multiple places
- **Discoverability**: Hard to find all usages of a string value
- **Type safety**: No way to validate string values at development time
- **Refactoring**: Difficult to rename or change values across codebase

**When to Use Constants:**
- Configuration values (e.g., checkbox reasons, entry categories)
- Status codes or state identifiers
- Attribute names that are used in multiple places
- Any string that represents a fixed set of possible values

**When String Literals Are Acceptable:**
- User-facing messages or labels
- Format strings or templates
- One-off string values that are not reused
- File extensions or MIME types (though constants are still preferred)

## Violations Encountered

### 1. Relative Imports

**Issue:** Initially used relative imports in refactored code

**Example:**
```python
# WRONG - Relative imports
from .constants import GENERATE
from .core.util import Util
```

**Fix:**
```python
# CORRECT - Absolute imports
from amilib.core.constants import GENERATE
from amilib.core.util import Util
```

### 2. Non-Empty __init__.py Files

**Issue:** Created `__init__.py` files with re-export statements

**Example:**
```python
# WRONG - Non-empty __init__.py
from amilib.core.util import Util
from amilib.core.constants import NS_MAP
```

**Fix:**
```python
# CORRECT - Empty __init__.py
# File is empty
```

## Lessons Learned

### 1. Always Read Style Guide First

**Problem:** Started refactoring without checking existing style guide
**Solution:** Always read `../pygetpapers/docs/styleguide.md` before making changes

### 2. Follow Established Patterns

**Problem:** Assumed common Python patterns without checking project conventions
**Solution:** Examine existing codebase to understand established patterns

### 3. Don't Create Duplicate Documentation

**Problem:** Created separate style guide when one already existed
**Solution:** Update existing style guide rather than creating duplicates

### 4. Verify Compliance Before Claiming It

**Problem:** Claimed style compliance while actually violating rules
**Solution:** Thoroughly verify all changes follow established patterns

## Style Guide Updates

### Added Rules

We updated the official style guide with additional rules:

```markdown
### STYLE: All __init__.py files should be empty unless explicitly agreed

- ✅ **Good**: Empty `__init__.py` files
- ❌ **Bad**: `__init__.py` files with import statements or other code

### STYLE: Do not write business logic in tests without authorisation

- ✅ **Good**: Tests that call existing library methods
- ✅ **Good**: Tests that verify library functionality
- ❌ **Bad**: Tests that implement business logic
- ❌ **Bad**: Tests that duplicate library functionality
- ❌ **Bad**: Tests that contain complex processing logic

**Rationale**: Business logic in tests pollutes the test suite, makes tests harder to maintain, 
and creates technical debt. Tests should focus on verifying existing functionality, not 
implementing new features.

### STYLE: Do not return values from tests other than None

- ✅ **Good**: Tests that return None (implicit or explicit)
- ✅ **Good**: Tests that use assertions to verify behavior
- ❌ **Bad**: Tests that return True/False or other values
- ❌ **Bad**: Tests that return data for other tests to use

**Rationale**: Tests should focus on verification through assertions, not data flow. 
Returning values from tests creates dependencies between tests电能 makes the test suite 
harder to understand and maintain.

### STYLE: Use Resources.TEMP_DIR for temporary files with module/class-based subdirectories

**Rule:** All temporary files must be created under `<root>/temp`, which is defined in `Resources.TEMP_DIR`. Use subdirectories based on modules and classes.

**✅ CORRECT:**
```python
from pathlib import Path
from test.resources import Resources

# For test files - use Path constructor with multiple arguments
self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaTest")
self.temp_dir.mkdir(parents=True, exist_ok=True)

# For scripts
temp_dir = Path(Resources.TEMP_DIR, "scripts", "annotation")
```

**❌ WRONG:**
```python
import tempfile

# Using system temp directory
self.temp_dir = Path(tempfile.mkdtemp())

# Using relative temp directory
self.temp_dir = Path("temp")

# Using / operator instead of Path constructor
self.temp_dir = Resources.TEMP_DIR / "test" / "encyclopedia"
```

**Rationale**: Using a centralized temp directory:
- Keeps all temporary files in one predictable location
- Makes cleanup easier
- Allows easy inspection of test outputs
- Follows consistent directory structure based on modules/classes
- Defined in Resources for consistency across the codebase
- Using Path() constructor explicitly makes path operations clearer and more consistent

**Subdirectory Naming:**
- Tests: `Path(Resources.TEMP_DIR, "test", <module_name>, <class_name>)`
- Scripts: `Path(Resources.TEMP_DIR, "scripts", <module_name>)`
- Examples: `Path(Resources.TEMP_DIR, "examples", <example_name>)`
- Other modules: `Path(Resources.TEMP_DIR, <module_name>, <class_or_function>)`

### STYLE: Distinguish between fixture temp files and human-inspection temp artifacts

We use temporary files in two complementary ways:

1. **Test fixtures (ephemeral)**: created for automated tests and cleaned up automatically.
2. **Human inspection artifacts (persisted)**: written to `<root>/temp/` for manual validation after test runs.

**Rule:**
- ✅ **Fixtures** should create isolated temporary directories/files (e.g., `tmp_path`, `TemporaryDirectory`, or project fixtures in `conftest.py`) and use them for assertions.
- ✅ **Human inspection outputs** may be written to `<root>/temp/...` (via `Resources.TEMP_DIR`) to support manual review.
- ✅ Human inspection outputs may **overwrite previous versions** (to avoid unbounded growth).
- ✅ The `<root>/temp/` directory is **not committed to GitHub** and is **not long-term storage**.
- ✅ Even if outputs are persisted for review, tests should still assert at least **existence** and **basic content/sanity** (e.g., non-empty HTML, expected tags/strings).
- ❌ Do not rely on environment variables to control this behavior (the project is distributed across many people with heterogeneous environments).

**Rationale**:
- Fixture outputs keep tests deterministic and self-contained.
- Persisted artifacts in `<root>/temp/` enable visual/human QA for transformations (e.g., PDF→HTML) without polluting the repository or requiring commits of generated files.

### STYLE: Always use Path to create filenames, never use isolated "/"

**Rule:** Always use `Path()` constructor with multiple arguments or `Path.joinpath()` for building file paths. Never use string concatenation with "/" or isolated "/" characters.

**✅ CORRECT:**
```python
from pathlib import Path

# Use Path constructor with multiple arguments
file_path = Path("temp", "dictionaries", "wg3", "annex-vi.html")
output_dir = Path(Resources.TEMP_DIR, "scripts", "glossary_processor")

# Use Path.joinpath() for dynamic paths
base_path = Path("temp")
file_path = base_path.joinpath("dictionaries", "wg3", "annex-vi.html")

# For combining with existing Path objects
parent_dir = Path("temp")
file_path = Path(parent_dir, "dictionaries", "file.html")
```

**❌ WRONG:**
```python
# Using string concatenation with "/"
file_path = "temp" + "/" + "dictionaries" + "/" + "wg3" + "/" + "annex-vi.html"

# Using isolated "/" in Path
file_path = Path("temp/dictionaries/wg3/annex-vi.html")

# Using / operator (prefer Path constructor)
file_path = Path("temp") / "dictionaries" / "wg3" / "annex-vi.html"
```

**Rationale**: 
- Using Path constructor with multiple arguments is explicit and clear
- Avoids platform-specific path separator issues
- Makes path construction more readable
- Consistent with style guide preference for explicit Path construction
- Prevents accidental string concatenation errors
```

## Best Practices Established

### Before Making Changes

1. **Read the style guide** - Always check `../pygetpapers/docs/styleguide.md`
2. **Examine existing code** - Look at how similar patterns are implemented
3. **Follow established conventions** - Don't assume common patterns apply
4. **Ask for clarification** - If unsure about style rules, ask before proceeding

### During Development

1. **Use absolute imports** - Always with module prefix (`amilib.`)
2. **Keep __init__.py empty** - Unless explicitly agreed otherwise
3. **Test thoroughly** - Ensure changes don't break existing functionality
4. **Document decisions** - Record why certain style choices were made

### After Changes

1. **Verify compliance** - Double-check all changes follow style guide
2. **Run tests** - Ensure functionality is maintained
3. **Update documentation** - Keep style guide current with new rules
4. **Review with team** - Get feedback on style compliance

## Impact of Style Violations

### Problems Caused

1. **Inconsistent codebase** - Mixed import styles create confusion
2. **Maintenance issues** - Harder to understand and modify code
3. **Team confusion** - Different developers using different patterns
4. **Code review delays** - Violations need to be caught and fixed

### Benefits of Compliance

1. **Consistency** - All code follows same patterns
2. **Maintainability** - Easier to understand and modify
3. **Team productivity** - Clear standards reduce confusion
4. **Code quality** - Consistent patterns improve overall quality

## Recommendations

### For Future Development

1. **Make style guide mandatory reading** - Require all developers to read it
2. **Use automated tools** - Implement linters to catch violations
3. **Regular reviews** - Periodically audit code for style compliance
4. **Documentation updates** - Keep style guide current with project evolution

### For Code Reviews

1. **Check style compliance** - Always verify against style guide
2. **Be consistent** - Apply same standards to all code
3. **Provide feedback** - Help developers understand style rules
4. **Update guide** - Add new rules as patterns evolve

### For Project Management

1. **Prioritize consistency** - Make style compliance a priority
2. **Provide training** - Ensure team understands style rules
3. **Use tools** - Implement automated style checking
4. **Regular audits** - Periodically review codebase for compliance

## Conclusion

Style guide compliance is critical for:
- **Code quality** - Consistent patterns improve maintainability
- **Team productivity** - Clear standards reduce confusion
- **Project success** - Consistent code is easier to maintain and extend

The lessons learned during this refactoring emphasize the importance of:
1. **Reading existing documentation** before making changes
2. **Following established patterns** rather than assuming common practices
3. **Verifying compliance** before claiming it
4. **Updating documentation** to reflect new rules and patterns

By following these principles, we can maintain a high-quality, consistent codebase that is easy to understand, maintain, and extend. 