# Dictionary Editor - TODO List

## 🚀 **High Priority Features**

### 0. **Core File Management & UI Improvements**
- [ ] **Save dictionary with file explorer**: Add file picker dialog for save destination
- [ ] **Dictionary filename management**: Separate filename from dictionary title/name
- [ ] **Change dictionary name button**: Quick button to edit dictionary name/title
- [ ] **Entry term display**: Ensure entries display the term field prominently

**Current Status**: Basic save/load implemented but needs file explorer and better filename handling
**Files**: `production.html` (save/load functionality)

### 1. **Foreign Format Import/Export**
- [ ] **XML Import**: Convert amilib XML dictionaries to JSON format
- [ ] **XML Export**: Convert JSON back to XML for amilib compatibility
- [ ] **HTML Import**: Import HTML dictionary files
- [ ] **CSV Import**: Import CSV word lists
- [ ] **TXT Import**: Import plain text word lists

**Current Status**: Placeholder buttons exist but conversion logic not implemented
**Files**: `production.html:530`, `demo.html:493`

### 2. **Wikidata Integration**
- [ ] **Client-side Wikidata API calls**: Lookup terms automatically
- [ ] **Wikidata ID validation**: Verify Q-numbers are valid
- [ ] **Auto-populate descriptions**: Fetch descriptions from Wikidata
- [ ] **Wikidata search**: Search for terms and suggest matches

**Current Status**: Fields exist but no API integration
**Files**: `production.html` (wikidata_id, wikipedia_url fields)

### 3. **Advanced Search & Filtering**
- [ ] **Regex search**: Search with regular expressions
- [ ] **Category filtering**: Filter by entry categories
- [ ] **Tag-based filtering**: Filter by entry tags
- [ ] **Advanced search operators**: AND, OR, NOT combinations
- [ ] **Search history**: Remember recent searches

**Current Status**: Basic search implemented
**Files**: `production.html:680`

---

## 🔧 **Medium Priority Features**

### 4. **Data Validation & Quality**
- [ ] **Schema validation**: Validate JSON against dictionary schema
- [ ] **Duplicate detection**: Find and flag duplicate terms
- [ ] **Required field validation**: Ensure required fields are filled
- [ ] **Data quality scoring**: Score entries for completeness
- [ ] **Validation rules**: Custom validation rules for different dictionary types

**Current Status**: Basic validation exists
**Files**: `README.md` mentions validation.js

### 5. **Batch Operations**
- [ ] **Bulk import**: Import multiple files at once
- [ ] **Bulk edit**: Edit multiple entries simultaneously
- [ ] **Bulk delete**: Delete multiple entries with confirmation
- [ ] **Bulk export**: Export selected entries only
- [ ] **Find and replace**: Global find and replace across entries

**Current Status**: Console-based batch operations documented
**Files**: `PRODUCTION_GUIDE.md:95`

### 6. **Advanced UI Features**
- [ ] **Keyboard shortcuts**: Hotkeys for common operations
- [ ] **Drag and drop**: Drag entries to reorder
- [ ] **Context menus**: Right-click context menus
- [ ] **Undo/Redo**: Undo and redo operations
- [ ] **Split view**: Side-by-side editing modes

**Current Status**: Basic UI implemented
**Files**: `production.html`, `css/style.css`

---

## 📊 **Low Priority Features**

### 7. **Performance & Storage**
- [ ] **IndexedDB support**: For larger dictionaries (>5MB)
- [ ] **Lazy loading**: Load large dictionaries progressively
- [ ] **Compression**: Compress stored data
- [ ] **Offline sync**: Sync when connection restored
- [ ] **Memory optimization**: Optimize for large datasets

**Current Status**: LocalStorage only
**Files**: `README.md:146`

### 8. **Collaboration Features**
- [ ] **Multi-user editing**: Real-time collaboration
- [ ] **Change tracking**: Track who made what changes
- [ ] **Comments**: Add comments to entries
- [ ] **Version control**: Track dictionary versions
- [ ] **Merge conflicts**: Handle conflicting edits

**Current Status**: Single-user only
**Files**: Not implemented

### 9. **Advanced Export Options**
- [ ] **Multiple formats**: Export to XML, HTML, CSV, TXT
- [ ] **Custom templates**: User-defined export templates
- [ ] **Filtered export**: Export only selected entries
- [ ] **Metadata export**: Export dictionary metadata separately
- [ ] **Backup scheduling**: Automatic backup scheduling

**Current Status**: JSON export only
**Files**: `production.html:511`

---

## 🎯 **Integration Features**

### 10. **amilib Integration**
- [ ] **Direct amilib API**: Call amilib functions from browser
- [ ] **Dictionary validation**: Use amilib validation rules
- [ ] **Wikidata lookup**: Use amilib Wikidata integration
- [ ] **File format conversion**: Use amilib conversion utilities
- [ ] **Dictionary merging**: Merge multiple dictionaries

**Current Status**: Planned integration
**Files**: `README.md:146`, `architecture.dot`

### 11. **External API Integration**
- [ ] **Wikipedia API**: Fetch Wikipedia content
- [ ] **Wiktionary API**: Fetch Wiktionary definitions
- [ ] **Translation APIs**: Multi-language support
- [ ] **Image APIs**: Fetch relevant images
- [ ] **Citation APIs**: Auto-generate citations

**Current Status**: Placeholder fields exist
**Files**: `production.html` (wikipedia_url field)

---

## 🛠 **Technical Improvements**

### 12. **Code Organization**
- [ ] **Modular JavaScript**: Split into separate modules
- [ ] **TypeScript**: Add type safety
- [ ] **Build system**: Webpack/Vite for bundling
- [ ] **Testing framework**: Unit and integration tests
- [ ] **Documentation**: API documentation

**Current Status**: Single HTML file with embedded JS
**Files**: `production.html`, `demo.html`

### 13. **Accessibility**
- [ ] **Screen reader support**: ARIA labels and roles
- [ ] **Keyboard navigation**: Full keyboard accessibility
- [ ] **High contrast mode**: Accessibility color schemes
- [ ] **Font scaling**: Support for larger fonts
- [ ] **Voice commands**: Voice control support

**Current Status**: Basic accessibility
**Files**: `production.html`, `css/style.css`

---

## 📋 **Documentation & Help**

### 14. **User Documentation**
- [ ] **Interactive tutorial**: Step-by-step guide
- [ ] **Video tutorials**: Screen recordings
- [ ] **Help system**: Context-sensitive help
- [ ] **FAQ**: Frequently asked questions
- [ ] **Examples**: Sample dictionaries and workflows

**Current Status**: Basic documentation exists
**Files**: `README.md`, `PRODUCTION_GUIDE.md`, `CLI_GUIDE.md`

### 15. **Developer Documentation**
- [ ] **API documentation**: JavaScript API reference
- [ ] **Architecture diagrams**: System design documentation
- [ ] **Contributing guide**: How to contribute
- [ ] **Deployment guide**: Production deployment
- [ ] **Troubleshooting guide**: Common issues and solutions

**Current Status**: Basic architecture documentation
**Files**: `architecture.dot`, `README.md`

---

## 🚨 **Bug Fixes & Issues**

### 16. **Known Issues**
- [ ] **Foreign import not implemented**: XML/HTML/CSV import buttons don't work
- [ ] **Large file handling**: Performance issues with large dictionaries
- [ ] **Browser compatibility**: Test across all major browsers
- [ ] **Mobile responsiveness**: Improve mobile experience
- [ ] **Error handling**: Better error messages and recovery

**Current Status**: Some issues identified
**Files**: `production.html:530`, `demo.html:493`

---

## 📅 **Implementation Priority**

### 🎯 **TOP PRIORITY (User Selected)**
0. **Core File Management & UI Improvements** - File explorer, filename management, dictionary name editing, entry term display
1. **Foreign Format Import/Export** - XML Import/Export for amilib compatibility
2. **Wikidata Integration** - Client-side Wikidata API calls and validation
3. **Advanced Search & Filtering** - Regex search, category/tag filtering
4. **Data Validation & Quality** - Schema validation, duplicate detection
5. **Batch Operations** - Bulk import, edit, delete, export operations

### Phase 2 (Short-term)
1. Advanced UI features
2. Performance optimizations
3. Better error handling
4. External API integrations

### Phase 3 (Long-term)
1. Collaboration features
2. Advanced export options
3. Accessibility improvements
4. Code organization improvements

---

**Last Updated**: January 27, 2025  
**Status**: Active development  
**Priority**: High Priority features should be implemented first for amilib integration
