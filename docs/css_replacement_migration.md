# CSSStyle Migration to cssutils

**Date**: 2025-01-27
**Branch**: pmr_202507

## Rationale
- The original `CSSStyle` class was custom and hard to maintain.
- cssutils is a mature, standards-compliant library for CSS parsing and generation.
- Replacing the custom code with cssutils reduces maintenance and increases reliability.

## Migration Process
1. **Test Suite Creation**: Comprehensive tests were written to capture all current `CSSStyle` behaviors and edge cases.
2. **Wrapper Development**: A compatibility wrapper (`CSSStyleWrapper`) was created to match the existing API and formatting.
3. **Behavioral Matching**: The wrapper was iteratively improved until all tests passed, ensuring full compatibility.
4. **Integration Plan**:
    - Backup the legacy `CSSStyle` code in `ami_html.py` (rename to `CSSStyleLegacy`).
    - Copy the tested `CSSStyleWrapper` code into `ami_html.py` as the new `CSSStyle`.
    - Update all internal references in `ami_html.py` to use the new `CSSStyle`.
    - Optionally add a feature flag to allow switching between implementations.
    - Run the full amilib test suite to ensure no regressions.

## Key Findings
- The current API and formatting (including edge cases) are preserved.
- cssutils normalizes some values (e.g., colors, quotes), but the wrapper preserves original input where needed.
- The wrapper is fully compatible with all tested usage patterns.

## Next Steps
- Complete code integration in `ami_html.py`.
- Remove legacy code after a period of dual support/testing.
- Document cssutils usage in the style guide.

## References
- `docs/css_replacement_test_results.md` for detailed test results
- `test/css_replacement/` for all test and wrapper code 