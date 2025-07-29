# CSS Library Replacement Test Plan

**Date**: 2025-01-27  
**Purpose**: Test plan for replacing custom CSSStyle class with cssutils library

## Test Strategy

### **Phase 1: Current Functionality Tests**
Test all existing CSSStyle functionality to establish baseline behavior.

### **Phase 2: cssutils Compatibility Tests**
Test cssutils can handle all current use cases.

### **Phase 3: Migration Tests**
Test wrapper/compatibility layer maintains existing API.

### **Phase 4: Integration Tests**
Test CSS functionality within larger amilib workflows.

## Test Cases

### **1. Basic CSS Property Operations**

#### **Test 1.1: Setting Individual Properties**
```python
# Test current CSSStyle
css_style = CSSStyle()
css_style.set_attribute('color', 'red')
css_style.set_attribute('font-size', '12px')
assert css_style.get_css_value() == "color: red; font-size: 12px;"

# Test cssutils equivalent
style_decl = CSSStyleDeclaration()
style_decl.setProperty('color', 'red')
style_decl.setProperty('font-size', '12px')
assert style_decl.cssText == "color: red; font-size: 12px;"
```

#### **Test 1.2: Getting Individual Properties**
```python
# Test current CSSStyle
css_style = CSSStyle.create_css_style_from_css_string("color: blue; font-size: 14px;")
assert css_style.get_attribute('color') == "blue"
assert css_style.get_attribute('font-size') == "14px"

# Test cssutils equivalent
style_decl = CSSStyleDeclaration(cssText="color: blue; font-size: 14px;")
assert style_decl.getPropertyValue('color') == "blue"
assert style_decl.getPropertyValue('font-size') == "14px"
```

### **2. CSS Parsing Tests**

#### **Test 2.1: Simple CSS String Parsing**
```python
test_css = "color: red; font-size: 12px; font-weight: bold;"

# Current CSSStyle
css_style = CSSStyle.create_css_style_from_css_string(test_css)
assert css_style.get_attribute('color') == "red"
assert css_style.get_attribute('font-size') == "12px"
assert css_style.get_attribute('font-weight') == "bold"

# cssutils equivalent
style_decl = CSSStyleDeclaration(cssText=test_css)
assert style_decl.getPropertyValue('color') == "red"
assert style_decl.getPropertyValue('font-size') == "12px"
assert style_decl.getPropertyValue('font-weight') == "bold"
```

#### **Test 2.2: Complex CSS String Parsing**
```python
complex_css = "font-family: Arial, sans-serif; font-size: 14px; color: #ff0000; border: 1px solid black;"

# Test both implementations handle complex CSS
# (Test with various CSS properties, units, colors, etc.)
```

#### **Test 2.3: Malformed CSS Handling**
```python
malformed_css = "color: red; font-size: ; font-weight: bold;"

# Test how both handle malformed CSS
# Current CSSStyle might be more forgiving
# cssutils should provide better error handling
```

### **3. CSS Generation Tests**

#### **Test 3.1: CSS String Generation**
```python
# Test that generated CSS is valid and equivalent
css_style = CSSStyle()
css_style.set_attribute('color', 'red')
css_style.set_attribute('font-size', '12px')

style_decl = CSSStyleDeclaration()
style_decl.setProperty('color', 'red')
style_decl.setProperty('font-size', '12px')

# Both should generate equivalent CSS
assert css_style.get_css_value() == style_decl.cssText
```

#### **Test 3.2: CSS with Curly Braces**
```python
# Test CSS generation with and without curly braces
css_style = CSSStyle()
css_style.set_attribute('color', 'red')

# Current: get_css_value(wrap_with_curly=True)
# cssutils: might handle differently
```

### **4. Font-Specific Tests**

#### **Test 4.1: Font Weight Setting**
```python
# Test font weight normalization
css_style = CSSStyle()
css_style.set_font_weight('bold')
assert css_style.get_attribute('font-weight') == 'bold'

style_decl = CSSStyleDeclaration()
style_decl.setProperty('font-weight', 'bold')
assert style_decl.getPropertyValue('font-weight') == 'bold'
```

#### **Test 4.2: Font Style Setting**
```python
# Test font style normalization
css_style = CSSStyle()
css_style.set_font_style('italic')
assert css_style.get_attribute('font-style') == 'italic'

style_decl = CSSStyleDeclaration()
style_decl.setProperty('font-style', 'italic')
assert style_decl.getPropertyValue('font-style') == 'italic'
```

### **5. HTML Integration Tests**

#### **Test 5.1: Applying Styles to HTML Elements**
```python
from lxml import etree

# Create test HTML element
html_element = etree.Element('div')

# Current CSSStyle approach
css_style = CSSStyle()
css_style.set_attribute('color', 'red')
css_style.apply_to(html_element)
assert html_element.get('style') == "color: red;"

# cssutils approach
style_decl = CSSStyleDeclaration()
style_decl.setProperty('color', 'red')
html_element.set('style', style_decl.cssText)
assert html_element.get('style') == "color: red;"
```

### **6. Edge Cases and Error Handling**

#### **Test 6.1: Empty CSS**
```python
# Test handling of empty CSS strings
empty_css = ""

# Both should handle gracefully
```

#### **Test 6.2: Invalid Properties**
```python
# Test handling of invalid CSS properties
css_style = CSSStyle()
css_style.set_attribute('invalid-property', 'value')

style_decl = CSSStyleDeclaration()
style_decl.setProperty('invalid-property', 'value')

# cssutils should provide validation
```

#### **Test 6.3: Special Characters**
```python
# Test CSS with special characters, quotes, etc.
complex_css = "font-family: 'Times New Roman', serif; content: \"Hello World\";"
```

### **7. Performance Tests**

#### **Test 7.1: Large CSS Processing**
```python
# Test performance with large CSS strings
large_css = "; ".join([f"property{i}: value{i}" for i in range(1000)])

# Compare performance between current and cssutils
```

### **8. Integration Tests**

#### **Test 8.1: PDF to HTML Conversion**
```python
# Test CSS processing in PDF conversion workflow
# Use real PDF files and verify CSS generation is correct
```

#### **Test 8.2: HTML Restructuring**
```python
# Test CSS processing in HTML restructuring workflow
# Verify styles are preserved correctly
```

## Test Implementation Plan

### **Step 1: Create Test Infrastructure**
1. Create test directory structure
2. Set up pytest configuration
3. Create test data files (sample CSS, HTML, PDFs)

### **Step 2: Implement Current Functionality Tests**
1. Write tests for all CSSStyle methods
2. Document current behavior
3. Create baseline test results

### **Step 3: Implement cssutils Tests**
1. Write equivalent tests using cssutils
2. Compare results with current implementation
3. Identify any differences or issues

### **Step 4: Create Compatibility Wrapper Tests**
1. Test wrapper maintains existing API
2. Verify all existing functionality works
3. Test error handling

### **Step 5: Integration Tests**
1. Test CSS functionality in real workflows
2. Use actual amilib files and processes
3. Verify no regressions

## Test Files to Create

### **test_css_style_current.py**
- Tests for current CSSStyle implementation
- Establishes baseline behavior

### **test_css_style_cssutils.py**
- Tests for cssutils implementation
- Compares with current behavior

### **test_css_style_wrapper.py**
- Tests for compatibility wrapper
- Ensures API compatibility

### **test_css_integration.py**
- Integration tests with PDF and HTML processing
- End-to-end workflow tests

### **test_data/**
- Sample CSS files
- Sample HTML files with styles
- Sample PDF files for conversion testing

## Success Criteria

### **Functional Requirements**
- All existing CSSStyle functionality preserved
- No regressions in CSS processing
- Better error handling for invalid CSS
- Improved CSS validation

### **Performance Requirements**
- No significant performance degradation
- Memory usage remains reasonable
- CSS processing speed maintained or improved

### **Compatibility Requirements**
- Existing code continues to work
- API remains compatible (if using wrapper)
- No breaking changes to external interfaces

## Risk Mitigation

### **Rollback Plan**
1. Keep current CSSStyle class as backup
2. Use feature flags to switch between implementations
3. Maintain ability to revert quickly if issues arise

### **Gradual Migration**
1. Start with non-critical CSS operations
2. Test thoroughly before moving to core functionality
3. Monitor for issues in development environment

---
*This test plan will be updated as we implement and discover additional requirements.* 