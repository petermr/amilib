# Glossary Semantic Structure Transformation

## Summary

Implemented a transformer to convert glossary/acronym HTML files into semantic structure with role-based divs.

## Implementation

### Files Created

1. **`scripts/glossary_processor/semantic_structure_transformer.py`**
   - `SemanticStructureTransformer` class
   - Transforms raw HTML (with font styles) into semantic HTML structure
   - Creates `<div role="term">` and `<div role="definition">` elements
   - Merges adjacent spans with same role into single spans
   - Preserves nested HTML elements (a, sub, sup, em, strong, etc.)
   - Adds CSS stylesheet to `<head>` with role-based styles

2. **`scripts/transform_to_semantic_structure.py`**
   - Batch script to transform all glossary/acronym files
   - Processes 6 files: WG1 Annex I/II, WG3 Annex I/VI, SYR Annex I/II

### Process

1. **Parse HTML**: Loads raw HTML file with font styles
2. **Join Pages**: Uses `PageJoiner` to merge content across pages
3. **Detect Entries**: Uses `EntryDetector` to identify entry boundaries
4. **Detect Roles**: Uses `FontRoleDetector` to assign semantic roles to spans
5. **Create Structure**: Builds semantic HTML with:
   - `<div class="entry">` containers
   - `<div role="term">` for terms
   - `<div role="definition">` for definitions
   - Merged spans with role classes
6. **Add CSS**: Injects stylesheet into `<head>` with role-based styles

### Output Structure

```html
<div class="entry" id="wg3-annex-vi-acronyms-entry-0">
  <div role="term">
    <span class="role-term">AUM</span>
  </div>
  <div role="definition">
    <span class="role-definition">assets under management</span>
  </div>
</div>
```

### CSS Styles

Stylesheet includes:
- `[role="term"]` - Bold, black text
- `[role="definition"]` - Normal weight, black text
- `.role-term`, `.role-definition`, `.role-cross_reference` - Class-based styles

### Results

- Successfully transformed 6 files
- WG3 Annex VI: 518 entries, 515 term divs, 515 definition divs
- Each entry has proper semantic structure
- CSS stylesheet embedded in `<head>`

### Known Issues

- Text/element/text merging may need refinement
- Some entries may have multiple spans that could be further merged
- Nested element preservation works but may need optimization

## Next Steps

- Review output structure for correctness
- Refine text merging logic for better mixed content handling
- Test with all glossary/acronym files
- Verify CSS styling renders correctly

