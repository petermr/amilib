import copy
import html
import logging
import os
import pprint
import re
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

import chardet
import lxml
import lxml.etree
import requests
# import tkinterweb
from lxml import etree as ET
from lxml.etree import _Element, _ElementTree, _ElementUnicodeResult, XPathEvalError
from lxml.html import HTMLParser
# import tkinter as tk

from amilib.file_lib import FileLib
from amilib.util import Util

logger = Util.get_logger(__name__)

# make leafnodes and copy remaning content as XML
TERMINAL_COPY = {
    "abstract",
    "aff",
    "article-id",
    "article-categories",
    "author-notes",
    "caption",
    "contrib-group",
    "fig",
    "history",
    "issue",
    "journal_id",
    "journal-title-group",
    "kwd-group",
    "name",
    "notes",
    "p",
    "permissions",
    "person-group",
    "pub-date",
    "publisher",
    "ref",
    "table",
    "title",
    "title-group",
    "volume",
}

TERMINALS = [
    "inline-formula",
]

TITLE = "title"

IGNORE_CHILDREN = {
    "disp-formula",
}

HTML_TAGS = {
    "italic": "i",
    "p": "p",
    "sub": "sub",
    "sup": "sup",
    "tr": "tr",
}

H_TD = "td"
H_TR = "tr"
H_TH = "th"
LINK = "link"
UTF_8 = "UTF-8"
SCRIPT = "script"
STYLESHEET = "stylesheet"
TEXT_CSS = "text/css"
TEXT_JAVASCRIPT = "text/javascript"

H_HTML = "html"
H_BODY = "body"
H_TBODY = "tbody"
H_DIV = "div"
H_TABLE = "table"
H_THEAD = "thead"
H_HEAD = "head"
H_TITLE = "title"

RESULTS = "results"

SEC_TAGS = {
    "sec",
}

LINK_TAGS = {
    "xref",
}

SECTIONS = "sections"

HTML_NS = "HTML_NS"
MATHML_NS = "MATHML_NS"
SVG_NS = "SVG_NS"
XMLNS_NS = "XMLNS_NS"
XML_NS = "XML_NS"
XLINK_NS = "XLINK_NS"

XML_LANG = "{" + XML_NS + "}" + 'lang'

NS_MAP = {
    HTML_NS: "http://www.w3.org/1999/xhtml",
    MATHML_NS: "http://www.w3.org/1998/Math/MathML",
    SVG_NS: "http://www.w3.org/2000/svg",
    XLINK_NS: "http://www.w3.org/1999/xlink",
    XML_NS: "http://www.w3.org/XML/1998/namespace",
    XMLNS_NS: "http://www.w3.org/2000/xmlns/",
}

DEFAULT_DECLUTTER = [
    ".//style",
    ".//script",
    ".//noscript",
    ".//meta",
    ".//link",
    ".//button",
    ".//picture",
    ".//svg",  # the IPCC logo swamps the first page
    # "//footer",
    ".//textarea",
    # ".//img"
]

DECLUTTER_BASIC = [
    ".//style",
    ".//script",
    ".//noscript",
    ".//meta",
    ".//link",
    ".//textarea",
]

# elemnts which cause display problems
BAD_DISPLAY = [
    "//i[not(node())]",
    "//a[@href and not(node())]",
    "//div[contains(@style, 'position:absolute')]"
]

logger = logging.getLogger("xml_lib")
logger.setLevel(logging.WARNING)
logging.debug(f"===========LOGGING {logger.level} .. {logging.DEBUG}")


class XmlLib:
    SENTENCE_RE = ".*\\.(\\s*$|\\s+[A-Z].*)" # maybe obsolete
    SENTENCE_START_RE = ".*\\.\\s+[A-Z].*"

    def __init__(self, file=None, section_dir=SECTIONS):
        self.max_file_len = 30
        self.file = file
        self.parent_path = None
        self.root = None
        self.logger = logging.getLogger("xmllib")
        self.section_dir = section_dir
        self.section_path = None

    #         self.logger.setLevel(logging.INFO)

    def read(self, file):
        """reads XML file , saves file, and parses to self.root"""
        if file is not None:
            self.file = file
            self.parent_path = Path(file).parent.absolute()
            self.root = XmlLib.parse_xml_file_to_root(file)

    def make_sections(self, section_dir):
        """recursively traverse XML tree and write files for each terminal element"""
        self.section_dir = self.make_sections_path(section_dir)
        # indent = 0
        # filename = "1" + "_" + self.root.tag
        # self.logger.debug(" " * indent, filename)
        # subdir = os.path.join(self.section_dir, filename)
        # FileLib.force_mkdir(subdir)

        self.make_descendant_tree(self.root, self.section_dir)
        self.logger.info(
            f"wrote XML sections for {self.file} {self.section_dir}")

    @staticmethod
    def parse_xml_file_to_root(file):
        """read xml path and create root element"""
        file = str(file)  # if file is Path
        if not os.path.exists(file):
            raise IOError("path does not exist", file)
        xmlp = ET.XMLParser(encoding=UTF_8)
        element_tree = ET.parse(file, xmlp)
        root = element_tree.getroot()
        return root

    @staticmethod
    def parse_xml_string_to_root(xml):
        """read xml string and parse to root element"""
        tree = ET.parse(StringIO(xml), ET.XMLParser(ns_clean=True))
        return tree.getroot()

    @classmethod
    def parse_url_to_tree(cls, url):
        """parses URL to lxml tree
        :param url: to parse
        :return: lxml tree"""
        with urlopen(url) as f:
            tree = lxml.etree.parse(f)
            """
    def get_html(url, retry_count=0):
    try:
        request = Request(url)
        response = urlopen(request)
        html = response.read()
    except ConectionResetError as e:
        if retry_count == MAX_RETRIES:
            raise e
        time.sleep(for_some_time)
        get_html(url, retry_count + 1)
        """
        return tree

    def make_sections_path(self, section_dir):
        self.section_path = os.path.join(self.parent_path, section_dir)
        if not os.path.exists(self.section_path):
            FileLib.force_mkdir(self.section_path)
        return self.section_path

    def make_descendant_tree(self, elem, outdir):

        self.logger.setLevel(logging.INFO)
        if elem.tag in TERMINALS:
            self.logger.debug("skipped ", elem.tag)
            return
        TERMINAL = "T_"
        IGNORE = "I_"
        children = list(elem)
        self.logger.debug(f"children> {len(children)} .. {self.logger.level}")
        isect = 0
        for child in children:
            if "ProcessingInstruction" in str(type(child)):
                # logger.debug("PI", child)
                continue
            if "Comment" in str(type(child)):
                continue
            flag = ""
            child_child_count = len(list(child))
            if child.tag in TERMINAL_COPY or child_child_count == 0:
                flag = TERMINAL
            elif child.tag in IGNORE_CHILDREN:
                flag = IGNORE

            title = child.tag
            if child.tag in SEC_TAGS:
                title = XmlLib.get_sec_title(child)

            if flag == IGNORE:
                title = flag + title
            filename = str(
                isect) + "_" + FileLib.punct2underscore(title).lower()[:self.max_file_len]

            if flag == TERMINAL:
                xml_string = ET.tostring(child)
                filename1 = os.path.join(outdir, filename + '.xml')
                self.logger.setLevel(logging.INFO)
                self.logger.debug(f"writing dbg {filename1}")
                try:
                    with open(filename1, "wb") as f:
                        f.write(xml_string)
                except Exception:
                    logger.debug(f"cannot write {filename1}")
            else:
                subdir = os.path.join(outdir, filename)
                # creates empty dirx, may be bad idea
                FileLib.force_mkdir(subdir)
                if flag == "":
                    self.logger.debug(f">> {title} {child}")
                    self.make_descendant_tree(child, subdir)
            isect += 1

    @staticmethod
    def get_sec_title(sec):
        """get title of JATS section

        :sec: section (normally sec element
        """
        title = None
        for elem in list(sec):
            if elem.tag == TITLE:
                title = elem.text
                break

        if title is None:
            # don't know where the 'xml_file' comes from...
            if not hasattr(sec, "xml_file"):
                title = "UNKNOWN"
            else:
                title = "?_" + str(sec["xml_file"][:20])
        title = FileLib.punct2underscore(title)
        return title

    @staticmethod
    def remove_all(elem, xpaths, debug=False):
        """removes all sub/elements in result of applying xpath
        :param elem: to remove sub/elements from
        :param xpaths: """
        xpaths = [xpaths] if type(xpaths) is str else xpaths
        if debug:
            logger.debug(f"xpaths for removal {xpaths}")
        for xpath in xpaths:
            try:
                elems = elem.xpath(xpath)
            except XPathEvalError as e:
                logger.error(f"bad Xpath: {xpath}")
                continue

            if debug:
                logger.debug(f"elems to remove {elems}")
            for el in elems:
                if el.getparent() is not None:
                    el.getparent().remove(el)

    @staticmethod
    def get_or_create_child(parent, tag):
        child = None
        if parent is not None:
            child = parent.find(tag)
            if child is None:
                child = ET.SubElement(parent, tag)
        return child

    @classmethod
    def get_text(cls, node):
        """
        get text children as string
        """
        return ''.join(node.itertext())

    @staticmethod
    def add_UTF8(html_root):
        """adds UTF8 declaration to root

        """
        root = html_root.get_or_create_child(html_root, "head")
        ET.SubElement(root, "meta").attrib["charset"] = "UTF-8"

    # replace nodes with text
    @staticmethod
    def replace_nodes_with_text(data, xpath, replacement):
        """replace nodes with specific text

        """
        logger.debug(data, xpath, replacement)
        tree = ET.fromstring(data)
        for r in tree.xpath(xpath):
            XmlLib.replace_node_with_text(r, replacement)
        return tree

    @classmethod
    def replace_node_with_text(cls, r, replacement):
        logger.debug("r", r, replacement, r.tail)
        text = replacement
        if r.tail is not None:
            text += r.tail
        parent = r.getparent()
        if parent is not None:
            previous = r.getprevious()
            if previous is not None:
                previous.tail = (previous.tail or '') + text
            else:
                parent.text = (parent.text or '') + text
            parent.remove(r)

    @classmethod
    def remove_all_tags(cls, xml_string):
        """remove all tags from text

        :xml_string: string to be flattened
        :returns: flattened string
        """
        tree = ET.fromstring(xml_string.encode("utf-8"))
        strg = ET.tostring(tree, encoding='utf8',
                           method='text').decode("utf-8")
        return strg

    @classmethod
    def remove_elements(cls, elem, xpath, new_parent=None, debug=False):
        """remove all elems matching xpath
        :param elem: to remove elements from
        :param xpath: to select removable elemnts
        :param new_parent: new parent for removed nodes
        :param debug: output debug (def = False)
        """
        if elem is None or xpath is None:
            return None
        if type(xpath) is list:
            for xp in xpath:
                cls.remove_elements(elem, xp)
            return
        elems = elem.xpath(xpath, debug=True)
        if debug:
            logger.debug(f"{xpath} removes {len(elems)} elems")
        for elem in elems:
            XmlLib.remove_element(elem), debug
            if new_parent is not None:
                new_parent.append(elem)

    @classmethod
    def xslt_transform(cls, xmlstring, xslt_file):
        """transforms xmlstring using xslt
        :param xmlstring: xml string to transform
        :param xslt_file: stylesheet as xslt
        :return: transformed object"""
        xslt_root = ET.parse(xslt_file)
        root = cls.transform_xml_object(xmlstring, xslt_root)

        return root

    @classmethod
    def transform_xml_object(cls, xmlstring, xslt_root):
        """
        transforms html string using XSLT
        :param xmlstring: well-formed XML string
        :param xslt_root: xslt file (may include relative links)
        :return: transformed XML object
        """

        transform = ET.XSLT(xslt_root)
        if transform.error_log:
            logger.debug("bad xsl? XSLT log", transform.error_log)
        result_tree = transform(xmlstring)
        assert (result_tree is not None)
        html_root = result_tree.getroot()
        assert html_root is not None
        assert len(html_root.xpath("//*")) > 0
        return html_root

    @classmethod
    def xslt_transform_tostring(cls, data, xslt_file):
        root = cls.xslt_transform(data, xslt_file)
        return ET.tostring(root).decode("UTF-8") if root is not None else None

    @classmethod
    def validate_xpath(cls, xpath):
        """
        crude syntax validation of xpath string.
        tests xpath on a trivial element
        :param xpath:
        """
        tree = lxml.etree.fromstring("<foo/>")
        try:
            tree.xpath(xpath)
        except lxml.etree.XPathEvalError as e:
            logging.error(f"bad XPath {xpath}, {e}")
            raise e

    @classmethod
    def does_element_equal_serialized_string(cls, elem, string):
        try:
            elem1 = lxml.etree.fromstring(string)
            return cls.are_elements_equal(elem, elem1)
        except Exception:
            return False

    @classmethod
    def are_elements_equal(cls, e1, e2):
        """compares 2 elements
        :param e1:
        :param e2:
        :return: False if not equal
        """
        if type(e1) is not lxml.etree._Element or type(e2) is not lxml.etree._Element:
            raise ValueError(f" not a pair of XML elements {e1} {e2}")
        if e1.tag != e2.tag:
            return False
        if e1.text != e2.text:
            return False
        if e1.tail != e2.tail:
            return False
        if e1.attrib != e2.attrib:
            return False
        if len(e1) != len(e2):
            return False
        return all(cls.are_elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

    @classmethod
    def write_xml(cls, elem, path, encoding="UTF-8", method="xml", debug=False, mkdir=True):
        """
        Writes XML to file
        :param elem: xml element to write
        :param path: path to write to
        :param method: xml default, could be html
        :except: bad encoding
        The use of encoding='UTF-8' is because lxml has a bug in some releases
        """
        if not path:
            return
        if elem is None:
            return
        path = Path(path)
        if mkdir:
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            try:
                # this solves some problems but not unknown font encodings
                # xmlstr = lxml.etree.tostring(elem, encoding='UTF-8').decode(encoding)

                xmlstr = lxml.etree.tostring(elem).decode(encoding)
            except Exception as e:
                logger.debug(f"****** cannot decode XML to {path}: {e} *******")
                return None
            try:
                if debug:
                    logger.debug(f"writing XML {path}")
                f.write(xmlstr)
            except Exception as ee:
                raise Exception(f"cannot write XMLString {ee}")

    @classmethod
    def remove_attribute(cls, elem, att):
        """
        removes at attribute (by name) if it exists
        :param elem: element with the attribute
        :param att: att_name to delete
        """
        if elem is not None and att in elem.attrib:
            del elem.attrib[att]

    @classmethod
    def delete_atts(cls, attnames, span):
        for att in attnames:
            attval = span.attrib.get(att)
            if attval:
                del (span.attrib[att])

    @classmethod
    def set_attname_value(cls, elem, attname, value):
        """
        set attribute, if value==None remove attribute
        :param elem: element with attribute
        :param attname: attribute name
        :param value: attribute value; if "" or None remove attribute
        """
        if value is None or value == "":
            XmlLib.remove_attribute(elem, attname)
        else:
            elem.attrib[attname] = value

    @classmethod
    def remove_element(cls, elem):
        """cnvenience method to remove element from tree
        :param elem: elem to be removed
        no-op if elem or its parent is None"""
        # does not remove tail (I don't think)
        if elem is not None:
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

    @classmethod
    def get_next_element(cls, elem):
        """
        get next element after elem
        convenience method to use following::
        :param elem: element in tree
        :return: next elemnt or None
        """
        nexts = elem.xpath("following::*")
        return None if len(nexts) == 0 else nexts[0]

    @classmethod
    def get_following_elements(cls, elem, predicate=None, count=9999):
        """
        get next elements after elem
        convenience method to use following::
        :param elem: element in tree
        :param predicate: condition (with the []), e.g "[@class='.s1010']"
        :return: next elemnts or empty list
        """
        pred_string = f"" if predicate is None else f"{predicate}"
        xp = f"following::*{pred_string}"
        xp = f"following::*"
        logger.debug(f"xp: {xp} {lxml.etree.tostring(elem)}")
        nexts = elem.xpath(xp)
        # next = None if len(nexts) == 0 else nexts[:count]
        logger.debug(f"nexts {len(nexts)}")
        return nexts

    @classmethod
    def getparent(cls, elem, debug=False):
        if elem is None:
            return None
        parent = elem.getparent()
        if parent is None and debug:
            logger.debug(f" parent of {elem} is None")
        return parent

    @classmethod
    def read_xml_element_from_github(cls, github_url=None, url_cache=None):
        """reads raw xml and parses to elem

        ent. Errors uncaught
        """
        if not github_url:
            return None
        # logger.debug(f"url: {github_url}")
        if url_cache:
            xml_elem = url_cache.read_xml_element_from_github(github_url)
        else:
            xml_elem = lxml.etree.fromstring(requests.get(github_url).text)
        return xml_elem

    @classmethod
    def is_integer(cls, elem):
        """test whether text content parses as an integer"""
        try:
            i = int(elem.text)
            return True
        except Exception as e:
            return False

    @classmethod
    def remove_common_clutter(cls, elem, declutter=None, bad_display=None):
        """
        :param elem: to declutter
        :param declutter: If None
        :param debug: print removed elements
        """
        if elem is None:
            logger.debug(f"remove clutter : element is None")
            return
        if declutter is None:
            declutter = DEFAULT_DECLUTTER

        cls.remove_all(elem, declutter)
        #  this causes display problems
        bad_display = BAD_DISPLAY if bad_display is None else bad_display
        cls.remove_all(elem, bad_display)

    @classmethod
    def replaceStrings(cls, text_elem, strings, debug=False):
        """edit text child of element

        :param text_elem: element with text child
        :param strings: list od tuples (oldstring, newstring)
        :return: 0 if no change, 1 if change
        """
        t1 = text_elem.text
        if t1:
            t2 = t1
            t2 = cls.iteratively_replace_strings(strings, t2)

            if t2 != t1:
                if debug:
                    logger.debug(f"replaced {t1} by {t2}")
                text_elem.text = t2
                return 1
        return 0

    @classmethod
    def iteratively_replace_strings(cls, strings, t2):
        """iterates over list of (old, new) pukles to replace substrings
        """
        for string in strings:
            t2 = t2.replace(string[0], string[1])
        return t2

    @classmethod
    def replace_substrings_in_all_child_texts(cls, html_elem, subs_list, debug=False):
        """
        edit all text children of elements, replacing oldstr with newstr
        :param html_elem: elements with texts to edit
        :param subs_list: list of (oldStr, newstr) pairs
        """
        text_elems = html_elem.xpath(".//*[text()]")
        for text_elem in text_elems:
            XmlLib.replaceStrings(text_elem, subs_list, debug=debug)

    @classmethod
    def split_span_by_regex(cls, span, regex, ids=None, href=None, clazz=None, markup_dict=None, repeat=0):
        """this is phased out in favour or templates
        """
        """split a span into 3 sections but matching substring
        <parent><span attribs>foo bar plugh</span></parent>
        if "bar" matches regex gives:
        <parent><span attribs>foo </span><span attribs id=id>bar</span><span attribs> plugh</span></parent>
        if count > 1, repeats the splitting on the new RH span , decrementing repeat until zero

        :param span: the span to split
        :param regex: finds (first) match in span.text and extracts matched text into middle span
        :param id: if string, adds id to new mid element; if array of len 3 gives id[0], id[1], id[2] to each new span
        :param href: adds <a href=href>matched-text</a> as child of mid span (1) if un.GENERATE generates HREF
        :param clazz: 3-element array to add class attributes to split sections
        :param repeat: repeats split on (new) rh span
        :return: None if no match, else first match in span
        """
        logger.debug(f"USE TEMPLATES INSTEAD for HREF or ID generation")
        type_span = type(span)
        parent = span.getparent()

        if span is None or regex is None or type_span is not lxml.etree._Element \
                or parent is None or span.tag != 'span' or repeat < 0:
            return None
        text = span.text
        if text is None:
            # logger.debug(f"text is None")
            return None
        if regex is None:
            logger.debug("regex is None")
            return None
        match = None
        try:
            match = re.search(regex, text)
        except Exception as e:
            logger.debug(f"bad match {regex} /{e} --> {text}")
            return
        idx = parent.index(span)
        dummy_templater = Templater()
        # enhanced_regex = EnhancedRegex(regex=regex)
        if match:
            anchor_text = match.group(0)
            logger.info(f"matched: {regex} {anchor_text}")
            # href_new = enhanced_regex.get_href(href, text=anchor_text)
            # make 3 new spans
            # some may be empty
            offset = 1
            offset, span0 = cls.create_span(idx, match, offset, parent, span, text, "start")
            href_new = None
            mid = dummy_templater.create_new_span_with_optional_a_href_child(parent, idx + offset, span, anchor_text,
                                                                             href=href_new)
            offset += 1
            offset, span2 = cls.create_span(idx, match, offset, parent, span, text, "end")
            if ids and type(ids) is str:
                ids = [None, ids, None]
            if ids and len(ids) == 3:
                if span0 is not None:
                    span0.attrib["id"] = ids[0]
                mid.attrib["id"] = ids[1]
                if span2 is not None:
                    span2.attrib["id"] = ids[2]
            if clazz and len(clazz) == 3:
                if span0 is not None:
                    span0.attrib["class"] = clazz[0]
                mid.attrib["class"] = clazz[1]
                if span2 is not None:
                    span2.attrib["class"] = clazz[2]
            clazz = None if not markup_dict else markup_dict.get("class")
            if clazz is not None:
                mid.attrib["class"] = clazz
            if span2 is not None:
                logger.debug(f"style {span2.attrib.get('style')}")

            parent.remove(span)
            # recurse in RH split
            if regex is None:
                logger.error("no regex")
                return
            if repeat > 0:
                repeat -= 1
                cls.split_span_by_regex(span2, regex, ids=ids, href=href, repeat=repeat)
        return match

    @classmethod
    def create_span(cls, idx, match, offset, parent, span, text, pos_str=None):
        """
        :param idx: index of new child span relative to old span
        :param match: result of regex search
        :param offset: number of new child, incremented when added
        :param parent: of span, to which new soan is attached
        :param span: old span
        :param text: text to add
        :param pos_str: "start" or "end"
        :return: tuple (offset, new_span)
        """
        # note: match has a span() attribute!
        if pos_str == "start":
            span_text = text[0:match.span()[0]]  # first string
        elif pos_str == "end":
            span_text = text[match.span()[1]:]  # last string
        new_span = None
        if len(span_text) > 0:
            dummy_templater = Templater()
            new_span = dummy_templater.create_new_span_with_optional_a_href_child(parent, idx + offset, span, span_text)
            # new_span = XmlLib.create_and_add_anchor(href, span, span_text)
            offset += 1
        else:
            logger.error(f"zero-length span0 in {span.text}")
            pass
        return offset, new_span

    @classmethod
    def create_and_add_anchor(cls, href, span, atext):
        """makes a@href child of span
        :param href: href text
        :param soan: to add child to
        :param text: anchor text
        """
        a_elem = lxml.etree.SubElement(span, "a")
        a_elem.attrib["href"] = href
        a_elem.text = atext
        span.text = None

    """
    MIXED CONTENT IN lxml (!!!) NOT EASY
    see https://lxml.de/tutorial.html#using-xpath-to-find-text
    and 
    https://stackoverflow.com/questions/57301789/how-can-i-select-and-update-text-nodes-in-mixed-content-using-lxml
    
    the text references the previous elem through getparent()

    >> I found the key to this solution in the docs: Using XPath to find text
    
    >> Specifically the is_text and is_tail properties of _ElementUnicodeResult.

    """
    @classmethod
    def debug_direct_text_children(cls, elem):
        """
        iterate over sequence of elements and texts and replace by span(text)
        This gets rid of the node + node.tail  and converts the texts to a first class element
        :param elem: element with child elements and child texts
        Assumes no PIs, no textdata
        """
        if elem is None:
            return
        children = elem.xpath("*|text()")
        for child in children:
            if type(child) is _ElementUnicodeResult:
                 logger.info(f"T:{child}:Tail:{child.is_tail}, Text:{child.is_text}, Parent:{child.getparent().tag}")
            elif type(child) is _Element:
                logger.debug(f"E:{child}|{child.tail}")
            else:
                logger.debug(f"?:{child}")

    @classmethod
    def replace_tail_text_with_span(cls, elem):
        """
        <foo>...</foo>tail
        is replaced by
        <foo>...</foo><span>tail<span>
        :param elem: to be edited
        """
        if elem is None or elem.getparent() is None:
            return
        if elem.tail is not None:
            parent = elem.getparent()
            span = ET.Element("span")
            span.text = elem.tail
            elem.tail = None
            elem.addnext(span)

    @classmethod
    def replace_child_tail_texts_with_spans(cls, parent_elem):
        """
        find all (tail) text childrren and wrap in spans
        :param parent_elem: parent elem with child texts
        """
        if parent_elem is None:
            return
        texts = parent_elem.xpath("./text()")
        for text in texts:
            pre_elem = text.getparent()
            cls.replace_tail_text_with_span(pre_elem)
        return

    def get_sentence_breaks(self, texts):
        """
        split html/text iinto sentences
        :param texts: mixed content texts (tails)
        :return: array of splits (still being developed)
        """
        # texts = self.get_texts()

        text_breaks = [(j, t) for (j, t) in enumerate(texts) if re.match(self.SENTENCE_RE, t)]
        splits = []
        for (idx, txt) in text_breaks:
            prec = '^' if idx == 0 else texts[idx - 1]
            foll = '$' if idx == len(texts) - 1 else texts[idx + 1]
            splits.append(f"|{prec}|{txt}|{foll}|")
        return splits

    @classmethod
    def add_sentence_brs(cls, texts):
        """
        split html/text in paragrah into sentences
        add <br> element after period
        :return: None (modifies texts) (still being developed)
        """
        if len(texts) == 0:
            return
        parent = texts[0].getparent().getparent()
        logger.debug(f"parent: {parent}")
        for text in texts:
            head = text.getparent()
            # logger.debug(f"head: {head.tag}")
            if re.match(cls.SENTENCE_START_RE, text):
                splits = text.split('.', 1)
                prec_elem = text.getparent()
                prec_elem.tail = splits[0] + "."
                br_elem = ET.Element("br")
                br_elem.tail = splits[1]
                prec_elem.addnext(br_elem)
        return

    @classmethod
    def element_to_string(cls, element, method="xml", pretty_print=True, encoding="UTF-8"):
        """
        converts element to string
        :param element: to render
        :param method: "html" or "xml",default "xml"
        :param pretty_print: pretty print , default True
        :param encoding: default UTF-8

        """
        return None if element is None else lxml.etree.tostring(
            element, method=method, pretty_print=pretty_print).decode(encoding)

    @classmethod
    def get_single_element(cls, xmlx, xpath):
        """
        Convenience method to avoid testing for len()
        gets a single element from xpath or returns None
        :param xmlx: lxml element to query
        :param xpath:
        :return: single element or None
        """
        if xmlx is None:
            logger.debug("xmlx is None")
            return None
        if xpath is None:
            logger.debug("xpath is None ")
            return None
        results = xmlx.xpath(xpath)
        if len(results) == 1:
            return results[0]
        else:
            return None


class HtmlElement:
    """to provide fluent HTML builder and parser NYI"""
    pass


# class HtmlEditor:
#     """
#     Convenience method for creating HTML tree
#     skeleton html with attributes for head, style, body
#     hardcoded attributes (Html elements) are:
#     .html - the whole document
#     .head - the head
#     .style - a style stub in head (add others with SubElement)
#     .body - a stub body
#     (To create other elemnts you have to use SubElement or append)
#
#     example:
#     skel = HtmlSkeleton()
#     skel.style.text = "p {background: pink;}"
#     p = ET.SubElement(skel.body, "p")
#     p.text = "foo"
#     p = ET.SubElement(skel.body, "p")
#     p.text = "bar"
#     skel.write(myfile, debug=True)
#
#
#
#     """
#
#     def __init__(self):
#         """
#         creates elements self.html, self.head, self.body
#         """
#         self.html = lxml.etree.Element("html")
#         self.head = ET.SubElement(self.html, "head")
#         self.body = ET.SubElement(self.html, "body")
#
#     def write(self, file, debug=True):
#         HtmlLib.write_html_file(self.html, file, debug=debug)
#
#     def add_style(self, selector, value):
#         """
#         at present just use HTML style content,
#         content includes the "{...}'
#         e.g.
#         selector ="span"
#         value = "{background, pink; border: solid 1px blue;}
#         htmlx.add_style(selector, value)
#
#         """
#
#         style = ET.SubElement(self.head, "style")
#         style.text = f"{selector} {value}"


# class HtmlLib:
#
#     CLASS_ATTNAME = "class"
#
#     @classmethod
#     def convert_character_entities_in_lxml_element_to_unicode_string(cls, element, encoding="UTF-8") -> str:
#         """
#         converts character entities in lxml element to Unicode
#         1) extract string as bytes
#         2) converts bytes to unicode with html.unescape()
#         (NOTE: may be able to use tostring to do this)
#
#
#         :param element: lxml element
#         :return: unicode string representation of element
#         """
#         stringx = lxml.etree.tostring(element)
#         string_unicode = html.unescape(stringx.decode(encoding))
#         return string_unicode
#
#     @classmethod
#     def create_html_with_empty_head_body(cls):
#         """
#         creates
#         <html>
#           <head/>
#           <body/>
#         </html>
#         """
#         html_elem = lxml.etree.Element("html")
#         html_elem.append(lxml.etree.Element("head"))
#         html_elem.append(lxml.etree.Element("body"))
#         return html_elem
#
#     def create_html_container_with_head_style_body(cls):
#         """
#         creates
#         <html>
#           <head/>
#           <body/>
#         </html>
#         """
#         html_container = Html_Container()
#         html_elem = lxml.etree.Element("html")
#         html_elem.append(lxml.etree.Element("head"))
#         html_elem.append(lxml.etree.Element("body"))
#         return html_elem
#
#     @classmethod
#     def add_copies_to_head(cls, html_elem, elems):
#         """copies elems and adds them to <head> of html_elem
#         no checks made for duplicates
#         :param html_elem: elemnt to copy into
#         :param elems: list of elements to copy (or single elemnt
#         """
#         if html_elem is None or elems is None:
#             raise ValueError("Null arguments in HtmlLib.add_copies_to_head")
#         head = html_elem.xpath("./head")[0]
#         if type(elems) is not list:
#             elems = [elems]
#         for elem in elems:
#             head.append(copy.deepcopy(elem))
#
#     @classmethod
#     def get_body(cls, html_elem):
#         """
#         :oaram html_elem: if None, creates new Html element; if not must have a body
#         :return: body element
#         """
#         if html_elem is None:
#             html_elem = HtmlLib.create_html_with_empty_head_body()
#         bodys = html_elem.xpath("./body")
#         return bodys[0] if len(bodys) == 1 else None
#
#     @classmethod
#     def get_head(cls, html_elem=None):
#         """
#         :oaram html_elem: if None, creates new Html element; if not must have a head
#         :return: the head element
#         """
#         if html_elem is None:
#             html_elem = HtmlLib.create_html_with_empty_head_body()
#         head = XmlLib.get_single_element(html_elem, "/html/head")
#         return head
#
#     @classmethod
#     def add_base_url(cls, html_elem, base_url):
#         head = cls.get_head(html_elem)
#         base = head.xpath("base")
#         if len(base) > 1:
#             logger.info(f"too many base_urls; probable error")
#             return
#         if len(base) == 0:
#             base = lxml.etree.SubElement(head, "base")
#             base.attrib["href"] = base_url
#
#     @classmethod
#     def create_new_html_with_old_styles(cls, html_elem):
#         """
#         creates new HTML element with empty body and copies styles from html_elem
#         """
#         new_html_elem = HtmlLib.create_html_with_empty_head_body()
#         HtmlLib.add_copies_to_head(new_html_elem, html_elem.xpath(".//style"))
#         return new_html_elem
#
#     @classmethod
#     def add_head_style(cls, html, target, css_value_pairs):
#         """This might duplicate things in HtmlStyle
#         """
#
#         if html is None or not target or not css_value_pairs:
#             raise ValueError(f"None params in add_head_style")
#         head = HtmlLib.get_head(html)
#         style = lxml.etree.Element("style")
#         head.append(style)
#         style.text = target + " {"
#         for css_value_pair in css_value_pairs:
#             if len(css_value_pair) != 2:
#                 raise ValueError(f"bad css_value_pair {css_value_pair}")
#             style.text += css_value_pair[0] + " : " + css_value_pair[1] + ";"
#         style.text += "}"
#
#     @classmethod
#     def add_explicit_head_style(cls, html_page, target, css_string):
#         """
#         :param html_page: element receiving styles in head
#         :param target: the reference (e.g. 'div', '.foo')
#         """
#
#         if html_page is None or not target or not css_string:
#             raise ValueError(f"None params in add_head_style")
#         if not css_string.startswith("{") or not css_string.endswith("}"):
#             raise ValueError(f"css string must include {...}")
#         head = HtmlLib.get_head(html_page)
#         style = lxml.etree.Element("style")
#         head.append(style)
#         style.text = target + " " + css_string
#
#     @classmethod
#     def write_html_file(self, html_elem, outfile, debug=False, mkdir=True, pretty_print=False, encoding="UTF-8"):
#         """writes XML element (or tree) to file, making directory if needed .
#         adds method=True to ensure end tags
#         :param html_elem: element to write
#         :param outfile: file to write
#         :param mkdir: make directory if not exists (def True)
#         :param debug: output debug (def False)
#         :param pretty_print: pretty print output (def False)
#         """
#         if html_elem is None:
#             if debug:
#                 logger.info("null html elem to write")
#             return
#         if outfile is None:
#             if debug:
#                 logger.error("no outfile given")
#             return
#         if type(html_elem) is _ElementTree:
#             html_elem = html_elem.getroot()
#         if not (type(html_elem) is _Element or type(html_elem) is lxml.html.HtmlElement):
#             raise ValueError(f"type(html_elem) should be _Element or lxml.html.HtmlElement not {type(html_elem)}")
#         if encoding and encoding.lower() == "utf-8":
#             head = HtmlLib.get_or_create_head(html_elem)
#             if head is None:
#                 logger.error(f"cannot create <head> on html elem; not written")
#                 return
#
#         outdir = os.path.dirname(outfile)
#         if mkdir:
#             Path(outdir).mkdir(exist_ok=True, parents=True)
#
#         # cannot get this to output pretty_printed, (nor the encoding)
#         tostring = lxml.etree.tostring(html_elem, method="html", pretty_print=pretty_print).decode("UTF-8")
#
#         with open(str(outfile), "w") as f:
#             f.write(tostring)
#         if debug:
#             print(f"wrote: {Path(outfile).absolute()}")
#
#     @classmethod
#     def create_rawgithub_url(cls, site=None, username=None, repository=None, branch=None, filepath=None,
#                              rawgithubuser="https://raw.githubusercontent.com"):
#         """creates rawgithub url for programmatic HTTPS access to repository"""
#         site = "https://raw.githubusercontent.com"
#         url = f"{site}/{username}/{repository}/{branch}/{filepath}" if site and username and repository and branch and filepath else None
#         return url
#
#     @classmethod
#     def get_or_create_head(cls, html_elem):
#         """ensures html_elem is <html> and first child is <head>"""
#         if html_elem is None:
#             return None
#         if html_elem.tag.lower() != "html":
#             logger.error(f"not a full html element")
#             return None
#         head = HtmlLib.get_head(html_elem)
#         if head is None:
#             head = lxml.etree.SubElement(html_elem, "head")
#             html_elem.insert(0, head)
#         return head
#
#     @classmethod
#     def add_charset(cls, html_elem, charset="utf-8"):
#         """adds <meta charset=charset" to <head>"""
#         head = HtmlLib.get_or_create_head(html_elem)
#         if head is None:
#             logger.error(f"cannot create <head>")
#             return
#         cls.remove_charsets(head)
#         meta = lxml.etree.SubElement(head, "meta")
#         meta.attrib["charset"] = charset
#
#     @classmethod
#     def remove_charsets(cls, head):
#         XmlLib.remove_elements(head, ".//meta[@charset]")
#
#     @classmethod
#     def extract_ids_from_html_page(cls, input_html_path, regex_str=None, debug=False):
#         """
#         finds possible IDs in PDF HTML pages
#         must lead the text in a span
#         """
#         elem = lxml.etree.parse(str(input_html_path))
#         div_with_spans = elem.xpath(".//div[span]")
#         regex = re.compile(regex_str)
#         sectionlist = []
#         for div in div_with_spans:
#             spans = div.xpath(".//span")
#             for span in spans:
#                 matchstr = regex.match(span.text)
#                 if matchstr:
#                     if debug:
#                         logger.info(f"matched {matchstr.group(1)} {span.text[:50]}")
#                     sectionlist.append(span)
#         return sectionlist
#
#     @classmethod
#     def parse_html(cls, infile):
#         """
#         parse html file as checks for file existence
#         :param infile: file to parse or url (checks prefix)
#         :return: root element
#         """
#         if not infile:
#             logger.error(f"infile is None")
#             return None
#         if not str(infile).startswith("http"):
#             path = Path(infile)
#             if not path.exists():
#                 logger.error(f"file does not exist {infile}")
#                 return None
#         try:
#             infile = "https://en.wikipedia.org"
#             logger.debug(f"infile {infile}")
#             html_tree = lxml.html.parse(infile, HTMLParser())
#             if html_tree is None:
#                 logger.error(f"Cannot parse {infile}, returned None")
#             return html_tree.getroot()
#         except Exception as e:
#             logger.error(f"cannot parse {infile} because {e}")
#             return None
#
#     @classmethod
#     def parse_html_string(cls, string):
#         """
#         parse string
#         :param string: html
#         :return: html element or None
#         """
#         try:
#             html_element = lxml.html.fromstring(string)
#         except Exception as e:
#             logger.error(f"html error {e}")
#             return None
#
#         return html_element
#
#     @classmethod
#     def find_paras_with_ids(cls, html, xpath=None):
#         """
#         find all p's with @id and return ordered list
#         :param html: parsed html DOM
#         """
#         if not xpath:
#             xpath = ".//p[@id]"
#         paras = []
#         if html is None:
#             return paras
#         body = HtmlLib.get_body(html)
#         paras = body.xpath(xpath)
#         return paras
#
#     @classmethod
#     def para_contains_phrase(cls, para, phrase, ignore_case=True, markup=None):
#         """
#         search paragraph with phrase. If markuip is not None add hyperlinks
#
#         Parameters
#         ----------
#         para paragraph to search
#         phrase search phrase
#         ignore_case if True lowercase text and phrase
#         markup if True search each itertext and insert hrefs, else just seatch concatenation
#
#         Returns
#         -------
#
#         """
#         if ignore_case:
#             phrase = phrase.lower()
#         search_re = r'\b' + phrase + r'\b'
#         if not markup:
#             text = "".join(para.itertext())
#             if ignore_case:
#                 text = text.lower()
#             if re.search(search_re, text):
#                 return True
#         else:
#             texts = para.xpath(".//text()")
#             for text in texts:
#                 match = re.search(search_re, text)
#                 if match:
#                     cls._insert_ahref(markup, match, phrase, text)
#
#         return False
#
#     @classmethod
#     def _insert_ahref(cls, url_base, match, phrase, text):
#         """
#         Add hyperlinks to text. The order of opratyations matters
#         """
#         id = HtmlLib.generate_id(phrase)
#         href, title = cls._create_href_and_title(id, url_base)
#
#         # text before, inside and after <a> element
#         start_ = text[0:match.start()]
#         mid_ = text[match.start():match.end()]
#         end_ = text[match.end():]
#
#         # might be a text (contained within lead) or tail following it
#
#         # text contained in element
#         if text.is_text:
#             aelem = cls.add_href_for_lxml_text(start_, text)
#
#         # text following element
#         elif text.is_tail:
#             aelem = cls._add_href_for_lxml_tail(start_, text)
#         else:
#             logger.error(f"ERROR??? (not text of tail) {start_}|{mid_}|{end_}")
#
#         # add content and attributes to aelem
#         aelem.attrib["href"] = href
#         aelem.text = mid_
#         aelem.tail = end_
#         if title:
#             aelem.attrib["title"] = title
#
#     @classmethod
#     def _add_href_for_lxml_tail(cls, start_, text):
#         prev = text.getparent()
#         aelem = ET.Element("a")
#         aelem.attrib["style"] = "border:solid 1px; background: #ffbbbb;"
#         prev.addnext(aelem)  # order metters1
#         prev.tail = start_ + " "
#         return aelem
#
#     @classmethod
#     def add_href_for_lxml_text(cls, start_, text):
#         parent = text.getparent()
#         tail = parent.tail
#         aelem = ET.SubElement(parent, "a")
#         aelem.attrib["style"] = "border:solid 1px; background: #ffffbb;"
#         parent.text = start_
#         parent.tail = tail
#         return aelem
#
#     @classmethod
#     def _create_href_and_title(cls, id, url_base):
#         href = f"{url_base}"
#         href_elem = ET.parse(href, HTMLParser())
#         idelems = href_elem.xpath(f".//*[@id='{id}']")
#         title = id
#         if len(idelems) > 0:
#             ps = idelems[0].xpath("./p")
#             if len(ps) > 0:
#                 p = ps[0] if len(ps) == 1 else ps[1]
#                 if p is not None:
#                     title = "".join(p.itertext())
#         return href, title
#
#     @classmethod
#     def generate_id(cls, phrase):
#         """
#         strip, converts whitespace to single "-" and lowercase
#         """
#         phrase1 = re.sub(r"\s+", "_", phrase)
#         return phrase1
#
#     @classmethod
#     def search_phrases_in_paragraphs(cls, paras, phrases, markup=None):
#         """search for phrases in paragraphs
#         :param paras: list of HTML elems with text (normally <p>), must have @id else ignored
#         :param phrases: list of strings to search for (word boundary honoured)
#         :param markup:html dictionary with phrases
#         :return: dict() keyed on para_ids values are dict of search hits by phrase
#         """
#         para_phrase_dict = dict()
#         for para in paras:
#             para_id = para.get("id")
#             if para_id is None:
#                 continue
#             phrase_dict = dict()
#             for phrase in phrases:
#                 count = HtmlLib.para_contains_phrase(para, phrase, ignore_case=True, markup=markup)
#                 if count > 0:
#                     phrase_dict[phrase] = count
#                     para_phrase_dict[para_id] = phrase_dict
#         return para_phrase_dict
#
#     @classmethod
#     def retrieve_with_useragent_parse_html(cls, url, user_agent='my-app/0.0.1', encoding="UTF-8", debug=False):
#
#         """
#         Some servers give an Error 403 unless they have a user_agent.
#         This provides a dummy one and allows users to add the true one
#         """
#         content, encoding = FileLib.read_string_with_user_agent(url, user_agent=user_agent, encoding=encoding,
#                                                                 debug=debug)
#         assert type(content) is str
#         html = lxml.html.fromstring(content, base_url=url, parser=HTMLParser())
#
#         return html
#
#     @classmethod
#     def _extract_paras_with_ids(cls, infile, count=-1):
#         """
#
#         Parameters
#         ----------
#         infile html file with p[@id]
#         count number of paragraphs with @id (default -1) . if count >= 0, asserts number flound == count
#
#         Returns
#         -------
#
#         """
#         assert Path(infile).exists(), f"{infile} does not exist"
#         html = ET.parse(str(infile), HTMLParser())
#         paras = HtmlLib.find_paras_with_ids(html)
#         if count >= 0:
#             assert len(paras) == count
#         return paras
#
#     @classmethod
#     def add_link_stylesheet(self, css_file, htmlx):
#         """
#         add stylesheet link to <head>
#         creates <link rel='stylesheet' href=<css_file/>
#         does not remove other links
#         :param htmlx: html element with existing <head> element
#         :param css_file:file path , absolute or relative to html file
#
#         """
#
#         link = ET.SubElement(HtmlLib.get_head(htmlx), "link")
#         link.attrib["rel"] = "stylesheet"
#         link.attrib["href"] = css_file
#
#     @classmethod
#     def add_base_to_head(self, htmlx, base_href):
#         """
#         create or reuse a single <base> child of <head> and add self.base as href value
#         :param: html root element
#         :param base_href: value for @href on <base>
#         """
#         if htmlx is None:
#             logger.error("no HTML element")
#             return
#         if base_href is None:
#             logger.error("no base_href")
#             return
#         head = HtmlLib.get_head(htmlx)
#         bases = head.xpath("./base")
#         if len(bases) == 1:
#             base = bases[0]
#         else:
#             # create base
#             base = ET.SubElement(HtmlLib.get_head(htmlx), "base")
#         base.attrib["href"] = base_href
#


class DataTable:
    """
<html xmlns="http://www.w3.org/1999/xhtml">
 <head charset="UTF-8">
  <title>ffml</title>
  <link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"/>
  <script src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js" charset="UTF-8" type="text/javascript"> </script>
  <script src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js" charset="UTF-8" type="text/javascript"> </script>
  <script charset="UTF-8" type="text/javascript">$(function() { $("#results").dataTable(); }) </script>
 </head>
    """

    def __init__(self, title, colheads=None, rowdata=None):
        """create dataTables
        optionally add column headings (list) and rows (list of conformant lists)

        :param title: of data_title (required)
        :param colheads:
        :param rowdata:

        """
        self.html = ET.Element(H_HTML)
        self.head = None
        self.body = None
        self.create_head(title)
        self.create_table_thead_tbody()
        self.add_column_heads(colheads)
        self.add_rows(rowdata)
        self.head = None
        self.title = None
        # self.title.text = None

    def create_head(self, title):
        """
          <title>ffml</title>
          <link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"/>
          <script src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js" charset="UTF-8" type="text/javascript"> </script>
          <script src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js" charset="UTF-8" type="text/javascript"> </script>
          <script charset="UTF-8" type="text/javascript">$(function() { $("#results").dataTable(); }) </script>
        """

        self.head = ET.SubElement(self.html, H_HEAD)
        self.title = ET.SubElement(self.head, H_TITLE)
        self.title.text = title

        link = ET.SubElement(self.head, LINK)
        link.attrib["rel"] = STYLESHEET
        link.attrib["type"] = TEXT_CSS
        link.attrib["href"] = "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"
        link.text = '.'  # messy, to stop formatter using "/>" which dataTables doesn't like

        script = ET.SubElement(self.head, SCRIPT)
        script.attrib["src"] = "http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js"
        script.attrib["charset"] = UTF_8
        script.attrib["type"] = TEXT_JAVASCRIPT
        script.text = '.'  # messy, to stop formatter using "/>" which dataTables doesn't like

        script = ET.SubElement(self.head, SCRIPT)
        script.attrib["src"] = "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"
        script.attrib["charset"] = UTF_8
        script.attrib["type"] = TEXT_JAVASCRIPT
        script.text = "."  # messy, to stop formatter using "/>" which dataTables doesn't like

        script = ET.SubElement(self.head, SCRIPT)
        script.attrib["charset"] = UTF_8
        script.attrib["type"] = TEXT_JAVASCRIPT
        script.text = "$(function() { $(\"#results\").dataTable(); }) "

    def create_table_thead_tbody(self):
        """
     <body>
      <div class="bs-example table-responsive">
       <table class="table table-striped table-bordered table-hover" id="results">
        <thead>
         <tr>
          <th>articles</th>
          <th>bibliography</th>
          <th>dic:country</th>
          <th>word:frequencies</th>
         </tr>
        </thead>
        """

        self.body = ET.SubElement(self.html, H_BODY)
        self.div = ET.SubElement(self.body, H_DIV)
        self.div.attrib["class"] = "bs-example table-responsive"
        self.table = ET.SubElement(self.div, H_TABLE)
        self.table.attrib["class"] = "table table-striped table-bordered table-hover"
        self.table.attrib["id"] = RESULTS
        self.thead = ET.SubElement(self.table, H_THEAD)
        self.tbody = ET.SubElement(self.table, H_TBODY)

    def add_column_heads(self, colheads):
        if colheads is not None:
            self.thead_tr = ET.SubElement(self.thead, H_TR)
            for colhead in colheads:
                th = ET.SubElement(self.thead_tr, H_TH)
                th.text = str(colhead)

    def add_rows(self, rowdata):
        if rowdata is not None:
            for row in rowdata:
                self.add_row_old(row)

    def add_row_old(self, row: [str]):
        """ creates new <tr> in <tbody>
        creates <td> child elements of row containing string values

        :param row: list of str
        :rtype: object
        """
        if row is not None:
            tr = ET.SubElement(self.tbody, H_TR)
            for val in row:
                td = ET.SubElement(tr, H_TD)
                td.text = val

    def make_row(self):
        """

        :return: row element
        """
        return ET.SubElement(self.tbody, H_TR)

    def append_contained_text(self, parent, tag, text):
        """create element <tag> and add text child
        :rtype: element

        """
        subelem = ET.SubElement(parent, tag)
        subelem.text = text
        return subelem

    def write_full_data_tables(self, output_dir: str) -> None:
        """

        :rtype: object
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        data_table_file = os.path.join(output_dir, "full_data_table.html")
        with open(data_table_file, "w") as f:
            text = bytes.decode(ET.tostring(self.html))
            f.write(text)
            logger.info("WROTE", data_table_file)

    def __str__(self):
        htmltext = ET.tostring(self.html)
        logger.info("SELF", htmltext)
        return htmltext


HREF_TEMPLATE = "href_template"
ID_TEMPLATE = "id_template"


class Templater:
    """
    inserts strings into templates
    uses format, not f-strings
    """

    def __init__(self, template=None, regex=None, href_template=None, id_template=None, repeat=0):
        self.template = template
        self.regex = regex
        self.href_template = href_template
        self.id_template = id_template
        self.repeat = repeat

    def __str__(self):
        return f"{str(self.template)}\n{str(self.regex)}\nhref: {str(self.href_template)}\nid: {str(self.id_template)}"

    def match_template(self, strng, template_type=None):
        if template_type is None:
            template = self.template
        if template_type == HREF_TEMPLATE:
            template = self.href_template
        elif template_type == ID_TEMPLATE:
            template = self.id_template
        else:
            logger.error(f"***Bad template type** {template_type}")
            return None
        return Templater.get_matched_template(self.regex, strng, self.template)

    def match_href_template(self, strng):
        href = Templater.get_matched_template(self.regex, strng, self.href_template)
        return href

    @classmethod
    def get_matched_templates(cls, regex, strings, template):
        matched_templates = []
        for strng in strings:
            matched_template = cls.get_matched_template(regex, strng, template)
            matched_templates.append(matched_template)
        return matched_templates

    # class Templater

    @classmethod
    def get_matched_template(cls, regex, strng, template):
        """
        matches strng with regex-named-capture-groups and extracts matches into template
        :parem regex: with named captures
        :param strng: to match
        :param template: final string with named groups in {} to substitute
        :return substituted strng

        Simple Examaple
        template = "{DecRes}_{decision}_{type}_{session}"
        regex = "(?P<DecRes>Decision|Resolution)\\s(?P<decision>\\d+)/(?P<type>CMA|CMP|CP)\\.(?P<session>\\d+)"
        strng = "Decision 12/CMP.5"
        returns 'Decision_12_CMP_5'

        but more complex templates can include repeats. However these are NOT f-strings and do not use eval()
        """
        if regex is None:
            logger.error(f"**************regex is None")
            return None
        if template is None:
            raise ValueError("template shuuld not be None")
        match = re.search(regex, strng)
        if not match:
            matched_template = None
        else:
            template_values = match.groupdict()
            matched_template = template.format(**template_values)
        return matched_template

    # class Templater

    @classmethod
    def create_template(cls, template=None, regex=None, href_template=None, id_template=None):
        templater = Templater()
        if not regex:
            logger.error(f"no regex in templater")
            return None
        templater.regex = regex
        templater.template = template
        templater.href_template = href_template
        templater.id_template = id_template
        return templater

    def split_span_by_templater(self, span, repeat=0, debug=False):
        """split a span into 3 sections but matching substring
        <parent><span attribs>foo bar plugh</span></parent>
        if "bar" matches regex gives:
        <parent><span attribs>foo </span><span attribs id=id>bar</span><span attribs> plugh</span></parent>
        if count > 1, repeats the splitting on the new RH span , decrementing repeat until zero

        :param span: the span to split
        :param regex: finds (first) match in span.text and extracts matched text into middle span
        :param id: if string, adds id to new mid element; if array of len 3 gives id[0], id[1], id[2] to each new span
        :param href: adds <a href=href>matched-text</a> as child of mid span (1) if un.GENERATE generates HREF
        :param clazz: 3-element array to add class attributes to split sections
        :param repeat: repeats split on (new) rh span
        :return: None if no match, else first match in span
        """
        if span is None:
            logger.error(f"span is None")
            return None
        type_span = type(span)
        parent = span.getparent()

        if span is None or type_span is not lxml.etree._Element \
                or parent is None or span.tag != 'span' or repeat < 0:
            return None
        text = span.text
        if text is None:
            return None
        match = None
        regex = self.regex
        if regex is None:
            logger.error(f"************no regex in templater")
            return
        try:
            match = re.search(regex, text)
        except Exception as e:
            logger.error(f"bad match {regex} /{e} => {text}")
            return
        idx = parent.index(span)
        # enhanced_regex = EnhancedRegex(regex=regex)
        if match:
            anchor_text = match.group(0)
            if debug:
                logger.info(f"matched: {regex} {anchor_text}")
            # href_new = enhanced_regex.get_href(href, text=anchor_text)
            # make 3 new spans
            # some may be empty
            offset = 1
            offset, span0 = XmlLib.create_span(idx, match, offset, parent, span, text, "start")
            mid = self.create_new_span_with_optional_a_href_child(parent, idx + offset, span, anchor_text)
            offset += 1
            offset, span2 = XmlLib.create_span(idx, match, offset, parent, span, text, "end")
            id_markup = False
            ids = None

            parent.remove(span)
            # recurse in RH split
            if repeat > 0 and span2 is not None:
                repeat -= 1
                self.split_span_by_templater(span2, repeat=repeat, debug=debug)
        return match

    # class Templater

    def create_new_span_with_optional_a_href_child(self, parent, idx, span, textx, href=None):
        """
        :param parent: of span, to which new soan is attached
        :param idx: index of new child span relative to old span
        :param span: old span
        :param textx: text to add
        :param href: optional href (address) to add
        :return: new span
        """
        new_span = lxml.etree.Element("span")

        if self.href_template:
            href = self.match_href_template(textx)
            XmlLib.create_and_add_anchor(href, new_span, textx)
        elif href:
            XmlLib.create_and_add_anchor(href, new_span, textx)
        else:
            new_span.text = textx

        new_span.attrib.update(span.attrib)
        parent.insert(idx, new_span)
        return new_span

    # class Templater

    @classmethod
    def get_anchor_templaters(cls, markup_dict, template_ref_list):
        """
        templates are of the form
            "paris" : {
                "regex": "([Tt]he )?Paris Agreement",
                "target_template": "https://unfccc.int/process-and-meetings/the-paris-agreement",

            more complex:

            "decision": {
                "example": ["decision 1/CMA.2", "noting decision 1/CMA.2, paragraph 10 and ", ],
                "regex": [f"decision{WS}(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})",
                          f"decision{WS}(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})(,{WS}paragraph(?P<paragraph>{WS}{INT}))?",
                          ],
                "href": "FOO_BAR",
                "split_span": True,
                "idgen": "NYI",
                "_parent_dir": f"{PARENT_DIR}", # this is given from environment
                "target_template": "{_parent_dir}/{type}_{session}/Decision_{decision}_{type}_{session}",
    },


        """
        templater_list = []

        for template_ref in template_ref_list:
            sub_markup_dict = markup_dict.get(template_ref)
            if not sub_markup_dict:
                logger.error(f"cannot find template {template_ref}")
                continue
            regex = sub_markup_dict.get("regex")
            target_template = sub_markup_dict.get("target_template")
            id_template = sub_markup_dict.get("id_template")
            href_template = sub_markup_dict.get("href_template")
            if not regex:
                raise Exception(f"missing key regex in {template_ref} {markup_dict} ")
                continue
            templater = Templater.create_template(
                regex=regex, template=target_template, href_template=href_template, id_template=id_template)
            templater_list.append(templater)
        return templater_list

    # class Templater

    @classmethod
    def create_id_from_section(cls, html_elem, id_xpath, template=None, regex=None, maxchar=100):
        """create id from html content
        id_xpath is where to find the content
        template is how to transform it
        """
        divs = html_elem.xpath(id_xpath)
        if len(divs) == 0:
            logger.error(f"cannot find id {id_xpath}")
            return
        div = divs[0]
        div_content = ''.join(html_elem.itertext())
        templater = Templater.create_template(template, regex)
        id = templater.match_template(div_content, template_type=ID_TEMPLATE)
        logger.debug(f">>id {id}")
        return id


# class Web:
#     def __init__(self):
#         root = tk.Tk()
#         site = "http://google.com"
#         self.display_html(root, site)
#         root.mainloop()
#
#     @classmethod
#     def display_html(cls, master, site):
#         frame = tkinterweb.HtmlFrame(master)
#         frame.load_website(site)
#         frame.pack(fill="both", expand=True)
#
#     @classmethod
#     def tkinterweb_demo(cls):
#         tkinterweb.Demo()


def main():
    XmlLib().test_recurse_sections()  # recursively list sections


#    test_data_table()
#    test_xml()

#    web = Web()
#    Web.tkinterweb_demo()


def test_xml():
    xml_string = "<a>foo <b>and</b> with <d/> bar</a>"
    logger.debug(XmlLib.remove_all_tags(xml_string))


def test_data_table():
    data_table = DataTable("test")
    data_table.add_column_heads(["a", "b", "c"])
    data_table.add_row_old(["a1", "b1", "c1"])
    data_table.add_row_old(["a2", "b2", "c2"])
    data_table.add_row_old(["a3", "b3", "c3"])
    data_table.add_row_old(["a4", "b4", "c4"])
    html = ET.tostring(data_table.html).decode("UTF-8")
    HOME = os.path.expanduser("~")
    with open(os.path.join(HOME, "junk_html.html"), "w") as f:
        f.write(html)
    pprint.pprint(html)


def test_replace_strings_with_unknown_encodings():
    s = """
    form to mean âaerosol particlesâ. Aerosols 
    """
    tuple_list = [
        ("â", "‘"),
        ("â", "’"),
    ]
    target = "âaerosol particlesâ."
    assert len(tuple_list[0][0]) == 3
    sout = XmlLib.iteratively_replace_strings(tuple_list, target)
    logger.debug(sout)
    assert sout == "‘aerosol particles’."


def test_replace_element_child_text_with_unknown_encodings():
    tuple_list = [
        ("â", "‘"),
        ("â", "’"),
    ]
    target = "âaerosol particlesâ."
    elem = lxml.etree.Element("foo")
    elem.text = target
    assert elem.text == "â\x80\x98aerosol particlesâ\x80\x99."
    XmlLib.replaceStrings(elem, tuple_list)
    assert elem.text == "‘aerosol particles’."


if __name__ == "__main__":
    print("running file_lib main")
    main()
else:
    #    print("running file_lib main anyway")
    #    main()
    pass
