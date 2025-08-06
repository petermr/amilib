# Dictionary Editor - Command Line Interface Guide

## 🚀 (a) Launch the Editor

### **Quick Start:**
```bash
# Open directly in browser
open dictionary_editor/demo.html

# Or start local server
python -m http.server 8000
# Then visit: http://localhost:8000/dictionary_editor/demo.html
```

### **Alternative Servers:**
```bash
# Node.js
npx serve dictionary_editor/

# PHP
php -S localhost:8000

# Python 3
python -m http.server 8000
```

---

## 🎮 (b) Drive CRUD Operations

### **Method 1: Browser Console Commands**

Open browser developer tools (F12) and use these commands:

#### **Load Sample Data**
```javascript
dictionaryEditor.loadSample()
// Returns: "Sample dictionary loaded"
```

#### **Add New Entry**
```javascript
dictionaryEditor.addEntry("solar energy", "Energy from the sun", "Solar energy is radiant light and heat from the Sun...")
// Returns: "Entry "solar energy" added with ID cc_4"
```

#### **Get Entry by ID**
```javascript
dictionaryEditor.getEntry("cc_1")
// Returns: Entry object for "climate change"
```

#### **Update Entry**
```javascript
dictionaryEditor.updateEntry("cc_2", {
    synonyms: ["greenhouse gases", "GHG", "GHGs", "carbon dioxide", "methane"],
    tags: ["atmosphere", "climate", "emissions", "carbon", "methane"]
})
// Returns: "Entry cc_2 updated"
```

#### **Delete Entry**
```javascript
dictionaryEditor.deleteEntry("cc_3")
// Returns: "Entry cc_3 deleted"
```

#### **List All Entries**
```javascript
dictionaryEditor.listEntries()
// Returns: 
// cc_1: climate change
// cc_2: greenhouse gas
// cc_4: solar energy
```

#### **Export Dictionary**
```javascript
dictionaryEditor.export()
// Downloads: dictionary_export.json
```

#### **Get Full Dictionary**
```javascript
dictionaryEditor.getDictionary()
// Returns: Complete dictionary object
```

#### **Set Dictionary**
```javascript
dictionaryEditor.setDictionary(myDictionaryObject)
// Returns: "Dictionary updated"
```

---

### **Method 2: Button Clicks (Interactive)**

```javascript
// Load sample
document.getElementById('loadBtn').click();

// Add entry
document.getElementById('addBtn').click();

// Edit entry
document.getElementById('editBtn').click();

// Delete entry
document.getElementById('deleteBtn').click();

// Export
document.getElementById('exportBtn').click();
```

---

## 📋 **Example Workflow**

### **1. Launch and Load**
```bash
# Terminal
open dictionary_editor/demo.html
```

```javascript
// Browser Console (F12)
dictionaryEditor.loadSample()
```

### **2. Add Multiple Entries**
```javascript
dictionaryEditor.addEntry("wind power", "Energy from wind turbines", "Wind power is the use of wind energy...")
dictionaryEditor.addEntry("geothermal energy", "Energy from Earth's heat", "Geothermal energy is thermal energy...")
dictionaryEditor.addEntry("biofuel", "Fuel from biological sources", "Biofuel is a fuel that is produced...")
```

### **3. Update Entries**
```javascript
dictionaryEditor.updateEntry("cc_4", {
    category: "renewable_energy",
    tags: ["solar", "renewable", "clean_energy"]
})
```

### **4. List and Export**
```javascript
console.log(dictionaryEditor.listEntries())
dictionaryEditor.export()
```

---

## 🔧 **Advanced Operations**

### **Batch Operations**
```javascript
// Add multiple entries
const terms = [
    ["hydropower", "Energy from flowing water", "Hydropower is power derived from..."],
    ["nuclear energy", "Energy from nuclear reactions", "Nuclear energy is the energy..."]
];

terms.forEach(([term, def, desc]) => {
    dictionaryEditor.addEntry(term, def, desc);
});
```

### **Search and Filter**
```javascript
// Get all entries with "energy" in term
const dict = dictionaryEditor.getDictionary();
const energyTerms = dict.entries.filter(e => 
    e.term.toLowerCase().includes('energy')
);
console.log(energyTerms);
```

### **Bulk Updates**
```javascript
// Add tag to all entries
const dict = dictionaryEditor.getDictionary();
dict.entries.forEach(entry => {
    if (!entry.tags.includes('climate_science')) {
        entry.tags.push('climate_science');
    }
});
dictionaryEditor.setDictionary(dict);
```

---

## 🎯 **Quick Reference**

| Operation | Command | Returns |
|-----------|---------|---------|
| Load Sample | `dictionaryEditor.loadSample()` | Status message |
| Add Entry | `dictionaryEditor.addEntry(term, def, desc)` | Entry ID |
| Get Entry | `dictionaryEditor.getEntry(id)` | Entry object |
| Update Entry | `dictionaryEditor.updateEntry(id, updates)` | Status message |
| Delete Entry | `dictionaryEditor.deleteEntry(id)` | Status message |
| List All | `dictionaryEditor.listEntries()` | Formatted list |
| Export | `dictionaryEditor.export()` | Downloads file |
| Get Dict | `dictionaryEditor.getDictionary()` | Full object |
| Set Dict | `dictionaryEditor.setDictionary(obj)` | Status message |

---

## 🚨 **Troubleshooting**

### **Editor Not Loaded**
```javascript
// Check if editor is available
typeof dictionaryEditor !== 'undefined'
// Should return: true
```

### **Entry Not Found**
```javascript
// List all entries to see available IDs
dictionaryEditor.listEntries()
```

### **Export Not Working**
```javascript
// Check if dictionary has data
const dict = dictionaryEditor.getDictionary();
console.log(dict.entries.length);
```

---

**Status**: ✅ **Ready for command-line driving!** 