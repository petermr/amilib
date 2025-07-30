# HTMLEditor Declarative Structure Analysis

**Date**: July 30, 2025 (system date of generation)

## Overview

The `HtmlEditor` class in `amilib/ami_html.py` provides a declarative approach to HTML editing using JSON configuration files. This system allows non-coders to define HTML transformations through external configuration files, aligning perfectly with the project's style principle of external configuration.

## Core Structure

### HtmlEditor Class Location
- **File**: `amilib/ami_html.py` (lines 2957-3168)
- **Key Methods**:
  - `read_commands(command_path)` - Loads JSON command file
  - `execute_commands()` - Executes all commands in sequence
  - `execute_command(command)` - Executes individual command

### Command Execution Flow
1. **Load HTML**: `read_html(inpath)` - Parses target HTML file
2. **Load Commands**: `read_commands(json_path)` - Loads JSON command file
3. **Execute**: `execute_commands()` - Applies all commands sequentially

## JSON Command Structure

### Basic Format
```json
{
  "commands": [
    {
      "command_type": {
        "parameters": "values"
      }
    }
  ]
}
```

### Supported Command Types

#### 1. Delete Command
**Purpose**: Remove elements from HTML using XPath selectors

**Structure**:
```json
{
  "delete": {
    "xpath": "//xpath/selector",
    "comment": "optional description",
    "keep": "descendants",  // optional
    "iterate": "99"         // optional
  }
}
```

**Examples**:
- Single XPath: `"xpath": "//noscript"`
- Multiple XPaths: `"xpath": ["//noscript", "//meta", "//script"]`
- Complex conditions: `"xpath": "//div[count(*)=0 and count(text()=0)]"`

#### 2. Move Command
**Purpose**: Move elements to different locations

**Structure**:
```json
{
  "move": {
    "xpath": "//source/elements",
    "target": "//destination/location"
  }
}
```

#### 3. Add IDs Command
**Purpose**: Ensure elements have unique IDs

**Structure**:
```json
{
  "add_ids": {
    "xpath": "//elements/to/add/ids"
  }
}
```

#### 4. Style Command (Not Yet Implemented)
**Purpose**: Apply CSS styling

**Structure**:
```json
{
  "style": [
    {
      "css": {
        "selector": "div",
        "value": {
          "border": "solid red 1px",
          "margin": "5px"
        }
      }
    }
  ]
}
```

#### 5. Edit Command (Not Yet Implemented)
**Purpose**: Edit element content (placeholder)

#### 6. No-op Command
**Purpose**: Placeholder command for testing

**Structure**:
```json
{
  "no-op": {}
}
```

## Real-World Examples

### 1. Gatsby Cleanup (`de_gatsby.json`)
**Purpose**: Remove Gatsby-specific markup and interactive elements

```json
{
  "commands": [
    {
      "delete": {
        "xpath": [
          "//noscript",
          "//meta",
          "//iframe",
          "//script",
          "//style",
          "//link",
          "//div[not(*) and not(text())]",
          "//footer",
          "//span[@class='arrow-up' or @class='arrow-down' or @class='share-block']",
          "//div[@class='ch-figure-button-cont'",
          "//div[h3='Explore more']",
          "//div[a[button[span='Read more']]]",
          "//div[nav]",
          "//button[.='Expand section']",
          "//div[@class='ref-tooltip' or @class='share-tooltip']",
          "//div[@id='section-tooltip']",
          "//div[div[@class='dropdown']]",
          "//button[span='View']",
          "//div[a[button='Open figure']]"
        ]
      }
    }
  ]
}
```

### 2. Structural Cleanup (`de_gatsby1.json`)
**Purpose**: Remove redundant div structures

```json
{
  "commands": [
    {
      "delete": {
        "xpath": "//div[h1 and count(*)=1]",
        "comment": "div with single child is redundant",
        "keep": "descendants",
        "iterate": "99"
      }
    },
    {
      "delete": {
        "xpath": "//div[count(*)=0 and count(text()=0)]",
        "comment": "empty div",
        "iterate": "99"
      }
    }
  ]
}
```

### 3. Top-level Cleanup (`edit_toplevel.json`)
**Purpose**: Remove common unwanted elements and add debugging styles

```json
{
  "commands": [
    {"delete": {"xpath": "//noscript", "comment": "no useful content"}},
    {"delete": {"xpath": "//script"}},
    {"delete": {"xpath": "//meta"}},
    {"delete": {"xpath": "//style"}},
    {"delete": {"xpath": "//link"}},
    {"delete": {"xpath": "//footer"}},
    {"delete": {"xpath": "//picture"}},
    {"delete": {"xpath": "//div[@class='artistLink']"}},
    {"delete": {"xpath": "//div[@class='nav2']"}},
    {"delete": {"xpath": "//div[count(*)=0]", "comment": "empty divs"}},
    {"delete": {"xpath": "//div[img]"}},
    {
      "style": [
        {
          "css": {
            "selector": "div",
            "value": {
              "border": "solid red 1px",
              "margin": "5px"
            }
          }
        }
      ]
    }
  ]
}
```

## XPath Patterns Used

### Common Patterns
1. **Element Types**: `//noscript`, `//script`, `//meta`, `//style`
2. **Empty Elements**: `//div[count(*)=0 and count(text()=0)]`
3. **Single Child**: `//div[h1 and count(*)=1]`
4. **Class-based**: `//span[@class='arrow-up' or @class='arrow-down']`
5. **Content-based**: `//button[.='Expand section']`
6. **Nested Conditions**: `//div[a[button[span='Read more']]]`

### Advanced XPath Features
- **Count Functions**: `count(*)`, `count(text())`
- **Logical Operators**: `and`, `or`
- **Attribute Matching**: `@class='value'`
- **Text Content**: `.='text'`
- **Nested Predicates**: `//div[condition1 and condition2]`

## Integration with Corpus Design

### Alignment with External Configuration Principle
This declarative approach perfectly aligns with the corpus design principle:
- **Non-coder Accessibility**: JSON files are readable by business users
- **External Configuration**: Transformations defined outside code
- **Reusability**: Same commands can apply to different documents
- **Version Control**: Transformation logic tracked separately

### Potential Extensions for Corpus Workflow
1. **Document Type Detection**: Different command sets for different document types
2. **Transformation Chaining**: Multiple command files applied in sequence
3. **Conditional Commands**: Commands that apply based on document characteristics
4. **Metadata Integration**: Commands that reference corpus metadata

## Implementation Details

### Command Processing
```python
def execute_commands(self):
    commands = self.commands.get("commands")
    for command in commands:
        self.execute_command(command)

def execute_command(self, command):
    if cmd := command.get("delete"):
        self.delete_elements(cmd)
    elif cmd := command.get("move"):
        self.move_elements(cmd)
    elif cmd := command.get("add_ids"):
        self.add_ids(cmd)
    # ... other command types
```

### Error Handling
- Missing commands: Warning logged, no action taken
- Invalid XPath: Warning logged, command skipped
- Missing HTML: Warning logged, no action taken

## Usage Examples

### Basic Usage
```python
editor = HtmlEditor()
editor.read_html("input.html")
editor.read_commands("commands.json")
editor.execute_commands()
editor.write("output.html")
```

### Test Integration
The system is well-integrated with the test suite:
- `test/test_html.py` - Comprehensive HtmlEditor tests
- `test/test_graph.py` - Graph-related editing tests
- `test/test_ipcc.py` - IPCC-specific editing tests

## Future Enhancements

### Planned Features
1. **Style Commands**: Full CSS styling support
2. **Edit Commands**: Content editing capabilities
3. **Conditional Commands**: Context-aware transformations
4. **Validation**: Schema validation for command files

### Potential Applications
1. **IPCC Document Processing**: Standardized cleanup for IPCC documents
2. **Multi-format Support**: Commands for different input formats
3. **Pipeline Integration**: Integration with corpus transformation pipelines
4. **Visual Debugging**: Enhanced debugging styles and tools

## Conclusion

The HTMLEditor declarative system provides a powerful, flexible approach to HTML transformation that:
- **Follows Style Principles**: External configuration, non-coder accessibility
- **Supports Complex Operations**: XPath-based element selection and manipulation
- **Enables Reusability**: Command files can be shared across projects
- **Facilitates Testing**: Comprehensive test coverage and examples
- **Aligns with Corpus Design**: Perfect fit for the planned corpus transformation workflow

This system represents an excellent foundation for the corpus PDF annotation project's transformation needs. 