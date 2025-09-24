# Dictionary Editor User Guide

## Overview

The Dictionary Editor is a powerful client-side tool for creating, editing, and managing dictionaries in JSON format. It supports importing legacy formats (XML, HTML, CSV, TXT) and provides a full CRUD interface for dictionary entries.

## Quick Start

### 1. Launch the Editor

**Option 1: Direct Browser Access (Simplest)**
```bash
cd /Users/pm286/workspace/amilib/dictionary_editor
open production_with_import.html
```

**Option 2: Local Server (Recommended)**
```bash
cd /Users/pm286/workspace/amilib
python -m http.server 8000
# Then visit: http://localhost:8000/dictionary_editor/production_with_import.html
```

### 2. Create a New Dictionary

1. Click **"New Dictionary"** button
2. The editor will create a blank dictionary with default metadata
3. Use **"Edit Name"** button to customize title and filename

### 3. Add Entries

**Method 1: Form Interface**
1. Click **"Add Entry"** button
2. Fill in the form fields:
   - **Term** (required): The main term/word
   - **Definition** (required): Brief definition
   - **Description**: Detailed explanation (supports HTML)
   - **Synonyms**: Comma-separated list
   - **Examples**: Comma-separated examples
   - **Category**: Classification
   - **Tags**: Comma-separated tags
   - **References**: Comma-separated references
   - **Wikidata ID**: Wikidata entity ID (e.g., Q12345)
   - **Wikipedia URL**: Link to Wikipedia page
3. Click **"Save Entry"**

**Method 2: JSON Editor**
1. Switch to **"Code"** mode in the JSON editor
2. Edit the JSON directly
3. Switch back to **"Tree"** mode to see changes

### 4. Import Legacy Dictionaries

The editor supports importing from multiple legacy formats:

#### HTML Dictionaries
**Example**: `test/resources/dictionary/climate/carbon_cycle.html`
- **Format**: HTML with `<div role="ami_dictionary">` and `<div role="ami_entry">`
- **Features**: Rich HTML content, links, formatting
- **Import**: Click **"Import Legacy"** → Select HTML file

#### XML Dictionaries
**Examples**: 
- `output/dict/human_influence_wp.xml`
- `output/dict/human_influence.xml`
- `output/dict/water_cyclone_wp.xml`
- **Format**: XML with `<dictionary>` and `<entry>` elements
- **Features**: Simple structure, clean metadata
- **Import**: Click **"Import Legacy"** → Select XML file

#### CSV Dictionaries
**Format**: Comma-separated values with headers
**Headers**: term, definition, synonyms, category, tags, wikidata_id, wikipedia_url
**Import**: Click **"Import Legacy"** → Select CSV file

#### Text Dictionaries
**Format**: One word per line
**Example**: Plain text word lists
**Import**: Click **"Import Legacy"** → Select TXT file

### 5. Edit and Manage Entries

#### Select an Entry
- Click on any entry in the sidebar
- The entry will be highlighted and edit/delete buttons enabled

#### Edit an Entry
1. Select an entry from the sidebar
2. Click **"Edit Entry"** button
3. Modify the form fields
4. Click **"Save Entry"**

#### Delete an Entry
1. Select an entry from the sidebar
2. Click **"Delete Entry"** button
3. Confirm deletion

#### Search Entries
- Use the search box in the sidebar
- Searches across terms, definitions, and synonyms
- Real-time filtering as you type

### 6. Save and Export

#### Save Dictionary
- Click **"Save Dictionary"** button
- Uses modern file picker (if supported) or download
- Saves as JSON format
- Auto-saves to browser storage

#### Export Dictionary
- Click **"Export JSON"** button
- Downloads a copy with "_export" suffix
- Useful for sharing or backups

## Real Examples

### Example 1: Climate Science Dictionary
**Source**: `test/resources/dictionary/climate/carbon_cycle.html`
**Content**: 40+ climate science terms with rich definitions
**Features**: HTML formatting, Wikipedia links, scientific references

**Sample Entry**:
```json
{
  "id": "anthropogenic",
  "term": "anthropogenic",
  "definition": "Anthropogenic (\"human\" + \"generating\") is an adjective that may refer to:",
  "description": "<p><b>Anthropogenic</b> (\"human\" + \"generating\") is an adjective that may refer to:</p>",
  "category": "climate_science",
  "tags": ["human_impact", "climate_change"]
}
```

### Example 2: Human Influence Dictionary
**Source**: `output/dict/human_influence_wp.xml`
**Content**: 50+ terms related to human influence on climate
**Features**: Simple XML structure, clean metadata

**Sample Entry**:
```json
{
  "id": "entry_1",
  "term": "positive radiative forcing",
  "definition": "Definition for positive radiative forcing",
  "category": "climate_forcing"
}
```

### Example 3: Water Cycle Dictionary
**Source**: `output/dict/water_cyclone_wp.xml`
**Content**: Water cycle and cyclone-related terms
**Features**: Meteorological terminology

## Dictionary Structure

### JSON Schema
```json
{
  "metadata": {
    "title": "Dictionary Title",
    "filename": "dictionary.json",
    "version": "1.0.0",
    "description": "Dictionary description",
    "created": "2025-01-27T10:00:00.000Z",
    "modified": "2025-01-27T10:00:00.000Z",
    "author": "Author Name",
    "language": "en",
    "source_format": "json"
  },
  "entries": [
    {
      "id": "unique_id",
      "term": "Term name",
      "definition": "Brief definition",
      "description": "Detailed description (can include HTML)",
      "synonyms": ["synonym1", "synonym2"],
      "examples": ["example1", "example2"],
      "category": "category_name",
      "tags": ["tag1", "tag2"],
      "references": ["ref1", "ref2"],
      "wikidata_id": "Q12345",
      "wikipedia_url": "https://en.wikipedia.org/wiki/Term"
    }
  ]
}
```

## Advanced Features

### Auto-Save
- Dictionary automatically saves to browser localStorage
- Previous work is restored when reopening the editor
- No data loss if browser crashes

### File Management
- **Modern File API**: Uses `showSaveFilePicker()` when available
- **Fallback Download**: Automatic download for older browsers
- **Filename Management**: Separate filename from dictionary title

### Import Progress
- Real-time progress tracking during import
- Error handling with user-friendly messages
- Support for large files

### Search and Filter
- Real-time search across all entry fields
- Filter by term, definition, or synonyms
- Visual highlighting of search results

## Troubleshooting

### Common Issues

**File Import Fails**
- Check file format is supported (XML, HTML, CSV, TXT)
- Ensure file is not corrupted
- Try refreshing the page and importing again

**Entries Not Displaying**
- Check browser console for errors (F12 → Console)
- Verify JSON structure is valid
- Try switching between Tree and Code modes

**Save Issues**
- Check browser permissions for file access
- Try using Export instead of Save
- Clear browser cache if needed

### Browser Compatibility
- **Modern Browsers**: Full functionality (Chrome, Firefox, Safari, Edge)
- **File API**: Chrome 86+, Firefox 88+, Safari 14+
- **Fallback**: Download method for older browsers

## Integration with amilib

The Dictionary Editor is designed to work with the amilib ecosystem:

### Import from amilib
- Import existing XML dictionaries from `output/dict/`
- Convert to JSON format for editing
- Maintain compatibility with amilib structure

### Export for amilib
- Export as JSON for further processing
- Compatible with amilib's dictionary processing tools
- Can be converted back to XML if needed

## Best Practices

### Dictionary Organization
1. **Use descriptive titles** and filenames
2. **Categorize entries** with meaningful categories
3. **Add tags** for easy filtering and search
4. **Include references** for authoritative sources

### Entry Quality
1. **Clear, concise definitions**
2. **Consistent terminology**
3. **Proper citations** and references
4. **Regular updates** and maintenance

### File Management
1. **Regular backups** using Export feature
2. **Version control** with descriptive filenames
3. **Test imports** before large-scale use
4. **Validate JSON** structure regularly

## Support and Resources

### Documentation
- **Production Guide**: `dictionary_editor/PRODUCTION_GUIDE.md`
- **CLI Guide**: `dictionary_editor/CLI_GUIDE.md`
- **Architecture**: `dictionary_editor/architecture.dot`

### Examples and Templates
- **Climate Dictionary**: `test/resources/dictionary/climate/carbon_cycle.html`
- **Human Influence**: `output/dict/human_influence_wp.xml`
- **Water Cycle**: `output/dict/water_cyclone_wp.xml`

### Development
- **Source Code**: `dictionary_editor/legacy_importer.js`
- **Enhanced Editor**: `dictionary_editor/production_with_import.html`
- **TODO List**: `dictionary_editor/TODO.md`

---

**Last Updated**: January 27, 2025  
**Version**: 1.0.0  
**Author**: Dictionary Editor Team


















