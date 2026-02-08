# Python Make-Like Tools Recommendation

**Date:** 2025-12-19  
**Use Case:** Incremental processing of IPCC AR6 documents with dependency tracking

---

## Recommendation: **doit**

**Best Choice:** [`doit`](https://pydoit.org/) - A Python task management and automation tool

### Why `doit`?

1. ✅ **File Dependency Tracking** - Automatically tracks file dependencies and skips tasks if inputs haven't changed
2. ✅ **Python-Native** - Pure Python, easy to integrate with existing codebase
3. ✅ **Simple Task Definition** - Clean, declarative task definitions
4. ✅ **Incremental Processing** - Built-in support for skipping completed work
5. ✅ **Active Maintenance** - Well-maintained, actively developed
6. ✅ **Lightweight** - Minimal dependencies, fast execution

### Example `doit` Configuration

**File: `dodo.py`** (doit's equivalent of Makefile)

```python
"""doit tasks for AR6 document processing."""

from pathlib import Path
from doit import create_after

# Define base directories
BASE_DIR = Path("test/resources/ipcc/cleaned_content")

def task_add_paragraph_ids():
    """Add paragraph IDs to SPM/TS documents."""
    
    # Find all SPM/TS documents
    for report in ['wg1', 'wg2', 'wg3']:
        for doc_type in ['summary-for-policymakers', 'technical-summary']:
            doc_dir = BASE_DIR / report / doc_type
            cleaned_file = doc_dir / "de_gatsby.html"
            output_file = doc_dir / "html_with_ids.html"
            
            if not cleaned_file.exists():
                continue
            
            yield {
                'name': f'{report}-{doc_type}',
                'file_dep': [cleaned_file],
                'targets': [output_file],
                'actions': [
                    f'python scripts/add_spm_ts_paragraph_ids.py --report {report} --doc-type {doc_type.replace("-", "_")}'
                ],
                'clean': True,  # Allow cleaning
            }

def task_add_section_ids():
    """Add section IDs to documents."""
    # Similar pattern...
    pass
```

**Usage:**
```bash
# Run all tasks
doit

# Run specific task
doit add_paragraph_ids

# Force re-run (ignore dependencies)
doit --force

# List tasks
doit list

# Show task details
doit info
```

---

## Alternative Options

### 2. **invoke** (formerly Fabric)

**Pros:**
- Simple task execution
- Good for command-line automation
- Clean Python API

**Cons:**
- No built-in dependency tracking
- Requires manual implementation of "skip if done" logic

**Example:**
```python
# tasks.py
from invoke import task
from pathlib import Path

@task
def add_paragraph_ids(c, report=None, doc_type=None):
    """Add paragraph IDs."""
    # Manual dependency checking required
    pass
```

**Usage:**
```bash
invoke add-paragraph-ids --report wg1
```

---

### 3. **Snakemake**

**Pros:**
- Powerful workflow management
- Excellent for complex pipelines
- Built-in parallelization

**Cons:**
- More complex than needed for this use case
- Designed primarily for scientific workflows
- Steeper learning curve

**Example:**
```python
# Snakefile
rule add_paragraph_ids:
    input:
        "test/resources/ipcc/cleaned_content/{report}/{doc}/de_gatsby.html"
    output:
        "test/resources/ipcc/cleaned_content/{report}/{doc}/html_with_ids.html"
    shell:
        "python scripts/add_spm_ts_paragraph_ids.py --report {wildcards.report}"
```

---

### 4. **Luigi** (Spotify)

**Pros:**
- Robust workflow management
- Good for complex pipelines
- Built-in visualization

**Cons:**
- More complex than needed
- Requires more boilerplate
- Better for distributed systems

---

### 5. **Enhance Existing Registry System**

**Pros:**
- Already implemented
- Customized to your needs
- No new dependencies

**Cons:**
- Manual maintenance
- Less standardized
- More code to maintain

**Current System:**
- `scripts/ar6_processor/registry.py` - Tracks component status
- `scripts/ar6_processor/pipeline.py` - Orchestrates stages
- Already implements make-like behavior!

---

## Comparison Table

| Tool | Complexity | Dependency Tracking | File-Based | Python-Native | Best For |
|------|-----------|---------------------|------------|---------------|----------|
| **doit** | ⭐⭐ Low | ✅ Built-in | ✅ Yes | ✅ Yes | **This use case** |
| invoke | ⭐ Low | ❌ Manual | ❌ No | ✅ Yes | Simple task execution |
| Snakemake | ⭐⭐⭐ Medium | ✅ Built-in | ✅ Yes | ✅ Yes | Scientific workflows |
| Luigi | ⭐⭐⭐⭐ High | ✅ Built-in | ✅ Yes | ✅ Yes | Distributed pipelines |
| Custom Registry | ⭐⭐ Low | ✅ Custom | ✅ Yes | ✅ Yes | Current system |

---

## Recommendation: Use `doit` OR Enhance Existing System

### Option A: Adopt `doit` (Recommended for New Features)

**Benefits:**
- Standard tool with good documentation
- Automatic dependency tracking
- Less custom code to maintain
- Easy to extend with new processing stages

**Migration Path:**
1. Install: `pip install doit`
2. Create `dodo.py` with task definitions
3. Gradually migrate existing registry logic to `doit` tasks
4. Keep registry for status tracking, use `doit` for execution

### Option B: Enhance Existing Registry System (Recommended for Current Workflow)

**Benefits:**
- Already working
- Customized to your needs
- No new dependencies
- Full control

**Enhancements Needed:**
1. Add file timestamp checking (like `make`)
2. Add dependency graph tracking
3. Add parallel execution support
4. Add better CLI interface

---

## Proposed Schema for Cascading ID Addition

### Schema Definition

```python
"""
Schema for cascading ID addition to divs and paragraphs.

Rules:
1. Section containers (h1-container, h2-container, etc.) get IDs from their headings
2. Paragraphs get IDs based on their parent section container
3. Nested divs get IDs based on their parent container
4. IDs are generated in a cascading manner: parent → child → grandchild
"""

ID_SCHEMA = {
    'section_containers': {
        'pattern': r'div[contains(@class, "h\d+-container")]',
        'id_source': 'heading_text',  # Extract from h1, h2, etc.
        'id_format': '{normalized_heading}',
        'priority': 1,  # Highest priority
    },
    'paragraphs': {
        'pattern': r'p',
        'id_source': 'parent_section_id',
        'id_format': '{section_id}_p{index}',
        'priority': 2,
        'requires': ['section_containers'],  # Depends on section IDs
    },
    'nested_divs': {
        'pattern': r'div[not(contains(@class, "container"))]',
        'id_source': 'parent_container_id',
        'id_format': '{parent_id}_{type}_{index}',
        'priority': 3,
        'requires': ['section_containers'],
    },
    'siblings_divs': {
        'pattern': r'div[contains(@class, "h\d+-siblings")]',
        'id_source': 'parent_section_id',
        'id_format': 'h{level}-{index}-siblings',
        'priority': 1,  # Same as containers
    },
}
```

### Implementation with `doit`

```python
"""dodo.py - doit tasks for cascading ID addition."""

from pathlib import Path
from doit import create_after

BASE_DIR = Path("test/resources/ipcc/cleaned_content")

def task_add_section_ids():
    """Step 1: Add IDs to section containers."""
    for report in ['wg1', 'wg2', 'wg3']:
        for doc_type in ['summary-for-policymakers', 'technical-summary']:
            doc_dir = BASE_DIR / report / doc_type
            cleaned_file = doc_dir / "de_gatsby.html"
            section_ids_file = doc_dir / "html_with_section_ids.html"
            
            if not cleaned_file.exists():
                continue
            
            yield {
                'name': f'section-ids-{report}-{doc_type}',
                'file_dep': [cleaned_file],
                'targets': [section_ids_file],
                'actions': [
                    f'python scripts/add_section_ids.py --input {cleaned_file} --output {section_ids_file}'
                ],
            }

@create_after(executed='add_section_ids', target_regex=r'.*html_with_section_ids\.html$')
def task_add_paragraph_ids():
    """Step 2: Add IDs to paragraphs (depends on section IDs)."""
    for report in ['wg1', 'wg2', 'wg3']:
        for doc_type in ['summary-for-policymakers', 'technical-summary']:
            doc_dir = BASE_DIR / report / doc_type
            section_ids_file = doc_dir / "html_with_section_ids.html"
            output_file = doc_dir / "html_with_ids.html"
            
            if not section_ids_file.exists():
                continue
            
            yield {
                'name': f'para-ids-{report}-{doc_type}',
                'file_dep': [section_ids_file],
                'targets': [output_file],
                'actions': [
                    f'python scripts/add_paragraph_ids.py --input {section_ids_file} --output {output_file}'
                ],
            }

@create_after(executed='add_paragraph_ids', target_regex=r'.*html_with_ids\.html$')
def task_add_nested_div_ids():
    """Step 3: Add IDs to nested divs (depends on paragraph IDs)."""
    # Similar pattern...
    pass
```

---

## Next Steps

1. **Decision:** Choose `doit` or enhance existing registry system
2. **If `doit`:**
   - Install: `pip install doit`
   - Create `dodo.py` with task definitions
   - Migrate existing processing logic
3. **If enhance existing:**
   - Add file timestamp checking to registry
   - Add dependency graph to pipeline
   - Add parallel execution support
4. **Create ID Schema:**
   - Define cascading ID rules
   - Implement schema-based ID generation
   - Add validation

---

## References

- **doit:** https://pydoit.org/
- **invoke:** https://www.pyinvoke.org/
- **Snakemake:** https://snakemake.readthedocs.io/
- **Luigi:** https://github.com/spotify/luigi

---

**Recommendation:** Start with `doit` for new features, keep existing registry for status tracking. This gives you the best of both worlds: standard tooling for execution, custom tracking for status.




