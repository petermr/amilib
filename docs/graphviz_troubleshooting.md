# Graphviz Troubleshooting Guide

## Error: "graphviz has no attribute Digraph"

This error occurs when the Python `graphviz` package is not properly installed or when the system graphviz binaries are missing.

## Quick Fix

### Step 1: Install System Dependencies

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install graphviz graphviz-dev
```

**Windows:**
- Download from: https://graphviz.org/download/
- Or use Chocolatey: `choco install graphviz`

### Step 2: Reinstall Python Package

```bash
pip uninstall graphviz
pip install graphviz==0.20.3
```

### Step 3: Verify Installation

Create a test file `test_graphviz.py`:

```python
import graphviz

def test_graphviz():
    try:
        # Test basic functionality
        dot = graphviz.Digraph(comment='Test')
        dot.node('A', 'Node A')
        dot.node('B', 'Node B')
        dot.edge('A', 'B')
        
        print("✅ Graphviz is working correctly!")
        print(f"Version: {graphviz.__version__}")
        print(f"Digraph available: {hasattr(graphviz, 'Digraph')}")
        
        # Test system binaries
        import subprocess
        result = subprocess.run(['dot', '-V'], capture_output=True, text=True)
        print(f"System dot version: {result.stdout}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_graphviz()
```

Run the test:
```bash
python test_graphviz.py
```

## Alternative Solutions

### Option 1: Use Conda
```bash
conda install graphviz
conda install python-graphviz
```

### Option 2: Try Different Version
```bash
pip install graphviz==0.19.2
```

### Option 3: Force Reinstall
```bash
pip install --force-reinstall --no-cache-dir graphviz==0.20.3
```

## Common Issues

### Issue 1: PATH Problems
If system binaries aren't found, add graphviz to your PATH:

**macOS/Linux:**
```bash
export PATH="/usr/local/bin:$PATH"
# or
export PATH="/opt/homebrew/bin:$PATH"  # Apple Silicon Macs
```

**Windows:**
Add `C:\Program Files\Graphviz\bin` to your system PATH.

### Issue 2: Virtual Environment
Make sure you're installing in the correct virtual environment:

```bash
# Activate your virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Then install
pip install graphviz==0.20.3
```

### Issue 3: Permission Issues
On Linux/macOS, you might need sudo for system packages:

```bash
sudo apt-get install graphviz graphviz-dev  # Ubuntu/Debian
sudo brew install graphviz                  # macOS (if needed)
```

## Verification Commands

Check if everything is working:

```bash
# Check Python package
python -c "import graphviz; print(graphviz.__version__)"

# Check system binary
dot -V

# Check PATH
echo $PATH | grep graphviz  # Linux/Mac
echo %PATH% | findstr graphviz  # Windows
```

## Project-Specific Setup

For this project, after fixing graphviz:

1. Install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the tests:
   ```bash
   pytest test/test_graph.py -v
   ```

3. Test the specific functionality:
   ```bash
   python -c "from amilib.ami_graph import AmiGraph; print('AmiGraph imported successfully')"
   ```

## Still Having Issues?

If the problem persists:

1. **Check your Python version**: Graphviz works with Python 3.7+
2. **Try a clean environment**: Create a new virtual environment
3. **Check for conflicting packages**: Some packages might conflict with graphviz
4. **Use Docker**: If all else fails, use the project's Docker setup

## Files That Use Graphviz

In this project, graphviz is used in:
- `amilib/ami_graph.py` - Main graph functionality
- `test/test_graph.py` - Graph tests
- Various documentation generation scripts

The main usage pattern is:
```python
import graphviz
graph = graphviz.Digraph(name, filename=output_file, engine='fdp')
```

## Support

If you continue to have issues, please:
1. Run the test script above
2. Share the output
3. Include your operating system and Python version
4. Check if you have any antivirus software that might be blocking the installation






















