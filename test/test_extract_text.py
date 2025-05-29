import logging
import os
import unittest
from collections import Counter, defaultdict
import csv
from pathlib import Path
import lxml.etree as ET
import pdfplumber
from keybert import KeyBERT
from lxml.html import HTMLParser

from amilib.ami_html import HtmlLib
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.xml_lib import XmlLib
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)

class ExtractTextTest(AmiAnyTest):

    """test PDFPlumber text extraction
    """
    def test_read_breward(self):
        """
        read a chapter of slides (we don't have chaps 2-8)
        """
        save_level = logger.level
        logger.setLevel(logging.INFO)
        print(f"pdfplumber: {pdfplumber.__version__}")
        maxchap = 1 # (there are 8 in all, this is for speed)
        chapnos = range(1, maxchap + 1)
        chapters_by_chapnos = defaultdict(list)
        for chapno in chapnos:
            infile = Path(Resources.TEST_RESOURCES_DIR, "pdf", f"breward_{chapno}.pdf")
            print(f"======= {chapno} ========")
            pdf = pdfplumber.open(infile)
            lines_by_page = defaultdict(list)
            for pageno, page in enumerate(pdf.pages):
                # text = page.extract_text()
                lines = page.extract_text_lines()
                imgs = page.images
                if imgs:
                    logger.info(f"\n=====images {len(imgs)}")
                    for imgno, img in enumerate(imgs):
                        logger.info(f"page {pageno}: image {imgno}: {img}")

                print("")
                for line in lines:
                    text_ = line['text']
                    # print(f"page {pageno} line {text_}")
                    lines_by_page[pageno].append(text_)
            logger.info(f"lines by page {lines_by_page}")
            chapters_by_chapnos[chapnos].append(lines_by_page)
            logger.info(f"chapters: {chapters_by_chapnos}")
        logger.setLevel(save_level)

    def test_keybert_breward_1(self):
        """
        uses keyBERT to extract phrases/words
        """
        from keybert import KeyBERT
      #   doc = """
      #    Supervised learning is the machine learning task of learning a function that
      #    maps an input to an output based on example input-output pairs. It infers a
      #    function from labeled training data consisting of a set of training examples.
      #    In supervised learning, each example is a pair consisting of an input object
      #    (typically a vector) and a desired output value (also called the supervisory signal).
      #    A supervised learning algorithm analyzes the training data and produces an inferred function,
      #    which can be used for mapping new examples. An optimal scenario will allow for the
      #    algorithm to correctly determine the class labels for unseen instances. This requires
      #    the learning algorithm to generalize from the training data to unseen situations in a
      #    'reasonable' way (see inductive bias).
      # """
        phrase_range = (1, 3)
        phrase_range = (1, 1)
        top_n = 4
        breward_dir = Path(Resources.TEMP_DIR, "pdf", "html", "breward_1")

        kw_counter = self._read_chapter_extract_keywords(breward_dir, phrase_range, top_n)
        assert kw_counter is not None
        assert len(kw_counter) > 10
        assert 'climate' in kw_counter


    def _read_chapter_extract_keywords(
            self, indir, phrase_range=(1,1), top_n=4, globstr="*.html", chunk_xpath=None):
        """
        iterate over files in directory and use keyBERT to extract keywords
        :param indir: input directory
        :param phrase_range: range of phrase lengths
        :param globstr: glob selection of files in dir
        :param chunk_xpath: selection of document components by xpath
        :return: counter of keywords
        """
        kw_counter, html_by_file, spans_by_file = \
            self._read_html_file_and_extract_keywords_from_spans(
                indir, phrase_range=phrase_range, top_n=top_n, globstr=globstr, chunk_xpath=chunk_xpath)
        # logger.info(f"kw_counter {len(kw_counter)}: {kw_counter.most_common()}")
        marked_out_dir = Path(list(spans_by_file.keys())[0].parent, "marked")
        FileLib.force_mkdir(marked_out_dir)
        counter_path = Path(marked_out_dir, "kw_counter.txt")
        with open(counter_path, "w", encoding="UTF-8") as f:
            logger.info(f"wrote {counter_path}")
            f.write(str(kw_counter))
        self._output_marked_html_files(kw_counter, html_by_file, spans_by_file)
        return kw_counter

    def _output_marked_html_files(self, all_keywords, html_by_file, spans_by_file, marked_out_dir=None, markup=True):
        """
        :param all_keywords: a dict() indexed by keywords
        :param html_by_file: html objects indexed by their files
        :param spans_by_file: html spans in files indexed by files
        :param marked_out_dir: output directory (default files.parent/marked)
        :param markup: add hyperlinks to text (default True)
        """
        marked_out_dir = Path(list(spans_by_file.keys())[0].parent, "marked")
        for file, spans in sorted(spans_by_file.items()):
            html = html_by_file[file]
            # logger.info(f"parent: {file.parent}")
            text = " ".join([s.text for s in spans if s.text is not None])
            words = text.split()
            markup = False
            for word in words:
                if word.casefold() in all_keywords.keys():
                    for span in spans:
                        HtmlLib.find_and_markup_phrases(span, word, markup=markup)
                        outpath = Path(marked_out_dir, f"{file.stem}.html")
            if markup:
                HtmlLib.write_html_file(html, outpath, debug=True)

    def _read_html_file_and_extract_keywords_from_spans(
            self, dir_with_html, phrase_range, top_n, globstr=None, chunk_xpath=None):
        """

        """
        if globstr is None:
            globstr = "*.html"
        if chunk_xpath is None:
            chunk_xpath = "//span"
            logger.info(f"using default chunk {chunk_xpath}")
        if top_n is None:
            top_n = 5
        if phrase_range is None:
            phrase_range = (1,1)
        files = FileLib.list_files(dir_with_html, globstr)
        kw_model = KeyBERT()
        kw_counter = Counter()
        chunks_by_file = dict()
        html_by_file = dict()
        logger.info(f"searching {len(files)} {files}")
        for file in files:
            html = HtmlLib.parse_html(file)
            html_by_file[file] = html
            chunks = html.xpath(chunk_xpath)
            # logger.info(f"chunks {chunk_xpath} => {len(chunks)}")
            if chunks is None or len(chunks) == 0:
                logger.warning(f"no chunks for {chunk_xpath}")
                continue
            # logger.info(f"chunking {file}")
            chunks_by_file[file] = chunks
            chunk_texts = [s.text for s in chunks if s.text is not None]
            text = " ".join(chunk_texts)
            wds = text.split()
            keyword_wts = kw_model.extract_keywords(
                text, top_n=top_n, keyphrase_ngram_range=phrase_range)
            # logger.info(f"keyword_wts {len(keyword_wts)}")
            for keyword_wt in keyword_wts:
                kw = keyword_wt[0]
                kw_counter[kw] += 1
        # logger.info(f"kw_counter {kw_counter}")
        return kw_counter, html_by_file, chunks_by_file

    def test_keybert_ipcc_wg1_3(self):
        """file:///Users/pm286/workspace/amilib/test/resources/ipcc/cleaned_content/wg1/Chapter03/html_with_ids.html"""
        indir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content","wg1", "Chapter03")
        assert indir.exists()
        kw_counter = self._read_chapter_extract_keywords(
            indir, phrase_range=(1,1), top_n=50, globstr="html_with_ids.html", chunk_xpath="//p")
        assert "madagascar" in kw_counter
        assert Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter03", "marked/kw_counter.txt").exists()


    def test_keybert_ipcc_wg1(self):
        """file:///Users/pm286/workspace/amilib/test/resources/ipcc/cleaned_content/wg1/Chapter03/html_with_ids.html"""

        wgdir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content","wg1")
        chapters = [
            # "Chapter01",
            "Chapter02",
            # "Chapter03",
            # "Chapter04",
            # "Chapter05",
            # "Chapter06",
            # "Chapter07",
            # "Chapter08",
            # "Chapter09",
            # "Chapter10",
            # "Chapter11",
            # "Chapter12",
        ]
        all_words = Counter()
        for chapter in chapters:
            indir = Path(wgdir, chapter)
            assert indir.exists()
            kw_counter = self._read_chapter_extract_keywords(
                indir, phrase_range=(1,1), top_n=100, globstr="html_with_ids.html", chunk_xpath="//p")
            for word, count in kw_counter.items():
                all_words[word] += count
        logger.info(f"all words {all_words.most_common()}")
        marked_dir = Path(wgdir, "marked")
        FileLib.force_mkdir(marked_dir)
        outpath = Path(marked_dir, "keywords.txt")
        with open(outpath, "w", encoding="UTF-8") as f:
            f.write(str(all_words))
        assert outpath.exists(), f"{outpath} should exist"

    def test_extract_title_id_para_from_ipcc_syr(self):
        """
        read a chapter from IPCC and extract paras with ids and their section titles

        Purpose is to create CSV for input to LLM/RAG
        reads IPCC SYR report, finds all divs with paragraphs and returns the title and
        first para.
        """

        chapter = "longer-report"
        wg = "syr"
        infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content",
                      wg, chapter, "html_with_ids.html")
        outdir = Path(Resources.TEMP_DIR, "csv", "ipcc")
        outfile_name = "syr_paras.csv"
        csvout = Path(outdir, outfile_name)

        MiscLib.create_and_write_csv(
            infile,
            outdir,
            csvout,
            div_with_p_with_ids_xpath=".//body//div[p[@id]]",
            para_xpath=".//p",
            title_xpath=".//h2/text()|.//h3/text()|.//h4/text()")

    def test_extract_title_id_para_from_ipcc_wg123(self):
        """
        read all chapters from IPCC WG1/2/3 and extract paras with ids and their section titles

        Purpose is to create CSV for input to LLM/RAG
        reads IPCC SYR report, finds all divs with paragraphs and returns the title and
        first para.
        """

        MAXWGS = 2
        MAXCHAPS = 3
        wgs = ["wg1", "wg2", "wg3"]
        chapters = [
            "Chapter01","Chapter02","Chapter03","Chapter04","Chapter05",
            "Chapter06","Chapter07","Chapter08","Chapter09","Chapter10",
            "Chapter11", "Chapter12", "Chapter13", "Chapter14", "Chapter15",
            "Chapter16", "Chapter17", "Chapter18", "Chapter19", "Chapter20",
        ]
        for wg in wgs[:MAXWGS]:
            for chapter in chapters[:MAXCHAPS]:
                ipcc_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", wg, chapter)
                infile = Path(ipcc_dir, "html_with_ids.html")
                if not infile.exists():
                    logger.info(f"skipped {infile}")
                    continue
                outdir = Path(Resources.TEMP_DIR, "csv", "ipcc", wg, chapter)
                outdir = ipcc_dir
                outfile_name = "paras.csv"
                csvout = Path(outdir, outfile_name)

                MiscLib.create_and_write_csv(
                    infile,
                    outdir,
                    csvout,
                    div_with_p_with_ids_xpath=".//body//div[p[@id]]",
                    para_xpath=".//p",
                    title_xpath=".//h2/text()|.//h3/text()|.//h4/text()",
                    wg=wg,
                    chap=f"ch{chapter[-2:]}"
                )
                assert csvout.exists(), f"csvout {csvout} should exist"
                # test it's a CSV file
                expected_rows = 500 # this is fragile not sure why
                with open (csvout, "r", encoding="UTF-8") as csvf:
                    csvreader = csv.reader(csvf)
                    rows = [row for row in csvreader]
                    nrows = len(rows)
                    assert nrows >= expected_rows, f"found {nrows}"


    # -------------------------------------------------

    def test_extract_title_id_para_from_makespace(self):
        """
        read makespace pages and extract text with titles

        Purpose is to create CSV for input to LLM/RAG
        reads makespace scrape, returns the title and
        text.
        """

        makespacedir = Path(Path(__file__).parent.parent.parent,
                            "ollama_langchain_rag", "AI-ML-Prj1", "MSWebScrape", "2025March")
        assert makespacedir.exists()
        outdir = Path(Resources.TEMP_DIR, "csv", "makespace")
        FileLib.force_mkdir(outdir)
        csvout = Path(outdir, "makespace.csv")
        files = os.listdir(str(Path(makespacedir)))
        with (open(csvout, 'w', encoding="UTF-8") as csvfile):
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["id", "title", "text"])
            for i, file in enumerate(files):
                if Path(file).is_dir():
                    continue
                logger.info(f"makespace_file: {file}")
                filename = Path(file).stem
                path = Path(makespacedir, filename)
                if not path.exists():
                    logger.error(f"Cannot read {path}")
                    continue
                if path.is_dir():
                    logger.warning(f"Skipped directory {path}")
                    continue
                with open(path, "r", encoding="UTF-8") as f:
                    strings = f.readlines()
                # print(f"strings {strings}")
                text_ = "".join(list(strings))
                divid = str(i)
                if text_ is None or len(text_) == 0:
                    logger.info(f"empty text for {divid}")
                    continue
                if divid:
                    # print(f"{pid}: [{title}] {text_}")
                    row = [divid, filename, text_]
                    csvwriter.writerow(row)
        logger.info(f"wrote CSV {csvout}")

class MiscLib:

    @classmethod
    def _add_ids_and_text_as_csv_row(cls, csvwriter, div_title, para, wg, chap):
        pid = para.get('id')
        p_text = list(para.itertext())  # gets text in spans, a, etc.
        if p_text is None:
            logger.info(f"no text for {pid}")
            return
        text_ = "".join(p_text)
        if pid:
            full_pid = f"{wg}_{chap}_{pid}"
            # logger.info(f"{chap}:{full_pid}")
            # print(f"{pid}: [{title}] {text_}")
            if text_ is None or len(text_) == 0:
                logger.info(f"empty text for {pid}")
                return
            row = [full_pid, div_title, text_]
            csvwriter.writerow(row)

    @classmethod
    def _write_csv(cls, csvout, divs_with_p_with_ids, para_xpath, title_xpath, wg, chap):

        with (open(csvout, 'w', encoding="UTF-8") as csvfile):
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["id", "title", "text"])
            for div in divs_with_p_with_ids:
                paras = div.xpath(para_xpath)
                for para in paras:
                    parent = para.getparent()
                    titles = parent.xpath(title_xpath)
                    div_title = "NO_TITLE" if len(titles) == 0 else titles[0]
                    if len(div_title.strip()) == 0:
                        div_title = "NO_TITLE_1"
                    cls._add_ids_and_text_as_csv_row(csvwriter, div_title, para, wg, chap)
        logger.info(f"wrote CSV {csvout}")

    @classmethod
    def create_and_write_csv(
            cls,
            infile,
            outdir,
            csvout,
            div_with_p_with_ids_xpath=".//body//div[p[@id]]",
            para_xpath=".//p",
            title_xpath=".//h2/text()|.//h3/text()|.//h4/text()",
            wg=None,
            chap=None,
    ):
        FileLib.force_mkdir(outdir)
        assert infile.exists()
        html = ET.parse(str(infile), HTMLParser())
        assert html is not None
        divs_with_p_with_ids = html.xpath(div_with_p_with_ids_xpath)
        # assert len(divs_with_p_with_ids) == divs_with_p_with_ids_count
        # get Id of div parent
        # div_parent_ids = sorted([div.getparent().get('id') for div in divs_with_p_with_ids])
        # logger.info(f"ids = {div_parent_ids}")
        cls._write_csv(csvout, divs_with_p_with_ids, para_xpath, title_xpath, wg, chap)



