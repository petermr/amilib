from pathlib import Path

import pdfplumber

from amilib.ami_html import HtmlLib
from amilib.xml_lib import XmlLib
from test.resources import Resources
from test.test_all import AmiAnyTest


class ExtractTextTest(AmiAnyTest):

    """test PDFPlumber text extraction
    """
    def test_read_breward(self):
        """
        read a chapter of slides (we don't have chaps 2-8)
        """
        print(pdfplumber.__version__)
        maxpage = 1
        chapnos = range(1, maxpage + 1)
        for chapno in chapnos:
            infile = Path(Resources.TEST_RESOURCES_DIR, "pdf", f"breward_{chapno}.pdf")
            print(f"======= {chapno} ========")
            pdf = pdfplumber.open(infile)
            for pageno, page in enumerate(pdf.pages):
                text = page.extract_text()
                lines = page.extract_text_lines()
                imgs = page.images
                if imgs:
                    print(f"\n=====images {len(imgs)}")
                    for imgno, img in enumerate(imgs):
                        print(f"page {pageno}: image {imgno}: {img}")

                print("")
                for line in lines:
                    print(f"page {pageno} line {line['text']}")
                    pass


    def test_keybert(self):
        """
        uses keyBERT to extract phrases/words
        """
        from keybert import KeyBERT
        doc = """
         Supervised learning is the machine learning task of learning a function that
         maps an input to an output based on example input-output pairs. It infers a
         function from labeled training data consisting of a set of training examples.
         In supervised learning, each example is a pair consisting of an input object
         (typically a vector) and a desired output value (also called the supervisory signal).
         A supervised learning algorithm analyzes the training data and produces an inferred function,
         which can be used for mapping new examples. An optimal scenario will allow for the
         algorithm to correctly determine the class labels for unseen instances. This requires
         the learning algorithm to generalize from the training data to unseen situations in a
         'reasonable' way (see inductive bias).
      """
        kw_model = KeyBERT()
        # keywords = kw_model.extract_keywords(doc)
        breward_dir = Path(Resources.TEMP_DIR, "pdf", "html", "breward_1")
        all_keywords = set()
        for page_no in range(0, 29):
            file = Path(breward_dir, f"page_{page_no}.html")
            html = HtmlLib.parse_html(file)
            texts = html.xpath("//span/text()")
            text = " ".join([t for t in texts])
            # print(f"text {text[:100]}")
            keyword_wts = kw_model.extract_keywords(text, top_n=7, )
            for keyword_wt in keyword_wts:
                all_keywords.add(keyword_wt[0])
        print(f"kw {all_keywords}")