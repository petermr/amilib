"""
Tests for CSSStyleWrapper compatibility layer.
Ensures the wrapper maintains existing CSSStyle API.
"""

import pytest
import sys
import os

# Add amilib to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from test.css_replacement.css_style_wrapper import CSSStyleWrapper, CSSStyle


class TestCSSStyleWrapper:
    """Test CSSStyleWrapper compatibility layer."""

    def test_basic_property_setting(self):
        """Test setting individual CSS properties."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        css_style.set_attribute('font-size', '12px')
        
        assert css_style.get_css_value() == "color: red; font-size: 12px;"

    def test_basic_property_getting(self):
        """Test getting individual CSS properties."""
        css_style = CSSStyleWrapper.create_css_style_from_css_string("color: blue; font-size: 14px;")
        
        assert css_style.get_attribute('color') == "blue"
        assert css_style.get_attribute('font-size') == "14px"

    def test_simple_css_parsing(self):
        """Test parsing simple CSS strings."""
        test_css = "color: red; font-size: 12px; font-weight: bold;"
        css_style = CSSStyleWrapper.create_css_style_from_css_string(test_css)
        
        assert css_style.get_attribute('color') == "red"
        assert css_style.get_attribute('font-size') == "12px"
        assert css_style.get_attribute('font-weight') == "bold"

    def test_complex_css_parsing(self):
        """Test parsing complex CSS strings."""
        complex_css = "font-family: Arial, sans-serif; font-size: 14px; color: #ff0000; border: 1px solid black;"
        css_style = CSSStyleWrapper.create_css_style_from_css_string(complex_css)
        
        assert css_style.get_attribute('font-family') == "Arial, sans-serif"
        assert css_style.get_attribute('font-size') == "14px"
        assert css_style.get_attribute('color') == "#ff0000"
        assert css_style.get_attribute('border') == "1px solid black"

    def test_css_generation(self):
        """Test CSS string generation."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        css_style.set_attribute('font-size', '12px')
        
        expected = "color: red; font-size: 12px;"
        assert css_style.get_css_value() == expected

    def test_css_with_curly_braces(self):
        """Test CSS generation with curly braces."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        
        expected_with_braces = "{color: red;}"
        assert css_style.get_css_value(wrap_with_curly=True) == expected_with_braces

    def test_font_weight_setting(self):
        """Test font weight normalization."""
        css_style = CSSStyleWrapper()
        css_style.set_font_weight('bold')
        assert css_style.get_attribute('font-weight') == 'bold'
        
        css_style.set_font_weight('normal')
        assert css_style.get_attribute('font-weight') == 'normal'

    def test_font_style_setting(self):
        """Test font style normalization."""
        css_style = CSSStyleWrapper()
        css_style.set_font_style('italic')
        assert css_style.get_attribute('font-style') == 'italic'
        
        css_style.set_font_style('normal')
        assert css_style.get_attribute('font-style') == 'normal'

    def test_font_family_setting(self):
        """Test font family setting."""
        css_style = CSSStyleWrapper()
        css_style.set_family('Arial')
        assert css_style.get_attribute('font-family') == 'Arial'

    def test_empty_css_handling(self):
        """Test handling of empty CSS strings."""
        css_style = CSSStyleWrapper.create_css_style_from_css_string("")
        assert css_style.get_css_value() == ""

    def test_none_css_handling(self):
        """Test handling of None CSS strings."""
        css_style = CSSStyleWrapper.create_css_style_from_css_string(None)
        assert css_style.get_css_value() == ""

    def test_special_characters(self):
        """Test CSS with special characters."""
        css_with_quotes = "font-family: 'Times New Roman', serif; content: \"Hello World\";"
        css_style = CSSStyleWrapper.create_css_style_from_css_string(css_with_quotes)
        
        assert css_style.get_attribute('font-family') == "'Times New Roman', serif"
        assert css_style.get_attribute('content') == '"Hello World"'

    def test_multiple_properties(self):
        """Test setting multiple properties."""
        css_style = CSSStyleWrapper()
        properties = {
            'color': 'red',
            'background-color': 'white',
            'margin': '10px',
            'padding': '5px',
            'border': '1px solid black'
        }
        
        for name, value in properties.items():
            css_style.set_attribute(name, value)
        
        for name, value in properties.items():
            assert css_style.get_attribute(name) == value

    def test_property_removal(self):
        """Test removing CSS properties."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        css_style.set_attribute('font-size', '12px')
        
        css_style.remove('color')
        assert css_style.get_attribute('color') is None
        assert css_style.get_attribute('font-size') == '12px'

    def test_multiple_property_removal(self):
        """Test removing multiple CSS properties."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        css_style.set_attribute('font-size', '12px')
        css_style.set_attribute('font-weight', 'bold')
        
        css_style.remove(['color', 'font-size'])
        assert css_style.get_attribute('color') is None
        assert css_style.get_attribute('font-size') is None
        assert css_style.get_attribute('font-weight') == 'bold'

    def test_equality_comparison(self):
        """Test CSSStyleWrapper equality comparison."""
        css_style1 = CSSStyleWrapper()
        css_style1.set_attribute('color', 'red')
        css_style1.set_attribute('font-size', '12px')
        
        css_style2 = CSSStyleWrapper()
        css_style2.set_attribute('color', 'red')
        css_style2.set_attribute('font-size', '12px')
        
        assert css_style1 == css_style2
        
        css_style3 = CSSStyleWrapper()
        css_style3.set_attribute('color', 'blue')
        css_style3.set_attribute('font-size', '12px')
        
        assert css_style1 != css_style3

    def test_string_representation(self):
        """Test string representation of CSSStyleWrapper."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        css_style.set_attribute('font-size', '12px')
        
        expected_str = "color: red; font-size: 12px;"
        assert str(css_style) == expected_str

    def test_repr_representation(self):
        """Test repr representation of CSSStyleWrapper."""
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        
        # repr should show the CSS text
        assert "color: red" in repr(css_style)

    def test_css_alias(self):
        """Test that CSSStyle alias works."""
        css_style = CSSStyle()
        css_style.set_attribute('color', 'red')
        assert css_style.get_css_value() == "color: red;"

    def test_html_element_integration(self):
        """Test applying styles to HTML elements."""
        from lxml import etree
        
        html_element = etree.Element('div')
        css_style = CSSStyleWrapper()
        css_style.set_attribute('color', 'red')
        css_style.apply_to(html_element)
        
        assert html_element.get('style') == "color: red;"

    def test_create_from_element(self):
        """Test creating CSSStyleWrapper from HTML element."""
        from lxml import etree
        
        html_element = etree.Element('div')
        html_element.set('style', 'color: red; font-size: 12px;')
        
        css_style = CSSStyleWrapper.create_css_style_from_attribute_of_body_element(html_element)
        assert css_style.get_attribute('color') == 'red'
        assert css_style.get_attribute('font-size') == '12px'

    def test_create_from_element_no_style(self):
        """Test creating CSSStyleWrapper from HTML element without style."""
        from lxml import etree
        
        html_element = etree.Element('div')
        
        css_style = CSSStyleWrapper.create_css_style_from_attribute_of_body_element(html_element)
        assert css_style.get_css_value() == ""

    def test_create_from_none_element(self):
        """Test creating CSSStyleWrapper from None element."""
        css_style = CSSStyleWrapper.create_css_style_from_attribute_of_body_element(None)
        assert css_style is None


if __name__ == "__main__":
    pytest.main([__file__]) 