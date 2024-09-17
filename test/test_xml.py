import os
import unittest
from pathlib import Path

import lxml.etree as ET

from amilib.ami_html import HtmlStyle, HtmlLib, HtmlEditor
from amilib.util import Util
from amilib.xml_lib import XmlLib
from test.resources import Resources

from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)

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
        logger.debug(file)
        html = HtmlLib.create_html_with_empty_head_body()
        styles = [
            (".class0", [("color", "red;")]),
            (".class1", [("background", "#ccccff;")]),
            (".class2", [("color", "#00cc00;")]),
        ]

        HtmlStyle.add_head_styles_orig(html, styles)
        HtmlLib.get_body(html).append(div)
        HtmlLib.write_html_file(html, file, debug=True)

    def test_skeleton_html(self):
        """create HTML with head, style, body
        """
        skel = HtmlEditor()
        skel.add_style("p", "{background: pink;}")
        p = ET.SubElement(skel.body, "p")
        p.text = "foo"
        p = ET.SubElement(skel.body, "p")
        p.text = "bar"
        myfile = Path(Resources.TEMP_DIR, "misc", "skeleton1.html")
        skel.write(myfile, debug=True)


class XmlTest(AmiAnyTest):
    XSLT_FILE = Path(Path(__file__).parent, "jats2html.xsl")


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
        logger.debug(ET.tostring(result))

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
        logger.debug(ET.tostring(doc))

    """transform = etree.XSLT(xslt_tree)
>>> result = transform(doc, a="'A'")
>>> bytes(result)
b'<?xml version="1.0"?>\n<foo>A</foo>\n'
    """

    @classmethod
    @unittest.skip("no XSLT file")
    def test_xslt_italic(cls):
        data = '''<p>essential oil extracted from
 <italic>T. bovei</italic> was comprised ... on the
 <italic>T. bovei</italic> activities ... activity.
</p>'''
        assert XmlTest.XSLT_FILE.exists()
        logger.info("italic", XmlLib.xslt_transform_tostring(data, XmlTest.XSLT_FILE))

    @classmethod
    @unittest.skip("no XSLT file")
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
        assert XmlTest.XSLT_FILE.exists()

        logger.info("copy", XmlLib.xslt_transform_tostring(data, XmlTest.XSLT_FILE))

    @classmethod
    def test_jats2html(cls):
        logger.debug("test_jats2html")
        data = '''<everything>
<m>Some text before <r/></m>
<m><r/> and some text after.</m>
<m><r/></m>
<m>Text before <r/> and after</m>
<m><b/> Text after a sibling <r/> Text before a sibling<b/></m>
</everything>
'''
        result = XmlLib.replace_nodes_with_text(data, "//r", "DELETED")
        logger.debug(ET.tostring(result))

    def test_debug_text_children(self):
        """

        """
        xml_str = "<p><a/>atail<b>cont</b>btail<c/><d>dcont</d></p>"
        xml_elem = ET.fromstring(xml_str)
        XmlLib.debug_direct_text_children(xml_elem)


    def test_replace_tail_text_with_spans(self):
        """
        wraps a mixed content text (tail text) in <span>
        """
        xml_str = "<p><a>acont</a>atail</p>"
        p_elem = ET.fromstring(xml_str)
        a_elem = p_elem.xpath('a')[0]
        XmlLib.replace_tail_text_with_span(a_elem)
        assert ET.tostring(p_elem) == b'<p><a>acont</a><span>atail</span></p>'

    def test_replace_child_tail_texts_with_spans(self):
        """
        wraps all mixed content text (tail texts) in <span>s
        """
        xml_str = "<p><a/>atail<b>cont</b>btail<c/><d>dcont</d></p>"
        p_elem = ET.fromstring(xml_str)
        XmlLib.replace_child_tail_texts_with_spans(p_elem)
        assert ET.tostring(p_elem) == b'<p><a/><span>atail</span><b>cont</b><span>btail</span><c/><d>dcont</d></p>'

    def test_split_to_sentences_with_brs(self):
        """

        """
        logger.info("NYI")

    def test_get_single_element_from_xpath(self):
        """
        get a single expected element by xpath or None
        Convenience method
        """
        # no hits
        foo = ET.Element("foo")
        barx = XmlLib.get_single_element(foo, "./bar")
        assert barx is None
        # 1 hit
        bar = ET.SubElement(foo, "bar")
        assert len(foo.xpath("bar")) == 1
        barx = XmlLib.get_single_element(foo, "./bar")
        assert barx is not None
        # 2 hits, returns None
        bar2 = ET.SubElement(foo, "bar")
        assert len(foo.xpath("bar")) == 2
        barx = XmlLib.get_single_element(foo, "./bar")
        assert barx is None


if __name__ == "__main__":
    logger.info(f"running {__name__} main")

    config_test = False
    wiki_test = False
    xml_test = False

    # NYI
    # if config_test:
    #     ConfigTests.tests()
    if xml_test:
        XmlTest.test_replace_nodes_with_text()
        XmlTest.test_replace_nodenames()
        XmlTest.test_jats2html()
        XmlTest.test_xslt_italic()
        XmlTest.test_xslt_copy()
