"""
for drawing networks/graphs
"""
import lxml.etree as ET
from amilib.ami_html import HtmlLib




class AmiGraph:
    """
    grahs can be nested?
    """

    def __init__(self):
        self.subgraphs = []

    def create_subgraph(self):
        subgraph = AmiGraph()
        self.subgraphs.append(subgraph)

    @classmethod
    def create_nested_uls_from_nested_divs(cls, html_elem):
        """
        treat all divs and their immediate childresn as nodes with
        edges parent->child
        """
        body = HtmlLib.get_body(html_elem)
        new_body, new_html = HtmlLib.create_html_with_body()
        cls._iterate_children(body, new_body, xpath="div | header | section")
        return new_html

    @classmethod
    def _iterate_children(cls, elem, new_html, xpath):
        children = elem.xpath(xpath)
        if (nchild := len(children)) == 0:
            return None
        ul = ET.SubElement(new_html, "ul")
        p = ET.SubElement(ul, "p")
        p.text = f"{nchild}.."
        for child in children:
            # print(f"{child.tag} => ({child.get('class')})")
            li = ET.SubElement(ul, "li")
            h = child.xpath("h1 | h2 | h3 | h4 | a")
            if h:
                h0 = h[0]
                li.text = h0.text
                if h0.text is None:
                    print(f"no text for {child.tag}@({child.attrib.get('class')})")
                else:
                    print(f" ... {h0.text}")
            else:
                print(f"no title for {child.attrib.get('class')}")
            cls._iterate_children(child, li, xpath)


