# Integration Guide: Extracted Modules for pygetpapers Streamlit UI

This guide explains how to integrate the extracted `datatables` and `corpus` modules into the pygetpapers Streamlit UI project.

## Overview

Based on the chat log from the pygetpapers project, we've extracted two key modules from amilib:

1. **datatables_module**: For creating interactive HTML tables (proven technology used for many years)
2. **corpus_module**: For corpus management and analysis

These modules can be integrated into the pygetpapers Streamlit UI to provide enhanced functionality for displaying search results and managing document corpora. **All data is exposed in the filestore for transparency and accessibility.**

## Why These Modules?

### DataTables: Proven Core Technology

DataTables has been our core technology for many years because it provides:

- **Proven Stability**: Battle-tested in production environments
- **Rich Functionality**: Sorting, filtering, pagination, and more
- **File-Based Output**: All data exposed in the filestore
- **Browser Compatibility**: Works across all modern browsers
- **Extensibility**: Easy to customize and extend
- **Performance**: Handles large datasets efficiently

### Filestore Integration

All data is exposed in the filestore for:
- **Transparency**: All data visible and accessible
- **Auditability**: Complete data trail
- **Reproducibility**: Data can be recreated from files
- **Integration**: Easy to integrate with other tools
- **Backup**: Data backed up with file system
- **Sharing**: Easy to share data files

## Module Structure

```
extracted_modules/
├── datatables_module/
│   ├── __init__.py
│   ├── datatables.py      # Core DataTables functionality (proven for years)
│   ├── html_table.py      # HTML table utilities
│   ├── setup.py
│   └── README.md
├── corpus_module/
│   ├── __init__.py
│   ├── corpus.py          # Main corpus management
│   ├── query.py           # Query management
│   ├── search.py          # Search functionality
│   ├── setup.py
│   └── README.md
└── integration_guide.md
```

## Installation Options

### Option 1: Local Development (Recommended for testing)

Copy the modules directly into your pygetpapers project:

```bash
# In your pygetpapers project directory
mkdir -p modules
cp -r extracted_modules/datatables_module modules/
cp -r extracted_modules/corpus_module modules/
```

### Option 2: Standalone Packages

Install as separate packages:

```bash
# Install datatables module
pip install -e extracted_modules/datatables_module/

# Install corpus module
pip install -e extracted_modules/corpus_module/
```

### Option 3: Direct Integration

Copy the source files directly into your Streamlit app:

```python
# Add to your streamlit_app.py
import sys
sys.path.append('extracted_modules')
from datatables_module import Datatables, DataTable
from corpus_module import AmiCorpus, CorpusQuery
```

## Integration with pygetpapers Streamlit UI

### 1. Enhanced Results Display with Filestore Integration

Replace the basic results display with interactive DataTables that also write to filestore:

```python
import streamlit as st
import lxml.etree as ET
from datatables_module import Datatables
from pathlib import Path

def display_search_results(results_data, output_dir="results"):
    """Display search results in an interactive DataTable with filestore integration."""
    
    # Create DataTable
    labels = ["Title", "Authors", "Journal", "Year", "DOI", "Abstract"]
    htmlx, tbody = Datatables.create_table(labels, "search_results_table")
    
    # Add results data
    for result in results_data:
        tr = tbody.makeelement("tr")
        for field in ["title", "authors", "journal", "year", "doi", "abstract"]:
            td = tr.makeelement("td")
            value = result.get(field, "")
            # Truncate long text
            if len(str(value)) > 100:
                value = str(value)[:100] + "..."
            td.text = str(value)
            tr.append(td)
        tbody.append(tr)
    
    # Display in Streamlit
    st.components.v1.html(
        ET.tostring(htmlx, encoding='unicode'),
        height=600,
        scrolling=True
    )
    
    # Write to filestore for transparency and accessibility
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "search_results_table.html", "w", encoding="utf-8") as f:
        f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))
    
    st.success(f"Results saved to filestore: {output_path / 'search_results_table.html'}")

# In your main Streamlit app
if st.session_state.get('search_results'):
    display_search_results(st.session_state['search_results'])
```

### 2. Corpus Management Page with Filestore Integration

Add a new page for corpus management that maintains all data in the filestore:

```python
from corpus_module import AmiCorpus, CorpusQuery
import json
from pathlib import Path

def corpus_management_page():
    st.header("Corpus Management")
    
    # Corpus creation
    st.subheader("Create New Corpus")
    corpus_name = st.text_input("Corpus Name")
    corpus_dir = st.text_input("Corpus Directory", value="./corpora")
    
    if st.button("Create Corpus"):
        if corpus_name and corpus_dir:
            try:
                corpus_path = Path(corpus_dir) / corpus_name
                corpus = AmiCorpus(
                    topdir=corpus_path,
                    globstr="**/*.{html,pdf,txt}",
                    make_descendants=True,
                    mkdir=True
                )
                st.success(f"Corpus '{corpus_name}' created successfully!")
                st.session_state['current_corpus'] = corpus
                
                # Create corpus metadata file in filestore
                metadata = {
                    "name": corpus_name,
                    "path": str(corpus_path),
                    "created": str(Path().cwd()),
                    "files": len(corpus.list_files("**/*"))
                }
                
                with open(corpus_path / "corpus_metadata.json", "w") as f:
                    json.dump(metadata, f, indent=2)
                    
            except Exception as e:
                st.error(f"Error creating corpus: {e}")
    
    # Corpus analysis
    if st.session_state.get('current_corpus'):
        st.subheader("Corpus Analysis")
        corpus = st.session_state['current_corpus']
        
        # File statistics
        files = corpus.list_files("**/*")
        st.write(f"Total files: {len(files)}")
        
        # Create DataTables with filestore integration
        if st.button("Generate DataTables"):
            try:
                corpus.make_datatables(
                    indir=corpus.topdir,
                    outdir=corpus.topdir,
                    outfile_h="corpus_overview.html"
                )
                st.success("DataTables generated successfully!")
                st.info(f"DataTables saved to: {corpus.topdir}/corpus_overview.html")
            except Exception as e:
                st.error(f"Error generating DataTables: {e}")

# Add to your main app
if page == "Corpus Management":
    corpus_management_page()
```

### 3. Advanced Search with Queries and Filestore Integration

Enhance the search functionality with query management that maintains all data in files:

```python
def advanced_search_page():
    st.header("Advanced Search")
    
    # Query management
    st.subheader("Search Queries")
    
    # Create new query
    with st.expander("Create New Query"):
        query_id = st.text_input("Query ID (no spaces)")
        query_phrases = st.text_area("Search Phrases (one per line)")
        
        if st.button("Save Query"):
            if query_id and query_phrases:
                phrases = [p.strip() for p in query_phrases.split('\n') if p.strip()]
                query = CorpusQuery(
                    query_id=query_id,
                    phrases=phrases
                )
                st.session_state['queries'] = st.session_state.get('queries', {})
                st.session_state['queries'][query_id] = query
                
                # Save query to filestore
                queries_dir = Path("queries")
                queries_dir.mkdir(exist_ok=True)
                
                query_data = {
                    "query_id": query_id,
                    "phrases": phrases,
                    "created": str(Path().cwd())
                }
                
                with open(queries_dir / f"{query_id}.json", "w") as f:
                    json.dump(query_data, f, indent=2)
                
                st.success(f"Query '{query_id}' saved to filestore!")
    
    # Run saved queries
    if st.session_state.get('queries'):
        st.subheader("Saved Queries")
        for query_id, query in st.session_state['queries'].items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{query_id}**: {', '.join(query.phrases)}")
            with col2:
                if st.button(f"Run {query_id}"):
                    run_query(query)

def run_query(query):
    """Run a saved query on the current corpus with filestore integration."""
    if st.session_state.get('current_corpus'):
        corpus = st.session_state['current_corpus']
        infiles = corpus.list_files("**/*.html")
        
        if infiles:
            try:
                from corpus_module import CorpusSearch
                
                # Create results directory
                results_dir = Path("query_results") / query.query_id
                results_dir.mkdir(parents=True, exist_ok=True)
                
                results = CorpusSearch.search_files_with_phrases_write_results(
                    infiles=infiles,
                    phrases=query.phrases,
                    outfile=results_dir / "search_results.html"
                )
                st.success(f"Query '{query.query_id}' completed!")
                
                # Save query metadata
                query_metadata = {
                    "query_id": query.query_id,
                    "phrases": query.phrases,
                    "files_searched": len(infiles),
                    "results_file": str(results_dir / "search_results.html")
                }
                
                with open(results_dir / "query_metadata.json", "w") as f:
                    json.dump(query_metadata, f, indent=2)
                
                # Display results
                if results:
                    st.components.v1.html(
                        ET.tostring(results, encoding='unicode'),
                        height=400,
                        scrolling=True
                    )
                    
                st.info(f"Results saved to: {results_dir}")
            except Exception as e:
                st.error(f"Error running query: {e}")
        else:
            st.warning("No HTML files found in corpus")
    else:
        st.warning("Please create or load a corpus first")
```

### 4. Results Visualization with Filestore Integration

Add visualization capabilities that maintain all data in the filestore:

```python
def visualize_results():
    st.header("Results Visualization")
    
    # Load results from pygetpapers
    results_file = st.file_uploader("Upload pygetpapers results (JSON)", type=['json'])
    
    if results_file:
        try:
            results_data = json.load(results_file)
            
            # Create summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Papers", len(results_data))
            
            with col2:
                years = [r.get('year', 'Unknown') for r in results_data]
                unique_years = len(set(years))
                st.metric("Publication Years", unique_years)
            
            with col3:
                journals = [r.get('journal', 'Unknown') for r in results_data]
                unique_journals = len(set(journals))
                st.metric("Unique Journals", unique_journals)
            
            # Create interactive DataTable
            st.subheader("Detailed Results")
            display_search_results(results_data, "visualization_results")
            
            # Export options with filestore integration
            st.subheader("Export Options")
            if st.button("Export as DataTable HTML"):
                from datatables_module import DataTable
                
                # Prepare data
                colheads = ["Title", "Authors", "Journal", "Year", "DOI"]
                rowdata = []
                for result in results_data:
                    row = [
                        result.get('title', ''),
                        result.get('authors', ''),
                        result.get('journal', ''),
                        result.get('year', ''),
                        result.get('doi', '')
                    ]
                    rowdata.append(row)
                
                # Create DataTable and save to filestore
                export_dir = Path("exports") / "datatables"
                export_dir.mkdir(parents=True, exist_ok=True)
                
                dt = DataTable("Search Results", colheads, rowdata)
                dt.write_full_data_tables(str(export_dir))
                
                # Save raw data as JSON for transparency
                with open(export_dir / "raw_data.json", "w") as f:
                    json.dump(results_data, f, indent=2)
                
                st.success(f"DataTable exported to filestore: {export_dir}")
                
        except Exception as e:
            st.error(f"Error processing results: {e}")
```

## Configuration

### Update requirements.txt

Add the new dependencies to your pygetpapers project:

```txt
# Existing dependencies
streamlit>=1.28.0
plotly>=5.17.0

# New dependencies for extracted modules
lxml>=4.6.0
```

### Update Streamlit Configuration

Add configuration for the new modules with filestore awareness:

```python
# In your streamlit_app.py
import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="pygetpapers UI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create filestore directories
filestore_dirs = ["corpora", "queries", "query_results", "exports", "visualization_results"]
for dir_name in filestore_dirs:
    Path(dir_name).mkdir(exist_ok=True)

# Session state initialization
if 'queries' not in st.session_state:
    st.session_state['queries'] = {}
if 'current_corpus' not in st.session_state:
    st.session_state['current_corpus'] = None
```

## Testing the Integration

### 1. Basic Functionality Test with Filestore Verification

```python
def test_integration():
    """Test basic integration functionality with filestore verification."""
    
    # Test DataTables
    from datatables_module import Datatables
    labels = ["Test", "Data"]
    htmlx, tbody = Datatables.create_table(labels, "test_table")
    
    # Add test data
    tr = tbody.makeelement("tr")
    for value in ["Test1", "Data1"]:
        td = tr.makeelement("td")
        td.text = value
        tr.append(td)
    tbody.append(tr)
    
    # Display in Streamlit
    st.components.v1.html(
        ET.tostring(htmlx, encoding='unicode'),
        height=200
    )
    
    # Verify filestore integration
    test_file = Path("test_output.html")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))
    
    st.success(f"Test table saved to filestore: {test_file}")
    
    # Test Corpus
    from corpus_module import AmiCorpus
    corpus = AmiCorpus("test_corpus", mkdir=True)
    st.write(f"Corpus created: {corpus.topdir}")
    
    # Verify corpus metadata in filestore
    if (corpus.topdir / "corpus_metadata.json").exists():
        st.success("Corpus metadata saved to filestore")

# Add to your app for testing
if st.sidebar.checkbox("Test Integration"):
    test_integration()
```

### 2. Error Handling with Filestore Logging

Add comprehensive error handling that logs to filestore:

```python
import logging
from datetime import datetime

def setup_filestore_logging():
    """Setup logging to filestore for transparency."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return log_file

def safe_corpus_operation(operation_func, *args, **kwargs):
    """Safely execute corpus operations with error handling and filestore logging."""
    try:
        result = operation_func(*args, **kwargs)
        
        # Log successful operation to filestore
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        with open(log_dir / "operations.log", "a") as f:
            f.write(f"{datetime.now()} - SUCCESS: {operation_func.__name__}\n")
        
        return result
    except Exception as e:
        # Log error to filestore
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        with open(log_dir / "errors.log", "a") as f:
            f.write(f"{datetime.now()} - ERROR in {operation_func.__name__}: {str(e)}\n")
        
        st.error(f"Error in {operation_func.__name__}: {str(e)}")
        logger.error(f"Corpus operation failed: {e}")
        return None

# Use in your app
log_file = setup_filestore_logging()
st.info(f"Logging to filestore: {log_file}")

corpus = safe_corpus_operation(
    AmiCorpus, 
    topdir="documents", 
    mkdir=True
)
```

## Migration from Original amilib

### Key Differences

1. **Simplified Dependencies**: Removed complex amilib dependencies
2. **Standalone Design**: Each module can be used independently
3. **Streamlit Integration**: Optimized for Streamlit UI patterns
4. **Enhanced Filestore Integration**: All data exposed in files for transparency
5. **Proven Technology**: DataTables core functionality maintained

### Migration Checklist

- [ ] Copy extracted modules to pygetpapers project
- [ ] Update imports in Streamlit app
- [ ] Test basic functionality
- [ ] Verify filestore integration
- [ ] Add error handling with filestore logging
- [ ] Update documentation
- [ ] Test with real pygetpapers data

## Future Enhancements

1. **Real-time Search**: Implement live search as user types
2. **Advanced Filtering**: Add date range, journal, author filters
3. **Export Options**: PDF, CSV, Excel export with filestore integration
4. **Collaborative Features**: Share queries and results via filestore
5. **Performance Optimization**: Caching and pagination
6. **Filestore Analytics**: Track usage patterns and data access

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure modules are in Python path
2. **HTML Display Issues**: Check browser console for JavaScript errors
3. **File Permission Errors**: Ensure write permissions for output directories
4. **Memory Issues**: Use pagination for large datasets
5. **Filestore Access**: Verify all directories are created and writable

### Debug Mode with Filestore Logging

Enable debug mode for troubleshooting with filestore integration:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In your Streamlit app
if st.sidebar.checkbox("Debug Mode"):
    st.write("Debug information:")
    st.write(f"Session state: {st.session_state}")
    st.write(f"Current corpus: {st.session_state.get('current_corpus')}")
    
    # Show filestore contents
    st.write("Filestore contents:")
    for dir_name in ["corpora", "queries", "query_results", "exports"]:
        dir_path = Path(dir_name)
        if dir_path.exists():
            files = list(dir_path.rglob("*"))
            st.write(f"{dir_name}: {len(files)} files")
```

This integration guide provides a comprehensive approach to enhancing the pygetpapers Streamlit UI with the extracted datatables and corpus modules, emphasizing the proven DataTables technology and complete filestore integration for transparency and accessibility. 