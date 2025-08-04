"""
Comparison tests between current CSSStyle and CSSStyleWrapper.
Ensures both implementations behave identically.
"""

import pytest
import sys
import os

# Note: amilib should be installed with 'pip install -e .' for tests to work properly

from amilib.ami_html import CSSStyle as CurrentCSSStyle
from test.css_replacement.css_style_wrapper import CSSStyleWrapper


class TestCSSComparison:
    """Compare current CSSStyle with CSSStyleWrapper."""

    def test_basic_property_setting_comparison(self):
        """Compare basic property setting between implementations."""
        current_style = CurrentCSSStyle()
        wrapper_style = CSSStyleWrapper()
        
        # Set same properties
        current_style.set_attribute('color', 'red')
        current_style.set_attribute('font-size', '12px')
        
        wrapper_style.set_attribute('color', 'red')
        wrapper_style.set_attribute('font-size', '12px')
        
        # Compare outputs
        assert current_style.get_css_value() == wrapper_style.get_css_value()

    def test_basic_property_getting_comparison(self):
        """Compare basic property getting between implementations."""
        test_css = "color: blue; font-size: 14px;"
        
        current_style = CurrentCSSStyle.create_css_style_from_css_string(test_css)
        wrapper_style = CSSStyleWrapper.create_css_style_from_css_string(test_css)
        
        assert current_style.get_attribute('color') == wrapper_style.get_attribute('color')
        assert current_style.get_attribute('font-size') == wrapper_style.get_attribute('font-size')

    def test_css_parsing_comparison(self):
        """Compare CSS parsing between implementations."""
        test_css = "color: red; font-size: 12px; font-weight: bold; font-family: Arial, sans-serif;"
        
        current_style = CurrentCSSStyle.create_css_style_from_css_string(test_css)
        wrapper_style = CSSStyleWrapper.create_css_style_from_css_string(test_css)
        
        # Compare all properties
        properties = ['color', 'font-size', 'font-weight', 'font-family']
        for prop in properties:
            current_val = current_style.get_attribute(prop)
            wrapper_val = wrapper_style.get_attribute(prop)
            assert current_val == wrapper_val, f"Property {prop} differs: {current_val} vs {wrapper_val}"

    def test_css_generation_comparison(self):
        """Compare CSS generation between implementations."""
        current_style = CurrentCSSStyle()
        wrapper_style = CSSStyleWrapper()
        
        # Set same properties
        properties = {
            'color': 'red',
            'background-color': 'white',
            'margin': '10px',
            'padding': '5px',
            'border': '1px solid black'
        }
        
        for name, value in properties.items():
            current_style.set_attribute(name, value)
            wrapper_style.set_attribute(name, value)
        
        # Compare generated CSS
        current_css = current_style.get_css_value()
        wrapper_css = wrapper_style.get_css_value()
        
        # Note: cssutils might format differently, so we check content rather than exact string
        for name, value in properties.items():
            assert f"{name}: {value}" in current_css
            assert f"{name}: {value}" in wrapper_css

    def test_font_methods_comparison(self):
        """Compare font-specific methods between implementations."""
        current_style = CurrentCSSStyle()
        wrapper_style = CSSStyleWrapper()
        
        # Test font weight
        current_style.set_font_weight('bold')
        wrapper_style.set_font_weight('bold')
        assert current_style.get_attribute('font-weight') == wrapper_style.get_attribute('font-weight')
        
        # Test font style
        current_style.set_font_style('italic')
        wrapper_style.set_font_style('italic')
        assert current_style.get_attribute('font-style') == wrapper_style.get_attribute('font-style')
        
        # Test font family
        current_style.set_family('Arial')
        wrapper_style.set_family('Arial')
        assert current_style.get_attribute('font-family') == wrapper_style.get_attribute('font-family')

    def test_property_removal_comparison(self):
        """Compare property removal between implementations."""
        current_style = CurrentCSSStyle()
        wrapper_style = CSSStyleWrapper()
        
        # Set same properties
        current_style.set_attribute('color', 'red')
        current_style.set_attribute('font-size', '12px')
        current_style.set_attribute('font-weight', 'bold')
        
        wrapper_style.set_attribute('color', 'red')
        wrapper_style.set_attribute('font-size', '12px')
        wrapper_style.set_attribute('font-weight', 'bold')
        
        # Remove same properties
        current_style.remove('color')
        wrapper_style.remove('color')
        
        assert current_style.get_attribute('color') == wrapper_style.get_attribute('color')
        assert current_style.get_attribute('font-size') == wrapper_style.get_attribute('font-size')
        assert current_style.get_attribute('font-weight') == wrapper_style.get_attribute('font-weight')

    def test_multiple_property_removal_comparison(self):
        """Compare multiple property removal between implementations."""
        current_style = CurrentCSSStyle()
        wrapper_style = CSSStyleWrapper()
        
        # Set same properties
        current_style.set_attribute('color', 'red')
        current_style.set_attribute('font-size', '12px')
        current_style.set_attribute('font-weight', 'bold')
        
        wrapper_style.set_attribute('color', 'red')
        wrapper_style.set_attribute('font-size', '12px')
        wrapper_style.set_attribute('font-weight', 'bold')
        
        # Remove multiple properties
        current_style.remove(['color', 'font-size'])
        wrapper_style.remove(['color', 'font-size'])
        
        assert current_style.get_attribute('color') == wrapper_style.get_attribute('color')
        assert current_style.get_attribute('font-size') == wrapper_style.get_attribute('font-size')
        assert current_style.get_attribute('font-weight') == wrapper_style.get_attribute('font-weight')

    def test_curly_braces_comparison(self):
        """Compare curly braces generation between implementations."""
        current_style = CurrentCSSStyle()
        wrapper_style = CSSStyleWrapper()
        
        current_style.set_attribute('color', 'red')
        wrapper_style.set_attribute('color', 'red')
        
        current_with_braces = current_style.get_css_value(wrap_with_curly=True)
        wrapper_with_braces = wrapper_style.get_css_value(wrap_with_curly=True)
        
        assert current_with_braces == wrapper_with_braces

    def test_empty_css_comparison(self):
        """Compare empty CSS handling between implementations."""
        current_style = CurrentCSSStyle.create_css_style_from_css_string("")
        wrapper_style = CSSStyleWrapper.create_css_style_from_css_string("")
        
        assert current_style.get_css_value() == wrapper_style.get_css_value()

    def test_none_css_comparison(self):
        """Compare None CSS handling between implementations."""
        current_style = CurrentCSSStyle.create_css_style_from_css_string(None)
        wrapper_style = CSSStyleWrapper.create_css_style_from_css_string(None)
        
        assert current_style.get_css_value() == wrapper_style.get_css_value()

    def test_special_characters_comparison(self):
        """Compare special characters handling between implementations."""
        css_with_quotes = "font-family: 'Times New Roman', serif; content: \"Hello World\";"
        
        current_style = CurrentCSSStyle.create_css_style_from_css_string(css_with_quotes)
        wrapper_style = CSSStyleWrapper.create_css_style_from_css_string(css_with_quotes)
        
        assert current_style.get_attribute('font-family') == wrapper_style.get_attribute('font-family')
        assert current_style.get_attribute('content') == wrapper_style.get_attribute('content')

    def test_equality_comparison(self):
        """Compare equality behavior between implementations."""
        current_style1 = CurrentCSSStyle()
        current_style1.set_attribute('color', 'red')
        current_style1.set_attribute('font-size', '12px')
        
        current_style2 = CurrentCSSStyle()
        current_style2.set_attribute('color', 'red')
        current_style2.set_attribute('font-size', '12px')
        
        wrapper_style1 = CSSStyleWrapper()
        wrapper_style1.set_attribute('color', 'red')
        wrapper_style1.set_attribute('font-size', '12px')
        
        wrapper_style2 = CSSStyleWrapper()
        wrapper_style2.set_attribute('color', 'red')
        wrapper_style2.set_attribute('font-size', '12px')
        
        # Both implementations should show equality for same properties
        assert current_style1 == current_style2
        assert wrapper_style1 == wrapper_style2

    def test_string_representation_comparison(self):
        """Compare string representation between implementations."""
        current_style = CurrentCSSStyle()
        current_style.set_attribute('color', 'red')
        current_style.set_attribute('font-size', '12px')
        
        wrapper_style = CSSStyleWrapper()
        wrapper_style.set_attribute('color', 'red')
        wrapper_style.set_attribute('font-size', '12px')
        
        # String representations should be equivalent
        current_str = str(current_style)
        wrapper_str = str(wrapper_style)
        
        # Check that both contain the same properties
        assert "color: red" in current_str
        assert "color: red" in wrapper_str
        assert "font-size: 12px" in current_str
        assert "font-size: 12px" in wrapper_str


if __name__ == "__main__":
    pytest.main([__file__]) 