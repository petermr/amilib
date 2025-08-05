# Dictionary Editor System

## Overview

This is a **client-side only** JSON dictionary editor that provides CRUD (Create, Read, Update, Delete) operations for managing dictionary entries. The system runs entirely in the browser using JavaScript and can work with local files.

## System Architecture

### Components

1. **HTML Interface** (`index.html`) - Main editor page
2. **JavaScript Core** (`js/editor.js`) - CRUD operations and data management
3. **JSONEditor Library** - Visual JSON editing component
4. **File API** - Browser-based file reading/writing
5. **Local Storage** - Browser storage for temporary data

### Data Flow

```
User Interface (JSONEditor) 
    ↓ JavaScript Events
CRUD Operations (editor.js)
    ↓ File API / Local Storage
JSON Dictionary Files
```

## Key Features

- **No Server Required**: Runs entirely in the browser
- **Tree View Editing**: Visual JSON editor with expandable/collapsible nodes
- **Code View**: Raw JSON editing for advanced users
- **Real-time Validation**: Schema validation as you type
- **Auto-save**: Automatic saving to browser storage
- **File Import/Export**: Load and save JSON files locally
- **Search & Filter**: Find entries quickly
- **Offline Capable**: Works without internet connection

## File Structure

```
dictionary_editor/
├── index.html              # Main editor interface
├── js/
│   ├── editor.js           # Core CRUD operations
│   ├── validation.js       # Schema validation
│   └── file-handler.js     # File import/export
├── css/
│   └── style.css           # Custom styles
├── data/
│   └── sample_dictionary.json  # Example dictionary
├── architecture.dot        # System diagram
└── README.md               # This file
```

## Data Schema

### Dictionary Structure
```json
{
  "metadata": {
    "title": "Dictionary Title",
    "version": "1.0.0",
    "description": "Description",
    "created": "2024-01-01T00:00:00Z",
    "modified": "2024-01-01T00:00:00Z",
    "author": "Author Name",
    "language": "en"
  },
  "entries": [
    {
      "id": "entry_001",
      "term": "Term Name",
      "definition": "Definition text",
      "synonyms": ["synonym1", "synonym2"],
      "antonyms": ["antonym1"],
      "examples": ["Example 1", "Example 2"],
      "category": "category_name",
      "tags": ["tag1", "tag2"],
      "references": ["ref1", "ref2"],
      "etymology": "Origin of term",
      "pronunciation": "prəˌnʌnsiˈeɪʃən",
      "wikidata_id": "Q12345",
      "wikipedia_url": "https://en.wikipedia.org/wiki/Term"
    }
  ]
}
```

## Installation & Setup

1. **No Installation Required**: Just open `index.html` in a modern browser

2. **Local Development Server** (Optional)
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Using PHP
   php -S localhost:8000
   ```

3. **Access the Editor**
   - Open `index.html` directly in browser, or
   - Visit http://localhost:8000 if using a local server

## Core JavaScript Functions

### CRUD Operations
```javascript
// Create
function createEntry(term, definition, ...) { ... }

// Read
function getEntry(id) { ... }
function getAllEntries() { ... }

// Update
function updateEntry(id, updates) { ... }

// Delete
function deleteEntry(id) { ... }
```

### File Operations
```javascript
// Import JSON file
function importDictionary(file) { ... }

// Export to JSON file
function exportDictionary() { ... }

// Auto-save to localStorage
function autoSave() { ... }
```

## Integration with amilib

The editor can work with existing `amilib` dictionaries:

- **Import XML**: Convert existing XML dictionaries to JSON format
- **Export XML**: Convert back to XML for amilib compatibility
- **Validation**: Use amilib's validation rules in JavaScript
- **Wikidata Integration**: Client-side Wikidata API calls

## Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Required APIs**: File API, LocalStorage, JSON
- **Optional**: IndexedDB for larger datasets

## Performance Benefits

- **No Network Latency**: All operations are local
- **Instant Response**: No server round-trips
- **Offline Capable**: Works without internet
- **No Server Costs**: Zero hosting requirements
- **Privacy**: Data never leaves the browser

## Security Considerations

- **Client-side Only**: No server-side security concerns
- **File Access**: Only reads files user explicitly selects
- **Local Storage**: Data stored in browser (consider privacy)
- **No External Dependencies**: JSONEditor loaded from CDN

## Development Guidelines

### Adding New Features
1. Update the data model in `js/editor.js`
2. Add UI elements in `index.html`
3. Implement validation in `js/validation.js`
4. Add file handling in `js/file-handler.js`

### Testing
- Test in multiple browsers
- Verify file import/export functionality
- Check localStorage persistence
- Test with large dictionaries

## Troubleshooting

### Common Issues
1. **File Not Loading**: Check browser console for errors
2. **LocalStorage Full**: Clear browser data or use IndexedDB
3. **JSON Validation Errors**: Check schema compliance
4. **CORS Issues**: Use local server for development

### Debug Mode
Open browser developer tools (F12) for detailed error messages and logging. 