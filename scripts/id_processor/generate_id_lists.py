#!/usr/bin/env python3
"""
Generate ID lists and paragraph lists from HTML with IDs.

Creates:
- id_list.html: List of all IDs with links
- para_list.html: List of all paragraphs with IDs
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lxml import html, etree
from lxml.html import HTMLParser


def generate_id_list(html_file: Path, id_list_file: Path):
    """Generate list of all IDs."""
    parser = HTMLParser(recover=True)
    tree = html.parse(str(html_file), parser=parser)
    root = tree.getroot()
    
    # Find all elements with IDs
    elements_with_ids = root.xpath('.//*[@id]')
    ids = [elem.get('id') for elem in elements_with_ids]
    
    # Create HTML document
    id_html = etree.Element('html')
    head = etree.SubElement(id_html, 'head')
    title = etree.SubElement(head, 'title')
    title.text = 'ID List'
    body = etree.SubElement(id_html, 'body')
    h1 = etree.SubElement(body, 'h1')
    h1.text = f'ID List ({len(ids)} IDs)'
    ul = etree.SubElement(body, 'ul')
    
    for elem_id in sorted(ids):
        li = etree.SubElement(ul, 'li')
        a = etree.SubElement(li, 'a')
        a.set('href', f'./html_with_all_ids.html#{elem_id}')
        a.text = elem_id
    
    # Write file
    id_list_file.parent.mkdir(parents=True, exist_ok=True)
    tree = etree.ElementTree(id_html)
    tree.write(str(id_list_file), pretty_print=True, encoding='utf-8')
    print(f"ID list written: {id_list_file} ({len(ids)} IDs)")


def generate_para_list(html_file: Path, para_list_file: Path):
    """Generate list of all paragraphs with IDs."""
    parser = HTMLParser(recover=True)
    tree = html.parse(str(html_file), parser=parser)
    root = tree.getroot()
    
    # Find all paragraphs with IDs
    paras_with_ids = root.xpath('.//p[@id]')
    
    # Create HTML document
    para_html = etree.Element('html')
    head = etree.SubElement(para_html, 'head')
    title = etree.SubElement(head, 'title')
    title.text = 'Paragraph List'
    body = etree.SubElement(para_html, 'body')
    h1 = etree.SubElement(body, 'h1')
    h1.text = f'Paragraph List ({len(paras_with_ids)} paragraphs)'
    ul = etree.SubElement(body, 'ul')
    
    for para in paras_with_ids:
        para_id = para.get('id')
        li = etree.SubElement(ul, 'li')
        h2 = etree.SubElement(li, 'h2')
        a = etree.SubElement(h2, 'a')
        a.set('href', f'./html_with_all_ids.html#{para_id}')
        a.text = para_id
        
        # Copy paragraph content
        para_copy = etree.SubElement(li, 'p')
        para_copy.text = para.text
        for child in para:
            para_copy.append(child)
    
    # Write file
    para_list_file.parent.mkdir(parents=True, exist_ok=True)
    tree = etree.ElementTree(para_html)
    tree.write(str(para_list_file), pretty_print=True, encoding='utf-8')
    print(f"Paragraph list written: {para_list_file} ({len(paras_with_ids)} paragraphs)")


def main():
    parser = argparse.ArgumentParser(description='Generate ID lists')
    parser.add_argument('--input', type=Path, required=True, help='Input HTML file with IDs')
    parser.add_argument('--id-list', type=Path, required=True, help='Output ID list HTML file')
    parser.add_argument('--para-list', type=Path, required=True, help='Output paragraph list HTML file')
    
    args = parser.parse_args()
    
    generate_id_list(args.input, args.id_list)
    generate_para_list(args.input, args.para_list)
    
    print("Done!")


if __name__ == '__main__':
    main()



