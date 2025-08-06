# Dictionary Editor - Production Guide

## 🚀 **Quick Start for Production Use**

### **1. Launch the Production Editor**
```bash
# Start server
python -m http.server 8000

# Visit production editor
http://localhost:8000/dictionary_editor/production.html
```

---

## 📋 **Production Workflow**

### **Step 1: Start Server**
```bash
cd /Users/pm286/workspace/amilib
python -m http.server 8000
```

### **Step 2: Load or Create Dictionary**
- **New Dictionary**: Click "New Dictionary" button
- **Load Existing**: Click "Load JSON" and select your dictionary file
- **Auto-recovery**: Previous work is automatically loaded from browser storage

### **Step 3: Manual CRUD Operations**

#### **Add Entry Manually**
1. Click "Add Entry" button
2. Fill in the form:
   - **Term**: The main word/phrase
   - **Definition**: Concise definition
   - **Description**: Authoritative source (Wikipedia/IPCC)
   - **Synonyms**: Comma-separated, can include regex patterns
   - **Examples**: Usage examples
   - **Category**: Classification
   - **Tags**: Searchable tags
   - **References**: Source citations
   - **Wikidata ID**: Q-number if available
   - **Wikipedia URL**: Link to Wikipedia page
3. Click "Save Entry"

#### **Edit Entry Manually**
1. **Option A**: Click entry in sidebar, then "Edit Entry"
2. **Option B**: Edit directly in JSON editor (Tree or Code mode)
3. **Option C**: Double-click values in Tree mode

#### **Delete Entry Manually**
1. Select entry in sidebar
2. Click "Delete Entry" button
3. Confirm deletion

### **Step 4: Save Dictionary Manually**
- **Save**: Click "Save Dictionary" (downloads file)
- **Export**: Click "Export JSON" (creates backup)
- **Auto-save**: Changes are automatically saved to browser storage

---

## 🎯 **Production Features**

### **Dual Interface**
- **Sidebar**: Quick navigation and selection
- **JSON Editor**: Full manual editing capability

### **Search & Navigation**
- **Real-time search**: Type in search box to filter entries
- **Sidebar navigation**: Click entries to select and edit
- **JSON search**: Use Ctrl+F in editor

### **Manual Editing Modes**
- **Tree Mode**: Expandable/collapsible JSON structure
- **Code Mode**: Raw JSON editing for power users

### **Auto-recovery**
- **Browser storage**: Work automatically saved
- **File persistence**: Manual save creates downloadable files

---

## 🔧 **Advanced Production Features**

### **Batch Operations**
```javascript
// In browser console (F12)
// Add multiple entries
const terms = [
    ["term1", "definition1", "description1"],
    ["term2", "definition2", "description2"]
];

terms.forEach(([term, def, desc]) => {
    // Use the form or programmatic API
});
```

### **Import/Export**
- **JSON Import**: Load existing dictionaries
- **Foreign Import**: Placeholder for XML/HTML/CSV (coming soon)
- **JSON Export**: Download in standard format

### **ID Management**
- **Automatic IDs**: `cc_1`, `cc_2`, `cc_3` etc.
- **Dictionary prefixes**: Prevents collisions when merging
- **Manual override**: Edit IDs directly in JSON

---

## 📊 **Production Tips**

### **For Large Dictionaries**
1. **Use Code Mode**: Faster for large datasets
2. **Search First**: Find entries before editing
3. **Batch Operations**: Use console for multiple entries
4. **Regular Saves**: Save frequently to avoid data loss

### **For Team Work**
1. **Consistent Prefixes**: Use same prefix for related dictionaries
2. **Standard Fields**: Fill all required fields consistently
3. **Authoritative Sources**: Always include Wikipedia/IPCC descriptions
4. **Regex Synonyms**: Use patterns for plurals and variations

### **For Data Quality**
1. **Validate Structure**: Check JSON format regularly
2. **Complete Entries**: Fill all relevant fields
3. **Consistent Formatting**: Use same style for similar entries
4. **Source Attribution**: Include references and URLs

---

## 🚨 **Troubleshooting**

### **Editor Not Loading**
```bash
# Check server is running
curl http://localhost:8000/dictionary_editor/production.html

# Check file exists
ls -la dictionary_editor/production.html
```

### **Data Loss Prevention**
- **Auto-save**: Check browser storage
- **Manual saves**: Download files regularly
- **Backup**: Export before major changes

### **Performance Issues**
- **Large dictionaries**: Use Code mode
- **Slow response**: Clear browser cache
- **Memory issues**: Restart browser

---

## 🎯 **Production Checklist**

### **Before Starting**
- [ ] Server running on correct port
- [ ] Production editor loaded
- [ ] Previous work recovered (if any)

### **During Work**
- [ ] Dictionary loaded or created
- [ ] Entries added/edited as needed
- [ ] Changes saved regularly
- [ ] Data validated

### **After Work**
- [ ] Final save completed
- [ ] Export backup created
- [ ] Work documented
- [ ] Server stopped (if needed)

---

## 📁 **File Locations**

- **Production Editor**: `dictionary_editor/production.html`
- **Demo Editor**: `dictionary_editor/demo.html`
- **Documentation**: `dictionary_editor/PRODUCTION_GUIDE.md`
- **CLI Guide**: `dictionary_editor/CLI_GUIDE.md`

---

**Status**: ✅ **Ready for production use!**

**Next**: Import foreign formats (XML/HTML/CSV) and advanced features. 