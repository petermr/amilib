import os
from pathlib import Path

import lxml.etree as ET

from amilib.ami_html import HtmlStyle
from amilib.xml_lib import XmlLib, HtmlLib

from test.test_all import AmiAnyTest
# from test.test_wikimedia import WikidataTest


class Xml0Test(AmiAnyTest):

    def test_is_integer(self):
        span = ET.Element("span")
        span.text = "12"
        assert XmlLib.is_integer(span), f"an integer {span}"

        span.text = "+12"
        assert XmlLib.is_integer(span), f"an integer {span}"

        span.text = "-12"
        assert XmlLib.is_integer(span), f"integer {span.text}"

        span.text = "b12"
        assert not XmlLib.is_integer(span), f"not an integer {span.text}"

        span.text = "-12.0"
        assert not XmlLib.is_integer(span), f"not an integer {span.text}"

    def test_split_span_by_regex(self):
        """
        takes simple HTML element:
        div
            span
        and splits the span with a regex, annotating the results
        adds classes
        tackles most of functionality

        """
        div = ET.Element("div")
        div.attrib["pos"] = "top"
        span = ET.SubElement(div, "span")
        span.attrib["biff"] = "boff"
        span.text = "This is foo and bar and more foo marked and plugh and foo not marked"
        regex = "fo+"  # searches for strings of form fo, foo, for etc
        ids = ["id0", "id1", "id2"]  # ids to give new spans
        clazz = ["class0", ":class1", "class2"]  # classes for result
        XmlLib.split_span_by_regex(span, regex, ids=ids, clazz=clazz, href="https://google.com")

        file = os.path.expanduser('~') + "/junk.html"
        print(file)
        html = HtmlLib.create_html_with_empty_head_body()
        styles = [
            (".class0", [("color", "red;")]),
            (".class1", [("background", "#ccccff;")]),
            (".class2", [("color", "#00cc00;")]),
        ]

        HtmlStyle.add_head_styles_orig(html, styles)
        HtmlLib.get_body(html).append(div)
        HtmlLib.write_html_file(html, file, debug=True)

class XmlTest:
    XSLT_FILE = os.path.join(Path(__file__).parent, "jats2html.xsl")

    @classmethod
    def test_replace_nodes_with_text(cls):
        data = '''<everything>
    <m>Some text before <r/></m>
    <m><r/> and some text after.</m>
    <m><r/></m>
    <m>Text before <r/> and after</m>
    <m><b/> Text after a sibling <r/> Text before a sibling<b/></m>
    </everything>
    '''
        result = XmlLib.replace_nodes_with_text(data, "//r", "DELETED")
        print(ET.tostring(result))

    @classmethod
    def test_replace_nodenames(cls):
        data = '''<p>essential oil extracted from
 <italic>T. bovei</italic> was comprised ... on the
 <italic>T. bovei</italic> activities ... activity.
</p>'''

        doc = ET.fromstring(data)
        italics = doc.findall("italic")
        for node in italics:
            node.tag = "i"
        print(ET.tostring(doc))

    """transform = etree.XSLT(xslt_tree)
>>> result = transform(doc, a="'A'")
>>> bytes(result)
b'<?xml version="1.0"?>\n<foo>A</foo>\n'
    """

    @classmethod
    def test_xslt_italic(cls):
        data = '''<p>essential oil extracted from
 <italic>T. bovei</italic> was comprised ... on the
 <italic>T. bovei</italic> activities ... activity.
</p>'''
        print("italic", XmlLib.xslt_transform_tostring(data, XmlTest.XSLT_FILE))

    @classmethod
    def test_xslt_copy(cls):
        data = """<ack>
 <title>Acknowledgements</title>
 <p>The authors acknowledge the assistance of the technicians Mohamad Arar and Linda Esa and for An-Najah National University and Birzeit University for their support.</p>
 <sec id="FPar1">
  <title>Funding</title>
  <p>None.</p>
 </sec>
 <boo>foo</boo>
 <sec id="FPar2">
  <title>Availability of data and materials</title>
  <p>Data are all contained within the article.</p>
 </sec>
</ack>
"""
        print("copy", XmlLib.xslt_transform_tostring(data, XmlTest.XSLT_FILE))

    @classmethod
    def test_jats2html(cls):
        print("test_jats2html")
        data = '''<everything>
<m>Some text before <r/></m>
<m><r/> and some text after.</m>
<m><r/></m>
<m>Text before <r/> and after</m>
<m><b/> Text after a sibling <r/> Text before a sibling<b/></m>
</everything>
'''
        result = XmlLib.replace_nodes_with_text(data, "//r", "DELETED")
        print(ET.tostring(result))


if __name__ == "__main__":
    print(f"running {__name__} main")

    config_test = False
    wiki_test = False
    xml_test = False

    # NYI
    # if config_test:
    #     ConfigTests.tests()
    if wiki_test:
        # TODO move to Wikimedia
        WikimediaTest.test_sparql_wrapper()
    if xml_test:
        XmlTest.test_replace_nodes_with_text()
        XmlTest.test_replace_nodenames()
        XmlTest.test_jats2html()
        XmlTest.test_xslt_italic()
        XmlTest.test_xslt_copy()
