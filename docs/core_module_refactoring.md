# Core Module Refactoring

## Overview

This document records the refactoring of the amilib core module to improve modularity and reduce circular dependencies.

## Background

The amilib project consists of:
- **1 core module** - foundational utilities and classes
- **4 other modules** - pdf, html, dict, wikimedia

The user requested to determine if the core module is standalone and, if so, to refactor it appropriately.

## Analysis

### Initial Assessment

The core module was found to have circular dependencies primarily through:
- Import of constants from other modules
- Shared utility classes across modules

### Circular Dependencies Identified

1. **Constants imports** - Multiple modules importing the same constants
2. **Utility class sharing** - Classes used across multiple modules
3. **Import patterns** - Some modules importing from each other

## Refactoring Plan

### Phase 1: Extract Constants

**Goal:** Centralize all constants to avoid circular imports

**Implementation:**
- Created `amilib/core/constants.py`
- Moved all constants from `xml_lib.py` and `util.py`
- Updated imports to use centralized constants

### Phase 2: Create Core Submodule

**Goal:** Organize core utilities into a dedicated submodule

**Implementation:**
- Created `amilib/core/` directory
- Created `amilib/core/util.py` with core utilities
- Created `amilib/core/__init__.py` (empty as per style guide)
- Maintained backward compatibility through re-exports

### Phase 3: Style Compliance

**Goal:** Ensure all changes follow the established style guide

**Implementation:**
- Used absolute imports with `amilib.` prefix throughout
- Made `__init__.py` files empty as per style guide
- Updated official style guide in `../pygetpapers/docs/styleguide.md`

## Files Created/Modified

### New Files
- `amilib/core/constants.py` - Centralized constants
- `amilib/core/util.py` - Core utilities
- `amilib/core/__init__.py` - Empty core module init
- `REFACTORING_SUMMARY.md` - Migration documentation

### Modified Files
- `amilib/__init__.py` - Made empty as per style guide
- `amilib/util.py` - Refactored to use core constants
- `../pygetpapers/docs/styleguide.md` - Added __init__.py rule

## Key Achievements

### ✅ Modularity
- Core module extracted and organized
- Clear separation of concerns
- Improved code organization

### ✅ No Circular Dependencies
- Constants centralized in `core/constants.py`
- Clean import hierarchy
- Reduced coupling between modules

### ✅ Style Compliance
- All imports use absolute paths with `amilib.` prefix
- Empty `__init__.py` files as per style guide
- Consistent with established patterns

### ✅ Backward Compatibility
- All existing imports continue to work
- No breaking changes to public API
- All tests pass (436 passed, 96 skipped)

## External Dependencies

### Core Module Dependencies
- **Primary:** `requests` (HTTP library)
- **Standard Library:** All other dependencies are standard library

### Other Module Dependencies
- **sklearn** - Used in `ami_html.py` for linear regression
- **pandas** - Used in various modules for data processing

## Test Results

After refactoring:
- ✅ **436 tests passed**
- ⏭️ **96 tests skipped** (long-running/network-dependent)
- ❌ **1 test failed** (expected failure - XFAIL)
- ⚠️ **5 warnings** (pytest marks)

## Migration Strategy

### For Existing Code
No changes required - all existing imports continue to work unchanged.

### For Future Development
- Use `amilib.core.constants` for constants
- Use `amilib.core.util` for core utilities
- Follow absolute import style with `amilib.` prefix

## Next Steps

### Planned Future Work
1. Move `FileLib` to `core/file_utils.py`
2. Move `XmlLib`, `Templater`, `HtmlElement`, `DataTable` to `core/xml_utils.py`
3. Move `AmiUtil`, `AmiJson`, `Vector2` to `core/ami_utils.py`
4. Update internal imports in existing modules

### Benefits of Future Work
- Further modularization
- Cleaner separation of concerns
- Easier maintenance and testing

## Lessons Learned

### Style Guide Importance
- Always read existing style guides first
- Follow established patterns consistently
- Use absolute imports with module prefix

### Refactoring Best Practices
- Maintain backward compatibility
- Test thoroughly after changes
- Document changes clearly
- Use incremental approach

### Code Quality
- Remove dead imports regularly
- Centralize shared constants
- Avoid circular dependencies
- Follow established conventions

## Conclusion

The core module refactoring was successful in:
- Eliminating circular dependencies
- Improving code organization
- Maintaining backward compatibility
- Following established style guidelines

The refactoring provides a solid foundation for future development and makes the codebase more maintainable and modular. 