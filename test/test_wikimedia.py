# Tests wikipedia and wikidata methods under pytest
import copy
import pprint
import unittest
from pathlib import Path

import lxml.etree as ET
import requests
from lxml import etree, html

from amilib.ami_dict import AmiDictionary
from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.amix import AmiLib
from amilib.file_lib import FileLib, HEADERS
from amilib.util import Util
from amilib.wikimedia import WikidataLookup, MediawikiParser
# local
from amilib.wikimedia import WikidataPage, WikidataExtractor, WikidataProperty, WikidataFilter, WikipediaPage, \
    WikipediaPara, WiktionaryPage, WikipediaInfoBox
from amilib.xml_lib import XmlLib
from amilib.ami_html import HtmlEditor
from test.resources import Resources
from test.test_all import AmiAnyTest
import warnings
import pytest
import time

"""This runs under Pycharm and also
cd pyami # toplevel checkout
python3 -m test.test_wikidata
"""

WIKIPEDIA_SERVICE_URL="https://en.wikipedia.org"
WIKIPEDIA_SERVICE_NAME="Wikipedia"


TEST_RESOURCES_DIR = Path(Path(__file__).parent.parent, "test", "resources")
# TEMP_DIR = Path(Path(__file__).parent.parent, "temp_oldx_delete")
# DICTIONARY_DIR = Path(os.path.expanduser("~"), "projects", "CEVOpen", "dictionary")
EO_COMPOUND = "eoCompound"
EO_COMPOUND_DIR = Path(Resources.TEST_RESOURCES_DIR, EO_COMPOUND)

"""
tests for Wikimedia routines for Wikipedia and Wikidata
"""

base_test = unittest.TestCase
logger = Util.get_logger(__name__)

class WikipediaTest(base_test):
    """
    tests Wikipedia lookup
    """

    def test_wikipedia_lookup_climate_words_short(self):
        """tests lookup of wikipedia page by name"""
        wordlist_dir = Path(Resources.TEST_RESOURCES_DIR, "wordlists")
        stem = "small_2"  # file stem
        wikipedia_pages = WikipediaPage.lookup_pages_for_words_in_file(stem, wordlist_dir)

    @unittest.skipUnless(AmiAnyTest.IS_PMR, "long and development only")
    def test_wikipedia_lookup_several_word_lists(self):
        """tests multiple lookup of wikipedia page by name"""
        wordlist_dir = Path(Resources.TEST_RESOURCES_DIR, "wordlists")
        wordlists = [
            # "carbon_cycle",
            # "climate_words",
            # "food_ecosystem",
            # "water_cyclone",
            # "poverty",
            "small_2"
        ]
        outdir = Path(Resources.TEMP_DIR, "html", "terms")
        for wordlist_stem in wordlists:
            word_dict = WikipediaPage.lookup_pages_for_words_in_file(wordlist_stem, wordlist_dir)

    def test_wikipedia_page_from_wikidata(self):
        qitem = "Q144362"  # azulene
        wpage = WikidataPage(qitem)
        links = wpage.get_wikipedia_page_links()
        assert links == {'en': 'https://en.wikipedia.org/wiki/Azulene'}
        url = wpage.get_wikipedia_page_link("en")
        assert url == 'https://en.wikipedia.org/wiki/Azulene'

    def test_lookup_wikipedia_commandline(self):
        """

        """
        stem = "small_5"
        wordsfile = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        assert wordsfile.exists(), f"{wordsfile} should exist"
        pyami = AmiLib()
        # args = ["DICT", "--help"]
        # pyami.run_command(args)

        dict_xml = str(Path(Resources.TEMP_DIR, "words", f"{stem}_wikipedia.xml"))
        dict_html = str(Path(Resources.TEMP_DIR, "words", f"{stem}_wikipedia.html"))
        args = ["DICT", "--words", str(wordsfile),
                "--dict", dict_xml,
                "--wikipedia"]
        pyami.run_command(args)


    def test_wikipedia_page_first_para(self):
        """
        creates WikipediaPage.FirstPage object
        """
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term("Greenhouse gas")
        first_para = wikipedia_page.create_first_wikipedia_para()
        assert first_para is not None

    def test_wikipedia_page_first_para_bold_ahrefs(self):
        """
        creates WikipediaPage.FirstPage object , looks for <b> and <a @href>
        TODO fails, needs debugging
        """
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term("Greenhouse gas")
        first_para = wikipedia_page.create_first_wikipedia_para()
        logger.info(f"first_para: {ET.tostring(first_para.para_element)}")
        assert first_para is not None
        bolds =  first_para.get_bolds()
        assert len(bolds) == 2
        assert bolds[0].text == "Greenhouse gases"
        ahrefs =  first_para.get_ahrefs()
        assert len(ahrefs) >= 7
        assert ahrefs[0].text == "atmosphere"
        assert ahrefs[0].attrib.get("href") == "/wiki/Atmosphere"


    def test_wikipedia_page_first_para_sentence_span_tails(self):
        """
        creates WikipediaPage.FirstPage object
        wraps all tails (mixed content text) in spans
        """
        term = "Greenhouse gas"
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        first_para = wikipedia_page.create_first_wikipedia_para()
        assert type(first_para) is WikipediaPara
        # texts = self.get_texts()
        XmlLib.replace_child_tail_texts_with_spans(first_para.para_element)
        tostring = ET.tostring(first_para.para_element).decode("UTF-8")
        print(f"Tailed text: {tostring}")
        assert tostring.startswith("""<p class="wpage_first_para"><b>Greenhouse gases</b><span> (</span><b>GHGs</b><span>) are the gases in an </span><a href="/wiki/Atmosphere" title="Atmosphere">atmosphere</a><span> that trap heat, raising the surface temperature of </span><a href="/wiki/Astronomical_bodies" class="mw-redirect" title="Astronomical bodies">astronomical bodies</a><span> such as Earth. Unlike other gases, greenhouse gases </span><a href="/wiki/Absorption_(electromagnetic_radiation)" title="Absorption (electromagnetic radiation)">absorb</a><span> the </span><a href="/wiki/Electromagnetic_spectrum" title="Electromagnetic spectrum">radiations</a><span> that a </span><a href="/wiki/Outgoing_longwave_radiation" title="Outgoing longwave radiation">planet emits</a><span>, resulting in the </span><a href="/wiki/Greenhouse_effect" title="Greenhouse effect">greenhouse effect</a><span>.</span><sup id="cite_ref-AR6WG1annexVII_1-0" class="reference"><a href="#cite_note-AR6WG1annexVII-1"><span class="cite-bracket">[</span>1<span class="cite-bracket">]</span></a></sup><span> The Earth is warmed by sunlight, causing its surface to </span><a href="/wiki/Radiant_energy" title="Radiant energy">radiate heat</a><span>, which is then mostly absorbed by greenhouse gases. Without greenhouse gases in the atmosphere, the average temperature of </span><a href="/wiki/Earth#Surface" title="Earth">Earth's surface</a><span> would be about &#8722;18&#160;&#176;C (0&#160;&#176;F),</span><sup id="cite_ref-NASACO2_2-0" class="reference"><a href="#cite_note-NASACO2-2"><span class="cite-bracket">[</span>2<span class="cite-bracket">]</span></a></sup><span> rather than the present average of 15&#160;&#176;C (59&#160;&#176;F).</span><sup id="cite_ref-Trenberth2003_3-0" class="reference"><a href="#cite_note-Trenberth2003-3"><span class="cite-bracket">[</span>3<span class="cite-bracket">]</span></a></sup><sup id="cite_ref-:0_4-0" class="reference"><a href="#cite_note-:0-4"><span class="cite-bracket">[</span>4<span class="cite-bracket">]</span></a></sup><span>
</span></p>""")

    @unittest.skip("duplicate")
    def test_wikipedia_page_first_para_sentence_add_brs(self):
        """
        creates WikipediaPage.FirstPage object
        wraps all tails (mixed content text) in spans
        """
        term = "Greenhouse gas"
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        first_para = wikipedia_page.create_first_wikipedia_para()
        assert type(first_para) is WikipediaPara
        XmlLib.replace_child_tail_texts_with_spans(first_para.para_element)
        assert ET.tostring(first_para.para_element) == """
<p><b>Greenhouse gases</b> (<b>GHGs</b>) are the gases in an <a href="/wiki/Atmosphere" title="Atmosphere">atmosphere</a> that trap heat, raising the surface temperature of <a href="/wiki/Astronomical_bodies" class="mw-redirect" title="Astronomical bodies">astronomical bodies</a> such as Earth. Unlike other gases, greenhouse gases <a href="/wiki/Absorption_(electromagnetic_radiation)" title="Absorption (electromagnetic radiation)">absorb</a> the <a href="/wiki/Electromagnetic_spectrum" title="Electromagnetic spectrum">radiations</a> that a <a href="/wiki/Outgoing_longwave_radiation" title="Outgoing longwave radiation">planet emits</a>, resulting in the <a href="/wiki/Greenhouse_effect" title="Greenhouse effect">greenhouse effect</a>.<sup id="cite_ref-AR6WG1annexVII_1-0" class="reference"><a href="#cite_note-AR6WG1annexVII-1"><span class="cite-bracket">&#91;</span>1<span class="cite-bracket">&#93;</span></a></sup> The Earth is warmed by sunlight, causing its surface to <a href="/wiki/Radiant_energy" title="Radiant energy">radiate heat</a>, which is then mostly absorbed by greenhouse gases. Without greenhouse gases in the atmosphere, the average temperature of <a href="/wiki/Earth#Surface" title="Earth">Earth's surface</a> would be about −18&#160;°C (0&#160;°F),<sup id="cite_ref-NASACO2_2-0" class="reference"><a href="#cite_note-NASACO2-2"><span class="cite-bracket">&#91;</span>2<span class="cite-bracket">&#93;</span></a></sup> rather than the present average of 15&#160;°C (59&#160;°F).<sup id="cite_ref-Trenberth2003_3-0" class="reference"><a href="#cite_note-Trenberth2003-3"><span class="cite-bracket">&#91;</span>3<span class="cite-bracket">&#93;</span></a></sup><sup id="cite_ref-:0_4-0" class="reference"><a href="#cite_note-:0-4"><span class="cite-bracket">&#91;</span>4<span class="cite-bracket">&#93;</span></a></sup>
</p>        """

        htmlx = HtmlEditor()
        htmlx.add_style("span", "{border:solid 1px;}")
        htmlx.body.append(first_para.para_element)
        htmlx.write(Path(Resources.TEMP_DIR, "misc", "ghg2.html"))

    def test_insert_br_for_lone_period(self):
        """
        insert a <br/> after a single '.'
        this will be developed to include more complex situations later

        """
        term = "Greenhouse gas"
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        first_para = wikipedia_page.create_first_wikipedia_para()
        assert type(first_para) is WikipediaPara
        XmlLib.add_sentence_brs(first_para.get_texts())
        # assert ET.tostring(first_para.para_element) == 'foo'
        html_file = Path(Resources.TEMP_DIR, "words", "html", "ghg_test.html")
        htmlx = HtmlEditor()
        htmlx.add_style("span", "{background: pink; border: solid 1px blue;}")

        htmlx.body.append(first_para.para_element)
        htmlx.write(html_file, debug=True)




    def test_create_html_dictionary_from_xml(self):
        """
        create semanticHtml from XML dictionary (created by lookup wikipedia)
        """
        xml_dict_file = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "xml", "breward_wikipedia.xml")
        assert xml_dict_file.exists()
        xml_ami_dict = AmiDictionary.create_from_xml_file(xml_dict_file)
        assert xml_ami_dict is not None
        entries = xml_ami_dict.get_ami_entries()
        assert len(entries) == 30, f"{xml_dict_file} should have 30 entries"
        ami_entry = entries[0]
        div = ami_entry.create_semantic_div_from_term()
        html_elem = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html_elem)
        body.append(div)
        path = Path(Resources.TEMP_DIR, "words", "html", "covid.html")
        HtmlLib.write_html_file(
            html_elem, path, debug=True)
        assert path.exists()

    def test_create_html_dictionary_from_words(self):
        """
        create semanticHtml from wordlist and lookup in Wikipedia
        """
        stem = "small_2"  # Reduced from small_10 for faster testing
        words_file = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        assert words_file.exists()
        xml_ami_dict, outpath = AmiDictionary.create_dictionary_from_wordfile(words_file)
        assert xml_ami_dict is not None
        xml_ami_dict.create_html_write_to_file(Path(Resources.TEMP_DIR, "words", "xml", f"{stem}.xml"))
        html_elem = xml_ami_dict.create_html_dictionary(create_default_entry=True, title=stem)
        path = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.html")
        HtmlLib.write_html_file(html_elem, path, debug=True)
        assert path.exists()

    def test_create_html_dictionary_from_words_COMMAND(self):
        """
        create HTML dictionary from amilib commandline
        """
        stem = "small_2"  # Reduced from small_10 for faster testing
        input = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        output_dict = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.html")
        logger.debug(f"output dict: {output_dict}")
        FileLib.delete_file(output_dict)
        args = ["DICT",
                "--words", input,
                "--dict", output_dict,
                "--wikipedia",
                ]
        amilib = AmiLib()
        # create by COMMANDLINE
        amilib.run_command(args)
        # check validity
        assert output_dict.exists()
        dict_elem = HtmlUtil.parse_html_file_to_xml(output_dict)
        assert dict_elem is not None
        assert dict_elem.tag == "html"
        dictionary_elem = dict_elem.xpath("./body/div[@role='ami_dictionary']")[0]
        assert dictionary_elem is not None
        assert dictionary_elem.attrib.get("title") is not None
        entry_divs = dict_elem.xpath("./body/div[@role='ami_dictionary']/div[@role='ami_entry']")
        LEN = 2  # Reduced from 10 for faster testing
        assert len(entry_divs) == LEN

        # validate
        ami_dict = AmiDictionary.create_from_html_file(output_dict)
        assert ami_dict is not None
        assert len(ami_dict.get_ami_entries()) == LEN

    def test_create_from_html_dictionary(self):
        """
        reads a valid HTML ami_dictionary
        """
        dict_file = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "html", "small_10.html")
        assert dict_file.exists(), f"cannot find HTML dictionary {dict_file}"
        ami_dict = AmiDictionary.create_from_html_file(dict_file)
        ami_entries = ami_dict.get_ami_entries()

    def test_create_semantic_html_split_sentences(self):
        """
        create semanticHtml from wordlist and lookup in Wikipedia
        """
        stem = "small_5"
        words_file = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        assert words_file.exists()
        xml_ami_dict, outpath = AmiDictionary.create_dictionary_from_wordfile(words_file)
        assert xml_ami_dict is not None
        xml_ami_dict.create_html_write_to_file(Path(Resources.TEMP_DIR, "words", f"{stem}.html"))
        html_elem = xml_ami_dict.create_html_dictionary(create_default_entry=True)
        path = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.html")
        HtmlLib.write_html_file(html_elem, path, debug=True)
        assert path.exists()

#    @unittest.skip("not yet working")

    def test_flat_disambiguation_page(self):
        """
        annotates disambiguation page
        """
        term = "AGW"
        wpage = WikipediaPage.lookup_wikipedia_page_for_term(term)
        basic_info = wpage.get_basic_information()
        assert basic_info is not None
        central_desc = basic_info.get_central_description()
        assert central_desc == WikipediaPage.WM_DISAMBIGUATION_PAGE
        assert wpage.is_disambiguation_page()
        diambig_list = wpage.get_disambiguation_list()
        html_new = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html_new)
        div = ET.SubElement(body, "div")
        ul = ET.SubElement(div, "ul")


        for i, li in enumerate(diambig_list):
            a = HtmlLib.get_first_object_by_xpath(li, "a")
            if a is not None:
                li_new = ET.SubElement(ul, "li")
                li_new.attrib["id"] = f"li_{i}"
                li_new.append(copy.copy(a))
                delete_button = ET.SubElement(li_new, "button")
                delete_button.attrib["id"] = f"delete_{i}"
                delete_button.text = "delete"
                li_new.append(delete_button)
                script = ET.SubElement(li_new, "script")
                script.text = f"""

    const button_{i} = document.getElementById('delete_{i}');
    const li_{i} = document.getElementById('li_{i}');
    button_{i}.addEventListener('click', (button) => {{button.remove()}});
                        """
            print(f"a {ET.tostring(script)}")

            """
              <button id="addButton">Add "OK"</button>

  <div id="container"></div>

  <script>
    // Get references to the button and the container div
    const button = document.getElementById('addButton');
    const container = document.getElementById('container');

    // Set up the event listener for the button
    button.addEventListener('click', () => {
      // Add "OK" to the container div
      const newContent = document.createElement('p');
      newContent.textContent = 'OK';
      container.appendChild(newContent);
   	  button.remove(); 
    });
  </script>
"""
        html_out = Path(Resources.TEMP_DIR, "html", "wiki", f"{term.lower().replace(' ', '_')}.html")
        HtmlLib.write_html_file(html_new, html_out, debug=True)


    def test_edit_disambiguation_page(self):
        """
        edits disambiguation page
        """
        term = "Tipping point"
        wpage = WikipediaPage.lookup_wikipedia_page_for_term(term)
        assert wpage is not None

        # html_file = Path(Resources.TEST_RESOURCES_DIR,"html", "tipping_disambig.html")
        # assert html_file.exists()
        # local_html = HtmlLib.parse_html(html_file)
        #
        # wpage = WikipediaPage.lookup_wikipedia_page_for_term(term)
        basic_info = wpage.get_basic_information()
        assert basic_info is not None
        central_desc = basic_info.get_central_description()
        assert central_desc == WikipediaPage.WM_DISAMBIGUATION_PAGE
        assert wpage.is_disambiguation_page()
        div = XmlLib.get_single_element(wpage.html_elem, "//*[@id='mw-content-text']")
        if div is None:
            logger.error("no 'mw-content-text'")
            return
        li_list = div.xpath(".//li")
        for li in li_list:
            self.get_target_first_para_text(li)

    @classmethod
    def get_target_first_para_text(cls, elem_with_a_href):

        a_list = elem_with_a_href.xpath(".//a[@href]")
        if len(a_list) == 0:
            elem_text = XmlLib.get_text(elem_with_a_href)
            logger.debug(f"NO hyperlink for: {elem_text}")
            return
        a_elem = a_list[0]
        href = a_elem.attrib['href']
        wp_target = f"{WikipediaPage.WIKIPEDIA_EN}{href}"
        wp_page = WikipediaPage.lookup_wikipedia_page_for_url(wp_target)
        if wp_page is None:
            logger.error(f"cannot find page {href}")
            return
        desc = wp_page.create_first_wikipedia_para()
        text = XmlLib.get_text(desc.para_element)
        print(f"desc {text}")

    def test_create_basic_info_for_page(self):
        """
        extract table with basic info for a wikipedia page
        """
        url = "https://en.wikipedia.org/wiki/Jawaharlal_Nehru_University"
        wpage = WikipediaPage.lookup_wikipedia_page_for_url(url)
        assert wpage is not None
        basic_info = wpage.get_basic_information()
        assert basic_info is not None
        href_id = basic_info.get_wikidata_href_id()
        assert href_id == ('https://www.wikidata.org/wiki/Special:EntityPage/Q1147063', 'Q1147063')
        image_url = basic_info.get_image_url()
        assert image_url == 'https://en.wikipedia.org//wiki/File:Jawaharlal_Nehru_University_Logo_vectorized.svg'

    def test_get_leading_image_in_page(self):
        """
from    "https://en.wikipedia.org/wiki/Jawaharlal_Nehru_University

    <div class="thumb tmulti tright">
      <div class="thumbinner multiimageinner" style="width:234px;max-width:234px">
        <div class="trow">
          <div class="tsingle" style="width:232px;max-width:232px">
            <div class="thumbimage">
              <span typeof="mw:File">
                <a href="/wiki/File:JNU_Admin.JPG" class="mw-file-description">
                  <img alt="Administration building at JNU campus" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/230px-JNU_Admin.JPG" decoding="async" width="230" height="173" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/345px-JNU_Admin.JPG 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/460px-JNU_Admin.JPG 2x" data-file-width="2048" data-file-height="1536">
                </a>
              </span>
            </div>
          </div>
        </div>
        <div class="trow" style="display:flex">
          <div class="thumbcaption">Administration building at JNU</div>
        </div>
      </div>
    </div>

    OR

THIS SEEMS TO BE THE BEST
<figure class="mw-default-size" typeof="mw:File/Thumb">
	<a href="/wiki/File:Stubble_field_in_Brastad.jpg" class="mw-file-description">
	  <img src="//upload.wikimedia.org/wikipedia/commons/thumb/9/96/Stubble_field_in_Brastad.jpg/220px-Stubble_field_in_Brastad.jpg" decoding="async" width="220" height="147" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/96/Stubble_field_in_Brastad.jpg/330px-Stubble_field_in_Brastad.jpg 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/96/Stubble_field_in_Brastad.jpg/440px-Stubble_field_in_Brastad.jpg 2x" data-file-width="5472" data-file-height="3648">
	</a>
	<figcaption>
		Stubble field in <a href="/wiki/Brastad" title="Brastad">Brastad</a>, Sweden
	</figcaption>
</figure>
        """

    def test_get_thumb_image(self):
        """
        look for first div[@class='thumbimage']
        """
        """
        <div class="thumbimage">
          <span typeof="mw:File">
            <a href="/wiki/File:JNU_Admin.JPG" class="mw-file-description">
              <img alt="Administration building at JNU campus" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/230px-JNU_Admin.JPG" decoding="async" width="230" height="173" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/345px-JNU_Admin.JPG 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/460px-JNU_Admin.JPG 2x" data-file-width="2048" data-file-height="1536">
            </a>
          </span><
        /div>
        """
        """
        <div class="thumb tmulti tright">
          <div class="thumbinner multiimageinner" style="width:234px;max-width:234px">
            <div class="trow">
              <div class="tsingle" style="width:232px;max-width:232px">
                <div class="thumbimage">
                  <span typeof="mw:File">
                    <a href="/wiki/File:JNU_Admin.JPG" class="mw-file-description">
                      <img alt="Administration building at JNU campus" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/230px-JNU_Admin.JPG" decoding="async" width="230" height="173" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/345px-JNU_Admin.JPG 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c6/JNU_Admin.JPG/460px-JNU_Admin.JPG 2x" data-file-width="2048" data-file-height="1536">
                    </a>
                  </span>
                </div>
              </div>
            </div>
            <div class="trow" style="display:flex">
              <div class="thumbcaption">Administration building at JNU</div>
            </div>
          </div>
        </div>"""
        url = "https://en.wikipedia.org/wiki/Jawaharlal_Nehru_University"
        wpage = WikipediaPage.lookup_wikipedia_page_for_url(url)
        assert wpage is not None
        content = wpage.html_elem
        # thumb_multis = content.xpath(".//div[contains(@class,'thumb ')][div[contains(@class,'thumbinner')][div[@class='troe']]")
        thumb_multis = content.xpath(".//div[contains(@class,'thumb ') and div[contains(@class,'thumbinner') and div[@class='trow']]]")
        logger.debug(f"thumb images {len(thumb_multis)}")

    def test_get_table_from_info_box(self):
        """
        <body>
  		  <table class="infobox vcard">
		    <tbody>
            <tr>
              <th colspan="2" class="infobox-above fn org" style="background-color: #cedeff; font-size: 125%;">
                Bay of Bengal
              </th>
            </tr>
            <tr>
              <td colspan="2" class="infobox-image" style="line-height: 1.2; border-bottom: 1px solid #cedeff;">
                <span class="mw-image-border" typeof="mw:File">
                  <a href="/wiki/File:Bay_of_Bengal_map.png" class="mw-file-description">
                    <img alt="Map of the Bay of Bengal" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/264px-Bay_of_Bengal_map.png" decoding="async" width="264" height="269" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/396px-Bay_of_Bengal_map.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/528px-Bay_of_Bengal_map.png 2x" data-file-width="1000" data-file-height="1019">
                  </a>
                </span>
                <div class="infobox-caption">Map of Bay of Bengal</div>
              </td>
            </tr>
            ...
            </body>
        """
        url = "https://en.wikipedia.org/wiki/Bay_of_Bengal"
        wpage = WikipediaPage.lookup_wikipedia_page_for_url(url)
        assert wpage is not None
        infobox = wpage.get_infobox()
        assert infobox is not None
        assert type(infobox) is WikipediaInfoBox

        table = infobox.get_table()
        table_html = XmlLib.element_to_string(table, pretty_print=True)
        logger.debug(f"infobox {table_html} ")

    def test_get_figure_from_info_box(self):
        """
        This is messy. The image and caption are not systematic
        """
        """
        <body>
  		  <table class="infobox vcard">
		    <tbody>
             <tr>
              <th colspan="2" class="infobox-above fn org" style="background-color: #cedeff; font-size: 125%;">
                Bay of Bengal
              </th>
            </tr>
            <tr>
              <td colspan="2" class="infobox-image" style="line-height: 1.2; border-bottom: 1px solid #cedeff;">
                <span class="mw-image-border" typeof="mw:File">
                  <a href="/wiki/File:Bay_of_Bengal_map.png" class="mw-file-description">
                    <img alt="Map of the Bay of Bengal" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/264px-Bay_of_Bengal_map.png" decoding="async" width="264" height="269" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/396px-Bay_of_Bengal_map.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/528px-Bay_of_Bengal_map.png 2x" data-file-width="1000" data-file-height="1019">
                  </a>
                </span>
                <div class="infobox-caption">Map of Bay of Bengal</div>
              </td>
            </tr>
            ...
            </body>
        """
        url = "https://en.wikipedia.org/wiki/Bay_of_Bengal"
        wpage = WikipediaPage.lookup_wikipedia_page_for_url(url)
        assert wpage is not None
        a_elem = wpage.extract_a_elem_with_image_from_infobox()
        assert a_elem is not None
        img_elems = a_elem.xpath("img")
        assert len(img_elems) > 0
        # these URLs and their content are fragile
        assert XmlLib.element_to_string(img_elems[0]) == \
            '<img alt="A map of the Bay of Bengal" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/330px-Bay_of_Bengal_map.png" decoding="async" width="264" height="269" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/500px-Bay_of_Bengal_map.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bay_of_Bengal_map.png/960px-Bay_of_Bengal_map.png 2x" data-file-width="1000" data-file-height="1019"/>\n'

    def cleartest_clean_disambiguation_page(self):
        """
        includes or excludes links in WP disambiguation page
        very empirical!
        """
        outdir = Path(Resources.TEMP_DIR, "disambig")
        FileLib.force_mkdir(outdir)
        page_names = [
            "acidification",
            "anthropogenic",
            "katrina",
            "migration",
            "sequestration",
            "superdome",
            "tipping point",
        ]
        disambig_include = [
            "meteorology",
            "science",
            "technical",
        ]
        disambig_exclude = [
            "arts",
            "entertainment",
            "literature",
            "media",
            "music",
            "people",
            "places",
            "proper name",
            "television",
        ]
        for page_name in page_names:
            page_name1 = page_name.replace(" ", "_").lower()
            page_dir = Path(outdir, page_name1)
            page = WikipediaPage.lookup_wikipedia_page_for_term(page_name)
            if page is not None and page.is_disambiguation_page():
                new_page = page.disambiguate(
                    include=disambig_include,
                    exclude=disambig_exclude
                )
                HtmlLib.write_html_file(page.html_elem, Path(page_dir, "disambig.html"), debug=True)
                HtmlLib.write_html_file(page.html_elem, Path(page_dir, "disambig_clean.html"), debug=True)

    def test_wikipedia_page_first_para_empirical_bold_detection(self):
        """
        Empirical approach: Find the first paragraph that starts with a bold or contains a bold near the start.
        This handles cases where the first few paragraphs are metadata/disambiguation.
        """
        term = "Greenhouse gas"
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Get the main content area
        main_elem = wikipedia_page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        # Find all paragraphs
        paras = main_elem.xpath('.//p')
        self.assertGreater(len(paras), 0)
        
        # Empirical logic: Find first paragraph with bold near the start
        first_meaningful_para = None
        for para in paras:
            if not para.text_content().strip():  # Skip empty paragraphs
                continue
                
            # Look for bold elements in this paragraph
            bolds = para.xpath('.//b')
            if not bolds:
                continue
                
            # Check if any bold is near the start (within first 50 characters of text)
            para_text = para.text_content()
            for bold in bolds:
                # Get the position of this bold element in the paragraph text
                # This is a simplified approach - we'll refine it later
                bold_text = bold.text_content()
                if bold_text and len(bold_text) > 0:
                    # If bold text appears in first 50 chars, consider it "near the start"
                    if bold_text in para_text[:50]:
                        first_meaningful_para = para
                        break
            
            if first_meaningful_para:
                break
        
        # Should find a meaningful paragraph
        self.assertIsNotNone(first_meaningful_para, "Should find a paragraph with bold near the start")
        
        # Verify it has the expected content structure
        para_text = first_meaningful_para.text_content()
        self.assertIn("Greenhouse gases", para_text)
        self.assertIn("GHGs", para_text)
        
        # Should have bold elements
        bolds = first_meaningful_para.xpath('.//b')
        self.assertGreater(len(bolds), 0)
        
        # Should have links
        links = first_meaningful_para.xpath('.//a[@href]')
        self.assertGreater(len(links), 0)
        
        print(f"Found meaningful paragraph: {para_text[:100]}...")
        print(f"Bold elements: {[b.text_content() for b in bolds]}")
        print(f"Link count: {len(links)}")




class WikidataTest(base_test):
    """
    lookup wikidata terms, Ids, Requires NET
    """

    def test_lookup_wikidata_acetone(self):
        """
        Lookup single term in Wikidata
        Needs connectivity
        :return:
        """
        term = "acetone"
        wikidata_lookup = WikidataLookup()
        qitem0, desc, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
        assert qitem0 == "Q49546"
        assert desc == "chemical compound"
        # assert wikidata_hits == ['Q49546', 'Q24634417', 'Q329022', 'Q63986955', 'Q4673277']
        assert 'Q49546' in wikidata_hits and len(wikidata_hits) >= 3

    def test_parse_wikidata_page(self):
        qitem = "Q144362"  # azulene
        wpage = WikidataPage(qitem)
        # note "zz" has no entries
        ahref_dict = wpage.get_wikipedia_page_links(["en", "de", "zz"])
        assert ahref_dict == {'en': 'https://en.wikipedia.org/wiki/Azulene',
                              'de': 'https://de.wikipedia.org/wiki/Azulen'}


    def test_lookup_wiki_properties_chemical_compound(self):
        """
        Lookup Wikidata page by Q number and confirm properties
        :return: None
        """
        wiki_page = WikidataPage("Q49546")
        # wiki_page.debug_page()
        description = wiki_page.get_description()
        assert description == "chemical compound"

        type_of_chemical_entity = "Q113145171"  # was "Q11173" (chemical entity)
        qval = wiki_page.get_predicate_object("P31", type_of_chemical_entity)
        assert len(qval) == 1
        wiki_page = WikidataPage("Q24634417")
        qval = wiki_page.get_predicate_object("P31", type_of_chemical_entity)
        assert len(qval) == 0
        # actually a scholarly article
        qval = wiki_page.get_predicate_object("P31", "Q13442814")
        assert len(qval) == 1

    def test_lookup_wikidata_commandline(self):
        """

        """
        stem = "small_2"
        wordsfile = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        assert wordsfile.exists(), f"{wordsfile} should exist"
        pyami = AmiLib()
        # args = ["DICT", "--help"]
        # pyami.run_command(args)

        args = ["DICT",
                "--words", str(wordsfile),
                "--dict", str(Path(Resources.TEMP_DIR, "words", f"{stem}_wikidata.xml")),
                "--wikidata"]
        logger.info(f"args {args}")
        pyami.run_command(args)


    def test_lookup_multiple_terms_solvents(self):
        """
        search multiple terms in Wikidata
        """
        terms = ["acetone", "chloroform"]
        wikidata_lookup = WikidataLookup()
        qitems, descs = wikidata_lookup.lookup_items(terms)
        assert qitems == ['Q49546', 'Q172275']
        assert descs == ['chemical compound', 'chemical compound']

    def test_parse_wikidata_html(self):
        """find Wikidata items with given property
        uses the HTML, tacky but works

        in this case the property is P31 (instance-of) and the value is one of
        three
        <div class="wikibase-snakview-value wikibase-snakview-variation-valuesnak">
                                            <a title="Q11173" href="/wiki/Q11173">chemical compound</a>
                                        </div>

        """
        """
    <div class="wikibase-statementgroupview listview-item" id="P31" data-property-id="P31">
        <div class="wikibase-statementgroupview-property">
            <div class="wikibase-statementgroupview-property-label" dir="auto">
                <a title="Property:P31" href="/wiki/Property:P31">instance of</a>
            </div>
        </div>
        <div class="wikibase-statementlistview">
            <div class="wikibase-statementlistview-listview">
                <div id="Q407418$8A24EA26-7C5E-4494-B40C-65356BBB3AA4" class="wikibase-statementview wikibase-statement-Q407418$8A24EA26-7C5E-4494-B40C-65356BBB3AA4 wb-normal listview-item wikibase-toolbar-item">
                    <div class="wikibase-statementview-rankselector">
                        <div class="wikibase-rankselector ui-state-disabled">
                            <span class="ui-icon ui-icon-rankselector wikibase-rankselector-normal" title="Normal rank"/>
                        </div>
                    </div>
                    <div class="wikibase-statementview-mainsnak-container">
                        <div class="wikibase-statementview-mainsnak" dir="auto">
                            <div class="wikibase-snakview wikibase-snakview-e823b98d1498aa78e139709b1b02f5decd75c887">
                                <div class="wikibase-snakview-property-container">
                                    <div class="wikibase-snakview-property" dir="auto"/>
                                </div>
                                <div class="wikibase-snakview-value-container" dir="auto">
                                    <div class="wikibase-snakview-typeselector"/>
                                    <div class="wikibase-snakview-body">
                                        <div class="wikibase-snakview-value wikibase-snakview-variation-valuesnak">
                                            <a title="Q11173" href="/wiki/Q11173">chemical compound</a>
                                        </div>
                                        ...
    """
        p31 = Path(EO_COMPOUND_DIR, "p31.html")
        tree = etree.parse(str(p31))
        root = tree.getroot()
        child_divs = root.findall("div")
        assert len(child_divs) == 2  # direct children
        child_divs = root.findall(".//div")
        assert len(child_divs) == 109  # all descendants
        snak_views = root.findall(".//div[@class='wikibase-snakview-body']")
        assert len(snak_views) == 6  # snkaviwes (boxes on right)
        # snak_a_views = root.findall(".//div[@class='wikibase-snakview-body']//a[starts-with(@title,'Q')]")
        snak_a_views = root.xpath(".//div[@class='wikibase-snakview-body']//a[starts-with(@title,'Q')]")
        assert len(snak_a_views) == 5  #
        texts = []
        titles = []
        for a in snak_a_views:
            texts.append(a.text)
            titles.append(a.get('title'))
        # assert texts == ['chemical compound',\n 'medication',\n 'p-menthan-3-ol',\n 'menthane monoterpenoids',\n 'LIPID MAPS']
        assert texts == ['chemical compound', 'medication', 'p-menthan-3-ol', 'menthane monoterpenoids', 'LIPID MAPS']
        assert titles == ['Q11173', 'Q12140', 'Q27109870', 'Q66124573', 'Q20968889']

    def test_get_predicate_value(self):
        """tests xpath working of predicate_subject test"""
        tree = html.parse(str(Path(EO_COMPOUND_DIR, "q407418.html")))
        root = tree.getroot()
        hdiv_p31 = root.xpath(".//div[@id='P31']")
        assert len(hdiv_p31) == 1
        qvals = hdiv_p31[0].xpath(".//div[@class='wikibase-snakview-body']//a[starts-with(@title,'Q')]")
        assert len(qvals) == 5

    def test_page_get_values_for_property_id(self):
        """test get all values in triples with given property
        e.g. ?page wdt:P31 ?p31_value
        USEFUL

        """
        page = WikidataPage.create_wikidata_ppage_from_file(Path(EO_COMPOUND_DIR, "q407418.html"))
        qvals = page.get_qitems_for_property_id("P31")
        assert len(qvals) == 5
        assert qvals[0].text == "chemical compound"

    def test_get_property_list(self):
        """gets property list for a page
        """
        page = WikidataPage.create_wikidata_ppage_from_file(Path(EO_COMPOUND_DIR, "q407418.html"))
        property_list = page.get_data_property_list()
        assert len(property_list) == 72
        assert property_list[0].property_name == "instance of"
        assert property_list[0].id == "P31"

    def test_get_predicate_value_1(self):
        tree = html.parse(str(Path(EO_COMPOUND_DIR, "q407418.html")))
        root = tree.getroot()
        qvals = root.xpath(".//div[@id='P31']")[0].xpath(".//div[@class='wikibase-snakview-body']//a[@title='Q11173']")
        assert len(qvals) == 1
        assert qvals[0].text == 'chemical compound'
        qvals = root.xpath(".//div[@id='P31']//div[@class='wikibase-snakview-body']//a[@title='Q11173']")
        assert len(qvals) == 1
        assert qvals[0].text == 'chemical compound'

    def test_get_wikidata_predicate_value(self):
        """searches for instance-of (P31) chemical_compound (Q11173) in a wikidata page
        TODO allow for reading local files directly
        """
        pred_id = "P31"
        obj_id = "Q11173"
        file = str(Path(EO_COMPOUND_DIR, "q407418.html"))
        page = WikidataPage.create_wikidata_ppage_from_file(file)
        assert page is not None
        qval = page.get_predicate_object(pred_id, obj_id)
        assert qval[0].text == 'chemical compound'

    def test_get_title_of_page(self):
        qitem = "q407418"
        page = WikidataPage(qitem)
        title = page.get_title()
        if title == "No title":
            logger.debug(f"page for {qitem}:: {ET.tostring(page.root)}")
        else:
            assert title == "L-menthol"

    def test_get_alias_list(self):
        aliases = WikidataPage("q407418").get_aliases()
        assert len(aliases) >= 5 and "l-menthol" in aliases

    def test_get_description(self):
        desc = WikidataPage("q407418").get_description()
        # assert desc == "chemical compound"
        assert "compound" in desc  # wikidata changed this!! 'organic compound used as flavouring and for analgesic properties'

    def test_attval_contains(self):
        """does a concatenated attavl contain a word
        <th scope="col" class="wikibase-entitytermsforlanguagelistview-cell wikibase-entitytermsforlanguagelistview-language">Language</th>

        """
        language_elems = WikidataPage("q407418").get_elements_for_attval_containing_word(
            "class",
            "wikibase-entitytermsforlanguagelistview-language")
        assert len(language_elems) == 1
        assert language_elems[0].text == 'Language'

    @unittest.skip("bug is comparison of sets, needs fixing")
    def test_find_left_properties_and_statements(self):
        """
        TODO comparison of retrieved properties
            <div class="wikibase-snaklistview">
                <div class="wikibase-snaklistview-listview">
                    <div class="wikibase-snakview wikibase-snakview-755d14b02a41025911e80439cb6ed31dcc966768">
                        <div class="wikibase-snakview-property-container">
                            <div class="wikibase-snakview-property" dir="auto">
                               <a title="Property:P662" href="/wiki/Property:P662">PubChem CID</a>
                           </div>
                           ...
        """
        # property_list = WikidataPage("q407418").root.xpath(".//"
        #                                                    "div[@class='wikibase-snaklistview']/"
        #                                                    "div[@class='wikibase-snaklistview-listview']/"
        #                                                    "div/"
        #                                                    "div[@class='wikibase-snakview-property-container']/"
        #                                                    "div[@class='wikibase-snakview-property']/"
        #                                                    "a[starts-with(@title,'Property:')]")

        """<div class="wikibase-statementgroupview-property-label" dir="auto">
              <a title="Property:P274" href="/wiki/Property:P274">chemical formula</a></div>
        """
        lookup = "sroperty"
        lookup = "statement"
        property_list = []
        if lookup == "property":
            classx = "wikibase-statementgroupview-property-label"
            selector = f"@class='{classx}'"
            property_selector = f".//div[@class='{classx}']//a[starts-with(@title,'Property:')]"
            property_list = WikidataPage("q407418").root.xpath(property_selector)
        if lookup == "statement":
            """wikibase-statementgroupview listview-item"""
            # selector = f".//div[@class='wikibase-statementgroupview listview-item']"
            selector = f".//div[starts-with(@class,'wikibase-statementgroupview')]"
            selector = f".//div[@data-property-id]"
            selector = f".//div[@data-property-id]/div[@class='wikibase-statementlistview']//a"
            selector = f".//div[@data-property-id]"
            # selector = f".//div[contains(@class,'wikibase-statementgroupview') and contains(@class,'listview-item')]"
            # selector = f".//div[contains(@class,'listview-item')]"

        property_list = WikidataPage("q407418").root.xpath(selector)

        # <!-- property-[statement-list] container TOP LEVEL -->
        # <div class="wikibase-statementgroupview listview-item" id="P31" data-property-id="P31">
        # <!-- property-subject container -->
        # <div class="wikibase-statementgroupview-property">
        #   <div class="wikibase-statementgroupview-property-label" dir="auto"><a title="Property:P31" href="/wiki/Property:P31">instance of</a></div>
        # </div>
        # <!-- statementlist container -->
        # <div class="wikibase-statementlistview">
        # <div class="wikibase-statementlistview-listview">
        # <div id="Q407418$8A24EA26-7C5E-4494-B40C-65356BBB3AA4" class="wikibase-statementview wikibase-statement-Q407418$8A24EA26-7C5E-4494-B40C-65356BBB3AA4 wb-normal listview-item wikibase-toolbar-item">
        # <div class="wikibase-statementview-rankselector"><div class="wikibase-rankselector ui-state-disabled">
        # <!-- "button?" -->
        # <span class="ui-icon ui-icon-rankselector wikibase-rankselector-normal" title="Normal rank"></span>
        # </div></div>
        # <div class="wikibase-statementview-mainsnak-container">
        # <div class="wikibase-statementview-mainsnak" dir="auto"><div class="wikibase-snakview wikibase-snakview-e823b98d1498aa78e139709b1b02f5decd75c887">
        # <div class="wikibase-snakview-property-container">
        # <div class="wikibase-snakview-property" dir="auto"></div>
        # </div>
        # <!-- object-value-container -->
        # <div class="wikibase-snakview-value-container" dir="auto">
        # <div class="wikibase-snakview-typeselector"></div>
        # <div class="wikibase-snakview-body">
        # <div class="wikibase-snakview-value wikibase-snakview-variation-valuesnak"><a title="Q11173" href="/wiki/Q11173">chemical compound</a></div>
        # <div class="wikibase-snakview-indicators"></div>
        # </div>
        # </div>
        # </div></div>
        # <div class="wikibase-statementview-qualifiers"></div>
        # </div>
        # <span class="wikibase-toolbar-container wikibase-edittoolbar-container"><span class="wikibase-toolbar wikibase-toolbar-item wikibase-toolbar-container"><span class="wikibase-toolbarbutton wikibase-toolbar-item wikibase-toolbar-button wikibase-toolbar-button-edit"><a href="#" title=""><span class="wb-icon"></span>edit</a></span></span></span>
        # <div class="wikibase-statementview-references-container">
        # <div class="wikibase-statementview-references-heading"><a class="ui-toggler ui-toggler-toggle ui-state-default"><span class="ui-toggler-icon ui-icon ui-icon-triangle-1-s"></span><span class="ui-toggler-label">0 references</span></a><div class="wikibase-tainted-references-container" data-v-app=""><div class="wb-tr-app"><!----></div></div></div>
        # <div class="wikibase-statementview-references "><div class="wikibase-addtoolbar wikibase-toolbar-item wikibase-toolbar wikibase-addtoolbar-container wikibase-toolbar-container"><span class="wikibase-toolbarbutton wikibase-toolbar-item wikibase-toolbar-button wikibase-toolbar-button-add"><a href="#" title=""><span class="wb-icon"></span>add reference</a></span></div></div>
        # </div>
        # </div><div id="Q407418$A25EE807-DBE3-47CA-9272-00BF975DAEA8" class="wikibase-statementview wikibase-statement-Q407418$A25EE807-DBE3-47CA-9272-00BF975DAEA8 wb-normal listview-item wikibase-toolbar-item">
        # <div class="wikibase-statementview-rankselector"><div class="wikibase-rankselector ui-state-disabled">
        # <span class="ui-icon ui-icon-rankselector wikibase-rankselector-normal" title="Normal rank"></span>
        # </div></div>
        # <div class="wikibase-statementview-mainsnak-container">
        # <div class="wikibase-statementview-mainsnak" dir="auto"><div class="wikibase-snakview wikibase-snakview-87cdd435c7bb91eadb3355615e99ee224aa44984">
        # <div class="wikibase-snakview-property-container">
        # <div class="wikibase-snakview-property" dir="auto"></div>
        # </div>
        # <!-- object-value-container -->
        # <div class="wikibase-snakview-value-container" dir="auto">
        # <div class="wikibase-snakview-typeselector"></div>
        # <div class="wikibase-snakview-body">
        # <div class="wikibase-snakview-value wikibase-snakview-variation-valuesnak"><a title="Q12140" href="/wiki/Q12140">medication</a></div>
        # <div class="wikibase-snakview-indicators"></div>
        # <!-- ..... -->
        # </div>
        # </div></div>
        # </div></div>
        # </div></div><div class="wikibase-addtoolbar wikibase-toolbar-item wikibase-toolbar wikibase-addtoolbar-container wikibase-toolbar-container"><span class="wikibase-toolbarbutton wikibase-toolbar-item wikibase-toolbar-button wikibase-toolbar-button-add"><a href="#" title=""><span class="wb-icon"></span>add reference</a></span></div></div>
        # </div>
        # </div>
        # </div>
        # <span class="wikibase-toolbar-container"></span>
        # <span class="wikibase-toolbar-wrapper"><div class="wikibase-addtoolbar wikibase-toolbar-item wikibase-toolbar wikibase-addtoolbar-container wikibase-toolbar-container"><span class="wikibase-toolbarbutton wikibase-toolbar-item wikibase-toolbar-button wikibase-toolbar-button-add"><a href="#" title="Add a new value"><span class="wb-icon"></span>add value</a></span></div></span></div>
        # </div>"""
        # """wikibase-statementgroupview listview-item"""

        wikidata_page = WikidataPage("q407418")
        data_property_list = wikidata_page.get_data_property_list()
        property_set = set(data_property_list)
        assert 100 >= len(property_set) >= 70
        expected = {[
            'P31', 'P279', 'P361', 'P117', 'P8224', 'P2067', 'P274', 'P233', 'P2017', 'P2054']}
        difference = expected.symmetric_difference(property_set)
        assert expected.issubset(property_set), f"not found in {property_set}"
        assert set(wikidata_page.get_property_id_list()[:10]).difference(expected) == set()
        assert wikidata_page.get_property_name_list()[:10] == [
            'instance of', 'subclass of', 'part of', 'chemical structure', 'molecular model or crystal lattice model',
            'mass', 'chemical formula', 'canonical SMILES', 'isomeric SMILES', 'density']
        property_list = wikidata_page.get_data_property_list()
        assert 108 >= len(property_list) >= 70
        # assert wikidata_page.get_property_id_list()[:10] == [
        #     'P31', 'P279', 'P361', 'P117', 'P8224', 'P2067', 'P274', 'P233', 'P2017', 'P2054']
        assert 'P31' in wikidata_page.get_property_id_list()
        # assert wikidata_page.get_property_name_list()[:10] == [
        #     'instance of', 'subclass of', 'part of', 'chemical structure', 'molecular model or crystal lattice model',
        #     'mass', 'chemical formula', 'canonical SMILES', 'isomeric SMILES', 'density']
        assert "instance of" in wikidata_page.get_property_name_list()

        properties_dict = WikidataProperty.get_properties_dict(property_list)
        dict_str = pprint.pformat(properties_dict)
        assert properties_dict['P662'] == {'name': 'PubChem CID', 'value': '16666'}


    def test_get_instances(self):
        """<div class="wikibase-statementview-mainsnak-container">
<div class="wikibase-statementview-mainsnak" dir="auto"><div class="wikibase-snakview wikibase-snakview-e823b98d1498aa78e139709b1b02f5decd75c887">
<div class="wikibase-snakview-property-container">
<div class="wikibase-snakview-property" dir="auto"></div>
</div>
<div class="wikibase-snakview-value-container" dir="auto">
<div class="wikibase-snakview-typeselector"></div>
<div class="wikibase-snakview-body">
<div class="wikibase-snakview-value wikibase-snakview-variation-valuesnak"><a title="Q11173" href="/wiki/Q11173">chemical compound</a></div>
<div class="wikibase-snakview-indicators"></div>
</div>
</div>
</div></div>
<div class="wikibase-statementview-qualifiers"></div>
</div>"""
        pass

    # @unittest.skip("LONG DOWNLOAD")
    # def test_add_wikidata_to_imageanalysis_output(self):
    #     """creates dictionary from list of terms and looks up Wikidata"""
    #     terms = [
    #         "isopentyl-diphosphate delta-isomerase"
    #         "squalene synthase",
    #         "squalene monoxygenase",
    #         "phytoene synthase",
    #         "EC 2.5.1.6",
    #         "EC 4.4.1.14",
    #         "EC 1.14.17.4",
    #         "ETRL",
    #         "ETR2",
    #         "ERS1",
    #         "EIN4",
    #     ]
    #     with open(Path(RESOURCES_DIR, EO_COMPOUND, "compounds.txt"), "r") as f:
    #         terms = f.readlines()
    #         assert 100 > len(terms) > 87
    #     wikidata_lookup = WikidataLookup()
    #     # qitems, descs = wikidata_lookup.lookup_items(terms)
    #     temp_dir = Path(TEMP_DIR, "wikidata")
    #     temp_dir.mkdir(exist_ok=True)
    #     # limit = 10000
    #     limit = 5
    #     amidict, dictfile = AmiDictionary.create_dictionary_from_words(terms[:limit], title="compounds",
    #                                                                               wikidata=True, outdir=temp_dir)
    #     print(f"wrote to {dictfile}")
    #     assert os.path.exists(dictfile)

    def test_wikidata_extractor(self):
        query = '2-fluorobenzoic acid'
        extractor = WikidataExtractor('en')
        id = extractor.search(query)
        id_dict = extractor.load(id)

    def test_simple_wikidata_query(self):
        """get ID list for query results
        see https://www.wikidata.org/w/api.php for options
        each entry has a small number of attributes (e.g. description, URL, )"""
        query = "isomerase"
        url_str = f"https://www.wikidata.org/w/api.php?" \
                  f"action=wbsearchentities" \
                  f"&search={query}" \
                  f"&language=en" \
                  f"&format=json"
        try:
            response = requests.get(url_str, headers=HEADERS, timeout=10)
            if response.status_code == 429:
                warnings.warn("Wikidata rate limit (429) encountered. Skipping test.")
                pytest.skip("Wikidata rate limit (429) encountered. Skipping test.")
            if response.status_code != 200:
                warnings.warn(f"Wikidata returned status {response.status_code}. Skipping test.")
                pytest.skip(f"Wikidata returned status {response.status_code}. Skipping test.")
            js = response.json()
            # Basic validation that we got a response
            assert "search" in js or "error" in js
        except (requests.RequestException, ValueError) as e:
            warnings.warn(f"Network or JSON error: {e}. Skipping test.")
            pytest.skip(f"Network or JSON error: {e}. Skipping test.")

    def test_wikidata_id_lookup(self):
        """test query wikidata by ID
        """
        ids = "Q11966262"  # "Dyschirius politus" a species of insect
        url_str = f"https://www.wikidata.org/w/api.php?" \
                  f"action=wbgetentities" \
                  f"&ids={ids}" \
                  f"&language=en" \
                  f"&format=json"
        response = requests.get(url_str, headers=HEADERS)
        print(f"First request status: {response.status_code}")
        if response.status_code == 429:
            warnings.warn("Wikidata rate limit (429) encountered. Skipping test.")
            pytest.skip("Wikidata rate limit (429) encountered. Skipping test.")
        if response.status_code != 200:
            warnings.warn(f"Wikidata returned status {response.status_code}. Skipping test.")
            pytest.skip(f"Wikidata returned status {response.status_code}. Skipping test.")
        response_js = response.json()["entities"][ids]
        assert list(response_js.keys()) == ['pageid', 'ns', 'title', 'lastrevid', 'modified', 'type', 'id', 'labels',
                                            'descriptions', 'aliases', 'claims', 'sitelinks']
        assert response_js["id"] == ids
        assert response_js["title"] == "Q11966262"
        assert response_js["labels"]["en"]["value"] == "Dyschirius politus"
        assert response_js["descriptions"]["en"]["value"] == "species of insect"
        key_set = set(list(response_js["claims"].keys()))
        test_set = set(
            list(['P225', 'P105', 'P171', 'P31', 'P685', 'P846', 'P1939', 'P373', 'P815', 'P3151', 'P3186',
                  'P3405', 'P2464', 'P1843', 'P7202', 'P7552', 'P6105', 'P6864', 'P8915', 'P3240', 'P2671',
                  'P3606', 'P8707', 'P10243'])
        )
        assert test_set <= key_set

        # Sleep between requests to avoid rate limiting
        time.sleep(1)

        ids = "P117"  # chemical compound
        url_str = f"https://www.wikidata.org/w/api.php?" \
                  f"action=wbgetentities" \
                  f"&ids={ids}" \
                  f"&language=en" \
                  f"&format=json"
        response = requests.get(url_str, headers=HEADERS)
        print(f"Second request status: {response.status_code}")
        if response.status_code == 429:
            warnings.warn("Wikidata rate limit (429) encountered. Skipping test.")
            pytest.skip("Wikidata rate limit (429) encountered. Skipping test.")
        if response.status_code != 200:
            warnings.warn(f"Wikidata returned status {response.status_code}. Skipping test.")
            pytest.skip(f"Wikidata returned status {response.status_code}. Skipping test.")
        response_js = response.json()["entities"][ids]
        assert list(response_js.keys()) == ['pageid', 'ns', 'title', 'lastrevid', 'modified', 'type', 'datatype', 'id',
                                            'labels', 'descriptions', 'aliases', 'claims']
        assert response_js["id"] == "P117"
        assert response_js["title"] == "Property:P117"
        assert response_js["labels"]["en"]["value"] == "chemical structure"
        assert response_js["descriptions"]["en"][
                   "value"] == "image of a representation of the structure for a chemical compound"
        assert set(['P31', 'P1855', 'P3254', 'P2302', 'P1629', 'P1647', 'P2875', 'P1659']).issubset(
            set(list(response_js["claims"].keys()))
        )

    #        wikidata_page = WikidataPage.create_from_response(response)

    def test_multiple_wikidata_ids(self):
        ids = "P31|P117"
        url_str = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids}&language=en&format=json"
        response = requests.get(url_str, headers=HEADERS)
        json_dict = response.json()
        assert list(json_dict['entities'].keys()) == ['P31', 'P117']
        assert list(json_dict['entities']['P117'].keys()) == [
            'pageid', 'ns', 'title', 'lastrevid', 'modified', 'type', 'datatype', 'id', 'labels',
            'descriptions', 'aliases', 'claims']
        assert json_dict['entities']['P117']['labels']['en']['value'] == 'chemical structure'
        assert json_dict['entities']['P31']['labels']['en']['value'] == 'instance of'

    def test_read_wikidata_filter(self):
        path = Path(Resources.TEST_RESOURCES_DIR, "filter00.json")
        assert path.exists(), f"{path} should exist"
        filter = WikidataFilter.create_filter(path)
        assert filter.json['plugh'] == "xyzzy"
        assert filter.json['filter']['description'] == "chemical"
        assert filter.json['filter'][
                   'regex'] == "(chemical compound|chemical element)", f"found {filter.json['filter']['regex']}"



class WiktionaryTest(AmiAnyTest):
    """
    Tests WiktionaryPage routines
    """
    """
    Think the content structure has changed yet again
    """

    """
    https://en.wiktionary.org/w/index.php?search=bear&title=Special:Search&profile=advanced&fulltext=1&ns0=1
    """

    def test_validate_mw_content_FAIL(self):
        """
        checks that mw_content_text div is correct
        FAIL Wiktionary has changed markup
        """
        term = "curlicue"
        outdir = Path(FileLib.get_home(), "junk")
        nchild = 3

        html_element, mw_content_text = WiktionaryPage.lookup_wiktionary_content(term)

        term = WiktionaryPage.get_term_from_html_element(html_element)
        WiktionaryPage.validate_mw_content(mw_content_text, term=term, outdir=outdir, nchild=nchild)

    @unittest.skip("not yet working")
    def test_lookup_single_term(self):
        """
       test failure to find unkown terms
        """
        html_page = HtmlLib.create_html_with_empty_head_body()
        base = ET.SubElement(html_page, "base")
        base.attrib["href"] = WiktionaryPage.WIKTIONARY_BASE

        term = "nimby"
        html_div = self.create_div_for_term(term)

        html_body = HtmlLib.get_body(html_page)
        html_body.append(html_div)
        html_out = Path(Resources.TEMP_DIR, "wiktionary", f"{term}.html")
        if html_page is not None:
            logger.info(f"wrote to {html_out}")
            HtmlUtil.write_html_elem(html_page, html_out)

    @unittest.skip("not yet working")
    def test_lookup_terms(self):
        """
       test lookup of list of terms in Wiktionary
       Inclucdes some missing terms
        """
        terms = [
            "nimby",
            "fruitcake",
            "KJABSDd",
            "crusty",
            "xjhade",
            "grockle",
        ]
        html_page = WiktionaryPage.lookup_list_of_terms(terms)
        assert html_page is not None
        body = HtmlLib.get_body(html_page)
        assert body is not None
        divs = body.xpath("div")
        assert len(divs) == 4 # only nimby, fruitcake, crusty and grockle are in Wiktionary
        div0 = divs[0]
        # <div class="wiktionary_pos"><p><span class="headword-line"><strong class="Latn headword" lang="en">nimby</strong>
        terms = div0.xpath("p/span/strong")
        assert len(terms) >= 1
        assert terms[0].text == 'nimby'

        html_out = Path(Resources.TEMP_DIR, "wiktionary", f"terms.html")
        logger.info(f"wrote to {html_out}")
        HtmlUtil.write_html_elem(html_page, html_out)



    def test_lookup_plants_write_to_file(self):
        """
        lookup 2 plants
        """
        terms = [
            "parijat",
            "lemon verbena"
        ]
        stem = "plants"
        html_page = WiktionaryPage.lookup_list_of_terms(terms, add_style=None)
        html_out = Path(Resources.TEMP_DIR, "wiktionary", f"{stem}.html")
        logger.info(f"wrote to {html_out}")
        HtmlUtil.write_html_elem(html_page, html_out)
        assert html_out.exists()

    @unittest.skip("not yet working")
    def test_lookup_words_in_file(self):
        """
        read text file and lookup each line
        """
        wordfile = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "chap2.txt")
        assert wordfile.exists()
        with open(wordfile, "r") as f:
            terms = f.readlines()
        assert len(terms) == 63
        terms1 = []
        for term in terms:
            # term = term.lower()
            if len(term.strip()) > 0:
                terms1.append(term)
        assert len(terms1) == 60

        stem = "chap_2"
        html_page = WiktionaryPage.lookup_list_of_terms(terms1, add_style=WiktionaryPage.DEFAULT_STYLE)

        html_out = Path(Resources.TEMP_DIR, "wiktionary", f"{stem}.html")
        logger.info(f"wrote to {html_out}")
        HtmlUtil.write_html_elem(html_page, html_out)
        assert html_out.exists()

    @unittest.skip("not yet working")

    def test_lookup_wordfile_write_html(self):
        """
        read text file and lookup each line
        """
        html_stem = "carbon_cycle"
        wordfile = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{html_stem}.txt")
        outdir = Path(Resources.TEMP_DIR, "wiktionary")

        html_out = WiktionaryPage.loookup_wordlist_file_write_html(wordfile, outdir, html_stem)
        logger.info(f"wrote to {html_out}")
        assert html_out.exists()

    def test_group_languages_pos(self):
        """
        try to group the Wiktionary output (effort 1)
        """
        stem = "peat_bread_cow"
        terms = ["peat", "bread", "cow"]
        terms = ["bread", "cow", "hurricane"]
        outdir = Path(Resources.TEMP_DIR, "wiktionary")
        html_page = WiktionaryPage.lookup_list_of_terms(
            terms, add_style=WiktionaryPage.DEFAULT_STYLE)
        html_out = Path(outdir, f"{stem}.html")
        print (f"wrote {html_out}")
        HtmlUtil.write_html_elem(html_page, html_out)

    def test_create_html(self):

        """
        read toc and try to use it to navigate the linera elements
        """
        terms = [
            "bread",
            "curlicue",
            # "xxqz",
            # "fish",
            # "hydrogen",
            # "opacity",
            # "stubble",
        ]
        stem = "test_words"
        parts_of_speech = [
            "Noun",
            "Verb",
            # "Adjective",

        ]
        languages = "English"
        languages = "Spanish"
        add_toc = True
        add_toc = False

        htmlx = WiktionaryPage.search_terms_create_html(terms, languages, parts_of_speech, add_toc)

        HtmlLib.add_link_stylesheet("wiktionary.css", htmlx)
        outpath = Path(Resources.TEMP_DIR, "wiktionary", f"{stem}.html")
        HtmlUtil.write_html_elem(htmlx, outpath, debug=True)
        assert outpath.exists(), f"output html should exist {outpath}"
        FileLib.copyanything(Path(Resources.TEST_RESOURCES_DIR, "wiktionary", "wiktionary.css"),
                          Path(Resources.TEMP_DIR, "wiktionary", "wiktionary.css"))

    def test_get_ancestor_language(self):
        termx = "curlicue"
        html_element, mw_content_text = WiktionaryPage.lookup_wiktionary_content(termx)

    def test_lookup_wiktionary_command_line(self):
        """
        Looks up words in Wiktionary and creates HTML
        """
        stem = "small_5"
        wordsfile = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        dict_xml = str(Path(Resources.TEMP_DIR, "words", f"{stem}_wiktionary.xml"))
        # dict_html = str(Path(Resources.TEMP_DIR, "words", f"{stem}_wikipedia.html"))

        assert wordsfile.exists(), f"{wordsfile} should exist"
        pyami = AmiLib()

        args = ["DICT",
                "--words", wordsfile,
                "--dict", dict_xml,
                "--wiktionary"]

        pyami.run_command(args)




class MWParserTest(AmiAnyTest):

    def test_wiktionary_mw_parser_complex(self):
        """
        parse complex output
        """
        stems = [
            "bread",
            "curlicue",
            "xyzzy"
        ]

        mw_parser = MediawikiParser(MediawikiParser.WIKTIONARY)

        mw_parser.style_txt = """
        div {border:1px solid red; margin: 2px;}
        div.mw-heading2 {border:5px solid red; margin: 5px; background: #eee;}
        div.mw-heading3 {border:4px solid orange; margin: 4px; background: #ddd;}
        div.mw-heading4 {border:3px solid yellow; margin: 3px; background: #ccc;}
        div.mw-heading5 {border:2px solid green; margin: 2px; background: #bbb;}
        """

        mw_parser.break_classes = [
            "mw-heading mw-heading2",
            "mw-heading mw-heading3",
            "mw-heading mw-heading4",
            "mw-heading mw-heading5",
        ]

        mw_parser.levels = [5, 4, 3, 2]



        for stem in stems:
            input_file = Path(Resources.TEST_RESOURCES_DIR, "wiktionary", f"{stem}.html")
            output = Path(Resources.TEMP_DIR, "mw_wiki", f"{stem}.html")

            mw_parser.parse_nest_write_entry(input_file, output)

    def test_wiktionary_new_parser(self):
        stems = [
            "bread",
            "curlicue",
            "xyzzy",
        ]
        mw_parser = MediawikiParser(target=MediawikiParser.WIKTIONARY)
        for stem in stems:
            input_file = Path(Resources.TEST_RESOURCES_DIR, "wiktionary", f"{stem}.html")
            output = Path(Resources.TEMP_DIR, "mw_wiki", f"{stem}.html")
            mw_parser.parse_nest_write_entry(input_file, output)

    def test_wikipedia_mw_parser(self):
        """
        parse Wikpedia page with MWParser
        """
        stems = [
            "Net_zero_emissions",
            "parijat",
            ]
        for stem in stems:
            input_file = Path(Resources.TEST_RESOURCES_DIR, "wikipedia", f"{stem}.html")
            assert input_file.exists(), f"Wikipedia file should exist {input_file}"

            mw_parser = MediawikiParser()
            # mw_parser.add_div_style(mw_parser.htmlx)
            mw_parser.read_file_and_make_nested_divs(input_file)
            mw_parser.add_div_style(mw_parser.htmlx)

            assert mw_parser.htmlx is not None

            path = Path(Resources.TEMP_DIR, "mw_wiki", f"{stem}.html")
            logger.debug(f"writing {path}")
            HtmlLib.write_html_file(mw_parser.htmlx, path)

    def test_wikimedia_remove_non_content_and_empty(self):
        """
        Parses an arbitrary wikipedia page and removes all elements whih do not hole content
        my be recursi
        """
        stem = "Net_zero_emissions"
        input_file = Path(Resources.TEST_RESOURCES_DIR, "wikipedia", f"{stem}.html")
        assert input_file.exists()
        # htmlx = HtmlUtil.parse_html_file_to_xml(input_file)
        # assert htmlx is not None
        # body = HtmlLib.get_body(htmlx)

        mw_parser = MediawikiParser()
        input_html, body = mw_parser.read_html_path(
            input_file, remove_non_content=True, remove_head=True, remove_empty_elements=False)
        assert input_html is not None and body is not None
        HtmlUtil.write_html_elem(input_html, Path(Resources.TEMP_DIR, "mw_wiki", f"{stem}.html"))

    def test_wikipedia_lookup_direct_entry(self):
        """Test Wikipedia lookup for a direct entry (climate term)."""
        
        # Test with a climate term that should have a direct Wikipedia entry
        term = "climate change"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should find the page
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Should not be disambiguation page
        self.assertFalse(page.is_disambiguation_page())
        
        # Should have content
        main_elem = page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        first_para = page.create_first_wikipedia_para()
        self.assertIsNotNone(first_para)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_disambiguation(self):
        """Test Wikipedia lookup for a disambiguation page (climate term)."""
        
        # Test with a climate term that leads to disambiguation
        term = "AGW"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should find the page
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Should be disambiguation page
        self.assertTrue(page.is_disambiguation_page())
        
        # Should have disambiguation options
        disambig_list = page.get_disambiguation_list()
        self.assertIsNotNone(disambig_list)
        self.assertGreater(len(disambig_list), 0)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_redirect(self):
        """Test Wikipedia lookup for a redirect page (climate term)."""
        
        # Test with a climate term that redirects
        term = "global warming"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should find the page
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Should not be disambiguation page
        self.assertFalse(page.is_disambiguation_page())
        
        # For redirect pages, we can check if the content is different from expected
        # Redirects often have different content structure
        main_elem = page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_page_not_found(self):
        """Test Wikipedia lookup for a non-existent page (climate term)."""
        
        # Test with a climate term that doesn't exist
        term = "nonexistentclimateterm12345"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should not find the page - page object exists but html_elem contains error content
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Check that the content indicates "page not found"
        main_elem = page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        # Look for indicators that this is a "not found" page
        text_content = ''.join(main_elem.itertext())
        self.assertIn("There were no results matching the query", text_content)
        self.assertIn("does not exist", text_content)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_acronym_direct_entry(self):
        """Test Wikipedia lookup for acronym with direct entry (climate acronym)."""
        
        # Test with a climate acronym that should have a direct entry
        term = "IPCC"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should find the page
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Should not be disambiguation page
        self.assertFalse(page.is_disambiguation_page())
        
        # Should have content
        main_elem = page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        first_para = page.create_first_wikipedia_para()
        self.assertIsNotNone(first_para)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_acronym_disambiguation(self):
        """Test Wikipedia lookup for acronym with disambiguation (climate acronym)."""
        
        # Test with a climate acronym that leads to disambiguation
        term = "AGW"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should find the page
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Should be disambiguation page
        self.assertTrue(page.is_disambiguation_page())
        
        # Should have disambiguation options
        disambig_list = page.get_disambiguation_list()
        self.assertIsNotNone(disambig_list)
        self.assertGreater(len(disambig_list), 0)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_acronym_redirect(self):
        """Test Wikipedia lookup for acronym with redirect (climate acronym)."""
        
        # Test with a climate acronym that redirects
        term = "GE"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should find the page
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Should not be disambiguation page
        self.assertFalse(page.is_disambiguation_page())
        
        # For redirect pages, we can check if the content is different from expected
        # Redirects often have different content structure
        main_elem = page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

    def test_wikipedia_lookup_acronym_page_not_found(self):
        """Test Wikipedia lookup for non-existent acronym (climate acronym)."""
        
        # Test with a climate acronym that doesn't exist
        term = "NONEXISTENT123"
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        # Should not find the page - page object exists but html_elem contains error content
        self.assertIsNotNone(page)
        self.assertIsNotNone(page.html_elem)
        
        # Check that the content indicates "page not found"
        main_elem = page.get_main_element()
        self.assertIsNotNone(main_elem)
        
        # Look for indicators that this is a "not found" page
        text_content = ''.join(main_elem.itertext())
        self.assertIn("There were no results matching the query", text_content)
        self.assertIn("does not exist", text_content)
        
        # Test connection before lookup
        connection_result = FileLib.check_service_connection(
            service_url=WIKIPEDIA_SERVICE_URL,
            service_name=WIKIPEDIA_SERVICE_NAME,
            timeout=10
        )
        self.assertTrue(connection_result['connected'])

class SPARQLTests:
    @classmethod
    @unittest.skip("WS symbol?")
    def test_sparql_wrapper_WIKI(cls):
        """
        Author Shweata N Hegde
        from wikidata query site
        """
        #
        # query = """#research council
        # SELECT ?researchcouncil ?researchcouncilLabel
        # WHERE
        # {
        #   ?researchcouncil wdt:P31 wd:Q10498148.
        #   SERVICE wikibase:label_xml { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        # }"""
        #
        # results = WS.get_results_xml(query)
        # print(results)




class SPARQLTests:
    @classmethod
    @unittest.skip("WS symbol?")
    def test_sparql_wrapper_WIKI(cls):
        """
        Author Shweata N Hegde
        from wikidata query site
        """
        #
        # query = """#research council
        # SELECT ?researchcouncil ?researchcouncilLabel
        # WHERE
        # {
        #   ?researchcouncil wdt:P31 wd:Q10498148.
        #   SERVICE wikibase:label_xml { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        # }"""
        #
        # results = WS.get_results_xml(query)
        # print(results)


if __name__ == '__main__':
    unittest.main()
    # if wiki_test:
    #     # TODO move to Wikimedia
    #     WikimediaTest.test_sparql_wrapper()

