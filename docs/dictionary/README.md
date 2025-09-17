# Dictionary Documentation

This directory contains comprehensive documentation for the AmiDictionary system, including the new HTML-based schema design and implementation plans.

## 📚 Documentation Overview

### **Core Documentation**
- **[Schema Design Summary](amidictionary_schema_design.md)** - Complete overview of the HTML-based redesign
- **[User Guide](../dictionary_editor/USER_GUIDE.md)** - How to use the dictionary editor
- **[Style Guide Compliance](../style_guide_compliance.md)** - Project coding standards

## 🎯 What This System Does

AmiDictionary is a flexible, multilingual dictionary system that supports:

- **Text Annotation** - Linking text to dictionary entries for semantic analysis
- **Educational Content** - Rich, browsable encyclopedia-style entries
- **Creative Authoring** - Flexible content creation with multimedia support

## 🔄 Major Changes in v2.0

### **From XML to HTML**
- **Before**: Complex XML structure, difficult to edit, limited content support
- **After**: Simple HTML with roles, easy to edit, rich content support

### **New Schema Features**
- **Lightweight validation** using HTML roles and data attributes
- **UTF-8 encoding** for direct multilingual input
- **Rich content support** including MathML, SVG, tables, and multimedia
- **Graceful error handling** with clear validation messages

## 🚀 Quick Start

### **Basic HTML Dictionary Structure**
```html
<div role="ami_dictionary" data-schema-version="2.0">
    <div role="ami_entry" id="Q123" term="climate change">
        <span role="term" lang="en">climate change</span>
        <p role="definition" lang="en">Long-term change in weather patterns</p>
    </div>
</div>
```

### **Required Fields**
- `role="ami_dictionary"` at root level
- `role="ami_entry"` for each entry
- `id` attribute (unique within dictionary)
- `term` attribute
- At least one `<span role="term">` element

## 🔧 Implementation Status

### **✅ Completed**
- [x] Schema design and documentation
- [x] Validation rules definition
- [x] Example structures
- [x] Implementation plan

### **🔄 In Progress**
- [ ] Core HTML dictionary implementation
- [ ] Schema validation functions
- [ ] Migration tools from XML

### **📋 Planned**
- [ ] Integration with Wikipedia classification
- [ ] Disambiguation classifier updates
- [ ] User interface improvements
- [ ] Performance optimization

## 🎨 Use Cases

### **1. Text Annotation**
- Fast term lookup and linking
- Synonym management
- Reference tracking

### **2. Educational Encyclopedia**
- Rich multimedia content
- Hierarchical organization
- Related concept linking

### **3. Creative Authoring**
- Flexible content types
- Custom multimedia elements
- Interactive features

## 🛠️ Technical Details

### **Schema Validation**
- **Lightweight approach** - no external schema files
- **Role-based validation** - checks HTML roles and attributes
- **Graceful failure** - clear error messages, no crashes

### **Content Support**
- **Text content** - paragraphs, headings, lists
- **Scientific content** - MathML, chemical formulas
- **Visual content** - SVG, images, diagrams
- **Interactive content** - forms, multimedia

### **Multilingual Support**
- **UTF-8 encoding** - direct input in any language
- **Language attributes** - standard HTML `lang` attributes
- **Flexible structure** - any language combination supported

## 📖 Getting Started

### **For Users**
1. **Read the schema design** - understand the new structure
2. **Try the dictionary editor** - create simple entries
3. **Explore examples** - see how rich content works
4. **Provide feedback** - help improve the system

### **For Developers**
1. **Review the implementation plan** - understand the roadmap
2. **Examine existing code** - see what can be reused
3. **Start with tests** - bottom-up development approach
4. **Contribute improvements** - help build the system

### **For Migrators**
1. **Understand the new schema** - HTML vs XML differences
2. **Use conversion tools** - when available
3. **Validate new dictionaries** - ensure schema compliance
4. **Test thoroughly** - verify all functionality works

## 🆘 Support & Resources

### **Documentation**
- **Schema Design** - complete technical specification
- **User Guide** - practical usage instructions
- **Examples** - sample dictionaries and entries

### **Tools**
- **Dictionary Editor** - web-based creation interface
- **Validation Tools** - schema compliance checking
- **Migration Tools** - XML to HTML conversion

### **Community**
- **Feedback** - report issues and suggest improvements
- **Examples** - share your dictionary creations
- **Contributions** - help improve the system

## 🔮 Future Development

### **Short Term (Next 2 weeks)**
- Core HTML dictionary implementation
- Basic schema validation
- Migration tool development

### **Medium Term (Next month)**
- Full system integration
- Performance optimization
- User interface improvements

### **Long Term (Next quarter)**
- Advanced features
- Machine learning integration
- Community tools

---

**AmiDictionary v2.0 represents a significant evolution from a complex XML-based system to a simple, powerful HTML-based system that's easier to use, more flexible, and better integrated with modern web technologies.**















