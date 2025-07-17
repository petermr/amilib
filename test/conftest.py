"""
Pytest configuration for headless operation.
Ensures all tests run without opening GUI windows.
"""
import os
import sys
from pathlib import Path

# Configure environment for headless operation BEFORE any imports
os.environ['MPLBACKEND'] = 'Agg'
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':99'
os.environ['GRAPHVIZ_DOT'] = 'dot'

# Add the parent directory to the path so we can import from amilib
sys.path.insert(0, str(Path(__file__).parent.parent))

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