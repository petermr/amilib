# Headless Test Configuration

## Overview
This document describes the changes made to ensure all tests run in headless mode without opening GUI windows or flashing images.

## Issues Identified and Fixed

### 1. Graphviz Viewer Windows ✅ FIXED
- **Location**: `test/test_graph.py` and `amilib/ami_graph.py`
- **Issue**: `graph.view()` and `ipcc.view()` calls were opening graphviz viewer windows
- **Fix**: Commented out these calls to prevent GUI windows
- **Status**: ✅ All graphviz viewer calls are now disabled

### 2. Matplotlib Backend ✅ FIXED
- **Location**: `amilib/ami_graph.py`
- **Issue**: Matplotlib could potentially open GUI windows for plotting
- **Fix**: Added `matplotlib.use('Agg')` to force headless backend
- **Status**: ✅ Matplotlib is configured to use headless backend

### 3. Environment Configuration ✅ FIXED
- **Issue**: Tests could open GUI windows depending on system configuration
- **Fix**: Added comprehensive headless environment configuration
- **Status**: ✅ Environment variables are set before any imports

## Configuration Files

### 1. `test/conftest.py`
- Sets environment variables at module level (before imports)
- Configures matplotlib backend to 'Agg'
- Sets DISPLAY to ':99' for headless operation
- Configures graphviz to run in headless mode

### 2. `test/pytest.ini`
- Configures pytest for headless operation
- Sets environment variables for headless mode
- Defines test markers for categorization

### 3. `amilib/ami_graph.py`
- Sets matplotlib backend to 'Agg' before importing pyplot
- Comments out `plt.show()` calls
- Comments out `graph.view()` calls

## Verification

### Test Results
- ✅ Graph tests run without opening GUI windows
- ✅ Matplotlib visualization works in headless mode
- ✅ No flashing images or plot windows
- ✅ All tests pass with headless configuration

### Environment Check
```bash
# Before: Backend: macosx (GUI-capable)
# After: Backend: Agg (headless)
MPLBACKEND=Agg python -c "import matplotlib; print('Backend:', matplotlib.get_backend())"
```

## Summary

All GUI-related issues have been resolved:
- **Graphviz viewer windows**: Disabled
- **Matplotlib plot windows**: Headless backend configured
- **Environment variables**: Set for headless operation
- **Test configuration**: Properly configured for CI environments

The test suite now runs completely in headless mode, making it suitable for:
- Continuous Integration environments
- Automated testing without GUI dependencies
- Server environments without display
- Background processing without user interaction 