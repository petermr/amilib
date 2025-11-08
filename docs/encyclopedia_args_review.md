# Encyclopedia Args Review - pmr202511

**Date:** November 7, 2025 (system date of generation)  
**Branch:** `pmr202511`  
**Issue:** ENCYCLOPEDIA subparser exists but doesn't appear in command line help

## Current State

### Files Involved
- `amilib/ami_encyclopedia_args.py` - Contains `EncyclopediaArgs` class
- `amilib/amix.py` - Main entry point that registers subparsers

### Problem

The `EncyclopediaArgs` class exists but:
1. **Not registered in `amix.py`** - Missing from subparser creation
2. **Wrong method name** - Uses `add_subparser_args()` instead of `add_arguments()`
3. **Missing `subparser_arg` attribute** - Not set in `__init__()`
4. **Wrong pattern** - Doesn't follow the standard subparser pattern used by other Args classes

## Current Implementation Issues

### In `amilib/ami_encyclopedia_args.py`:

**Issue 1: Missing `subparser_arg`**
```python
def __init__(self):
    super().__init__()
    # Missing: self.subparser_arg = "ENCYCLOPEDIA"
    self.operation = "create"
    ...
```

**Issue 2: Wrong method name and pattern**
```python
def add_subparser_args(self, subparser):
    """Add encyclopedia-specific arguments to subparser"""
    encyclopedia_parser = subparser.add_parser("ENCYCLOPEDIA", help="Encyclopedia operations")
    # This creates a NEW parser, but should add to self.parser
    ...
```

**Should be:**
```python
def add_arguments(self):
    """Add encyclopedia-specific arguments"""
    # self.parser is already set by make_sub_parser()
    self.parser.add_argument(...)
    ...
```

### In `amilib/amix.py`:

**Issue 3: Not registered in subparser creation (lines 109-116)**
```python
html_parser = AmiLibArgs.make_sub_parser(HTMLArgs(), subparsers)
dict_parser = AmiLibArgs.make_sub_parser(AmiDictArgs(), subparsers)
pdf_parser = AmiLibArgs.make_sub_parser(PDFArgs(), subparsers)
search_parser = AmiLibArgs.make_sub_parser(SearchArgs(), subparsers)
# Missing: encyclopedia_parser = AmiLibArgs.make_sub_parser(EncyclopediaArgs(), subparsers)
```

**Issue 4: Not registered in subparser_dict (lines 243-248)**
```python
subparser_dict = {
    "DICT": AmiDictArgs(),
    "SEARCH": SearchArgs(),
    "HTML": HTMLArgs(),
    "PDF": PDFArgs(),
    # Missing: "ENCYCLOPEDIA": EncyclopediaArgs(),
}
```

**Issue 5: Not mentioned in help text (lines 73-100)**
The description doesn't mention ENCYCLOPEDIA as a subcommand option.

## Proposed Arguments Review

### Current Arguments in `EncyclopediaArgs.add_subparser_args()`:

1. `--input, -i` (Path) - Input HTML file containing encyclopedia entries
2. `--output, -o` (Path) - Output file for normalized encyclopedia  
3. `--title, -t` (str, default="Encyclopedia") - Title for the encyclopedia
4. `--no-normalize` (flag) - Skip Wikipedia URL normalization
5. `--no-synonyms` (flag) - Skip synonym aggregation
6. `--stats` (flag) - Show encyclopedia statistics

### Questions for Review:

1. **Should we use `--input` or `--inpath`?** 
   - Other subparsers use `--inpath` (DICT, SEARCH, HTML, PDF)
   - Consistency suggests `--inpath`

2. **Should we use `--output` or `--outpath`?**
   - Other subparsers use `--outpath`
   - Consistency suggests `--outpath`

3. **Should we have an `--operation` argument?**
   - DICT and SEARCH have `--operation` with choices
   - Current implementation assumes single operation (normalize/aggregate)
   - May want: `create`, `normalize`, `aggregate`, `stats`, etc.

4. **Should we support `--description` like DICT?**
   - DICT has `--description` for wikipedia/wikidata/wiktionary
   - Encyclopedia might want similar options

5. **Should we support `--wikidata` or `--wikipedia` flags?**
   - For enabling/disabling specific lookups
   - Similar to DICT's description options

6. **Should we have `--normalize-by` option?**
   - Current code has `normalize_by_wikidata_id()` and `normalize_by_wikipedia_url()`
   - Should allow choosing which normalization method

## Required Fixes

### Fix 1: Update `EncyclopediaArgs.__init__()`
```python
def __init__(self):
    super().__init__()
    self.subparser_arg = "ENCYCLOPEDIA"  # ADD THIS
    self.operation = "create"
    self.input_file = None
    self.output_file = None
    self.title = "Encyclopedia"
    self.normalize = True
    self.aggregate_synonyms = True
```

### Fix 2: Rename and fix `add_subparser_args()` to `add_arguments()`
```python
def add_arguments(self):
    """Add encyclopedia-specific arguments"""
    if self.parser is None:
        self.parser = argparse.ArgumentParser()
    
    self.parser.description = 'Encyclopedia operations'
    
    # Use consistent naming with other subparsers
    self.parser.add_argument(
        "--inpath", "-i",  # Changed from --input
        type=str,
        help="Input HTML file containing encyclopedia entries"
    )
    
    self.parser.add_argument(
        "--outpath", "-o",  # Changed from --output
        type=str,
        help="Output file for normalized encyclopedia"
    )
    
    self.parser.add_argument(
        "--title", "-t",
        type=str,
        default="Encyclopedia",
        help="Title for the encyclopedia"
    )
    
    self.parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Skip Wikidata ID normalization"
    )
    
    self.parser.add_argument(
        "--no-synonyms",
        action="store_true", 
        help="Skip synonym aggregation"
    )
    
    self.parser.add_argument(
        "--stats",
        action="store_true",
        help="Show encyclopedia statistics"
    )
```

### Fix 3: Update `process_args()` to use consistent names
```python
def process_args(self):
    """Process encyclopedia arguments"""
    self.input_file = self.args.get("inpath")  # Changed from "input"
    self.output_file = self.args.get("outpath")  # Changed from "output"
    self.title = self.args.get("title", "Encyclopedia")
    self.normalize = not self.args.get("no_normalize", False)
    self.aggregate_synonyms = not self.args.get("no_synonyms", False)
    self.show_stats = self.args.get("stats", False)
    
    # Convert string paths to Path objects
    if self.input_file:
        self.input_file = Path(self.input_file)
    if self.output_file:
        self.output_file = Path(self.output_file)
    
    # Validate arguments
    if not self.input_file:
        raise ValueError("Input file (--inpath) is required")
    
    if not self.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {self.input_file}")
    
    if not self.output_file:
        # Generate default output filename
        self.output_file = self.input_file.parent / f"{self.input_file.stem}_normalized.html"
```

### Fix 4: Add to `amix.py` - Import and register
```python
# At top of file, add import:
from amilib.ami_encyclopedia_args import EncyclopediaArgs

# In create_arg_parser() method, add (around line 115):
encyclopedia_parser = AmiLibArgs.make_sub_parser(EncyclopediaArgs(), subparsers)
logger.debug(f"encyclopedia_parser {encyclopedia_parser}")

# In run_arguments() method, add to subparser_dict (around line 243):
subparser_dict = {
    "DICT": AmiDictArgs(),
    "SEARCH": SearchArgs(),
    "HTML": HTMLArgs(),
    "PDF": PDFArgs(),
    "ENCYCLOPEDIA": EncyclopediaArgs(),  # ADD THIS
}
```

### Fix 5: Update help text in `amix.py`
```python
# In create_arg_parser() description (around line 85):
'The subcommands:\n\n'
'  DICT <options>      # create and edit Ami Dictionaries\n'
'  HTML <options>      # create/edit HTML\n'
'  PDF <options>       # convert PDF into HTML and images\n'
'  SEARCH <options>    # search and index documents\n'
'  ENCYCLOPEDIA <options>  # normalize and aggregate encyclopedia entries\n'  # ADD THIS
```

### Fix 6: Update `run_encyclopedia_operation()` to call `process_args()`
The current implementation doesn't call `process_args()` before running operations. Should integrate with the standard flow.

## Additional Considerations

### Method Name Consistency
- Current: `normalize_by_wikipedia_url()` 
- Also exists: `normalize_by_wikidata_id()` (from codebase search)
- Should we support both? Add `--normalize-by` option?

### Output Method Names
- Current: `save_normalized_html()`
- Also exists: `save_wiki_normalized_html()` (from codebase search)
- Should verify which method is correct

### Integration with Standard Flow
- Should `EncyclopediaArgs` follow the same pattern as other Args classes?
- Should it call `process_args()` automatically in `run_encyclopedia_operation()`?
- Should it integrate with `_parse_and_process1()` like other Args classes?

## Next Steps

1. **Review proposed arguments** - Confirm which arguments are needed
2. **Fix `EncyclopediaArgs` class** - Update to follow standard pattern
3. **Register in `amix.py`** - Add to subparser creation and dictionary
4. **Update help text** - Add ENCYCLOPEDIA to descriptions
5. **Test command line** - Verify `amilib ENCYCLOPEDIA --help` works
6. **Test operations** - Verify actual encyclopedia operations work

---

*This document was generated on November 7, 2025 (system date) for reviewing the ENCYCLOPEDIA subparser implementation.*



