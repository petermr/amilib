"""
Compatibility wrapper for CSSStyle using cssutils.
Maintains existing API while using cssutils internally.
"""

import cssutils
from cssutils.css import CSSStyleDeclaration
import re


class CSSStyleWrapper:
    """
    Compatibility wrapper for CSSStyle using cssutils.
    Maintains the existing CSSStyle API while using cssutils internally.
    """
    
    def __init__(self):
        """Initialize with empty CSSStyleDeclaration."""
        self._style_decl = CSSStyleDeclaration()
        self._original_values = {}  # Store original values to preserve them
    
    def set_attribute(self, name, value):
        """
        Set a CSS property.
        
        Args:
            name (str): CSS property name
            value (str): CSS property value
        """
        if value and len(str(value)) > 0:
            # Store original value to preserve it
            self._original_values[name] = value
            self._style_decl.setProperty(name, value)
    
    def get_attribute(self, name):
        """
        Get a CSS property value.
        
        Args:
            name (str): CSS property name
            
        Returns:
            str: CSS property value or None if not found
        """
        # Try to get original value first, then fall back to cssutils value
        if name in self._original_values:
            return self._original_values[name]
        
        value = self._style_decl.getPropertyValue(name)
        return value if value else None
    
    def set_family(self, family):
        """
        Set font-family property.
        
        Args:
            family (str): Font family name
        """
        if family:
            self.set_attribute('font-family', family)
    
    def set_font_weight(self, weight):
        """
        Set font-weight property with normalization.
        
        Args:
            weight (str): Font weight value
        """
        weight = weight.lower()
        if weight:
            if weight in ['normal', 'bold', 'light']:
                self.set_attribute('font-weight', weight)
    
    def set_font_style(self, style):
        """
        Set font-style property with normalization.
        
        Args:
            style (str): Font style value
        """
        if style:
            if style.lower() in ['normal', 'italic']:
                self.set_attribute('font-style', style.lower())
    
    def remove(self, name):
        """
        Remove CSS property(ies).
        
        Args:
            name (str or list): CSS property name(s) to remove
        """
        if isinstance(name, list):
            for n in name:
                self.remove(n)
        else:
            self._style_decl.removeProperty(name)
            # Also remove from original values
            if name in self._original_values:
                del self._original_values[name]
    
    def get_css_value(self, wrap_with_curly=False):
        """
        Get CSS string representation.
        Returns format with spaces after colons (like current implementation).
        
        Args:
            wrap_with_curly (bool): Whether to wrap in curly braces
            
        Returns:
            str: CSS string
        """
        # Get cssutils output and normalize it
        css_text = self._style_decl.cssText
        
        # Normalize the format to match current implementation get_css_value()
        normalized_css = self._normalize_css_format_with_spaces(css_text)
        
        if wrap_with_curly and normalized_css:
            return "{" + normalized_css + "}"
        return normalized_css
    
    def _normalize_css_format_with_spaces(self, css_text):
        """
        Normalize cssutils CSS format to match current implementation get_css_value().
        Returns format with spaces after colons.
        
        Args:
            css_text (str): Raw cssutils CSS text
            
        Returns:
            str: Normalized CSS text with spaces
        """
        if not css_text:
            return ""
        
        # Split by newlines and process each property
        lines = css_text.split('\n')
        properties = []
        
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # Extract property name and value
                parts = line.split(':', 1)
                if len(parts) == 2:
                    prop_name = parts[0].strip()
                    prop_value = parts[1].strip()
                    
                    # Remove trailing semicolon if present
                    if prop_value.endswith(';'):
                        prop_value = prop_value[:-1]
                    
                    # Use original value if available
                    if prop_name in self._original_values:
                        prop_value = self._original_values[prop_name]
                    
                    # Format with spaces after colon (like get_css_value())
                    properties.append(f"{prop_name}: {prop_value}")
        
        # Join with semicolons and add trailing semicolon
        if properties:
            return "; ".join(properties) + ";"
        return ""
    
    def _normalize_css_format_without_spaces(self, css_text):
        """
        Normalize cssutils CSS format to match current implementation str().
        Returns format without spaces after colons.
        
        Args:
            css_text (str): Raw cssutils CSS text
            
        Returns:
            str: Normalized CSS text without spaces
        """
        if not css_text:
            return ""
        
        # Split by newlines and process each property
        lines = css_text.split('\n')
        properties = []
        
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # Extract property name and value
                parts = line.split(':', 1)
                if len(parts) == 2:
                    prop_name = parts[0].strip()
                    prop_value = parts[1].strip()
                    
                    # Remove trailing semicolon if present
                    if prop_value.endswith(';'):
                        prop_value = prop_value[:-1]
                    
                    # Use original value if available
                    if prop_name in self._original_values:
                        prop_value = self._original_values[prop_name]
                    
                    # Format without spaces after colon (like str())
                    properties.append(f"{prop_name}:{prop_value}")
        
        # Join with semicolons and spaces (like current CSSStyle)
        if properties:
            return "; ".join(properties) + ";"
        return ""
    
    def apply_to(self, elem):
        """
        Apply styles to HTML element.
        
        Args:
            elem: lxml HTML element
        """
        css_str = self.get_css_value()
        elem.attrib['style'] = css_str
    
    def __eq__(self, other):
        """
        Compare with another CSSStyleWrapper.
        
        Args:
            other: Another CSSStyleWrapper instance
            
        Returns:
            bool: True if equal
        """
        if isinstance(other, CSSStyleWrapper):
            return self.get_css_value() == other.get_css_value()
        return False
    
    def __str__(self):
        """
        String representation.
        Returns format with spaces after colons (like current implementation str()).
        
        Returns:
            str: CSS string
        """
        css_text = self._style_decl.cssText
        return self._normalize_css_format_with_spaces(css_text)
    
    def __repr__(self):
        """
        Repr representation.
        
        Returns:
            str: Repr string
        """
        return f"CSSStyleWrapper({self.get_css_value()})"
    
    @classmethod
    def create_css_style_from_css_string(cls, css_string, remove_prefix=True):
        """
        Create CSSStyleWrapper from CSS string.
        Handles None and empty strings by returning empty CSSStyleWrapper (matching current CSSStyle behavior).
        
        Args:
            css_string (str): CSS string to parse
            remove_prefix (bool): Whether to remove PDF prefixes (not implemented in wrapper)
            
        Returns:
            CSSStyleWrapper: New instance (empty for empty/None strings)
        """
        wrapper = cls()
        
        if css_string:
            try:
                wrapper._style_decl = CSSStyleDeclaration(cssText=css_string)
                
                # Parse and store original values to preserve them
                if css_string.strip():
                    # Simple parsing to extract original values
                    properties = css_string.split(';')
                    for prop in properties:
                        prop = prop.strip()
                        if ':' in prop:
                            name, value = prop.split(':', 1)
                            name = name.strip()
                            value = value.strip()
                            wrapper._original_values[name] = value
                
            except Exception:
                # If parsing fails, return empty wrapper (matching current behavior)
                pass
        
        return wrapper
    
    @classmethod
    def create_css_style_from_attribute_of_body_element(cls, elem):
        """
        Create CSSStyleWrapper from HTML element's style attribute.
        
        Args:
            elem: lxml HTML element
            
        Returns:
            CSSStyleWrapper: New instance or None if no style attribute
        """
        if elem is None:
            return None
        
        style_attr = elem.get('style')
        if style_attr:
            return cls.create_css_style_from_css_string(style_attr)
        return cls()


# Alias for compatibility
CSSStyle = CSSStyleWrapper 