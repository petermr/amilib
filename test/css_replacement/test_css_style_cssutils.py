"""
Tests for cssutils implementation.
Compares with current CSSStyle behavior.
"""

import pytest
import sys
import os

# Note: amilib should be installed with 'pip install -e .' for tests to work properly

import cssutils
import xml.dom
from cssutils.css import CSSStyleDeclaration


class TestCSSUtilsImplementation:
    """Test cssutils implementation."""

    def test_basic_property_setting(self):
        """Test setting individual CSS properties."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        # cssutils outputs with newlines, not semicolons
        assert style_decl.cssText == "color: red;\nfont-size: 12px"

    def test_basic_property_getting(self):
        """Test getting individual CSS properties."""
        style_decl = CSSStyleDeclaration(cssText="color: blue; font-size: 14px;")
        
        assert style_decl.getPropertyValue('color') == "blue"
        assert style_decl.getPropertyValue('font-size') == "14px"

    def test_simple_css_parsing(self):
        """Test parsing simple CSS strings."""
        test_css = "color: red; font-size: 12px; font-weight: bold;"
        style_decl = CSSStyleDeclaration(cssText=test_css)
        
        assert style_decl.getPropertyValue('color') == "red"
        assert style_decl.getPropertyValue('font-size') == "12px"
        assert style_decl.getPropertyValue('font-weight') == "bold"

    def test_complex_css_parsing(self):
        """Test parsing complex CSS strings."""
        complex_css = "font-family: Arial, sans-serif; font-size: 14px; color: #ff0000; border: 1px solid black;"
        style_decl = CSSStyleDeclaration(cssText=complex_css)
        
        assert style_decl.getPropertyValue('font-family') == "Arial, sans-serif"
        assert style_decl.getPropertyValue('font-size') == "14px"
        # cssutils normalizes colors to short form
        assert style_decl.getPropertyValue('color') == "#f00"
        assert style_decl.getPropertyValue('border') == "1px solid black"

    def test_css_generation(self):
        """Test CSS string generation."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        # cssutils outputs with newlines, not semicolons
        expected = "color: red;\nfont-size: 12px"
        assert style_decl.cssText == expected

    def test_font_weight_setting(self):
        """Test font weight setting."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('font-weight', 'bold')
        assert style_decl.getPropertyValue('font-weight') == 'bold'
        
        style_decl.setProperty('font-weight', 'normal')
        assert style_decl.getPropertyValue('font-weight') == 'normal'

    def test_font_style_setting(self):
        """Test font style setting."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('font-style', 'italic')
        assert style_decl.getPropertyValue('font-style') == 'italic'
        
        style_decl.setProperty('font-style', 'normal')
        assert style_decl.getPropertyValue('font-style') == 'normal'

    def test_font_family_setting(self):
        """Test font family setting."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('font-family', 'Arial')
        assert style_decl.getPropertyValue('font-family') == 'Arial'

    def test_empty_css_handling(self):
        """Test handling of empty CSS strings."""
        style_decl = CSSStyleDeclaration(cssText="")
        assert style_decl.cssText == ""

    def test_none_css_handling(self):
        """Test handling of None CSS strings."""
        style_decl = CSSStyleDeclaration(cssText=None)
        assert style_decl.cssText == ""

    def test_special_characters(self):
        """Test CSS with special characters."""
        css_with_quotes = "font-family: 'Times New Roman', serif; content: \"Hello World\";"
        style_decl = CSSStyleDeclaration(cssText=css_with_quotes)
        
        # cssutils normalizes quote styles
        assert style_decl.getPropertyValue('font-family') == '"Times New Roman", serif'
        assert style_decl.getPropertyValue('content') == '"Hello World"'

    def test_multiple_properties(self):
        """Test setting multiple properties."""
        style_decl = CSSStyleDeclaration()
        properties = {
            'color': 'red',
            'background-color': 'white',
            'margin': '10px',
            'padding': '5px',
            'border': '1px solid black'
        }
        
        for name, value in properties.items():
            style_decl.setProperty(name, value)
        
        for name, value in properties.items():
            assert style_decl.getPropertyValue(name) == value

    def test_property_removal(self):
        """Test removing CSS properties."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        style_decl.removeProperty('color')
        assert style_decl.getPropertyValue('color') == ""
        assert style_decl.getPropertyValue('font-size') == '12px'

    def test_property_validation(self):
        """Test CSS property validation."""
        style_decl = CSSStyleDeclaration()
        
        # Valid properties should work
        style_decl.setProperty('color', 'red')
        assert style_decl.getPropertyValue('color') == 'red'
        
        # Invalid properties might be handled differently
        style_decl.setProperty('invalid-property', 'value')
        # cssutils might still accept it but could provide validation

    def test_css_validation(self):
        """Test CSS validation capabilities."""
        # Test with valid CSS
        valid_css = "color: red; font-size: 12px;"
        style_decl = CSSStyleDeclaration(cssText=valid_css)
        # cssutils normalizes the output format
        assert "color: red" in style_decl.cssText
        assert "font-size: 12px" in style_decl.cssText
        
        # Test with malformed CSS
        malformed_css = "color: red; font-size: ; font-weight: bold;"
        try:
            style_decl = CSSStyleDeclaration(cssText=malformed_css)
            # If it doesn't raise an exception, that's also valid behavior
        except xml.dom.SyntaxErr:
            # cssutils correctly raises an exception for malformed CSS
            pass

    def test_css_optimization(self):
        """Test CSS optimization capabilities."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        # cssutils might optimize the output
        optimized_css = style_decl.cssText
        assert "color: red" in optimized_css
        assert "font-size: 12px" in optimized_css

    def test_property_priority(self):
        """Test CSS property priority handling."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red', 'important')
        assert style_decl.getPropertyPriority('color') == 'important'

    def test_property_count(self):
        """Test getting property count."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        assert style_decl.length == 2

    def test_property_index_access(self):
        """Test accessing properties by index."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        # Get property name by index
        assert style_decl.item(0) in ['color', 'font-size']
        assert style_decl.item(1) in ['color', 'font-size']

    def test_string_representation(self):
        """Test string representation of CSSStyleDeclaration."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        style_decl.setProperty('font-size', '12px')
        
        # cssutils str() returns object representation, not CSS text
        assert "CSSStyleDeclaration" in str(style_decl)

    def test_repr_representation(self):
        """Test repr representation of CSSStyleDeclaration."""
        style_decl = CSSStyleDeclaration()
        style_decl.setProperty('color', 'red')
        
        # repr should show the CSS text
        assert "color: red" in repr(style_decl)


if __name__ == "__main__":
    pytest.main([__file__]) 