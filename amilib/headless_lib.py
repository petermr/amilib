"""classmethods from headless tests. May be useful elsewhere

"""
import csv
import re
from collections import Counter
from pathlib import Path
import lxml.etree as ET
from lxml.html import HTMLParser

from amilib.ami_html import HtmlLib
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.wikimedia import WikidataLookup
from amilib.xml_lib import HtmlElement, XmlLib

logger = Util.get_logger(__name__)


class HeadlessLib:

    @classmethod
    def predict_encoding(cls, file_path: Path, n_lines: int = 20) -> str:
        import chardet
        '''Predict a file's encoding using chardet'''

        # Open the file as binary data
        with Path(file_path).open('rb') as f:
            # Join binary lines for specified number of lines
            rawdata = b''.join([f.readline() for _ in range(n_lines)])

        return chardet.detect(rawdata)['encoding']

    @classmethod
    def edit_title(cls, dict_html):
        """edit main title, extracting brackets and guillemets"""
        h4 = dict_html.xpath(".//h4[contains(@class, 'bg-primary')]")
        if len(h4) == 1:
            title = h4[0].text
            parent = h4[0].getparent()
            title = cls.extract_chunks(title, "(.*)«([^»]*)»(.*)", parent, "wg")
            title = cls.extract_chunks(title, "(.*)\\(([^\\)]*)\\)(.*)", parent, "paren")
            title = title.strip()
            # lowercase unless string has embedded uppercase
            if sum(i.isupper() for i in title[1:]) == 0:
                title = title.lower()
            h4[0].text = title
            return title

    @classmethod
    def extract_chunks(cls, text, regex, parent, tag, count=999):
        """extracts inline chunks and closes up the text
        can be be iterative
        creates <div> children of <parent> and labels them with a class/tag attribute
        then adds chunks
        :param text: chunk to analyse
        :param regex: has 3 groups (pre, chunk, post)
        :param paraent: to add results to
        :param count: number of times to repeat (default = 999)
        :return: de-chunked text"""
        t = text
        while True:
            match = re.match(regex, t)
            if not match:
                return t
            wg = ET.SubElement(parent, "div")
            wg.attrib["class"] = tag
            wg.text = match.group(2)
            t = match.group(1) + match.group(3)
        return t

    @classmethod
    def analyze_parent(cls, h6):
        p_string = """
    <div class="p-3 small">
    <h6 class="fs-6">Parent-term</h6>
    <ul class="items text-muted fs-6"><li><span class="specificlink" data-report="AR6" data-phrase="Mass balance/budget (of glaciers or ice sheets)" data-phraseid="2202">Mass balance/budget (of glaciers or ice sheets)</span></li></ul>
    </div>
    """
        id_phrases = cls.extract_id_phrases(h6)
        if len(id_phrases) != 1:
            raise Exception(f"expected 1 parent, found {id_phrases}")
        return id_phrases[0]

    @classmethod
    def extract_id_phrases(cls, h6):
        """"""

        lis = h6.xpath("../ul/li")
        id_phrases = []
        for li in lis:
            span = li.xpath("span")[0]
            phrase = span.text
            data_phrase = span.attrib["data-phrase"]
            if phrase != data_phrase:
                logger.info(f"phrase {phrase} != data_phrase {data_phrase}")
            phrase_id = span.attrib["data-phraseid"]
            id_phrases.append((phrase_id, phrase))
        return id_phrases

    @classmethod
    def analyze_sub_terms(cls, entry_html):
        """
        <div class="ms-2 p-1 small text-muted">
    <h6 class="mb-0">Sub-terms</h6>
    <ul class="items mb-0">
    <li><span class="specificlink" data-report="AR6" data-phrase="Agricultural and ecological drought" data-phraseid="5559">Agricultural and ecological drought</span></li>
    <li><span class="specificlink" data-report="AR6" data-phrase="Hydrological drought" data-phraseid="5557">Hydrological drought</span></li>
    <li><span class="specificlink" data-report="AR6" data-phrase="Megadrought" data-phraseid="209">Megadrought</span></li>
    <li><span class="specificlink" data-report="AR6" data-phrase="Meteorological drought" data-phraseid="5587">Meteorological drought</span></li>
    </ul>
    </div>
        :return: list of (id, term) triples
        """
        id_phrases = cls.extract_id_phrases(entry_html)
        if len(id_phrases) == 0:
            raise Exception(f"expected 1 or more sub-terms, found {id_phrases}")
        return id_phrases

    @classmethod
    def analyze_references(cls, entry_html):
        """
        the text is messy. Seems to be
        - text <br>
        - text <br>
        <div class="ms-2 p-1 small text-muted">
    <h6 class="mb-0">References</h6> - SpanMarker, 2021: Reporting and accounting of LULUCF activities under the Kyoto Protocol. United Nations Framework Convention on Climate Change (SpanMarker), Bonn, Germany. Retrieved from: https://unfccc.int/topics/land-use/workstreams/land-use-land-use-change-and-forestry-lulucf/reporting-and-accounting-of-lulucf-activities-under-the-kyoto-protocol<br> - SpanMarker, 2021: Reporting and Review under the Paris Agreement. United Nations Framework Convention on Climate Change (SpanMarker), Bonn, Germany. Retrieved from: https://unfccc.int/process-and-meetings/transparency-and-reporting/reporting-and-review-under-the-paris-agreement<br>
    </div>
        """
        divs = entry_html.xpath(".//div[h6]")
        ld = len(divs) > 1
        for div in divs:
            if ld:
                # logger.info(f" DIV: {lxml.etree.tostring(div, pretty_print=True)}")
                pass
            nodes = div.xpath("./node()")
            texts = []
            text = "NONE"
            for node in nodes:
                if type(node) is HtmlElement:
                    if node.tag == "h6":
                        pass
                    elif node.tag == "br":
                        texts.append(text)
                    else:
                        raise Exception(f"unexpected tag: {node.tag}")
                elif type(node) is ET._ElementUnicodeResult:
                    text = str(node)
                else:
                    # logger.info(f":text {node}")
                    raise Exception(f" unknown node {type(node)}")
                if len(texts) == 0:
                    # logger.info("NO TEXTS")
                    pass
                else:
                    logger.info(f"texts: {len(texts)}:: {texts}")

    @classmethod
    def remove_styles(cls, entry_html):
        """

        """
        style_elems = entry_html.xpath(".//*[@style]")
        for style_elem in style_elems:
            style_elem.attrib["style"] = None

    @classmethod
    def edit_paras(cls, entry_html):
        """

        """
        # TODO fix regex to find missinf first sentences
        regex = re.compile("(.)\\s+(.*)")
        # this may not be universal
        mainclass = "fs-6 p-2 mb-0"
        ps = entry_html.xpath(f"//p")
        for p in ps:
            if p.text is None:
                continue
            # if p.text.startswith("A change in functional or"):
            #     logger.info(f"CHANGE")
            clazz = p.attrib.get('class')
            if clazz == mainclass:
                # this is crude; split first sentence into 2 paras
                text = ET.tostring(p, encoding=str)
                # find period to split sentence
                # TODO some paragraphs are not split
                # match = re.match(regex, s)
                split = re.split("\\.\\s+", text, 1)
                if len(split) == 1:
                    cls.make_definition_para(p)
                else:
                    div = None
                    for tag in ["p", "span"]:
                        ss = "<div>" + split[0] + "." + f"</{tag}><{tag}>" + split[1] + f"</div>"
                        # reparse; there may be subelements such as span
                        try:
                            div = ET.fromstring(ss)
                            break
                        except Exception as e:
                            pass
                    if div is None:
                        logger.warning(f"FAIL {ss}")
                        continue
                    p.getparent().replace(p, div)
                    p0 = div.xpath("./p")[0]
                    cls.make_definition_para(p0)

    @classmethod
    def make_definition_para(cls, p):
        p.attrib["style"] = "font-weight: bold"
        p.attrib["class"] = "definition"

    @classmethod
    def edit_lists(cls, entry_html, parent_id_set=None, subterm_id_set=None):
        """div class="p-3 small"><h6 class="fs-6">Parent-term<"""

        # h6s = entry_html.xpath(f".//div[@class='p-3 small']/h6")
        dh6s = entry_html.xpath(f".//div[h6]")
        if len(dh6s) == 0:
            # logger.warning(f"No div/h6 found")
            return
        for dh6 in dh6s:
            h6 = dh6.xpath("./h6")[0]
            txt = h6.text.strip()
            if txt == "Parent-term":
                parent_id = cls.analyze_parent(h6)
                parent_id_set.add(parent_id)
            elif txt == "Sub-terms":
                subterm_id_list = cls.analyze_sub_terms(h6)
                for id_phrase in subterm_id_list:
                    subterm_id_set.add(id_phrase[0])
            elif txt == "References":
                cls.analyze_references(h6)
            else:
                raise Exception(f"unknown list title {txt}")

        """
    
        <div class="ms-2 p-1 small text-muted">
    <h6 class="mb-0">Sub-terms</h6>
    <ul class="items mb-0"><li><span class="specificlink" data-report="AR6" data-phrase="Household carbon footprint" data-phraseid="5376">Household carbon footprint</span></li></ul>
    </div>
    <div class="ms-2 p-1 small text-muted">
    <h6 class="mb-0">References</h6> - Wiedmann, T. and Minx, J. C. (2008). A definition of carbon footprint, in C. Pertsova (ed.), Ecological Economics Research Trends, Nova Science Publishers, Hauppauge NY, chapter 1, pp. 1â11. URL: https://www.novapublishers.com/catalog/product info.php?products id=5999<br>
    </div>"""

    @classmethod
    def make_targets(cls, text):
        """creates a list to search with
        if text ends with 's' returns ['foos', 'foo']"""
        ss = []
        if text is not None:
            text = cls.make_title_id(text)
            ss.append(text)
            if text[-1:] == 's':
                ss.append(text[:-1])
        return ss

    @classmethod
    def markup_em_and_write_files(cls, entry_html_list, entry_by_id):
        """create a Counter of <em> to see which might be terms"""
        em_counter = Counter()
        missing_targets = set()
        for entry in entry_html_list:
            entry_html = entry[0]
            out_path = entry[1]
            name = entry_html.xpath(".//body/a/@name")
            name = name[0] if len(name) > 0 else ""
            # TODO include parent/subterms
            cls.find_mentions(em_counter, entry_by_id, entry_html, missing_targets)
            HtmlLib.write_html_file(entry_html, out_path, debug=True)
        return missing_targets, em_counter

    @classmethod
    def find_mentions(cls, em_counter, entry_by_id, entry_html, missing_targets):
        """TODO Badly need a class to manage this"""
        ems = entry_html.xpath(".//em")
        for em in ems:
            text = cls.make_title_id(em.text)
            em_targets = cls.make_targets(text)
            matched = None
            for em_target in em_targets:
                matched0 = cls.match_target_in_dict(em_target, entry_by_id)
                matched = matched0 if matched0 is not None else matched
            if matched:
                em_counter[em.text] += 1
                a = ET.SubElement(em, "a")
                a.attrib["href"] = "#" + em_target
                a.attrib["class"] = "mention"
                a.text = em.text
                em.text = ""
            else:
                missing_targets.add(em.text)

    @classmethod
    def find_wikidata(cls, entry_html):
        term = entry_html.xpath("//a/name")[0]
        term = term.replace("_", " ").strip()
        logger.info(f"term {term}")

        wikidata_lookup = WikidataLookup()
        qitem0, desc, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
        logger.info(f"qitem {qitem0}")

    @classmethod
    def match_target_in_dict(cls, em_target, entry_by_id):
        target_id = cls.make_title_id(em_target)
        match = entry_by_id.get(target_id)
        if match is not None:
            # logger.info(f"MATCHED {match}")
            pass
        return match is not None

    @classmethod
    def extract_term_from_title(cls, entry_html):
        """
        <h4 class="fw-bold fs-5 bg-primary text-light p-2">Aerosol effective radiative forcing (ERFari+aci)  « WGI »</h4>
        NYI
        """
        h4_fs_5 = entry_html.xpath(".//h4[contains(@class,'fs-5') and contains(@class, 'fw-bold')]")

    @classmethod
    def make_title_id(cls, title):
        if title is None:
            return None
        # strip brackets
        match = re.match("(.*)\\(.*", title)
        if match:
            title = match.group(1)
        title_id = title.strip().replace(" ", "_").lower()
        return title_id

    @classmethod
    def write_missing(cls, missing_targets, filename):
        targets = [t for t in missing_targets if t is not None]
        with open(filename, "w") as f:
            for t in sorted(targets):
                f.write(t + "\n")

    @classmethod
    def extract_mention_links(cls, entry_html_list, filename):
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["source", "role", "target", ])
            for (entry_html, _) in entry_html_list:
                name = entry_html.xpath(".//a/@name")[0]
                refs = entry_html.xpath(".//a[@class='mention']")
                for ref in refs:
                    href = ref.attrib["href"][1:]  # first char is hash
                    csvwriter.writerow([name, "mentions", href, ])

    @classmethod
    def extract_parent_subterms(cls, entry_html_list, filename):
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["source", "role", "target", ])
            for role_name, role in [("Parent-term", "parent"), ("Sub-terms", "subterm")]:
                for (entry_html, _) in entry_html_list:
                    name = entry_html.xpath(".//a/@name")[0]
                    refs = entry_html.xpath(f".//div[h6[.='{role_name}']]/ul/li/span")
                    # TODO move to earlier
                    for ref in refs:
                        if ref.text is None:
                            logger.info(f"Null text for name {name}")
                            continue
                        ref_id = cls.make_title_id(ref.text)
                        a = ET.SubElement(ref, "a")
                        a.attrib["href"] = "#" + ref_id
                        a.text = ref.text
                        ref.text = ""
                        csvwriter.writerow([name, role, ref_id, ])

    @classmethod
    def make_glossary(cls, dict_files, out_dir, total_gloss_dir=None, total_glossary=None, debug=True):
        titles = set()
        parent_id_set = set()
        subterm_id_set = set()
        encoding = "UTF-8"
        entry_by_id = dict()
        entry_html_list = []
        for dict_file in dict_files:
            entry_html = ET.parse(str(dict_file), parser=HTMLParser(encoding=encoding)).getroot()
            # remove "Cloae" button
            XmlLib.remove_all(entry_html, ".//div[@class='modal-footer']", debug=False)
            # remove "AR6" button
            XmlLib.remove_all(entry_html, ".//h5[button]", debug=False)

            title = cls.edit_title(entry_html)
            title_id = cls.make_title_id(title)
            dict_body = HtmlLib.get_body(entry_html)
            # html anchor for every element
            entry_a = ET.SubElement(dict_body, "a")
            entry_a.attrib["name"] = title_id
            # are there duplicate titles after trimming and lowercasing
            if entry_by_id.get(title_id) is not None:
                logger.info(f"duplicate title_id {title_id}")
                continue
            entry_by_id[title_id] = entry_html

            cls.remove_styles(entry_html)
            cls.extract_term_from_title(entry_html)
            cls.edit_paras(entry_html)
            cls.edit_lists(entry_html, parent_id_set=parent_id_set, subterm_id_set=subterm_id_set)
            titles.add(title)

            # output
            html_out = HtmlLib.create_html_with_empty_head_body()
            HtmlLib.add_charset(html_out)
            body = HtmlLib.get_body(html_out)

            body.getparent().replace(body, dict_body)
            a = ET.SubElement(dict_body, "a")
            a.attrib["name"] = title_id

            path = cls.create_out_path(dict_file, out_dir)
            if not path:
                continue
            entry_html_list.append((html_out, path))
        logger.info(f"parent: {len(parent_id_set)} {parent_id_set}")
        logger.info(f"parent: {len(subterm_id_set)} {subterm_id_set}")

        logger.info(f"Must fix to write the modified HTML file")

        cls.extract_mention_links(entry_html_list, Path(total_glossary, "mentions.csv"))
        cls.extract_parent_subterms(entry_html_list, Path(total_glossary, "parents.csv"))
        missing_targets, em_counter = cls.markup_em_and_write_files(entry_html_list, entry_by_id)
        cls.write_missing(missing_targets, Path(total_glossary, "missing_em_targets.txt"))
        logger.info(f"entry_dict {len(entry_by_id)}")
        gloss_ids_file = str(Path(total_glossary, "ids.txt"))
        with open(gloss_ids_file, "w") as f:
            for key in sorted(entry_by_id.keys()):
                entry = entry_by_id.get(key)
                f.write(f"{key} {entry.xpath('/html/body/a/@name')}\n")
        if debug:
            logger.info(f"wrote {gloss_ids_file}")
        logger.warning(f"missing targets: {len(missing_targets)} {missing_targets}")
        logger.info(f"em_counter {len(em_counter)} {em_counter}")

    @classmethod
    def make_header(cls, tr):
        th = ET.SubElement(tr, "th")
        th.text = "input"
        tr.append(th)
        th = ET.SubElement(tr, "th")
        th.text = "output"
        tr.append(th)

    @classmethod
    def make_cell(cls, file, output_name, tr, style=None, filename=False):
        td = ET.SubElement(tr, "td")
        td.attrib["style"] = "padding : 4px; margin : 4px; background : #fee;"
        if (filename):
            h3 = ET.SubElement(td, "h3")
            h3.text = output_name
        # html in output glossary
        try:
            body = ET.parse(str(file), parser=HTMLParser()).xpath("//body")[0]
        except Exception as e:
            logger.warning(f"failed to parse {file} giving {e}")
            return
        a = body.xpath("./a")
        divtop = ET.parse(str(file), parser=HTMLParser()).xpath("//body/div")[0]
        if len(a) > 0:
            divtop.insert(0, a[0])
        div = ET.SubElement(td, "div")
        if True or not style:
            style = "margin : 8px; padding : 8px; background : #eee;"
        div.attrib["style"] = style

        div.append(divtop)

    @classmethod
    def create_out_path(cls, dict_file, out_dir):
        path = dict_file
        stem0 = Path(dict_file).stem
        match = re.match("(.+)_(?:[A-Z]|123)$", stem0)
        if match:
            stem = match.group(1)
            path = Path(out_dir, f"{stem}.html")
        return path
