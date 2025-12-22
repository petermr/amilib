# AR6 Incremental Processing System Proposal

**Date:** 2025-12-19  
**Purpose:** Propose a "make"-like incremental processing system for AR6 components that skips already completed work and allows stepwise functionality addition

---

## Executive Summary

This proposal outlines an incremental processing system for AR6 IPCC components (chapters, SPMs, TS, Cross-Chapter boxes, annexes) that:

1. **Tracks processing stages** - Each component goes through 5 distinct transformation stages
2. **Skips completed work** - Automatically detects what's already done and only processes missing stages
3. **Enables incremental processing** - Can run partial jobs without redoing completed work
4. **Supports stepwise enhancement** - Easy to add new transformation steps or modify existing ones

---

## Current State Summary

### What Has Been Downloaded

#### AR6 Main Components (WG1/2/3)

**✅ Fully Processed:**
- **WG1 Chapters:** 12/12 chapters (Chapter01-Chapter12) - All have `html_with_ids.html`
- **WG2 Chapters:** 18/18 chapters (Chapter01-Chapter18) - All have `html_with_ids.html`
- **WG3 Chapters:** 17/17 chapters (Chapter01-Chapter17) - All have `html_with_ids.html`
- **WG2 Annex II (Glossary):** ✅ Processed with semantic IDs
- **WG2 Cross-Chapter Boxes:** 7/7 downloaded (ccp1-ccp7), but only ccp5 has been cleaned

**⚠️ Partially Processed:**
- **WG1 SPM:** Downloaded (`gatsby_raw.html` exists, ~560 KB) but missing IDs
- **WG1 TS:** Downloaded (`gatsby_raw.html` exists, ~1,061 KB) but missing IDs
- **WG2 SPM:** Downloaded but missing IDs
- **WG2 TS:** Downloaded but missing IDs
- **WG3 SPM:** Downloaded but missing IDs
- **WG3 TS:** Downloaded but missing IDs
- **SYR Longer Report:** ✅ Processed with IDs

**❌ Not Downloaded/Processed:**
- **WG1 Annex I (Glossary):** PDF only (~574 KB), needs PDF→HTML conversion
- **WG1 Annex II (Acronyms):** PDF only (~70 KB), needs PDF→HTML conversion
- **WG2 Annex III (Acronyms):** PDF downloaded (~80 KB), needs PDF→HTML conversion
- **WG2 Cross-Chapter Boxes:** ccp1-ccp4, ccp6-ccp7 downloaded but not cleaned
- **WG3 Annex I (Glossary):** PDF only (~267 KB), needs PDF→HTML conversion
- **WG3 Annex VI (Acronyms):** PDF only (~131 KB), needs PDF→HTML conversion
- **SYR SPM:** Small HTML file (~50 KB), may need PDF
- **SYR TS:** Small HTML file (~50 KB), may need PDF
- **SYR Annex I (Glossary):** PDF only (~81 KB), needs processing
- **SYR Annex II (Acronyms):** PDF only (~81 KB), needs processing
- **SYR Annexes and Index:** PDF only (~346 KB), needs processing

### What Transformations Have Been Applied

#### Transformation Pipeline (5 Stages)

1. **Stage 1: Download (Scrape)**
   - **Input:** IPCC website URL
   - **Output:** `gatsby_raw.html` or `wordpress_raw.html` or `.pdf`
   - **Status:** Most components downloaded, some PDFs need conversion

2. **Stage 2: PDF to Raw HTML (if PDF source)**
   - **Input:** PDF file
   - **Output:** Raw HTML pages (`total_pages.html` or page-by-page HTML)
   - **Status:** Only applied to some annexes, many PDFs still need conversion

3. **Stage 3: Clean HTML (Remove Navigation/Tooltips)**
   - **Input:** Raw HTML (`gatsby_raw.html`, `wordpress_raw.html`, or PDF-derived HTML)
   - **Output:** `de_gatsby.html` or `de_wordpress.html`
   - **Transformation:** Removes navigation bars, tooltips, popups, footer content, style attributes, JavaScript
   - **Status:** Most chapters cleaned, some SPM/TS cleaned, annexes partially cleaned

4. **Stage 4: Structure HTML (Add Semantic Structure)**
   - **Input:** Cleaned HTML (`de_gatsby.html` or `de_wordpress.html`)
   - **Output:** Structured HTML with proper section hierarchy
   - **Transformation:** Ensures proper nested structure (`h1-container`, `h2-container`, etc.)
   - **Status:** Applied to most chapters, may need enhancement for SPM/TS/annexes

5. **Stage 5: Add Semantic IDs**
   - **Input:** Structured HTML
   - **Output:** `html_with_ids.html`, `id_list.html`, `para_list.html`
   - **Transformation:** 
     - Adds paragraph IDs: `{section_id}_p{index}` (e.g., `3.1.2_p1`)
     - Adds section IDs: `\d+(\\.\d+)*` (e.g., `3.1.2`)
     - Adds IDs to lists, tables, figures, boxes
     - Generates ID lists for validation
   - **Status:** Applied to all chapters, missing for SPM/TS/annexes

#### File Naming Conventions

**Raw Files:**
- `gatsby_raw.html` - Raw HTML from Gatsby-based IPCC site
- `wordpress_raw.html` - Raw HTML from WordPress-based IPCC site
- `*.pdf` - Original PDF files

**Intermediate Files:**
- `de_gatsby.html` - Cleaned Gatsby HTML (navigation/tooltips removed)
- `de_wordpress.html` - Cleaned WordPress HTML
- `total_pages.html` - Combined PDF pages as HTML
- `page_*.html` - Individual PDF pages as HTML

**Final Files:**
- `html_with_ids.html` - Final output with semantic IDs
- `id_list.html` - List of all IDs in document
- `para_list.html` - List of all paragraphs with IDs

#### Current Coverage Statistics

- **Chapters with IDs:** 47/47 (100% of downloaded chapters)
- **Paragraph ID Coverage:** ~74.5% average (varies by chapter)
- **Section ID Coverage:** ~99.7% average
- **SPM/TS with IDs:** 0/6 (0%)
- **Annexes with IDs:** 1/8 (12.5%)
- **Cross-Chapter Boxes with IDs:** 0/7 (0%)

---

## Proposed Incremental Processing System

### Core Concept: Stage-Based Dependency Tracking

Each AR6 component (chapter, SPM, TS, annex, cross-chapter box) is processed through a pipeline of stages. The system tracks which stages have been completed and only runs missing stages.

### Architecture

#### 1. Component Registry

A registry file (JSON/YAML) defines all AR6 components and their metadata:

```yaml
components:
  - id: "wg1-chapter01"
    report: "wg1"
    type: "chapter"
    number: 1
    url: "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/"
    stages:
      download: {status: "complete", file: "gatsby_raw.html", date: "2025-12-06"}
      pdf_convert: {status: "skip", reason: "HTML source"}
      clean: {status: "complete", file: "de_gatsby.html", date: "2025-12-06"}
      structure: {status: "complete", date: "2025-12-06"}
      add_ids: {status: "complete", file: "html_with_ids.html", date: "2025-12-06"}
  
  - id: "wg1-spm"
    report: "wg1"
    type: "spm"
    url: "https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf"
    stages:
      download: {status: "complete", file: "gatsby_raw.html", date: "2025-12-06"}
      pdf_convert: {status: "skip", reason: "HTML source"}
      clean: {status: "complete", file: "de_gatsby.html", date: "2025-12-06"}
      structure: {status: "pending"}
      add_ids: {status: "pending"}
  
  - id: "wg1-annex-i-glossary"
    report: "wg1"
    type: "annex"
    annex_type: "glossary"
    url: "https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_AnnexI.pdf"
    stages:
      download: {status: "complete", file: "IPCC_AR6_WGI_AnnexI.pdf", date: "2025-12-10"}
      pdf_convert: {status: "pending"}
      clean: {status: "pending"}
      structure: {status: "pending"}
      add_ids: {status: "pending"}
```

#### 2. Stage Detection Logic

For each component, the system checks file existence and content to determine stage completion:

```python
def check_stage_status(component_id, stage_name, component_dir):
    """
    Check if a stage has been completed by examining files.
    
    Returns: dict with 'status' ('complete', 'pending', 'skip'), 
             'file' (path if complete), 'date' (completion date)
    """
    stage_checks = {
        'download': {
            'files': ['gatsby_raw.html', 'wordpress_raw.html', '*.pdf'],
            'min_size': 10000  # bytes
        },
        'pdf_convert': {
            'files': ['total_pages.html', 'page_*.html'],
            'depends_on': 'download',
            'condition': lambda c: c['source_type'] == 'pdf'
        },
        'clean': {
            'files': ['de_gatsby.html', 'de_wordpress.html'],
            'depends_on': ['download', 'pdf_convert'],
            'min_size': 5000
        },
        'structure': {
            'check': 'has_section_structure',  # Custom check function
            'depends_on': 'clean'
        },
        'add_ids': {
            'files': ['html_with_ids.html'],
            'depends_on': 'structure',
            'validation': 'check_id_coverage'  # Must have >95% paragraph IDs
        }
    }
    
    check_config = stage_checks[stage_name]
    # Implementation checks files, dependencies, validation
```

#### 3. Processing Pipeline

The system processes components through stages, skipping completed ones:

```python
def process_component(component_id, target_stage=None):
    """
    Process a component through all stages up to target_stage.
    Skips already completed stages.
    
    Args:
        component_id: ID of component to process
        target_stage: Final stage to reach (None = all stages)
    """
    component = registry.get(component_id)
    stages = ['download', 'pdf_convert', 'clean', 'structure', 'add_ids']
    
    if target_stage:
        stages = stages[:stages.index(target_stage) + 1]
    
    for stage in stages:
        status = check_stage_status(component_id, stage, component['dir'])
        
        if status['status'] == 'complete':
            logger.info(f"{component_id}: Stage '{stage}' already complete, skipping")
            continue
        
        if status['status'] == 'skip':
            logger.info(f"{component_id}: Stage '{stage}' skipped: {status['reason']}")
            continue
        
        # Check dependencies
        if not check_dependencies(component_id, stage):
            logger.warning(f"{component_id}: Dependencies not met for '{stage}', skipping")
            continue
        
        # Run stage processor
        logger.info(f"{component_id}: Running stage '{stage}'")
        result = run_stage_processor(component_id, stage)
        
        if result['success']:
            update_registry(component_id, stage, result)
        else:
            logger.error(f"{component_id}: Stage '{stage}' failed: {result['error']}")
            break  # Stop pipeline on failure
```

#### 4. Batch Processing

Process multiple components, respecting dependencies:

```python
def process_batch(component_ids=None, report=None, component_type=None, 
                  target_stage=None, force=False):
    """
    Process multiple components in batch.
    
    Args:
        component_ids: List of specific component IDs (None = all)
        report: Filter by report (wg1, wg2, wg3, syr)
        component_type: Filter by type (chapter, spm, ts, annex, cross-chapter-box)
        target_stage: Final stage to reach
        force: If True, re-run completed stages
    """
    components = filter_components(component_ids, report, component_type)
    
    for component_id in components:
        if force:
            # Clear stage statuses before processing
            clear_stage_statuses(component_id, target_stage)
        
        process_component(component_id, target_stage)
```

### Benefits

1. **Incremental Processing**
   - Can run partial jobs (e.g., "process all SPMs up to clean stage")
   - Can resume interrupted jobs
   - Can process subsets (e.g., "only WG1 components")

2. **Efficiency**
   - Skips already completed work
   - Only processes what's needed
   - Can parallelize independent components

3. **Stepwise Enhancement**
   - Easy to add new stages (e.g., "add_wikimedia_ids")
   - Easy to modify existing stages
   - Can add validation steps between stages

4. **Transparency**
   - Clear status tracking
   - Logs show what was skipped vs. processed
   - Registry provides audit trail

### Implementation Structure

```
scripts/ar6_processor/
├── __init__.py
├── registry.py              # Component registry management
├── stage_detector.py        # Stage completion detection
├── stage_processors.py      # Stage-specific processors
│   ├── download_stage.py
│   ├── pdf_convert_stage.py
│   ├── clean_stage.py
│   ├── structure_stage.py
│   └── add_ids_stage.py
├── pipeline.py              # Main pipeline orchestrator
├── batch_processor.py       # Batch processing logic
└── config/
    ├── components.yaml      # Component registry
    └── stages.yaml          # Stage definitions
```

### Usage Examples

#### Example 1: Process All Missing SPMs

```bash
# Process all SPMs that haven't been fully processed
python scripts/ar6_processor/pipeline.py \
    --component-type spm \
    --target-stage add_ids
```

#### Example 2: Convert All PDF Annexes to HTML

```bash
# Only run PDF conversion stage for annexes
python scripts/ar6_processor/pipeline.py \
    --component-type annex \
    --target-stage pdf_convert
```

#### Example 3: Add IDs to Already-Cleaned Files

```bash
# Process components that are cleaned but missing IDs
python scripts/ar6_processor/pipeline.py \
    --target-stage add_ids \
    --skip-if-stage-complete clean
```

#### Example 4: Process Single Component

```bash
# Process specific component through all stages
python scripts/ar6_processor/pipeline.py \
    --component-id wg1-spm
```

#### Example 5: Force Re-run (for testing)

```bash
# Force re-run even if stages are complete
python scripts/ar6_processor/pipeline.py \
    --component-type spm \
    --force
```

### Adding New Functionality

#### Adding a New Stage

1. **Define stage in `config/stages.yaml`:**
```yaml
stages:
  add_wikimedia_ids:
    depends_on: add_ids
    processor: wikimedia_ids_stage.py
    output_files: ['html_with_wikimedia_ids.html']
    validation: check_wikimedia_id_coverage
```

2. **Create stage processor:**
```python
# scripts/ar6_processor/stage_processors/wikimedia_ids_stage.py
def process_wikimedia_ids(component_id, component_dir, input_file):
    # Implementation
    pass
```

3. **Update pipeline:**
```python
# Add to stages list in pipeline.py
stages = ['download', 'pdf_convert', 'clean', 'structure', 
          'add_ids', 'add_wikimedia_ids']
```

#### Modifying Existing Stage

Simply update the stage processor file. The system will detect that the stage needs re-running if:
- Output file is missing
- Output file is older than processor code
- Validation fails

### Registry Management

The registry can be:
- **Auto-generated** from file system (scans `test/resources/ipcc/cleaned_content/`)
- **Manually maintained** (for components not yet downloaded)
- **Hybrid** (auto-detect existing, manual for missing)

### Validation and Quality Checks

Each stage can include validation:

```python
def validate_stage_output(component_id, stage, output_file):
    """
    Validate stage output meets quality requirements.
    
    Returns: dict with 'valid' (bool), 'issues' (list), 'metrics' (dict)
    """
    validations = {
        'download': {
            'min_size': 10000,
            'file_type_check': True
        },
        'clean': {
            'no_navigation': True,
            'no_tooltips': True,
            'min_content_size': 5000
        },
        'add_ids': {
            'paragraph_coverage': 0.95,  # 95%+
            'section_coverage': 0.99,    # 99%+
            'no_duplicates': True
        }
    }
    # Implementation
```

---

## Migration Path

### Phase 1: Registry Creation (Week 1)
1. Scan existing filesystem to auto-generate registry
2. Identify missing components
3. Create registry file with all AR6 components

### Phase 2: Stage Detection (Week 1)
1. Implement stage detection logic
2. Test on existing components
3. Verify correct detection of completed stages

### Phase 3: Pipeline Implementation (Week 2)
1. Implement stage processors (reuse existing code)
2. Implement pipeline orchestrator
3. Test on subset of components

### Phase 4: Batch Processing (Week 2)
1. Implement batch processor
2. Add filtering options
3. Test on all components

### Phase 5: Documentation and Testing (Week 3)
1. Document usage
2. Create examples
3. Test edge cases

---

## Next Steps

1. **Review and approve proposal**
2. **Create component registry** (scan filesystem + manual entries)
3. **Implement stage detection** (start with file existence checks)
4. **Implement pipeline** (reuse existing processors)
5. **Test on subset** (e.g., all SPMs)
6. **Roll out to all components**

---

## Questions for Discussion

1. **Registry format:** JSON vs. YAML vs. SQLite database?
2. **Stage detection:** File-based only, or also content validation?
3. **Parallelization:** Process multiple components in parallel?
4. **Error handling:** Continue on error, or stop pipeline?
5. **Reporting:** How detailed should progress reports be?

---

## Conclusion

This incremental processing system will:
- ✅ Skip already completed work
- ✅ Enable incremental processing
- ✅ Support stepwise functionality addition
- ✅ Provide clear status tracking
- ✅ Make it easy to resume interrupted jobs
- ✅ Allow processing subsets of components

The system is designed to be flexible and extensible, making it easy to add new transformation stages or modify existing ones as requirements evolve.




