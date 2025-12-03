# Encyclopedia Interaction Scheme - Proposal

## User's Proposed Scheme

### Workflow
1. **Resolve all wikidata_ids** - Ensure all entries have Wikidata IDs
2. **Normalize entries** - Collapse entries with same Wikidata ID into single entry with synonyms
3. **Categorize entries**:
   - **DISAMBIG**: Entries pointing to disambiguation pages
   - **NO_WIKIDATA**: Entries where no Wikidata ID was found
   - **SINGLE**: All other entries (have valid Wikidata ID, not disambiguation)
4. **For DISAMBIG**: Show target page with radio buttons for all possible links
5. **For SINGLE**: Listbox with options: ACCEPT, TOO BROAD, FALSE
6. **For NO_WIKIDATA**: Listbox with options: ACCEPT, HIDE
7. **Use CSS visibility** to hide entries

## Comments on the Scheme

### ✅ Strengths

1. **Clear categorization**: Three distinct categories make the workflow clear
2. **Progressive refinement**: Resolve IDs → Normalize → Categorize → Interact
3. **User control**: Listboxes provide clear action choices
4. **CSS visibility**: Non-destructive hiding (can be toggled)

### 🤔 Considerations

1. **SINGLE category**: Currently we have `CATEGORY_TRUE_WIKIPEDIA` which is similar. The scheme's "SINGLE" is clearer.

2. **Radio buttons vs Listbox for DISAMBIG**: 
   - Radio buttons are better for mutually exclusive selection
   - Current implementation uses `<select>` (listbox) - could switch to radio buttons

3. **Action semantics**:
   - **ACCEPT**: Entry is valid (keep visible)
   - **TOO BROAD**: Entry is too general (hide)
   - **FALSE**: Entry is incorrect (hide)
   - **HIDE**: Explicitly hide entry

4. **State management**: Need to track user selections and apply CSS visibility accordingly

5. **Metadata**: All user actions should be recorded in metadata

## Proposed Implementation

### 1. Enhanced Entry Categorization

Add new category constant:
```python
CATEGORY_SINGLE = "single"  # Valid Wikidata ID, not disambiguation
```

Update `_classify_entry()` to use three categories:
- `DISAMBIG`: Disambiguation page detected
- `NO_WIKIDATA`: No Wikidata ID found
- `SINGLE`: Valid Wikidata ID, not disambiguation

### 2. HTML Structure with CSS Classes

```html
<div role="ami_entry" 
     data-entry-id="entry_001" 
     data-wikidata-id="Q7942"
     data-category="single"
     class="encyclopedia-entry">
    
    <!-- Entry controls container -->
    <div class="entry-controls" data-category="single">
        
        <!-- SINGLE: Listbox with ACCEPT, TOO BROAD, FALSE -->
        <select class="entry-action-select" 
                data-entry-id="entry_001"
                data-category="single">
            <option value="">-- Select action --</option>
            <option value="accept">ACCEPT</option>
            <option value="too_broad">TOO BROAD</option>
            <option value="false">FALSE</option>
        </select>
        
    </div>
    
    <!-- Entry content -->
    <div class="entry-content">
        <!-- Entry details here -->
    </div>
</div>
```

### 3. CSS Visibility Implementation

```css
/* Hide entries based on action selection */
.encyclopedia-entry[data-action="hide"],
.encyclopedia-entry[data-action="too_broad"],
.encyclopedia-entry[data-action="false"] {
    display: none;  /* Or visibility: hidden; */
}

/* Alternative: Use class-based hiding */
.encyclopedia-entry.hidden {
    display: none;
}

/* Show entries that are accepted */
.encyclopedia-entry[data-action="accept"] {
    display: block;
}
```

### 4. JavaScript for Interaction (Client-side)

```javascript
// Handle SINGLE category actions
document.querySelectorAll('.entry-action-select[data-category="single"]').forEach(select => {
    select.addEventListener('change', function() {
        const entryId = this.getAttribute('data-entry-id');
        const action = this.value;
        const entryDiv = document.querySelector(`[data-entry-id="${entryId}"]`);
        
        // Update entry data attribute
        entryDiv.setAttribute('data-action', action);
        
        // Apply CSS visibility
        if (action === 'accept') {
            entryDiv.classList.remove('hidden');
        } else {
            entryDiv.classList.add('hidden');
        }
        
        // Record action in metadata
        recordAction(entryId, action);
    });
});

// Handle DISAMBIG radio buttons
document.querySelectorAll('input[type="radio"][name^="disambig_"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const entryId = this.getAttribute('data-entry-id');
        const selectedUrl = this.value;
        
        // Update entry with selected Wikipedia URL
        updateEntryWikipediaUrl(entryId, selectedUrl);
        
        // Record action
        recordAction(entryId, 'disambiguation_select', {selected_url: selectedUrl});
    });
});

// Handle NO_WIKIDATA actions
document.querySelectorAll('.entry-action-select[data-category="no_wikidata"]').forEach(select => {
    select.addEventListener('change', function() {
        const entryId = this.getAttribute('data-entry-id');
        const action = this.value;
        const entryDiv = document.querySelector(`[data-entry-id="${entryId}"]`);
        
        if (action === 'accept') {
            entryDiv.classList.remove('hidden');
        } else if (action === 'hide') {
            entryDiv.classList.add('hidden');
        }
        
        recordAction(entryId, action);
    });
});
```

### 5. Python Implementation Changes

#### Update Category Constants

```python
# Entry category constants
CATEGORY_DISAMBIG = "disambig"  # Disambiguation page
CATEGORY_NO_WIKIDATA = "no_wikidata"  # No Wikidata ID found
CATEGORY_SINGLE = "single"  # Valid Wikidata ID, not disambiguation
```

#### Update `_classify_entry()` Method

```python
def _classify_entry(self, entry_or_group: Dict) -> str:
    """Classify entry into category based on Wikidata ID and Wikipedia status
    
    Categories:
    - disambig: Disambiguation page found
    - no_wikidata: No Wikidata ID found
    - single: Valid Wikidata ID, not disambiguation
    
    Args:
        entry_or_group: Entry dictionary or synonym group dictionary
        
    Returns:
        Category string
    """
    wikidata_id = entry_or_group.get('wikidata_id', '')
    wikipedia_url = entry_or_group.get('wikipedia_url', '')
    
    # NO_WIKIDATA: No Wikidata ID found
    if not wikidata_id or wikidata_id in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
        return self.CATEGORY_NO_WIKIDATA
    
    # DISAMBIG: Disambiguation page
    if wikipedia_url and self._is_disambiguation_page(wikipedia_url):
        return self.CATEGORY_DISAMBIG
    
    # SINGLE: Valid Wikidata ID, not disambiguation
    return self.CATEGORY_SINGLE
```

#### Add Action Selector Methods

```python
def _add_single_entry_action_selector(self, container, entry_id: str) -> None:
    """Add action selector for SINGLE category entries
    
    Options: ACCEPT, TOO BROAD, FALSE
    """
    label = ET.SubElement(container, "label")
    label.text = "Action: "
    
    select = ET.SubElement(container, "select")
    select.attrib["class"] = "entry-action-select"
    select.attrib["data-entry-id"] = entry_id
    select.attrib["data-category"] = self.CATEGORY_SINGLE
    
    # Default option
    default_option = ET.SubElement(select, "option")
    default_option.attrib["value"] = ""
    default_option.text = "-- Select action --"
    
    # ACCEPT option
    accept_option = ET.SubElement(select, "option")
    accept_option.attrib["value"] = "accept"
    accept_option.text = "ACCEPT"
    
    # TOO BROAD option
    too_broad_option = ET.SubElement(select, "option")
    too_broad_option.attrib["value"] = "too_broad"
    too_broad_option.text = "TOO BROAD"
    
    # FALSE option
    false_option = ET.SubElement(select, "option")
    false_option.attrib["value"] = "false"
    false_option.text = "FALSE"

def _add_no_wikidata_action_selector(self, container, entry_id: str) -> None:
    """Add action selector for NO_WIKIDATA category entries
    
    Options: ACCEPT, HIDE
    """
    label = ET.SubElement(container, "label")
    label.text = "Action: "
    
    select = ET.SubElement(container, "select")
    select.attrib["class"] = "entry-action-select"
    select.attrib["data-entry-id"] = entry_id
    select.attrib["data-category"] = self.CATEGORY_NO_WIKIDATA
    
    # Default option
    default_option = ET.SubElement(select, "option")
    default_option.attrib["value"] = ""
    default_option.text = "-- Select action --"
    
    # ACCEPT option
    accept_option = ET.SubElement(select, "option")
    accept_option.attrib["value"] = "accept"
    accept_option.text = "ACCEPT"
    
    # HIDE option
    hide_option = ET.SubElement(select, "option")
    hide_option.attrib["value"] = "hide"
    hide_option.text = "HIDE"

def _add_disambiguation_radio_buttons(self, container, entry_id: str, wikipedia_url: str, wikidata_id: str) -> None:
    """Add radio buttons for DISAMBIG category entries
    
    Shows all possible disambiguation options as radio buttons
    """
    label = ET.SubElement(container, "label")
    label.text = "Select target page: "
    
    # Get disambiguation options
    options = self._get_disambiguation_options(wikipedia_url)
    
    if not options:
        # Fallback: show original URL as option
        options = [(wikipedia_url, wikipedia_url.split('/')[-1].replace('_', ' '))]
    
    # Create radio button group
    radio_group = ET.SubElement(container, "div")
    radio_group.attrib["class"] = "disambiguation-radio-group"
    radio_group.attrib["data-entry-id"] = entry_id
    
    for option_url, option_text in options:
        radio_wrapper = ET.SubElement(radio_group, "div")
        radio_wrapper.attrib["class"] = "radio-option"
        
        radio = ET.SubElement(radio_wrapper, "input")
        radio.attrib["type"] = "radio"
        radio.attrib["name"] = f"disambig_{entry_id}"
        radio.attrib["value"] = option_url
        radio.attrib["data-entry-id"] = entry_id
        
        radio_label = ET.SubElement(radio_wrapper, "label")
        radio_label.text = option_text
        radio_label.attrib["for"] = radio.attrib.get("id", "")
```

#### Update `_add_entry_checkboxes()` Method

```python
def _add_entry_checkboxes(self, entry_div, group: Dict, entry_id: str, wikidata_id: str = '') -> None:
    """Add interactive controls to entry div based on category"""
    # Classify entry
    category = self._classify_entry(group)
    
    # Create controls container
    controls_container = ET.SubElement(entry_div, "div")
    controls_container.attrib["class"] = "entry-controls"
    controls_container.attrib["data-category"] = category
    
    # Add entry div category attribute
    entry_div.attrib["data-category"] = category
    
    # Add controls based on category
    if category == self.CATEGORY_DISAMBIG:
        wikipedia_url = group.get('wikipedia_url', '')
        self._add_disambiguation_radio_buttons(
            controls_container,
            entry_id,
            wikipedia_url,
            wikidata_id
        )
    
    elif category == self.CATEGORY_NO_WIKIDATA:
        self._add_no_wikidata_action_selector(controls_container, entry_id)
    
    elif category == self.CATEGORY_SINGLE:
        self._add_single_entry_action_selector(controls_container, entry_id)
```

### 6. CSS Stylesheet

```css
/* Entry visibility control */
.encyclopedia-entry {
    margin: 10px 0;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

/* Hide entries based on action */
.encyclopedia-entry[data-action="hide"],
.encyclopedia-entry[data-action="too_broad"],
.encyclopedia-entry[data-action="false"] {
    display: none;
}

/* Show accepted entries */
.encyclopedia-entry[data-action="accept"] {
    display: block;
}

/* Entry controls styling */
.entry-controls {
    margin-bottom: 10px;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.entry-controls label {
    font-weight: bold;
    margin-right: 8px;
}

.entry-action-select {
    padding: 4px 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

/* Disambiguation radio buttons */
.disambiguation-radio-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.radio-option {
    display: flex;
    align-items: center;
    gap: 8px;
}

.radio-option input[type="radio"] {
    margin: 0;
}

.radio-option label {
    font-weight: normal;
    cursor: pointer;
}
```

### 7. Metadata Recording

```python
def _record_action(self, entry_id: str, action: str, metadata: Dict = None) -> None:
    """Record user action in metadata"""
    action_record = {
        "action": action,
        "entry_id": entry_id,
        "timestamp": self._get_system_date()
    }
    
    if metadata:
        action_record.update(metadata)
    
    self.metadata[self.METADATA_ACTIONS].append(action_record)
    
    # Update last_edited timestamp
    self._update_last_edited()
```

## Implementation Steps

1. ✅ Update category constants (DISAMBIG, NO_WIKIDATA, SINGLE)
2. ✅ Update `_classify_entry()` to use three categories
3. ✅ Add `_add_single_entry_action_selector()` method
4. ✅ Add `_add_no_wikidata_action_selector()` method
5. ✅ Update `_add_disambiguation_radio_buttons()` method (change from select to radio)
6. ✅ Update `_add_entry_checkboxes()` to use new selectors
7. ✅ Add CSS stylesheet to HTML output
8. ✅ Add JavaScript for client-side interaction (optional, for immediate feedback)
9. ✅ Update metadata recording for new actions

## Benefits

1. **Clear workflow**: Resolve → Normalize → Categorize → Interact
2. **User-friendly**: Listboxes provide clear action choices
3. **Non-destructive**: CSS visibility allows toggling
4. **Trackable**: All actions recorded in metadata
5. **Flexible**: Can add more categories/actions later

## Testing

1. Test with entries in each category (DISAMBIG, NO_WIKIDATA, SINGLE)
2. Verify CSS visibility works correctly
3. Verify metadata recording captures all actions
4. Test disambiguation radio button selection
5. Test action selector changes

