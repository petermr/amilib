# Corpus Implementation Guide

## Quick Start

### 1. Basic Corpus Creation

```python
from corpus_module.corpus import AmiCorpus
from pathlib import Path

# Create corpus with automatic directory creation
corpus = AmiCorpus(
    topdir=Path("test", "resources", "corpus", "my_corpus"),
    mkdir=True
)
```

### 2. File Ingestion

```python
# Ingest PDF files
ingested_files = corpus.ingest_files(
    source_dir=Path("input", "documents"),
    file_pattern="*.pdf",
    target_container="files",
    file_type="pdf"
)

# Ingest text files
text_files = corpus.ingest_files(
    source_dir=Path("input", "texts"),
    file_pattern="*.txt",
    target_container="text_files",
    file_type="text"
)
```

### 3. Corpus Structure Setup

```python
# Create standard BagIt structure
data_container = corpus.ami_container.create_corpus_container("data", bib_type="bagit_data", mkdir=True)
data_container.create_corpus_container("files", bib_type="files", mkdir=True)
data_container.create_corpus_container("metadata", bib_type="metadata", mkdir=True)
data_container.create_corpus_container("indices", bib_type="indices", mkdir=True)
data_container.create_corpus_container("processed", bib_type="processed", mkdir=True)

# Create non-BagIt directories
corpus.ami_container.create_corpus_container("search_results", bib_type="search", mkdir=True)
corpus.ami_container.create_corpus_container("summaries", bib_type="summary", mkdir=True)
corpus.ami_container.create_corpus_container("temp", bib_type="temp", mkdir=True)
```

## Breward2023 Specific Implementation

### 1. Ingest Breward2023 PDFs

```bash
# Run the ingestion script
python scripts/ingest_breward2023.py
```

This script:
- Ingests 8 PDF files from `test/resources/corpus/breward2025/`
- Places them in `test/resources/corpus/breward2023_corpus/data/files/`
- Uses BagIt-compliant structure

### 2. Programmatic Ingestion

```python
from corpus_module.corpus import AmiCorpus
from pathlib import Path

# Initialize corpus
corpus = AmiCorpus(
    topdir=Path("test", "resources", "corpus", "breward2023_corpus"),
    mkdir=True
)

# Ingest PDFs
pdf_files = corpus.ingest_files(
    source_dir=Path("test", "resources", "corpus", "breward2025"),
    file_pattern="*.pdf",
    target_container="files",
    file_type="pdf"
)

print(f"Ingested {len(pdf_files)} files")
```

## Testing

### 1. Run Corpus Tests

```bash
# Run all corpus tests
cd test
python -m pytest test_breward2023/ -v

# Run specific test
python -m pytest test_breward2023/test_corpus_ingestion.py -v -s
```

### 2. Test Coverage

The test suite covers:
- ✅ File ingestion with glob patterns
- ✅ Directory creation and management
- ✅ Duplicate file handling
- ✅ Error conditions
- ✅ Full workflow validation

## File Organization

### Source Files
```
test/resources/corpus/breward2025/
├── SCE-24-2023-U3AC-Climate-Change-Seminar-1-Framing-Climate-Change.pdf
├── SCE-24-2023-U3AC-Climate-Change-Seminar-2-The-Key-Systems.pdf
├── SCE-24-2023-U3AC-Climate-Change-Seminar-3-Evidence-Tipping-Points-New-Tech-and-Projections.pdf
├── SCE-24-2023-U3AC-Climate-Change-Seminar-4-Key-Players-and-Psychology.pdf
├── SCE-24-2023-U3AC-Climate-Change-Seminar-5-Misinformation.pdf
├── SCE-24-2023-U3AC-Climate-Change-Seminar-6-What-Humankind-needs-to-do-and-What-to-do-personal(0).pdf
├── SCE-24-2023-U3AC-Climate-Change-Seminar-7-What-to-do-Group.pdf
└── SCE-24-2023-U3AC-Climate-Change-Seminar-8-Tools-QandA-and-Plans.pdf
```

### Corpus Structure
```
test/resources/corpus/breward2023_corpus/
├── bag-info.txt                    # BagIt metadata
├── bagit.txt                      # BagIt version info
├── manifest-md5.txt               # BagIt checksums
├── data/                          # BagIt-managed content
│   ├── files/                     # Ingested PDF files
│   ├── metadata/                  # Extracted metadata
│   ├── indices/                   # Term indices
│   └── processed/                 # Processed files
├── search_results/                # Non-BagIt: Search results
├── summaries/                     # Non-BagIt: Summary info
└── temp/                          # Non-BagIt: Temporary files
```

## API Reference

### AmiCorpus.ingest_files()

```python
def ingest_files(self, source_dir: Union[str, Path], file_pattern: str = "*", 
                target_container: str = "files", file_type: str = "unknown") -> List[Path]:
```

**Parameters:**
- `source_dir`: Directory containing files to ingest
- `file_pattern`: Glob pattern to match files (default: "*")
- `target_container`: Name of container to ingest into (default: "files")
- `file_type`: Type of files being ingested (default: "unknown")

**Returns:**
- List of paths to ingested files

**Example:**
```python
# Ingest all PDF files
files = corpus.ingest_files(
    source_dir=Path("input"),
    file_pattern="*.pdf",
    target_container="documents",
    file_type="pdf"
)

# Ingest specific files
files = corpus.ingest_files(
    source_dir=Path("input"),
    file_pattern="report_*.txt",
    target_container="reports",
    file_type="text"
)
```

### AmiCorpus Constructor

```python
def __init__(self, topdir: Optional[Union[str, Path]] = None, mkdir: bool = False, ...):
```

**Parameters:**
- `topdir`: Corpus directory path
- `mkdir`: Create directory if it doesn't exist (default: False)

**Example:**
```python
# Create corpus with automatic directory creation
corpus = AmiCorpus(topdir=Path("my_corpus"), mkdir=True)

# Use existing directory
corpus = AmiCorpus(topdir=Path("existing_corpus"))
```

## Best Practices

### 1. Path Construction
```python
# ✅ Correct - comma-separated Path construction
corpus_dir = Path("test", "resources", "corpus", "my_corpus")

# ❌ Wrong - uses / in Path construction
corpus_dir = Path("test/resources/corpus/my_corpus")
```

### 2. File Type Specification
```python
# ✅ Always specify file type for clarity
corpus.ingest_files(source_dir=src, file_type="pdf")

# ❌ Avoid default "unknown" type
corpus.ingest_files(source_dir=src)  # file_type="unknown"
```

### 3. Error Handling
```python
try:
    files = corpus.ingest_files(source_dir=src, file_pattern="*.pdf")
    print(f"Successfully ingested {len(files)} files")
except ValueError as e:
    print(f"Error: {e}")
```

### 4. Testing
```python
# Use temporary directories for tests
import tempfile
from pathlib import Path

test_dir = Path(tempfile.mkdtemp())
corpus = AmiCorpus(topdir=test_dir, mkdir=True)
# ... test code ...
shutil.rmtree(test_dir)  # Clean up
```

## Troubleshooting

### Common Issues

1. **"AmiCorpus() requires valid directory"**
   - Solution: Use `mkdir=True` parameter
   - Or create directory manually before initialization

2. **"No files found matching pattern"**
   - Check that source directory exists
   - Verify file pattern matches your files
   - Use `*.pdf` for PDFs, `*.txt` for text files, etc.

3. **"Could not find data container"**
   - Ensure corpus structure is set up
   - Create data container before ingesting files

### Debug Mode

Enable logging to see detailed information:
```python
import logging
logging.basicConfig(level=logging.INFO)

# Now corpus operations will show detailed logs
corpus.ingest_files(...)
```

## Next Steps

1. **Text Extraction**: Extract text from ingested PDFs
2. **Indexing**: Create searchable term indices
3. **Search**: Implement file-based search functionality
4. **Annotation**: Add hyperlinks to PDFs based on terms
5. **Configuration**: Add YAML-based configuration management 