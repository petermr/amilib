"""
Pytest configuration for headless operation.
Ensures all tests run without opening GUI windows.
"""
import os
import sys
import warnings
from pathlib import Path

# Configure environment for headless operation BEFORE any imports
os.environ['MPLBACKEND'] = 'Agg'
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':99'
os.environ['GRAPHVIZ_DOT'] = 'dot'

# Filter out SWIG-related deprecation warnings from C extensions (lxml, etc.)
# These warnings come from SWIG bindings (typically from lxml) and are harmless.
# They are emitted during module import before Python's warnings system can filter them,
# so they may still appear in test output. This is a known issue with SWIG bindings
# in Python 3.12 and does not affect functionality.
# Set up warnings filters in Python to suppress them when possible
warnings.filterwarnings("ignore", message=".*builtin type SwigPyPacked.*")
warnings.filterwarnings("ignore", message=".*builtin type SwigPyObject.*")
warnings.filterwarnings("ignore", message=".*builtin type swigvarlink.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="importlib._bootstrap")

# Note: amilib should be installed with 'pip install -e .' for tests to work properly

def pytest_ignore_collect(collection_path):
    """Ignore IPCC and UNFCCC application test files during collection."""
    path_str = str(collection_path)
    if 'test_ipcc.py' in path_str or 'test_unfccc_pdf.py' in path_str:
        return True
    return False

# Configure environment for headless operation
def pytest_configure(config):
    """Configure pytest for headless operation."""
    # Set matplotlib backend to headless
    os.environ['MPLBACKEND'] = 'Agg'
    
    # Set display to headless (for systems that need it)
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':99'
    
    # Configure graphviz to run in headless mode
    os.environ['GRAPHVIZ_DOT'] = 'dot'
    
    # Disable any GUI-related warnings
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
    warnings.filterwarnings("ignore", category=UserWarning, module="PIL")
    
    # Filter out SWIG-related deprecation warnings from C extensions (lxml, etc.)
    # These warnings come from SWIG bindings and are harmless
    warnings.filterwarnings("ignore", message=".*builtin type SwigPyPacked.*")
    warnings.filterwarnings("ignore", message=".*builtin type SwigPyObject.*")
    warnings.filterwarnings("ignore", message=".*builtin type swigvarlink.*")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names and filter out application tests."""
    # Filter out IPCC and UNFCCC application tests
    items[:] = [item for item in items if not (
        'test_ipcc.py' in str(item.fspath) or 
        'test_unfccc_pdf.py' in str(item.fspath)
    )]
    
    for item in items:
        # Mark graph-related tests as potentially GUI-related
        if 'graph' in item.name.lower() or 'visualize' in item.name.lower():
            item.add_marker('gui')
        
        # Mark network tests
        if 'network' in item.name.lower() or 'download' in item.name.lower():
            item.add_marker('network')
        
        # Mark slow tests
        if any(slow_indicator in item.name.lower() for slow_indicator in ['long', 'verylong', 'slow']):
            item.add_marker('slow') 