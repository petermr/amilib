# CSS Library Evaluation for Amilib

**Date**: 2025-01-27  
**Purpose**: Evaluate CSS libraries to replace custom CSSStyle class (lines 5476-6108 in ami_html.py)

## Current CSSStyle Analysis

### What CSSStyle Does:
1. **CSS Parsing**: Parses CSS strings into name-value dictionaries
2. **CSS Generation**: Converts dictionaries back to CSS strings
3. **Style Management**: Sets/gets individual CSS properties
4. **Font Analysis**: Extracts font properties from CSS
5. **Style Validation**: Validates CSS property values
6. **HTML Integration**: Applies styles to HTML elements

### Key Methods:
- `create_css_style_from_css_string()` - Parse CSS
- `get_css_value()` - Generate CSS string
- `set_attribute()` / `get_attribute()` - Property management
- `set_font_weight()` / `set_font_style()` - Font-specific setters
- `apply_to()` - Apply to HTML element

## CSS Library Candidates

### 1. **cssutils** (Recommended)

**GitHub**: https://github.com/cthedot/cssutils  
**PyPI**: https://pypi.org/project/cssutils/  
**License**: LGPL-3.0

#### ✅ **Pros**:
- **Comprehensive**: Full CSS parsing and generation
- **Standards Compliant**: Follows CSS specifications
- **Active Development**: Regular updates
- **Well Documented**: Good documentation and examples
- **CSS Validation**: Built-in validation
- **CSS Optimization**: Minification and optimization

#### ❌ **Cons**:
- **Heavy**: Full CSS parser (might be overkill)
- **Complex API**: More complex than needed for simple cases

#### **Example Usage**:
```python
import cssutils

# Parse CSS
sheet = cssutils.parseString('p { color: red; font-size: 12px; }')

# Generate CSS
css_string = sheet.cssText

# Access properties
for rule in sheet:
    if rule.type == rule.STYLE_RULE:
        for property in rule.style:
            print(f"{property.name}: {property.value}")
```

### 2. **tinycss2** (Lightweight Option)

**GitHub**: https://github.com/Kozea/tinycss2  
**PyPI**: https://pypi.org/project/tinycss2/  
**License**: BSD-3-Clause

#### ✅ **Pros**:
- **Lightweight**: Minimal dependencies
- **Fast**: Optimized for performance
- **Simple API**: Easy to use
- **Well Maintained**: Part of WeasyPrint project
- **CSS3 Support**: Modern CSS features

#### ❌ **Cons**:
- **Parsing Only**: No CSS generation (would need separate library)
- **Limited Features**: Basic parsing only

#### **Example Usage**:
```python
import tinycss2

# Parse CSS
rules = tinycss2.parse_stylesheet('p { color: red; }')

# Extract properties
for rule in rules:
    if rule.type == 'qualified-rule':
        for token in rule.content:
            if token.type == 'declaration':
                print(f"{token.name}: {token.value}")
```

### 3. **css-parser** (Alternative)

**GitHub**: https://github.com/strangerofsweden/css-parser  
**PyPI**: https://pypi.org/project/css-parser/  
**License**: MIT

#### ✅ **Pros**:
- **Simple API**: Easy to understand
- **CSS Generation**: Can generate CSS
- **MIT License**: Very permissive
- **Pure Python**: No C dependencies

#### ❌ **Cons**:
- **Less Active**: Fewer updates
- **Limited Features**: Basic functionality only
- **Less Documentation**: Limited examples

#### **Example Usage**:
```python
from css_parser import parseString, CSSParser

# Parse CSS
sheet = parseString('p { color: red; }')

# Generate CSS
css_string = sheet.cssText

# Access properties
for rule in sheet:
    if rule.type == rule.STYLE_RULE:
        for property in rule.style:
            print(f"{property.name}: {property.value}")
```

## Recommendation: **cssutils**

### Why cssutils is the best choice:

1. **Complete Solution**: Handles both parsing and generation
2. **Standards Compliant**: Follows CSS specifications
3. **Active Development**: Regular maintenance and updates
4. **Rich Features**: Validation, optimization, minification
5. **Good Documentation**: Clear examples and API docs
6. **Mature Library**: Well-tested and stable

### Migration Strategy:

#### Phase 1: Basic Replacement
```python
# Current CSSStyle usage:
css_style = CSSStyle()
css_style.set_attribute('color', 'red')
css_style.set_attribute('font-size', '12px')
css_string = css_style.get_css_value()

# Replace with cssutils:
import cssutils
from cssutils.css import CSSStyleDeclaration

style_decl = CSSStyleDeclaration()
style_decl.setProperty('color', 'red')
style_decl.setProperty('font-size', '12px')
css_string = style_decl.cssText
```

#### Phase 2: Advanced Features
```python
# CSS validation
sheet = cssutils.parseString(css_string)
if sheet.valid:
    print("Valid CSS")
else:
    print("Invalid CSS:", sheet.errors)

# CSS optimization
sheet = cssutils.parseString(css_string)
optimized_css = sheet.cssText  # Automatically optimized
```

#### Phase 3: HTML Integration
```python
# Apply styles to HTML elements
from lxml import etree

def apply_css_to_element(element, css_string):
    style_decl = CSSStyleDeclaration(cssText=css_string)
    element.set('style', style_decl.cssText)
```

### Estimated Code Reduction:

- **CSSStyle class**: ~632 lines
- **CSS parsing methods**: ~200 lines
- **CSS generation methods**: ~150 lines
- **Font analysis methods**: ~100 lines
- **Total**: ~1,082 lines (significant reduction!)

### Implementation Plan:

1. **Install cssutils**: `pip install cssutils`
2. **Create wrapper class**: Simple interface to cssutils
3. **Test with existing code**: Ensure compatibility
4. **Gradually replace**: One method at a time
5. **Remove old code**: Once fully tested

### Dependencies:
```python
# requirements.txt addition
cssutils>=2.7.0
```

## Alternative: Hybrid Approach

If cssutils is too heavy, consider a hybrid approach:

1. **Use tinycss2** for parsing (lightweight)
2. **Use simple string formatting** for generation (custom but simple)
3. **Keep minimal CSSStyle** for HTML integration

This would still reduce code significantly while keeping dependencies minimal.

---
*This evaluation will be updated as we test specific libraries.* 