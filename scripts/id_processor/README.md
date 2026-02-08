# ID Processor Module

This module implements cascading ID addition to HTML documents using a schema-based approach.

## Overview

The ID addition process follows a cascading pattern:

1. **Section Containers** → Get IDs from headings
2. **Paragraphs** → Get IDs based on parent section (`{section_id}_p{index}`)
3. **Nested Divs** → Get IDs based on parent container (`{parent_id}_{type}_{index}`)

## Files

- `id_schema.py` - Schema definitions and ID generation rules
- `add_section_ids.py` - Step 1: Add IDs to section containers
- `add_paragraph_ids.py` - Step 2: Add IDs to paragraphs
- `add_nested_div_ids.py` - Step 3: Add IDs to nested divs
- `generate_id_lists.py` - Generate ID and paragraph lists
- `validate_ids.py` - Validate ID uniqueness and format

## Usage

### Individual Scripts

```bash
# Step 1: Add section IDs
python scripts/id_processor/add_section_ids.py \
    --input test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/de_gatsby.html \
    --output test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_section_ids.html \
    --report wg1

# Step 2: Add paragraph IDs
python scripts/id_processor/add_paragraph_ids.py \
    --input test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_section_ids.html \
    --output test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_ids.html \
    --report wg1

# Step 3: Add nested div IDs
python scripts/id_processor/add_nested_div_ids.py \
    --input test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_ids.html \
    --output test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_all_ids.html \
    --report wg1

# Generate ID lists
python scripts/id_processor/generate_id_lists.py \
    --input test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_all_ids.html \
    --id-list test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/id_list.html \
    --para-list test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/para_list.html

# Validate IDs
python scripts/id_processor/validate_ids.py \
    --input test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/html_with_all_ids.html
```

### Using doit

```bash
# Install doit
pip install doit

# Run all tasks
doit

# Run specific task
doit add_section_ids

# List tasks
doit list

# Show task details
doit info
```

## Schema

The ID schema defines rules for each element type:

- **section_containers**: Extract IDs from headings
- **paragraphs**: Format `{section_id}_p{index}`
- **nested_divs**: Format `{parent_id}_{type}_{index}`

See `id_schema.py` for detailed schema definitions.




