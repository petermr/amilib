# Pipeline Design for Breward2023

## Overview

The pipeline design provides a structured approach to document processing that is:
- **Human-visible**: All intermediate results are inspectable
- **Pipeline-friendly**: Clear input/output relationships between steps
- **Testable**: Each step can be tested independently
- **Reproducible**: Can re-run any step with its inputs
- **Make-like**: Supports suffix-based processing for production

## Directory Structure

```
pipeline/
├── breward2023/                    # Project-specific pipeline
│   ├── 00_input/                   # Raw input files
│   │   └── pdfs/                   # Original PDFs
│   ├── 01_corpus/                  # Step 1: Corpus creation
│   │   ├── corpus/                 # AmiCorpus structure
│   │   └── logs/                   # Step 1 logs
│   ├── 02_extraction/              # Step 2: Text extraction
│   │   ├── extracted_text/         # Extracted text files
│   │   └── logs/
│   ├── 03_indexing/                # Step 3: Term indexing
│   │   ├── indices/                # Term indices
│   │   └── logs/
│   ├── 04_annotation/              # Step 4: PDF annotation
│   │   ├── annotated_pdfs/         # Final annotated PDFs
│   │   └── logs/
│   └── config/                     # Pipeline configuration
│       ├── pipeline.yaml           # Overall pipeline config
│       └── steps/                  # Step-specific configs
├── other_project/                  # Other projects
└── shared/                         # Shared resources
    ├── templates/                  # Reusable templates
    └── tools/                      # Pipeline tools
```

## Pipeline Steps

### 1. Corpus Creation (`01_corpus`)
- **Input**: Raw PDF files
- **Output**: BagIt-compliant corpus structure
- **Purpose**: Organize documents into a structured corpus
- **Technology**: AmiCorpus with declarative commands

### 2. Text Extraction (`02_extraction`)
- **Input**: PDF files from corpus
- **Output**: Extracted text files
- **Purpose**: Extract text content from PDFs
- **Technology**: PyMuPDF
- **Suffix Rule**: `.pdf` → `.txt`

### 3. Term Indexing (`03_indexing`)
- **Input**: Extracted text files
- **Output**: Term indices and significance scores
- **Purpose**: Create searchable term indices
- **Technology**: TF-IDF with scikit-learn
- **Suffix Rule**: `.txt` → `.idx`

### 4. PDF Annotation (`04_annotation`)
- **Input**: Original PDFs + term indices
- **Output**: Annotated PDFs with hyperlinks
- **Purpose**: Add hyperlinks to significant terms
- **Technology**: PyMuPDF
- **Suffix Rule**: `.idx` → `.annotated.pdf`

## Configuration

### Main Pipeline Config (`pipeline.yaml`)
```yaml
project:
  name: "breward2023"
  version: "1.0"

pipeline:
  steps:
    - name: "corpus_creation"
      input: "00_input/pdfs/"
      output: "01_corpus/corpus/"
      dependencies: []
    # ... more steps

suffixes:
  ".pdf": ".txt"
  ".txt": ".idx"
  ".idx": ".annotated.pdf"
```

### Step-Specific Configs
Each step has its own YAML configuration file:
- `config/steps/corpus.yaml` - Corpus creation parameters
- `config/steps/extraction.yaml` - Text extraction settings
- `config/steps/indexing.yaml` - Term indexing parameters
- `config/steps/annotation.yaml` - PDF annotation settings

## Usage

### Development/Testing
```bash
# List available steps
python pipeline/shared/tools/pipeline_runner.py pipeline/breward2023 --list

# Run specific step
python pipeline/shared/tools/pipeline_runner.py pipeline/breward2023 --step corpus_creation

# Run pipeline from start to end
python pipeline/shared/tools/pipeline_runner.py pipeline/breward2023 --start corpus_creation --end pdf_annotation
```

### Production (Make-like)
```bash
# Process all PDFs through the pipeline
make -f pipeline/breward2023/Makefile all

# Process specific file
make -f pipeline/breward2023/Makefile document.pdf.annotated.pdf
```

## Benefits

### For Development
- **Visibility**: All intermediate results are inspectable
- **Debugging**: Easy to identify where issues occur
- **Testing**: Each step can be tested independently
- **Incremental**: Can re-run specific steps without full pipeline

### For Production
- **Make-like**: Familiar suffix-based processing
- **Efficient**: Only re-process changed files
- **Parallel**: Can process multiple files simultaneously
- **Robust**: Clear dependency management

### For Collaboration
- **Standardized**: Consistent structure across projects
- **Documented**: Configuration files serve as documentation
- **Reusable**: Templates and tools can be shared
- **Versionable**: All intermediate results can be version controlled

## Git Integration

The `.gitignore` is configured to exclude:
- Log files (`pipeline/*/logs/`)
- Temporary files (`pipeline/*/temp/`)
- Output files (`pipeline/*/output/`)
- Non-BagIt directories

This allows version control of:
- Configuration files
- Templates and tools
- Final outputs (when desired)
- Corpus structure (BagIt-managed content)

## Future Enhancements

1. **Makefile Generation**: Auto-generate Makefiles from pipeline config
2. **Parallel Processing**: Support for parallel step execution
3. **Cloud Integration**: Support for cloud storage and processing
4. **Monitoring**: Real-time pipeline monitoring and metrics
5. **Rollback**: Ability to rollback to previous pipeline states 