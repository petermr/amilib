# AR6 Incremental Processing System

A make-like system for processing AR6 IPCC components through transformation stages. Skips already completed work and enables incremental processing.

## Overview

This system processes AR6 components (chapters, SPMs, TS, annexes, cross-chapter boxes) through 5 transformation stages:

1. **Download** - Download from IPCC website
2. **PDF Convert** - Convert PDF to raw HTML (if PDF source)
3. **Clean** - Remove navigation and unnecessary markup
4. **Structure** - Ensure proper HTML structure
5. **Add IDs** - Add semantic IDs to paragraphs and sections

## Features

- ✅ **Incremental Processing** - Skips already completed stages
- ✅ **Batch Processing** - Process multiple components at once
- ✅ **Status Tracking** - Registry tracks stage completion
- ✅ **Resumable** - Can resume interrupted jobs
- ✅ **Flexible Filtering** - Filter by report, component type, etc.

## Usage

### Process Single Component

```bash
python scripts/ar6_processor/cli.py process --component-id wg1-spm
```

### Process All SPMs

```bash
python scripts/ar6_processor/cli.py process --component-type spm --target-stage add_ids
```

### Process All Missing Components for a Report

```bash
python scripts/ar6_processor/cli.py process --report wg1 --target-stage add_ids
```

### Check Component Status

```bash
python scripts/ar6_processor/cli.py status --component-id wg1-spm
```

### Show Summary Statistics

```bash
python scripts/ar6_processor/cli.py status --summary --report wg1
```

### Update Registry from Filesystem

```bash
python scripts/ar6_processor/cli.py registry --scan
```

### List All Components

```bash
python scripts/ar6_processor/cli.py registry --list
```

## Examples

### Process All Missing SPMs

```bash
# Process all SPMs that haven't been fully processed
python scripts/ar6_processor/cli.py process \
    --component-type spm \
    --target-stage add_ids
```

### Convert PDF Annexes to HTML

```bash
# Only run PDF conversion stage for annexes
python scripts/ar6_processor/cli.py process \
    --component-type annex \
    --target-stage pdf_convert
```

### Force Re-run (for testing)

```bash
# Force re-run even if stages are complete
python scripts/ar6_processor/cli.py process \
    --component-type spm \
    --force
```

## Architecture

- **Registry** (`registry.py`) - Tracks components and stage status
- **Pipeline** (`pipeline.py`) - Orchestrates stage processing
- **Stage Processors** (`stage_processors/`) - Individual stage implementations
- **Batch Processor** (`batch_processor.py`) - Batch processing logic
- **CLI** (`cli.py`) - Command-line interface

## Registry

The registry is stored at: `temp/ar6_processor/registry.json`

It tracks:
- Component metadata (report, type, directory, URL)
- Stage completion status
- Output files for each stage
- Completion dates

## Stage Dependencies

- `pdf_convert` depends on `download`
- `clean` depends on `download` or `pdf_convert`
- `structure` depends on `clean`
- `add_ids` depends on `structure`

## Adding New Stages

To add a new stage:

1. Create stage processor in `stage_processors/`
2. Add to `AR6Pipeline.STAGES` list
3. Add processor class to `AR6Pipeline.STAGE_PROCESSORS`
4. Update stage dependencies if needed

## Notes

- The system automatically detects existing files and skips completed stages
- PDF conversion stage is not yet fully implemented (placeholder)
- Registry is auto-generated from filesystem on first run
- Components can be manually added to registry if needed





