from pathlib import Path

import pdfplumber

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

