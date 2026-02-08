# IPCC Glossary/Acronym Dictionary Template Proposal

## Overview

This document proposes a formal HTML template for converting IPCC glossary and acronym PDFs into structured, semantic dictionaries. The template is designed to handle the complexities of PDF-to-HTML conversion including font-based role detection, page breaks, floats, and multi-column layouts.

## Template Structure

### 1. Root Dictionary Container

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IPCC AR6 {Report} - {Annex Type}: {Annex Name}</title>
  <style type="text/css">
    /* Role-based styles defined here */
  </style>
</head>
<body>
  <div role="ipcc_dictionary" 
       class="ipcc-dictionary"
       data-schema-version="1.0"
       data-report="{report}"           <!-- e.g., "wg1", "wg2", "wg3", "syr" -->
       data-annex="{annex}"             <!-- e.g., "i", "ii", "vi" -->
       data-annex-type="{type}"         <!-- "glossary" or "acronyms" -->
       data-source-pdf="{pdf_path}"
       data-conversion-date="{iso_date}"
       data-conversion-tool="{tool_name}">
    
    <!-- Metadata section -->
    <!-- Entries section -->
    
  </div>
</body>
</html>
```

### 2. Metadata Section

```html
<div role="dictionary_metadata" class="dictionary-metadata">
  <h1 class="dictionary-title">
    <span role="title_main">Annex {Annex Number}</span>
    <span role="title_subtitle">{Glossary | Acronyms}</span>
  </h1>
  
  <div role="metadata_details" class="metadata-details">
    <dl class="metadata-list">
      <dt>Report</dt>
      <dd data-report="{report}">{Report Full Name}</dd>
      
      <dt>Annex</dt>
      <dd data-annex="{annex}">{Annex Number}</dd>
      
      <dt>Type</dt>
      <dd data-type="{type}">{Glossary | Acronyms}</dd>
      
      <dt>Source PDF</dt>
      <dd data-source="{pdf_path}">{PDF filename}</dd>
      
      <dt>Conversion Date</dt>
      <dd data-date="{iso_date}">{YYYY-MM-DD}</dd>
      
      <dt>Entry Count</dt>
      <dd data-entry-count="{count}">{number}</dd>
      
      <dt>Layout</dt>
      <dd data-layout="{layout}">{single-column | two-column | multi-column}</dd>
    </dl>
  </div>
</div>
```

### 3. Entry Structure

Each entry follows this structure:

```html
<div role="dictionary_entry" 
     class="entry"
     id="entry-{normalized_term}"
     data-entry-number="{index}"
     data-term="{term}"
     data-has-definition="{true|false}"
     data-has-description="{true|false}"
     data-has-abbreviation="{true|false}"
     data-section="{section_letter}">  <!-- Optional: A, B, C, etc. -->
  
  <!-- Term (required) -->
  <div role="term" class="term">
    <span class="term-text">{term_text}</span>
    <!-- Optional: abbreviation/acronym variant -->
    <span role="abbreviation" class="abbreviation" data-variant="{variant}">{abbrev}</span>
  </div>
  
  <!-- Definition (optional) -->
  <div role="definition" class="definition">
    <span class="definition-text">{definition_text}</span>
    <!-- Mixed content: text, links, subscripts, superscripts, emphasis -->
  </div>
  
  <!-- Description (optional, for extended content) -->
  <div role="description" class="description">
    <p class="description-paragraph">{paragraph_text}</p>
    <!-- Multiple paragraphs allowed -->
  </div>
  
  <!-- Cross-references (optional) -->
  <div role="cross_references" class="cross-references">
    <span class="cross-ref-label">See also:</span>
    <a href="#entry-{target_term}" class="cross-ref-link">{referenced_term}</a>
  </div>
  
</div>
```

### 4. Section Headings (Optional)

For alphabetically organized glossaries:

```html
<section role="dictionary_section" 
         class="dictionary-section"
         data-section-letter="{A|B|C|...}"
         id="section-{letter}">
  
  <h2 role="section_heading" class="section-heading">{Section Letter}</h2>
  
  <!-- Entries for this section -->
  
</section>
```

### 5. Mixed Content Handling

The template supports rich mixed content within definitions and descriptions:

```html
<div role="definition" class="definition">
  <span class="definition-text">
    Text content with 
    <a href="#entry-{term}" class="internal-link">cross-reference</a>
    and 
    <sub class="subscript">subscript</sub>
    and 
    <sup class="superscript">superscript</sup>
    and 
    <em class="emphasis">emphasis</em>
    and 
    <strong class="strong">strong</strong>
    formatting.
  </span>
</div>
```

### 6. Complete Example Entry

```html
<div role="dictionary_entry" 
     class="entry"
     id="entry-ipcc"
     data-entry-number="123"
     data-term="IPCC"
     data-has-definition="true"
     data-has-description="false"
     data-has-abbreviation="false"
     data-section="I">
  
  <div role="term" class="term">
    <span class="term-text">IPCC</span>
  </div>
  
  <div role="definition" class="definition">
    <span class="definition-text">
      Intergovernmental Panel on Climate Change. See also 
      <a href="#entry-ar6" class="cross-ref-link">AR6</a>
      and 
      <a href="#entry-wg1" class="cross-ref-link">WG1</a>.
    </span>
  </div>
  
</div>
```

## CSS Styling

### Role-Based Styles

```css
/* Dictionary container */
[role="ipcc_dictionary"] {
  font-family: sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Metadata */
[role="dictionary_metadata"] {
  border-bottom: 2px solid #333;
  padding-bottom: 20px;
  margin-bottom: 30px;
}

.dictionary-title {
  font-size: 2em;
  margin-bottom: 10px;
}

.metadata-list dt {
  font-weight: bold;
  display: inline-block;
  min-width: 150px;
}

.metadata-list dd {
  display: inline-block;
  margin-left: 10px;
}

/* Entry */
[role="dictionary_entry"] {
  margin-bottom: 20px;
  padding: 10px;
  border-left: 3px solid #0066cc;
}

[role="dictionary_entry"]:hover {
  background-color: #f5f5f5;
}

/* Term */
[role="term"] {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 5px;
}

.term-text {
  color: #000;
}

/* Definition */
[role="definition"] {
  margin-left: 20px;
  margin-top: 5px;
  line-height: 1.6;
}

.definition-text {
  color: #333;
}

/* Description */
[role="description"] {
  margin-left: 20px;
  margin-top: 10px;
}

.description-paragraph {
  margin-bottom: 10px;
  line-height: 1.6;
}

/* Cross-references */
[role="cross_references"] {
  margin-left: 20px;
  margin-top: 10px;
  font-style: italic;
  font-size: 0.9em;
}

.cross-ref-link {
  color: #0066cc;
  text-decoration: underline;
}

.cross-ref-link:hover {
  color: #004499;
}

/* Section headings */
[role="section_heading"] {
  font-size: 1.5em;
  font-weight: bold;
  margin-top: 30px;
  margin-bottom: 15px;
  border-bottom: 1px solid #ccc;
  padding-bottom: 5px;
}

/* Internal links */
.internal-link {
  color: #0066cc;
  text-decoration: underline;
  font-style: italic;
}

.internal-link:hover {
  color: #004499;
}

/* Abbreviation */
[role="abbreviation"] {
  font-weight: normal;
  font-size: 0.9em;
  color: #666;
}
```

## Transformation Requirements

### Input Handling

1. **PDF-to-HTML Conversion**
   - Preserve font properties (family, weight, style, size)
   - Preserve coordinate information (x0, y0, x1, y1)
   - Handle page breaks
   - Detect and handle floats/figures
   - Detect column layout (single vs. multi-column)

2. **Font-Based Role Detection**
   - Use `font_role_config.json` to map font properties to roles
   - Support report-specific overrides
   - Handle coordinate-based rules (x0, y0 ranges)
   - Detect section headings by font size and position

3. **Entry Detection**
   - Identify entry boundaries using:
     - Font changes (term vs. definition)
     - Coordinate clustering (column detection)
     - Vertical spacing
     - Section markers

4. **Content Merging**
   - Merge adjacent text nodes with same role
   - Preserve nested HTML elements (a, sub, sup, em, strong)
   - Handle text/element/text sequences
   - Normalize whitespace

### Processing Pipeline

1. **Stage 1: Page Joining**
   - Remove page break artifacts
   - Merge content across pages
   - Preserve coordinate continuity

2. **Stage 2: Layout Detection**
   - Detect single vs. multi-column layout
   - Identify column boundaries
   - Handle floats and figures

3. **Stage 3: Section Detection**
   - Identify section headings (A, B, C, etc.)
   - Group entries by section

4. **Stage 4: Entry Detection**
   - Detect entry boundaries
   - Extract terms and definitions
   - Handle multi-paragraph definitions

5. **Stage 5: Role Assignment**
   - Apply font-based role detection
   - Assign roles to all text elements
   - Handle cross-references (italicized terms)

6. **Stage 6: Structure Creation**
   - Create semantic HTML structure
   - Merge content with same roles
   - Generate entry IDs
   - Add metadata

7. **Stage 7: Validation**
   - Validate structure against template
   - Check for required fields
   - Verify entry IDs are unique
   - Validate cross-reference links

## Validation Rules

### Required Elements

- Root: `<div role="ipcc_dictionary">`
- Metadata: `<div role="dictionary_metadata">` with title
- At least one entry: `<div role="dictionary_entry">`
- Each entry must have: `<div role="term">`

### Optional Elements

- Section headings: `<section role="dictionary_section">`
- Definitions: `<div role="definition">`
- Descriptions: `<div role="description">`
- Cross-references: `<div role="cross_references">`
- Abbreviations: `<span role="abbreviation">`

### Data Attributes

- `data-report`: Required, must be one of: "wg1", "wg2", "wg3", "syr"
- `data-annex`: Required, annex identifier
- `data-annex-type`: Required, "glossary" or "acronyms"
- `data-entry-number`: Required for entries, unique integer
- `data-term`: Required for entries, normalized term text
- `id`: Required for entries, format: `entry-{normalized_term}`

### Content Rules

- Term text must be non-empty
- Entry IDs must be unique within dictionary
- Cross-reference links must reference valid entry IDs
- Section letters must be single uppercase letters (A-Z)

## Alternative Structure: Definition List

For simpler cases, the template can use HTML `<dl>` elements:

```html
<dl role="ipcc_dictionary" class="ipcc-dictionary">
  
  <dt role="term" class="term" id="entry-{term}">
    {term_text}
  </dt>
  
  <dd role="definition" class="definition">
    {definition_text}
  </dd>
  
  <!-- Multiple definitions allowed -->
  <dd role="description" class="description">
    {extended_description}
  </dd>
  
</dl>
```

This structure is semantically equivalent but more compact. The transformer should support both formats via a configuration option.

## Testing Requirements

### Test Cases

1. **Single-column layout**
   - Input: SYR Annex I (Glossary)
   - Expected: All entries detected, proper term/definition separation

2. **Two-column layout**
   - Input: WG3 Annex VI (Acronyms)
   - Expected: Column detection works, entries span columns correctly

3. **Multi-paragraph definitions**
   - Input: Glossary entries with multiple paragraphs
   - Expected: Paragraphs preserved in description divs

4. **Cross-references**
   - Input: Entries with italicized cross-references
   - Expected: Cross-references converted to internal links

5. **Section headings**
   - Input: Alphabetically organized glossary
   - Expected: Section headings detected and entries grouped

6. **Mixed content**
   - Input: Definitions with subscripts, superscripts, links
   - Expected: All formatting preserved, merged correctly

7. **Page breaks**
   - Input: Entries spanning multiple pages
   - Expected: Entries merged correctly across pages

8. **Floats/Figures**
   - Input: PDF with inserted figures/floats
   - Expected: Floats handled gracefully, entries not disrupted

### Validation Tests

- Structure validation (required elements present)
- ID uniqueness validation
- Cross-reference link validation
- Metadata completeness validation
- Content preservation validation (no data loss)

## Implementation Notes

1. **Backward Compatibility**
   - Template should be compatible with existing `semantic_structure_transformer.py`
   - Support migration from current structure to new template

2. **Configuration**
   - Use `font_role_config.json` for role detection
   - Add template-specific configuration (use_dl, section_detection, etc.)

3. **Performance**
   - Efficient processing for large glossaries (500+ entries)
   - Incremental processing for multi-file batches

4. **Accessibility**
   - Semantic HTML with proper roles
   - ARIA labels where appropriate
   - Keyboard navigation support

5. **Internationalization**
   - Support for non-English content
   - Proper encoding (UTF-8)
   - Language attributes (`lang`)

## Next Steps

1. **Review and Approval**
   - Review this template proposal
   - Approve structure and validation rules

2. **Implementation**
   - Update `semantic_structure_transformer.py` to use this template
   - Add validation module
   - Create test suite

3. **Testing**
   - Run tests on all 6 current glossary/acronym files
   - Validate output against template
   - Fix any issues

4. **Documentation**
   - Create user guide
   - Document transformation process
   - Provide examples








