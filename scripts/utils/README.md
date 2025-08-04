# System Utilities

Utility scripts for system maintenance and file operations.

## Scripts

### **`sanitize_filenames.py`** ⭐⭐⭐⭐
**Purpose**: Make filenames Windows-compatible

**Current Status**:
- ✅ Useful utility for cross-platform compatibility
- ❌ Uses sys.argv instead of argparse
- ❌ Limited documentation
- ❌ Business logic in main()

**Planned Improvements**:
- Use argparse instead of sys.argv
- Better documentation and help text
- Add more file system compatibility options
- Move business logic to parameterized methods

**Usage**:
```bash
python sanitize_filenames.py /path/to/directory  # Dry run
python sanitize_filenames.py /path/to/directory --execute  # Actually rename files
```

**Planned Usage**:
```bash
python sanitize_filenames.py --directory /path/to/directory --execute --platform windows
```

### **`clean_git_history.py`** ⭐⭐
**Purpose**: Clean git history of problematic filenames

**Current Status**:
- ❌ Very specific, potentially dangerous operation
- ❌ Violates style guide (shell commands)
- ❌ Dangerous operation that rewrites git history
- ❌ Interactive prompts mixed with business logic

**Recommendation**: 
- **REMOVE** - This script is dangerous and violates multiple style guide rules
- Replace with safer alternatives or remove entirely
- Consider using `.gitignore` to prevent problematic files instead

**Alternative Approaches**:
1. Use `.gitignore` to prevent problematic files from being committed
2. Use `git filter-repo` (safer alternative to filter-branch)
3. Manual cleanup of specific files
4. Pre-commit hooks to prevent problematic filenames

## Planned Improvements

### **`sanitize_filenames.py`**
- Add support for different operating systems (Windows, macOS, Linux)
- Add configuration file support
- Add preview mode with detailed reporting
- Add undo functionality
- Better error handling and conflict resolution

### **General Utilities**
- Add file validation utilities
- Add path normalization utilities
- Add cross-platform compatibility helpers
- Add configuration management utilities

## Dependencies

- pathlib for cross-platform path handling
- argparse for command-line argument parsing (planned)
- os for file system operations 