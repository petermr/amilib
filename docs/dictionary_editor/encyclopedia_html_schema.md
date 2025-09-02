# Encyclopedia HTML Schema Design

## Overview

This document defines the HTML schema for the encyclopedia system. We use HTML throughout with carefully chosen attribute names to provide both rich content display and structured data management.

## Core Schema Structure

### 1. Encyclopedia Container
```html
<div class="encyclopedia" 
     data-title="Climate Change Encyclopedia" 
     data-version="1.0.0" 
     data-created="2025-01-27T00:00:00Z" 
     data-author="Author Name" 
     data-language="en" 
     data-source="Enhanced from Wikimedia sources">
  
  <!-- Encyclopedia content goes here -->
  
</div>
```

### 2. Entry Structure
```html
<div class="entry" 
     data-id="entry_001" 
     data-term="Greenhouse Gas" 
     data-category="climate_science" 
     data-wikidata-id="Q37836" 
     data-wikipedia-url="https://en.wikipedia.org/wiki/Greenhouse_gas" 
     data-frequency="1250" 
     data-ingestion-date="2025-01-27T00:00:00Z" 
     data-extraction-method="amilib_wikipedia_parser">
  
  <!-- Entry content goes here -->
  
</div>
```

## Content Elements

### 3. Term Header
```html
<h2 class="term" data-primary="true">Greenhouse Gas</h2>
```

### 4. Synonyms Structure
```html
<div class="synonyms">
  <!-- Wiktionary Synonyms -->
  <div class="synonym-group" data-type="wiktionary" data-source="wiktionary">
    <span class="synonym" data-confidence="0.95">GHG</span>
    <span class="synonym" data-confidence="0.90">atmospheric gas</span>
    <span class="synonym" data-confidence="0.85">heat-trapping gas</span>
  </div>
  
  <!-- Inline Text References -->
  <div class="synonym-group" data-type="inline" data-source="text_analysis">
    <span class="synonym" data-context="parenthetical">greenhouse gases (GHGs)</span>
    <span class="synonym" data-context="abbreviation">GHGs</span>
  </div>
  
  <!-- Language Equivalents -->
  <div class="synonym-group" data-type="languages" data-source="multilingual">
    <span class="synonym" data-language="fr" data-script="latin">gaz à effet de serre</span>
    <span class="synonym" data-language="hi" data-script="devanagari">ग्रीनहाउस गैस</span>
    <span class="synonym" data-language="ta" data-script="tamil">பசுமைக்குடில் வாயு</span>
  </div>
</div>
```

### 5. Content Sections
```html
<div class="content">
  <!-- Definition Section -->
  <div class="content-section" 
       data-type="definition" 
       data-source="wikipedia" 
       data-extraction-date="2025-01-27T00:00:00Z" 
       data-confidence="0.95">
    <h3 class="section-title">Definition</h3>
    <div class="section-content">
      <p><strong>Greenhouse gases</strong> are gases in Earth's atmosphere that trap heat by absorbing infrared radiation.</p>
    </div>
  </div>
  
  <!-- Description Section -->
  <div class="content-section" 
       data-type="description" 
       data-source="wikipedia" 
       data-extraction-date="2025-01-27T00:00:00Z" 
       data-confidence="0.90">
    <h3 class="section-title">Description</h3>
    <div class="section-content">
      <p>These gases include carbon dioxide, methane, nitrous oxide, and fluorinated gases. They contribute to the greenhouse effect, which is essential for maintaining Earth's temperature but can lead to global warming when concentrations increase.</p>
    </div>
  </div>
  
  <!-- Examples Section -->
  <div class="content-section" 
       data-type="examples" 
       data-source="wikipedia" 
       data-extraction-date="2025-01-27T00:00:00Z" 
       data-confidence="0.88">
    <h3 class="section-title">Examples</h3>
    <div class="section-content">
      <ul>
        <li data-wikidata-id="Q421">Carbon dioxide (CO₂)</li>
        <li data-wikidata-id="Q3710">Methane (CH₄)</li>
        <li data-wikidata-id="Q190909">Nitrous oxide (N₂O)</li>
      </ul>
    </div>
  </div>
</div>
```

### 6. Metadata and Tags
```html
<div class="metadata">
  <!-- Categories -->
  <div class="categories">
    <span class="category" data-primary="true" data-type="domain">climate_science</span>
    <span class="category" data-type="subdomain">atmospheric_chemistry</span>
  </div>
  
  <!-- Tags -->
  <div class="tags">
    <span class="tag" data-type="concept">atmosphere</span>
    <span class="tag" data-type="concept">climate</span>
    <span class="tag" data-type="concept">emissions</span>
    <span class="tag" data-type="process">greenhouse_effect</span>
  </div>
  
  <!-- Processing Information -->
  <div class="processing-info" data-extraction-method="amilib_wikipedia_parser">
    <span class="info" data-type="extraction_date">2025-01-27T00:00:00Z</span>
    <span class="info" data-type="content_sections">definition,description,examples</span>
    <span class="info" data-type="cross_references_found">3</span>
  </div>
</div>
```

## Wikimedia Integration

### 7. Wikidata Information
```html
<div class="wikidata-info" data-entity-id="Q37836">
  <h4 class="wikidata-title">Wikidata Information</h4>
  <div class="wikidata-properties">
    <div class="property" data-property-id="P31" data-property-value="Q11344">
      <span class="property-label">instance of</span>: 
      <span class="property-value">greenhouse gas</span>
    </div>
    <div class="property" data-property-id="P279" data-property-value="Q79529">
      <span class="property-label">subclass of</span>: 
      <span class="property-value">atmospheric gas</span>
    </div>
  </div>
</div>
```

### 8. Wikipedia Source
```html
<div class="wikipedia-source" data-url="https://en.wikipedia.org/wiki/Greenhouse_gas">
  <h4 class="wikipedia-title">Wikipedia Source</h4>
  <div class="wikipedia-content">
    <p>Content extracted from <a href="https://en.wikipedia.org/wiki/Greenhouse_gas" target="_blank">Wikipedia - Greenhouse Gas</a></p>
    <div class="extraction-details">
      <span class="detail" data-type="last_updated">2025-01-27</span>
      <span class="detail" data-type="extraction_method">amilib_wikipedia_parser</span>
      <span class="detail" data-type="content_quality">verified</span>
    </div>
  </div>
</div>
```

## Attribute Naming Convention

### Data Attributes
- **`data-*`**: All metadata uses HTML5 data attributes
- **`data-type`**: Categorizes content (definition, description, examples)
- **`data-source`**: Indicates content origin (wikipedia, wiktionary, manual)
- **`data-confidence`**: Extraction confidence score (0.0-1.0)
- **`data-language`**: Language code (ISO 639-1)
- **`data-script`**: Writing system (latin, devanagari, tamil, etc.)

### Class Names
- **Semantic classes**: `encyclopedia`, `entry`, `term`, `synonyms`
- **Functional classes**: `content-section`, `synonym-group`, `metadata`
- **Utility classes**: `section-title`, `section-content`, `processing-info`

## Content Validation Rules

### Required Attributes
- **Entry**: `data-id`, `data-term`, `data-category`
- **Content Section**: `data-type`, `data-source`
- **Synonym**: `data-type`, `data-source`

### Optional Attributes
- **Entry**: `data-frequency`, `data-wikidata-id`, `data-wikipedia-url`
- **Content**: `data-confidence`, `data-extraction-date`
- **Synonyms**: `data-language`, `data-script`, `data-context`

## Benefits of This Schema

### 1. **Single Format**: Everything is HTML - no mixing of formats
### 2. **Rich Content**: Full HTML formatting, links, and multimedia support
### 3. **Structured Data**: Data attributes provide searchable metadata
### 4. **Semantic HTML**: Meaningful structure for accessibility and SEO
### 5. **Extensible**: Easy to add new attributes and content types
### 6. **Wikimedia Compatible**: Direct integration with Wikipedia content
### 7. **Search Friendly**: Attributes enable advanced search and filtering
### 8. **Validation Ready**: Clear rules for content validation

## Next Steps

1. **Implement HTML Editor**: Extend dictionary editor to handle HTML content
2. **Create Conversion Tools**: CSV to HTML dictionary conversion
3. **Add Validation**: HTML schema validation and quality checks
4. **Integrate Extraction**: Connect with existing amilib Wikipedia extraction
5. **Build Search**: Attribute-based search and filtering system

---

*This schema provides a solid foundation for building a comprehensive, HTML-based encyclopedia system that integrates seamlessly with Wikimedia sources.*




