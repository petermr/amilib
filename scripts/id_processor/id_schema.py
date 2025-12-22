"""
Schema for cascading ID addition to divs and paragraphs.

This module defines the rules and patterns for adding IDs to HTML elements
in a cascading manner: parent → child → grandchild.

Rules:
1. Section containers (h1-container, h2-container, etc.) get IDs from their headings
2. Paragraphs get IDs based on their parent section container
3. Nested divs get IDs based on their parent container
4. IDs are generated in a cascading manner: parent → child → grandchild
"""

from typing import Dict, List, Optional
import re


class IDSchema:
    """Schema definition for cascading ID addition."""
    
    # Priority order: lower number = higher priority
    SECTION_CONTAINERS = 1
    PARAGRAPHS = 2
    NESTED_DIVS = 3
    
    SCHEMA = {
        'section_containers': {
            'pattern': r'div[contains(@class, "h\d+-container")]',
            'xpath': './/div[contains(@class, "h1-container")] | '
                     './/div[contains(@class, "h2-container")] | '
                     './/div[contains(@class, "h3-container")] | '
                     './/div[contains(@class, "h4-container")]',
            'id_source': 'heading_text',  # Extract from h1, h2, etc.
            'id_format': '{normalized_heading}',
            'priority': SECTION_CONTAINERS,
            'description': 'Section containers get IDs from their headings',
        },
        'siblings_divs': {
            'pattern': r'div[contains(@class, "h\d+-siblings")]',
            'xpath': './/div[contains(@class, "h1-siblings")] | '
                     './/div[contains(@class, "h2-siblings")] | '
                     './/div[contains(@class, "h3-siblings")] | '
                     './/div[contains(@class, "h4-siblings")]',
            'id_source': 'parent_section_id',
            'id_format': 'h{level}-{index}-siblings',
            'priority': SECTION_CONTAINERS,  # Same priority as containers
            'description': 'Siblings divs get IDs based on parent section',
        },
        'paragraphs': {
            'pattern': r'p',
            'xpath': './/p',
            'id_source': 'parent_section_id',
            'id_format': '{section_id}_p{index}',
            'priority': PARAGRAPHS,
            'requires': ['section_containers'],  # Depends on section IDs
            'description': 'Paragraphs get IDs based on parent section container',
        },
        'nested_divs': {
            'pattern': r'div[not(contains(@class, "container")) and not(contains(@class, "siblings"))]',
            'xpath': './/div[not(contains(@class, "h1-container")) and '
                     'not(contains(@class, "h2-container")) and '
                     'not(contains(@class, "h3-container")) and '
                     'not(contains(@class, "h4-container")) and '
                     'not(contains(@class, "h1-siblings")) and '
                     'not(contains(@class, "h2-siblings")) and '
                     'not(contains(@class, "h3-siblings")) and '
                     'not(contains(@class, "h4-siblings"))]',
            'id_source': 'parent_container_id',
            'id_format': '{parent_id}_{type}_{index}',
            'priority': NESTED_DIVS,
            'requires': ['section_containers', 'paragraphs'],
            'description': 'Nested divs get IDs based on parent container',
        },
    }
    
    @classmethod
    def get_schema(cls, element_type: str) -> Optional[Dict]:
        """Get schema definition for an element type."""
        return cls.SCHEMA.get(element_type)
    
    @classmethod
    def get_all_schemas(cls) -> Dict[str, Dict]:
        """Get all schema definitions."""
        return cls.SCHEMA
    
    @classmethod
    def get_schemas_by_priority(cls) -> List[tuple]:
        """Get schemas sorted by priority."""
        schemas = [(name, schema) for name, schema in cls.SCHEMA.items()]
        return sorted(schemas, key=lambda x: x[1]['priority'])
    
    @classmethod
    def normalize_id(cls, text: str) -> str:
        """
        Normalize text to create a valid HTML ID.
        
        Rules:
        - Convert to lowercase
        - Replace spaces and special chars with hyphens
        - Remove leading/trailing hyphens
        - Collapse multiple hyphens
        """
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower().strip()
        
        # Replace spaces and special characters with hyphens
        normalized = re.sub(r'[^\w\s-]', '', normalized)
        normalized = re.sub(r'[\s_]+', '-', normalized)
        
        # Remove leading/trailing hyphens
        normalized = normalized.strip('-')
        
        # Collapse multiple hyphens
        normalized = re.sub(r'-+', '-', normalized)
        
        return normalized
    
    @classmethod
    def extract_heading_text(cls, container_elem) -> Optional[str]:
        """
        Extract heading text from a section container.
        
        Looks for h1, h2, h3, h4 elements within the container.
        """
        from lxml import etree
        
        for level in [1, 2, 3, 4]:
            headings = container_elem.xpath(f'./h{level}')
            if headings:
                heading = headings[0]
                # Get text content, excluding spans with class markers
                text_parts = []
                for node in heading.iter():
                    if node.tag in ['span', 'a']:
                        # Skip special marker spans
                        if node.get('class') and any(marker in node.get('class') 
                                                     for marker in ['arrow-up', 'arrow-down', '_idGenBNMarker']):
                            continue
                    if node.text:
                        text_parts.append(node.text.strip())
                    if node.tail:
                        text_parts.append(node.tail.strip())
                
                text = ' '.join(text_parts).strip()
                # Remove section numbers (e.g., "3.1.2 Introduction" -> "Introduction")
                text = re.sub(r'^\d+([\.\d]+)?\s+', '', text)
                text = re.sub(r'^[A-Z][\.\d]+\s+', '', text)
                return text
        
        return None
    
    @classmethod
    def generate_section_id(cls, container_elem) -> Optional[str]:
        """
        Generate ID for a section container.
        
        Tries multiple strategies:
        1. Use existing ID if present
        2. Extract from heading text
        3. Use container class and index
        """
        # Check if already has ID
        existing_id = container_elem.get('id')
        if existing_id:
            return existing_id
        
        # Extract heading text
        heading_text = cls.extract_heading_text(container_elem)
        if heading_text:
            normalized = cls.normalize_id(heading_text)
            if normalized:
                return normalized
        
        # Fallback: use container class and position
        container_class = container_elem.get('class', '')
        match = re.search(r'h(\d+)-container', container_class)
        if match:
            level = match.group(1)
            parent = container_elem.getparent()
            if parent is not None:
                siblings = parent.xpath(f'.//div[contains(@class, "h{level}-container")]')
                index = siblings.index(container_elem) + 1
                return f'section-{level}-{index}'
        
        return None
    
    @classmethod
    def generate_paragraph_id(cls, para_elem, section_id: str, index: int) -> str:
        """
        Generate ID for a paragraph.
        
        Format: {section_id}_p{index}
        """
        return f"{section_id}_p{index}"
    
    @classmethod
    def generate_nested_div_id(cls, div_elem, parent_id: str, div_type: str, index: int) -> str:
        """
        Generate ID for a nested div.
        
        Format: {parent_id}_{type}_{index}
        """
        return f"{parent_id}_{div_type}_{index}"



