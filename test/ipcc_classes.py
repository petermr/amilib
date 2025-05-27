# classes from AMIClimate
import argparse
import copy
import logging
import re
import textwrap
from abc import abstractmethod, ABC
from collections import defaultdict
from io import BytesIO
from pathlib import Path

import lxml
import requests
from lxml.etree import HTMLParser, _ElementUnicodeResult
import lxml.etree as ET

import pandas as pd
from lxml.html import HtmlComment

from amilib.ami_args import AbstractArgs
from amilib.ami_dict import RAW
from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.amidriver import AmiDriver
from amilib.amix import AmiLib
from amilib.file_lib import FileLib
from amilib.html_generator import HtmlGenerator
from amilib.util import Util
from amilib.xml_lib import XmlLib
from test.ipcc_constants import HTML_WITH_IDS, GATSBY_RAW, GATSBY, DE_GATSBY, ID_LIST, PARA_LIST, DE, WORDPRESS_RAW, \
    WORDPRESS, DE_WORDPRESS

logger = logging.Logger(__file__)


class AMIClimate:
    """runs commands - dummy at present"""

    def run_command(self, args):
        parser = argparse.ArgumentParser()
        if type(args) is str:
            args = args.split()
        logger.info(f"args: {args}")
        err = AbstractArgs.parse_error(parser, args)
        pyami = AmiLib()
        if err:
            logger.error(f"BAD COMMAND: {err}")
            print("======== allowed args ==========")
            pyami.run_command(f"--help")
            print("================================")
            pyami.run_command(f"{args[0]} --help")
            print("================================")
            # raise ValueError(f"{args} gives error:\n {err}")
            return
        logger.info(f"running command {args}")
        pyami.run_command(args)


class IPCCCommand:

    @classmethod
    def get_paths(cls, inputs):

        """ expands any globs and also creates BytesIO from URLs
        """
        paths = []
        if not inputs:
            logger.warning(f"no inputs given")
            return paths
        if type(inputs) is not list:
            inputs = [inputs]

        _globbed_inputs = FileLib.expand_glob_list(inputs)
        if _globbed_inputs:
            logger.info(f"inputs {inputs}")
            paths = [Path(input) for input in _globbed_inputs if Path(input).exists() and not Path(input).is_dir()]
            return paths

        for input in inputs:
            if str(input).startswith("http"):
                response = requests.get(input)
                bytes_io = BytesIO(response.content)
                paths.append(bytes_io)
        return paths

    @classmethod
    def extract_authors_and_roles(cls, filename, author_roles=None, output_dir=None, outfilename="author_table.html"):
        """
        extracts author names and countries from frontmatter
        :param filename: input html file
        :param author_roles: Roles of authors (subsection titles)
        :param output_dir: if not, uses input file parent
        :param outfilename: output filename (default "author_table.html")
        """
        if not author_roles:
            author_roles = cls.get_author_roles()

        if not output_dir:
            output_dir = Path(filename).parent
        chap_html = ET.parse(str(Path(output_dir, filename)))
        table = []
        for role in author_roles:
            htmls = chap_html.xpath(f".//div/span[normalize-space(.)='{role}']")
            if len(htmls) == 0:
                logger.warning(f"{role} not found")
                continue
            following = htmls[0].xpath("following-sibling::span")
            if len(following) != 1:
                logger.warning(f"FAIL to find author_list")
            else:
                cls.extract_authors(following, role, table)
        df = pd.DataFrame(table, columns=["author", "country", "role"])
        # html_table = df.to_html()
        # HtmlLib.write_html_file(html_table, str(Path(output_dir, outfilename)))
        df.to_html()
        return df

    @classmethod
    def extract_authors(cls, following, role, table):
        AUTHOR_RE = re.compile("\\s*(?P<auth>.*)\\s+\\((?P<country>.*)\\)")
        authors = following[0].text.split(",")
        for author in authors:
            match = AUTHOR_RE.match(author)
            if match:
                auth = match.group('auth')
                country = match.group('country')
                table.append([auth, country, role])
            else:
                logger.warning(f"FAIL {author}")
                pass

    @classmethod
    def get_author_roles(cls):
        author_roles = [
            "Core Writing Team:",
            "Extended Writing Team:",
            "Contributing Authors:",
            "Review Editors:",
            "Scientific Steering Committee:",
            "Visual Conception and Information Design:",
        ]
        return author_roles

    @classmethod
    def save_args_to_global(cls, kwargs_dict, overwrite=False):
        return None

        for key, value in kwargs_dict.items():
            if overwrite or key not in doc_info:
                doc_info[key] = value
        # print(f"config doc_info {doc_info}")


class IPCCChapter:

    @classmethod
    def make_pure_ipcc_content(cls, html_file=None, html_url=None, html_elem=None, outfile=None):
        """
        Strips non-content elements and attributes
        :param html_file: file to read
        :param html_url: url to download if html_file is None
        :param outfile: file to save parsed cleaned html
        :return: (html element,error)  errors or non-existent files return (None, error)
        """

        """
        <div class="nav2">
          <nav class="navbar py-0 fixed-top navbar navbar-expand navbar-light"><div class="navbar__wrapper d-flex align-items-center justify-content-between position-relative h-100">
            <div class="logo-box d-flex h-100 align-items-center hamburger">
              <div class="text-white d-flex justify-content-center align-items-center text-decoration-none nav-item dropdown">
                <a id="basic-nav-dropdown" aria-expanded="false" role="button" class="dropdown-toggle nav-link" tabindex="0">
                  <button class="menu bg-transparent h-100 border-0">
                    <i class="uil uil-bars text-white"></i>
                    <span class="d-block text-white fw-bold">Menu</span>
                    </button>
                    </a>
                    </div>
                    <a class="logo fw-bold text-white flex-column align-items-start text-decoration-none" href="https://www.ipcc.ch/report/ar6/wg3/">IPCC Sixth Assessment Report<small class="d-block opacity-75 nav-subtitle">Working Group III: Mitigation of Climate Change</small></a></div><div class=" h-100 d-flex list-top"><div class="text-white d-flex justify-content-center align-items-center text-decoration-none nav-item dropdown t-link nav-item dropend"><a id="basic-nav-dropdown" aria-expanded="false" role="button" class="dropdown-toggle nav-link" tabindex="0">About</a></div><div class="text-white d-flex justify-content-center align-items-center text-decoration-none nav-item dropdown t-link report-menu nav-item dropend"><a id="basic-nav-dropdown" aria-expanded="false" role="button" class="dropdown-toggle nav-link" tabindex="0">Report</a></div><div class="text-white d-flex justify-content-center align-items-center text-decoration-none nav-item dropdown t-link nav-item dropend"><a id="basic-nav-dropdown" aria-expanded="false" role="button" class="dropdown-toggle nav-link" tabindex="0">Resources</a></div><div class="text-white d-flex justify-content-center align-items-center text-decoration-none t-link nav-item dropend"><a id="basic-nav-dropdown" aria-expanded="false" role="button" class="dropdown-toggle nav-link" tabindex="0">Download</a></div><div class="text-white d-flex justify-content-center align-items-center text-decoration-none icon-download t-link nav-item dropdown"><a id="basic-nav-dropdown" aria-expanded="false" role="button" class="dropdown-toggle nav-link" tabindex="0"><div class="text-white d-flex justify-content-center align-items-center text-decoration-none"><i class="uil uil-import"></i></div></a></div><a class="text-white d-flex justify-content-center align-items-center text-decoration-none t-link nav-item dropend translations-icon" href="https://www.ipcc.ch/report/ar6/wg3/resources/translations"><svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="globe" class="svg-inline--fa fa-globe fa-w-16 " role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 512"><path fill="currentColor" d="M336.5 160C322 70.7 287.8 8 248 8s-74 62.7-88.5 152h177zM152 256c0 22.2 1.2 43.5 3.3 64h185.3c2.1-20.5 3.3-41.8 3.3-64s-1.2-43.5-3.3-64H155.3c-2.1 20.5-3.3 41.8-3.3 64zm324.7-96c-28.6-67.9-86.5-120.4-158-141.6 24.4 33.8 41.2 84.7 50 141.6h108zM177.2 18.4C105.8 39.6 47.8 92.1 19.3 160h108c8.7-56.9 25.5-107.8 49.9-141.6zM487.4 192H372.7c2.1 21 3.3 42.5 3.3 64s-1.2 43-3.3 64h114.6c5.5-20.5 8.6-41.8 8.6-64s-3.1-43.5-8.5-64zM120 256c0-21.5 1.2-43 3.3-64H8.6C3.2 212.5 0 233.8 0 256s3.2 43.5 8.6 64h114.6c-2-21-3.2-42.5-3.2-64zm39.5 96c14.5 89.3 48.7 152 88.5 152s74-62.7 88.5-152h-177zm159.3 141.6c71.4-21.2 129.4-73.7 158-141.6h-108c-8.8 56.9-25.6 107.8-50 141.6zM19.3 352c28.6 67.9 86.5 120.4 158 141.6-24.4-33.8-41.2-84.7-50-141.6h-108z"></path></svg></a><div class="logo-box d-flex h-100 align-items-center gap-5"><a id="nav-primary-logo" class="ipcc-logo-svg" href="https://www.ipcc.ch/"><svg version="1.1" x="0px" y="0px" viewBox="0 0 82 50"><path d="M7.8,4.6C7.8,6.4,6.2,8,4.4,8C2.5,8,1,6.4,1,4.6c0-1.9,1.5-3.4,3.4-3.4C6.2,1.2,7.8,2.7,7.8,4.6z M1.6,42.7h5.6V10.7H1.6
    V42.7z M29.3,13c2,1.8,2.9,4.1,2.9,7.2v13.4c0,3.1-1,5.5-2.9,7.2c-2,1.8-4,2.7-6.3,2.7c-2,0-3.7-0.5-5-1.5v6.8h-5.6V20.2
    c0-3.1,1-5.5,2.9-7.2c2-1.8,4.3-2.7,7-2.7C25,10.2,27.4,11.1,29.3,13z M26.7,20.2c0-3.7-1.9-5.3-4.3-5.3c-2.4,0-4.3,1.6-4.3,5.3....9-7.2v-3.2h-5.6v3.2
    c0,3.6-1.9,5.3-4.3,5.3c-2.4,0-4.3-1.6-4.3-5.2V20.2c0-3.7,1.9-5.3,4.3-5.3c2.4,0,4.3,1.6,4.3,5.3v0.6H81z"></path></svg></a></div></div></div></nav></div>
        """
        """
        <div class="ref-tooltip" id="ref-tooltip"><textarea class="ref-tooltip-text" id="ref-tooltip-text"></textarea><div class="reflinks"><button class="btn-ipcc btn btn-primary copy-reference" id="copy-reference">Copy</button><a href="https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-6/" id="doilink" target="_blank">doi</a></div></div>        
        """
        """
        The 3-circle 'share' icon
        <div class="share-tooltip" id="share-tooltip"><span><img id="section-twitter-share" class="twitter" src="./expanded_files/twitter-icon.png"><button id="section-twitter-share-button" class="btn-ipcc btn btn-primary">Share on Twitter</button></span><span><img id="section-facebook-share" class="facebook" src="./expanded_files/facebook-icon.png"><button id="section-facebook-share-button" class="btn-ipcc btn btn-primary">Share on Facebook</button></span><span><img id="section-link-copy" class="link" src="./expanded_files/link-icon.png"><button id="section-link-copy-button" class="btn-ipcc btn btn-primary">Copy link</button><input class="section-link-input" id="section-link-input"></span><span><img class="link" src="./expanded_files/email-icon.png"><a id="section-email-share" target="_blank" href="https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-6/"><button id="section-email-share-button" class="btn-ipcc btn btn-primary">Share via email</button></a></span><span class="ref-tooltip-close"></span></div>        
        """
        """
        Dropdown menus (e.g. from top of page)
        <div class="dropdown"><button id="dropdown-basic" aria-expanded="false" type="button" class="btn-ipcc btn btn-primary dl-dropdown dropdown-toggle btn btn-success">Downloads</button></div>
        """
        """
        <div class="section-tooltip" id="section-tooltip"><span class="section-tooltip-text" id="section-tooltip-text"></span><a href="https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-6/" id="section-link" target="_blank"><button class="btn-ipcc btn btn-primary open-section">Open section</button></a><span class="section-tooltip-close"></span></div>
        """
        """
        rectangular buttons
        <div class="mt-auto gap-3 d-flex flex-row align-items-left pb-3"><button class="btn-ipcc btn btn-primary" id="authors-button">Authors</button><button class="btn-ipcc btn btn-primary" id="figures-button">Figures</button><button class="btn-ipcc btn btn-primary" id="citation-button">How to cite</button><button class="btn-ipcc btn btn-primary" id="toggle-all-content">Expand all sections</button></div>
        """
        """
        Figures
        <div class="col-lg-3 col-12"><h3>Figure&nbsp;6.4</h3><img src="./expanded_files/IPCC_AR6_WGIII_Figure_6_4.png" alt="" class="img-card" srl_elementid="11"><a href="https://www.ipcc.ch/report/ar6/wg3/figures/chapter-6/figure-6-4"><button type="button" class="btn-ipcc btn btn-primary"><svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="chart-bar" class="svg-inline--fa fa-chart-bar fa-w-16 " role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M332.8 320h38.4c6.4 0 12.8-6.4 12.8-12.8V172.8c0-6.4-6.4-12.8-12.8-12.8h-38.4c-6.4 0-12.8 6.4-12.8 12.8v134.4c0 6.4 6.4 12.8 12.8 12.8zm96 0h38.4c6.4 0 12.8-6.4 12.8-12.8V76.8c0-6.4-6.4-12.8-12.8-12.8h-38.4c-6.4 0-12.8 6.4-12.8 12.8v230.4c0 6.4 6.4 12.8 12.8 12.8zm-288 0h38.4c6.4 0 12.8-6.4 12.8-12.8v-70.4c0-6.4-6.4-12.8-12.8-12.8h-38.4c-6.4 0-12.8 6.4-12.8 12.8v70.4c0 6.4 6.4 12.8 12.8 12.8zm96 0h38.4c6.4 0 12.8-6.4 12.8-12.8V108.8c0-6.4-6.4-12.8-12.8-12.8h-38.4c-6.4 0-12.8 6.4-12.8 12.8v198.4c0 6.4 6.4 12.8 12.8 12.8zM496 384H64V80c0-8.84-7.16-16-16-16H16C7.16 64 0 71.16 0 80v336c0 17.67 14.33 32 32 32h464c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16z"></path></svg><span>View</span></button></a></div>
        """
        """
        <span class="share-block"><img class="share-icon" src="./expanded_files/share.png"></span>
        """
        """
        Related pages -  links to other chapters, etc
        <div class="related_pages pt-4"><div class="container"><div class="gx-3 gy-5 ps-2 row"><div class="col-lg-12 col-12 offset-lg-0"><div class="gx-3 gy-3 row"><div class="col-12"><h3 class="fw-bold color-heading mb-2">Explore more</h3></div><div class="col-lg-4 col-sm-6 col-12"><div class="card card-custom-1 bg-white d-flex flex-column justify-content-between"><div class="thumb-overlay"></div><div data-gatsby-image-wrapper="" class="gatsby-image-wrapper gatsby-image-wrapper-constrained img-card"><div><img alt="" role="presentation" aria-hidden="true" src="data:image/svg+xml;charset=utf-8,%3Csvg%20height='294'%20width='600'%20xmlns='http://www.w3.org/2000/svg'%20version='1.1'%3E%3C/svg%3E"></div></div><h3 class="pt-3 px-3">Fact Sheets</h3><p class=" text-20 fw-normal px-3">The regional and crosscutting fact sheets give a snapshot of the key findings, distilled from the relevant Chapters.</p><div class="d-flex flex-row align-items-center gap-3 pb-4 mt-auto"></div></div></div><div class="col-lg-4 col-sm-6 col-12"><div class="card card-custom-1 bg-white d-flex flex-column justify-content-between"><div class="thumb-overlay"></div><div data-gatsby-image-wrapper="" class="gatsby-image-wrapper gatsby-image-wrapper-constrained img-card"><div><img alt="" role="presentation" aria-hidden="true" src="data:image/svg+xml;charset=utf-8,%3Csvg%20height='345'%20width='600'%20xmlns='http://www.w3.org/2000/svg'%20version='1.1'%3E%3C/svg%3E"></div></div><h3 class="pt-3 px-3">Frequently Asked Questions</h3><p class=" text-20 fw-normal px-3">FAQs explain important processes and aspects that are relevant to the whole report for a broad audience</p><div class="d-flex flex-row align-items-center gap-3 pb-4 mt-auto"></div></div></div><div class="col-lg-4 col-sm-6 col-12"><div class="card card-custom-1 bg-white d-flex flex-column justify-content-between"><div class="thumb-overlay"></div><div data-gatsby-image-wrapper="" class="gatsby-image-wrapper gatsby-image-wrapper-constrained img-card"><div><img alt="" role="presentation" aria-hidden="true" src="data:image/svg+xml;charset=utf-8,%3Csvg%20height='225'%20width='500'%20xmlns='http://www.w3.org/2000/svg'%20version='1.1'%3E%3C/svg%3E"></div></div><h3 class="pt-3 px-3">Authors</h3><p class=" text-20 fw-normal px-3">234 authors from 64 countries assessed the understanding of the current state of the climate, including how it is changing and the role of human influence.</p><div class="d-flex flex-row align-items-center gap-3 pb-4 mt-auto"></div></div></div></div></div></div></div></div>
        """
        """
        Text at end of page
        <div id="gatsby-announcer" aria-live="assertive" aria-atomic="true">Navigated to Chapter 6: Energy systems</div>
        """
        """
        Footer - no semantic informatiin
        <footer class="footer"><div class="footer-logo"><a href="https://ipcc.ch/" target="_blank" rel="noreferrer"><div data-gatsby-image-wrapper="" class="gatsby-image-wrapper gatsby-image-wrapper-constrained w-100 h-100 img-fluid footer-img"><div><img alt="" role="presentation" aria-hidden="true" src="data:image/svg+xml;charset=utf-8,%3Csvg%20height='135'%20width='873'%20xmlns='http://www.w3.org/2000/svg'%20version='1.1'%3E%3C/svg%3E"></div></div></a></div><div class="footer-social"><a href="https://twitter.com/IPCC_CH" target="_blank" class="link text-white" rel="noreferrer"><i class="bx bxl-twitter"></i></a><a href="https://www.facebook.com/IPCC/" target="_blank" class="link text-white" rel="noreferrer"><i class="bx bxl-facebook-square"></i></a><a href="https://www.instagram.com/ipcc/?hl=en" target="_blank" class="link text-white" rel="noreferrer"><i class="bx bxl-instagram"></i></a><a href="https://vimeo.com/ipcc" target="_blank" class="link text-white" rel="noreferrer"><i class="bx bxl-vimeo"></i></a></div></footer>
        """
        # TODO move file/url code to more generic library
        html_elem = None
        error = None
        if html_elem is not None:
            pass
        elif html_file is not None:
            if not Path(html_file).exists():
                error = FileNotFoundError()
            else:
                """
                encoding = etree.ElementTree.detect_encoding(data)
                # Parse the HTML file using the correct encoding
                parsed_html = etree.HTML(data.decode(encoding))
                """
                try:
                    html_elem = ET.parse(str(html_file), parser=HTMLParser())
                except Exception as e:
                    error = e
        elif html_url is not None:
            try:
                html_elem = HtmlLib.retrieve_with_useragent_parse_html(html_url, user_agent='my-app/0.0.1', debug=True)
            except Exception as e:
                print(f"cannot read {html_url} because {e}")
                raise e
            outfile1 = f"{outfile}.html"
            HtmlLib.write_html_file(html_elem, outfile1, debug=True)
            response = requests.get(html_url)
            if response.reason == "Not Found":  # replace this by a code
                html_elem = None
                error = response
            else:
                # print (f"response code {response.status_code}")
                html_elem = ET.fromstring(response.content, HTMLParser())
                assert html_elem is not None
        else:
            return (None, "no file or url given")

        if html_elem is None:
            print(f"cannot find html {error}")
            return (None, error)
        xpath_list = [
            "/html/head/style",
            "/html/head/link",
            "/html/head//button",
            "/html/head/script",

            "/html/body/script",
            "/html/body/*[starts-with(., 'Read more')]",
            "/html/body//div[@class='nav2'][nav]",
            "/html/body//div[@class='ref-tooltip'][textarea]",
            "/html/body//div[@class='share-tooltip']",
            "/html/body//div[@class='dropdown'][button]",
            "/html/body//div[@class='section-tooltip']",
            "/html/body//div[button]",
            "/html/body//a[button]",
            "/html/body//span[@class='share-block']",
            "/html/body//button",
            "/html/body//div[contains(@class,'related_pages')]",
            "/html/body//div[@id='gatsby-announcer']",
            "/html/body//noscript",
            "/html/body//footer",

        ]
        for xpath in xpath_list:
            HtmlUtil.remove_elems(html_elem, xpath=xpath)
        HtmlUtil.remove_style_attributes(html_elem)
        if outfile:
            HtmlLib.write_html_file(html_elem, outfile, debug=True)
        return (html_elem, error)

    @classmethod
    def atrip_wordpress(cls, html_elem):
        xpath_list = [
            "/html/head/style",
            "/html/head/link",
            "/html/head//button",
            "/html/head/script",

            "/html/body/script",
            "/html/body/header[div[nav]]",
            "/html/body/nav",
            "/html/body/main/nav",
            "/html/body/footer",
            "/html/body/section[@id='chapter-next']",
            "//article[@id='article-chapter-downloads']",
            "//article[@id='article-supplementary-material']",
            "//div[@class='share']",
            # "/html/body//div[@class='nav2'][nav]",
            # "/html/body//div[@class='ref-tooltip'][textarea]",
            # "/html/body//div[@class='share-tooltip']",
            # "/html/body//div[@class='dropdown'][button]",
            # "/html/body//div[@class='section-tooltip']",
            # "/html/body//div[button]",
            # "/html/body//a[button]",
            # "/html/body//span[@class='share-block']",
            # "/html/body//button",
            # "/html/body//div[contains(@class,'related_pages')]",
            # "/html/body//div[@id='gatsby-announcer']",
            # "/html/body//noscript",
            # "/html/body//footer",

        ]
        for xpath in xpath_list:
            HtmlUtil.remove_elems(html_elem, xpath=xpath)
        HtmlUtil.remove_style_attributes(html_elem)


class IPCC:
    """superclass of Gatsby and Wordpress
    """

    # styles for sections of IPCC chapters
    @classmethod
    def add_styles_to_head(cls, head):
        # generic styles acting as defaults

        HtmlLib.add_head_style(head, "div.col-lg-10.col-12.offset-lg-0::before", [("content", "'COL-LG'")])
        HtmlLib.add_head_style(head, ".box-container::before",
                               [("margin", "15px"), ("background", "#dddddd"), ("border", "dashed blue 5px"),
                                ("content", "'BOX'")])
        # IDs
        HtmlLib.add_head_style(head, "#chapter-button-content::before", [("content", "'CHAPTER-BUTTONS'")])
        HtmlLib.add_head_style(head, "#chapter-authors::before", [("content", "'AUTHORS'")])
        HtmlLib.add_head_style(head, "#chapter-figures::before", [("content", "'FIGURES'")])
        HtmlLib.add_head_style(head, "#chapter-citation::before", [("content", "'CITATION'")])
        HtmlLib.add_head_style(head, "#references::before", [("content", "'REFERENCES'")])
        HtmlLib.add_head_style(head, "#executive-summary::before", [("content", "'EXECUTIVE-SUMMARY'")])
        HtmlLib.add_head_style(head, "#frequently-asked-questions::before", [("content", "'FAQs'")])

        HtmlLib.add_head_style(head, ".figure-cont", [("background", "#ffffdd"), ("padding", "5px")])
        HtmlLib.add_head_style(head, "p.Caption", [("background", "#eeeeff")])
        HtmlLib.add_head_style(head, "p.LR-salmon-grey-box", [("background", "#eedddd")])
        HtmlLib.add_head_style(head, "p", [("background", "#f3f3f3"), ("padding", "5px"), ("margin", "5px")])

        HtmlLib.add_head_style(head, ".h1-container", [("background", "#ffffff"), ("border", "solid red 2px"),
                                                       ("padding", "5px"), ("margin", "5px")])
        HtmlLib.add_head_style(head, ".h2-container", [("background", "#ffffff"), ("border", "solid red 1.3px"),
                                                       ("padding", "5px"), ("margin", "5px")])
        HtmlLib.add_head_style(head, ".h3-container", [("background", "#ffffff"), ("border", "solid red 0.8px"),
                                                       ("padding", "5px"), ("margin", "5px")])

        HtmlLib.add_head_style(head, "header", [("background", "#ffffff"), ("border", "solid black 0.5px")])
        HtmlLib.add_head_style(head, "header::before", [("background", "#ddffdd"), ("content", "'HEADER'")])
        HtmlLib.add_head_style(head, "main", [("background", "#ffffff"), ("border", "solid black 0.5px")])
        HtmlLib.add_head_style(head, "main::before", [("background", "#ddffdd"), ("content", "'MAIN'")])
        HtmlLib.add_head_style(head, "footer", [("background", "#ffffff"), ("border", "solid black 0.5px")])
        HtmlLib.add_head_style(head, "footer::before", [("background", "#ddffdd"), ("content", "'FOOTER'")])
        HtmlLib.add_head_style(head, "section", [("background", "#ffffff"), ("border", "solid black 0.5px")])
        HtmlLib.add_head_style(head, "section::before", [("background", "#ddffdd"), ("content", "'SECTION'")])
        HtmlLib.add_head_style(head, "article", [("background", "#ffffff"), ("border", "solid black 0.5px")])
        HtmlLib.add_head_style(head, "article::before", [("background", "#ddffdd"), ("content", "'ARTICLE'")])

        HtmlLib.add_head_style(head, "h1::before",
                               [("background", "#ddffdd"), ("border", "solid brown 0.5px"), ("content", "'H1>'")])
        HtmlLib.add_head_style(head, "h2::before",
                               [("background", "#ddffdd"), ("border", "solid brown 0.5px"), ("content", "'H2>'")])
        HtmlLib.add_head_style(head, "h3::before",
                               [("background", "#ddffdd"), ("border", "solid brown 0.5px"), ("content", "'H3>'")])
        HtmlLib.add_head_style(head, "h4::before",
                               [("background", "#ddffdd"), ("border", "solid brown 0.5px"), ("content", "'H4>'")])
        HtmlLib.add_head_style(head, "h5::before",
                               [("background", "#ddffdd"), ("border", "solid brown 0.5px"), ("content", "'H5>'")])
        HtmlLib.add_head_style(head, "h6::before",
                               [("background", "#ddffdd"), ("border", "solid brown 0.5px"), ("content", "'H6>'")])
        HtmlLib.add_head_style(head, "h1", [("background", "#dd77dd"), ("border", "dashed brown 0.5px")])
        HtmlLib.add_head_style(head, "h2", [("background", "#dd77dd"), ("border", "dashed brown 0.5px")])
        HtmlLib.add_head_style(head, "h3", [("background", "#dd77dd"), ("border", "dashed brown 0.5px")])
        HtmlLib.add_head_style(head, "h4", [("background", "#dd77dd"), ("border", "dashed brown 0.5px")])
        HtmlLib.add_head_style(head, "h5", [("background", "#dd77dd"), ("border", "dashed brown 0.5px")])
        HtmlLib.add_head_style(head, "h6", [("background", "#dd77dd"), ("border", "dashed brown 0.5px")])

        HtmlLib.add_head_style(head, "i,em", [("background", "#ffddff"), ("border", "dashed brown 0.5px")])
        HtmlLib.add_head_style(head, "b,strong", [("background", "#ffaaff"), ("border", "dashed brown 0.5px")])

        HtmlLib.add_head_style(head, "a[href]::before", [("background", "#ddffdd"), ("content", "'AHREF'")])
        HtmlLib.add_head_style(head, "a[href]", [("background", "#ddffdd"), ("border", "dashed orange 0.5px")])

        HtmlLib.add_head_style(head, "sup::before", [("background", "#ddffdd"), ("content", "'SUP'")])
        HtmlLib.add_head_style(head, "sup", [("background", "#ddffdd"), ("border", "dashed orange 0.5px")])
        HtmlLib.add_head_style(head, "sub::before", [("background", "#ddffdd"), ("content", "'SUB'")])
        HtmlLib.add_head_style(head, "sub", [("background", "#ddffdd"), ("border", "dashed orange 0.5px")])

        HtmlLib.add_head_style(head, "ul::before,ol::before",
                               [("background", "gray"), ("border", "solid blue 1px"), ("content", "'LIST>'")])
        HtmlLib.add_head_style(head, "ul,ol", [("border", "solid blue 1px")])
        HtmlLib.add_head_style(head, "li::before",
                               [("background", "yellow"), ("border", "solid cyan 2px"), ("content", "'LI>'")])
        HtmlLib.add_head_style(head, "li", [("border", "solid blue 1px")])

        HtmlLib.add_head_style(head, "table:before",
                               [("background", "yellow"), ("border", "solid brown 2px"), ("content", "'TABLE>'")])
        HtmlLib.add_head_style(head, "table", [("background", "#ddffff"), ("border", "solid black 1px")])

        HtmlLib.add_head_style(head, "figure:before",
                               [("background", "cyan"), ("border", "solid brown 0.5px"), ("content", "'FIG>'")])
        HtmlLib.add_head_style(head, "figure", [("background", "#ffddff"), ("border", "solid black 1px")])
        HtmlLib.add_head_style(head, "figcaption:before",
                               [("background", "cyan"), ("border", "solid brown 0.5px"), ("content", "'FIGCAP>'")])
        HtmlLib.add_head_style(head, "figcaption", [("background", "#ddffff"), ("border", "solid black 0.5px")])

        HtmlLib.add_head_style(head, "div", [("background", "#ddffff"), ("border", "dashed orange 2px")])
        HtmlLib.add_head_style(head, "div", [("border", "dotted red 0.5px"), ("margin", "5px")])
        HtmlLib.add_head_style(head, "div::before", [("background", "#ddffdd"), ("content", "'DIV'")])

        HtmlLib.add_head_style(head, "img", [("width", f"50%"), ("margin", "5px")])
        HtmlLib.add_head_style(head, "img::before", [("background", "#ddffdd"), ("content", "'IMG'")])

        HtmlLib.add_head_style(head, "dl", [("width", f"50%"), ("margin", "5px")])
        HtmlLib.add_head_style(head, "dl::before", [("background", "#ddffdd"), ("content", "'DL'")])
        HtmlLib.add_head_style(head, "dt", [("width", f"50%"), ("margin", "5px")])
        HtmlLib.add_head_style(head, "dt::before", [("background", "#ddffdd"), ("content", "'DT'")])
        HtmlLib.add_head_style(head, "dd", [("width", f"50%"), ("margin", "5px")])
        HtmlLib.add_head_style(head, "dd::before", [("background", "#ddffdd"), ("content", "'DD'")])

        HtmlLib.add_head_style(head, "p", [("background", "#ffffdd"), ("border", "dashed orange 0.5px")])
        HtmlLib.add_head_style(head, "*", [("background", "pink"), ("border", "solid black 5px")])
        HtmlLib.add_head_style(head, "span", [("background", "#ffdddd"), ("border", "dotted black 0.5px")])

    @classmethod
    def remove_unnecessary_containers(cls, html, removable_xpaths=None, debug=False):
        """
            <style> div.gx-3.gy-5.ps-2 {
            <style> div.gx-3.gy-5.ps-2.row {
            <style> div.col-lg-10.col-12.offset-lg-0 {
            <style> div.header__main {
            <style> div.header__content.pt-4 {
            <style> div.section-tooltip.footnote-tooltip {
            <style> #___gatsby {
            <style> #gatsby-focus-wrapper {
            <style> #gatsby-focus-wrapper>div {
            <style> div.s9-widget-wrapper.mt-3.mb-3 {
            <style> div[data-sal="slide-up"] {
            <style> div.container.chapters{
            """
        if removable_xpaths is None:
            return None
        removables = set()
        for xpath in removable_xpaths:
            elems = html.xpath(xpath)
            if debug:
                print(f"{xpath} => {len(elems)}")
            for elem in elems:
                removables.add(elem)
        for removable in removables:
            HtmlUtil.remove_element_in_hierarchy(removable)
        HtmlUtil.remove_empty_elements(html, "div")

    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_dict, hit_dict, infile, para_phrase_dict):
        """adds non-empty hits in hit_dict and all to all_dict
        :param all_dict: accumulates para_phrase_dict by infile

        TODO - move to amilib
        """
        item_paras = [item for item in para_phrase_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_dict[infile] = para_phrase_dict
            for para_id, hits in para_phrase_dict.items():
                for hit in hits:
                    # TODO should write file with slashes (on Windows we get %5C)
                    infile_s = f"{infile}"
                    infile_s = infile_s.replace("\\", "/")
                    infile_s = infile_s.replace("%5C", "/")
                    url = f"{infile_s}#{para_id}"
                    hit_dict[hit].append(url)

    @classmethod
    def create_hit_html_with_ids(
            cls,
            infiles,
            phrases=None,
            outfile=None,
            xpath=None,
            debug=False):
        """

        Parameters
        ----------
        infiles list of files to annotate (must contain p[@id])
        phrases (optional?) list of phrases to search with
        outfile (HTML) file for list of links to paragraphs
        xpath (optionaL) sections in target document
        debug (optional) print filenames, etc.

        Returns html element for list of hit links
        -------

        """
        all_paras = []
        all_dict = dict()
        hit_dict = defaultdict(list)
        if type(infiles) is str:
            infiles = [infiles]
        if type(phrases) is not list:
            phrases = [phrases]
        for infile in infiles:
            logger.info(f">>> html file {infile}")
            assert Path(infile).exists(), f"{infile} does not exist"
            html_tree = lxml.etree.parse(str(infile), HTMLParser())
            paras = HtmlLib.find_paras_with_ids(html_tree, para_xpath=xpath)
            all_paras.extend(paras)

            # this does the search
            para_phrase_dict = HtmlLib.search_phrases_in_paragraphs(paras, phrases)
            if len(para_phrase_dict) > 0:
                if debug:
                    print(f"para_phrase_dict {para_phrase_dict}")
                IPCC.add_hit_with_filename_and_para_id(all_dict, hit_dict, infile, para_phrase_dict)
        if debug:
            print(f"para count~: {len(all_paras)}")
        outfile = Path(outfile)
        outfile.parent.mkdir(exist_ok=True, parents=True)
        html1 = cls.create_html_from_hit_dict(hit_dict)
        if outfile:
            with open(outfile, "w") as f:
                if debug:
                    print(f" hitdict {hit_dict}")
                HtmlLib.write_html_file(html1, outfile, debug=True)
        return html1

    @classmethod
    def create_html_from_hit_dict(cls, hit_dict):
        html = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html)
        ul = ET.SubElement(body, "ul")
        for term, hits in hit_dict.items():
            li = ET.SubElement(ul, "li")
            p = ET.SubElement(li, "p")
            p.text = term
            ul1 = ET.SubElement(li, "ul")
            for hit in hits:
                # TODO manage hits with Paths
                # on windows some hits have "%5C' instead of "/"
                hit = str(hit).replace("%5C", "/")
                li1 = ET.SubElement(ul1, "li")
                a = ET.SubElement(li1, "a")
                a.text = hit.replace("/html_with_ids.html", "")
                ss = "ipcc/"
                try:
                    idx = a.text.index(ss)
                except Exception as e:
                    print(f"cannot find substring {ss} in {a}")
                    continue
                a.text = a.text[idx + len(ss):]
                a.attrib["href"] = hit
        return html

    @classmethod
    def find_analyse_curly_refs(cls, para_with_ids):
        CURLY_RE = ".*\\{(?P<links>.+)\\}.*"  # any matched non-empty curlies {...}
        for para in para_with_ids:
            text = ''.join(para.itertext()).strip()
            match = re.match(CURLY_RE, text)
            if match:
                IPCC._parse_curly(match, para)

    @classmethod
    def _parse_curly(cls, match, para):
        # strip any enclosing curly brackets and whitespace
        curly_content = match.groupdict()["links"].strip()
        print(f"====={curly_content}=====")
        nodes = para.xpath(".//node()")
        matches = 0
        matched_node = None
        for node in nodes:

            # print(f"TYPE {type(node)}")
            if type(node) is _ElementUnicodeResult:
                txt = str(node)
                matched_node = node
            elif type(node) is HtmlComment:
                continue
            else:
                txt = ''.join(node.itertext())
                matched_node = node
                # continue
            # print(f"TXT>> {txt}")
            if curly_content in txt:
                # print(f"MATCHED {tag} => {txt}")
                matches += 1
            else:
                # print(f"NO MATCH {txt}")
                pass
        if matches:
            node_parent = matched_node.getparent()
            # replace curly text with span to receive matched and unmatched links
            br = ET.SubElement(node_parent, "br")
            link_span = ET.SubElement(node_parent, "span")
            # this is a mess. The curlies are sometimes separate spans, sometimes not
            # just add the hyperlinks. Messy but best we can do
            # this is logically correct biut not supported by lxml
            # idx = node_parent.index(matched_node)
            # node_parent.insert(idx, link_span)
            # node_parent.remove(matched_node)

            link_texts = re.split("[;,]\\s+", curly_content)
            # print(f"links: {link_texts}")
            for link_text in link_texts:
                # print(f"link: {link_text}")
                cls._parse_link_add_anchor(link_text, link_span)

    @classmethod
    def _parse_link_add_anchor(cls, link_text, link_span):
        a = ET.SubElement(link_span, "a")
        spanlet = ET.SubElement(link_span, "span")
        spanlet.text = ", "
        links_re = "(?P<report>WGI|WG1|WGII|WGIII||SYR|SRCCL|SROCC|SR1\\.?5)\\s+(?P<chapter>SPM|TS|Box|CCB|Cross-(Section|Chapter)\\s+Box|Figure|Global to Regional Atlas Annex|Table|Annex|\\d+)(\\s+|\\.)(?P<section>.*)"
        link_match = re.match(links_re, link_text)
        if link_match:
            report = link_match['report']
            chapter = link_match['chapter']
            section = link_match['section']
            href = cls._create_href(report, chapter, section)
            a.attrib["href"] = href
            a.text = link_text
        else:
            i = ET.SubElement(a, "i")
            i.text = link_text
            print(f" FAILED TO MATCH Rep_chap_sect [{link_text}]")

    @classmethod
    def _create_href(cls, report, chapter, section):
        report = cls.normalize_report(report)
        chapter = cls.normalize_chapter(chapter)
        file = f"../../{report}/{chapter}/{HTML_WITH_IDS}#{section}"
        return file
        # print(f">> {file}")

    @classmethod
    def normalize_report(cls, report):
        report = report.replace("III", "3")
        report = report.replace("II", "2")
        report = report.replace("I", "1")
        report = report.lower()
        return report

    @classmethod
    def normalize_chapter(cls, chapter):
        return chapter.lower()

    @classmethod
    def download_save_chapter(cls, report, chap, wg_url, outdir=None, sleep=2):
        """
        creates url of form {wg_url}/{report}/chapter/{chap}
        Parameters
        ----------
        report
        chap
        wg_url
        outdir
        sleep

        Returns
        -------

    MESSY - should be in web_publisher
        """
        ami_driver = AmiDriver(sleep=sleep)
        web_publisher_classname = IPCCPublisherTool.get_web_publisher_classname(report)
        if not web_publisher_classname:
            print(f"Cannot find web_publisher from {report}")
            return
        print(f"web publisher assumed to be {web_publisher_classname}")
        web_publisher = web_publisher_classname()
        cleaned_file = Path(outdir, f"{report}", f"{chap}", f"{web_publisher.cleaned_filename}.html")
        raw_file = Path(outdir, f"{report}", f"{chap}", f"{web_publisher.raw_filename}.html")
        root_elem = ami_driver.download_and_save(raw_file, chap, report, wg_url)
        htmlx = HtmlLib.create_html_with_empty_head_body()
        web_publisher.clean_from_raw(htmlx, root_elem)

        XmlLib.write_xml(htmlx, cleaned_file)


class IPCCPublisherTool(ABC):

    @abstractmethod
    def get_removable_xpaths(self):
        pass

    @abstractmethod
    def create_and_add_id(self, id, p, parent, pindex):
        """
        :param id: id from document
        :param p: paragraph element
        :param parent of paragraph
        :param pindex index of p in parent
        """

    @property
    @abstractmethod
    def raw_filename(self):
        pass

    @property
    @abstractmethod
    def cleaned_filename(self):
        pass

    def create_pid(cls, p, debug=False):
        pid = None
        parent = p.getparent()
        if parent.tag == "div":
            pindex = parent.index(p) + 1  # 1-based
            id = parent.attrib.get("id")
            if id is None:
                text = "".join(p.itertext())
                if text is not None:
                    if debug:
                        print(f"p without id parent: {text[:20]}")
                else:
                    print(f"empty p without id-ed parent")
            else:
                pid = cls.create_and_add_id(id, p, parent, pindex)
        return pid

    def add_para_ids_and_make_id_list(self, infile, outfile=None, idfile=None, parafile=None, debug=False):
        """creates IDs for paragraphs
        :param idfile:"""
        inhtml = ET.parse(str(infile), HTMLParser())
        idset = set()
        elems = inhtml.xpath("//*[@id]")
        print(f"elems {len(elems)}")
        for elem in elems:
            id = elem.attrib.get("id")
            if id in idset:
                print(f"duplicate id {id}")
        pelems = inhtml.xpath("//p[text()]")
        print(f"pelems {len(pelems)}")
        """
            <div class="h2-container" id="3.1.2">
              <h2 class="Headings_•-H2---numbered" lang="en-GB">
                <span class="_idGenBNMarker-1">3.1.2</span>Linkages to Other Chapters in the Report <span class="arrow-up"></span>
                <span class="arrow-down"></span>
              </h2>
              <div class="h2-siblings" id="h2-2-siblings">
                <p class="Body-copy_•-Body-copy--full-justify-" lang="en-GB"><a class="section-link" data-title="Mitigation pathways
                <p...
               # id numbers may be off by 1 or more due to unnumbered divs (so 3.8 gives h1-9-siblings
            """
        pid_list = []
        pid_dict = dict()

        for p in pelems:
            pid = None
            pid = self.create_pid(p, debug=debug)
            if pid:
                pid_list.append(pid)
                pid_dict[pid] = p
        idhtml = HtmlLib.create_html_with_empty_head_body()
        idbody = HtmlLib.get_body(idhtml)
        idul = ET.SubElement(idbody, "ul")
        for pid in pid_list:
            idli = ET.SubElement(idul, "li")
            ida = ET.SubElement(idli, "a")
            ida.attrib["href"] = f"./html_with_ids.html#{pid}"
            ida.text = pid
        if outfile:
            HtmlLib.write_html_file(inhtml, outfile=outfile, debug=True)
        if idfile:
            HtmlLib.write_html_file(idhtml, idfile)
        if parafile and outfile:
            # this is too bulky normally
            print(f"searching {outfile} for p@ids")
            idhtml = ET.parse(str(outfile), HTMLParser())
            pids = idhtml.xpath(".//p[@id]")
            print(f"pids {len(pids)} {pids[:20]}")
            for pid in pids[:10]:
                print(f"pid: {pid.attrib['id']}")
            parahtml = HtmlLib.create_html_with_empty_head_body()
            parabody = HtmlLib.get_body(parahtml)
            paraul = ET.SubElement(parabody, "ul")
            for pid, p in pid_dict.items():
                if len(p) == 0:
                    print(f"cannot find id {pid}")
                    continue
                parali = ET.SubElement(paraul, "li")
                h2 = ET.SubElement(parali, "h2")
                h2.text = pid
                parali.append(copy.deepcopy(p))
            HtmlLib.write_html_file(parahtml, outfile=parafile, debug=True)

    def remove_unnecessary_markup(self, infile):
        """
        removes markukp from files downloaded from IPCC site
        :param infile: html file
        :return: html_elem for de_gatsby or de_wordpress etc.
        """

        html_elem = ET.parse(str(infile), HTMLParser())
        assert html_elem is not None
        head = HtmlLib.get_head(html_elem)
        IPCC.add_styles_to_head(head)
        removable_xpaths = self.get_removable_xpaths()
        IPCC.remove_unnecessary_containers(html_elem, removable_xpaths=removable_xpaths)
        return html_elem

    @classmethod
    def get_web_publisher_classname(cls, report):
        """
        factory method new instance of IPCCGatsby() or IPCCWordpress()
        :param report: wg1/2/3 or sr* or syr
        :return: classname (e.g. pyamihtmlx.ipcc.IPCCGatsby) or None
        """
        if not report:
            return None
        report = report.lower()
        # MAPPING = {c.lookup: c for c in WebPublisherTool.__subclasses__()}
        if report in {"sr15", "srocc", "srccl"}:
            name = "climate.ipcc.IPCCWordpress"
            name = "test.ipcc_classes.IPCCWordpress"
        if report in {"wg1", "wg2", "wg3", "syr"}:
            name = "climate.ipcc.IPCCGatsby"
            name = "test.ipcc_classes.IPCCGatsby"
        clazz = Util.get_class_from_name(name)
        return clazz

    @property
    @abstractmethod
    def base_filename(self):
        pass

    def download_clean_chapter(self, chap, minsize, outdir, report, wg_url):
        outdir = Path(outdir, report, chap)
        IPCC.download_save_chapter(report, chap, wg_url, outdir=outdir, sleep=1)
        raw_file = Path(outdir, f"{self.base_filename}_{RAW}.html")
        FileLib.assert_exist_size(raw_file, minsize=minsize, abort=False)
        html_elem = self.remove_unnecessary_markup(raw_file)
        assert html_elem is not None, f"{raw_file} should not give None html"
        body = HtmlLib.get_body(html_elem)
        de_gatsby_file = Path(outdir, f"{DE}_{self.base_filename}.html")
        HtmlLib.write_html_file(html_elem, outfile=de_gatsby_file, debug=True)
        html_ids_file, idfile, parafile = self.add_ids(de_gatsby_file, outdir, assert_exist=True,
                                                       min_id_sizs=10, min_para_size=10)


class IPCCGatsby(IPCCPublisherTool):
    """
    processes IPCC reports is Gatsby format
    """

    def __init__(self, filename=None):
        self.filename = filename if filename else HTML_WITH_IDS
        self.container_levels = ["h1-container", "h2-container", "h3-container", "h4-container"]

    @property
    def raw_filename(self):
        return "gatsby_raw"

    @property
    def cleaned_filename(self):
        return "gatsby"

    def get_removable_xpaths(self):
        removable_xpaths = [
            ".//div[contains(@class,'gx-3') and contains(@class,'gy-5') and contains(@class,'ps-2')]",
            # this fails
            # ".//div[contains(@class,'col-lg-10') and contains(@class,'col-12') and contains(@class,'offset-lg-0')]",
            ".//*[@id='___gatsby']",
            ".//*[@id='gatsby-focus-wrapper']/div",
            ".//*[@id='gatsby-focus-wrapper']",
            ".//*[@id='footnote-tooltip']",
            ".//div[contains(@class,'s9-widget-wrapper') and contains(@class,'mt-3') and contains(@class,'mb-3')]",
            ".//div[contains(@class,'chapter-figures')]",
            ".//header/div/div/div/div",
            ".//header/div/div/div",
            ".//header/div/div",
            ".//header/div",
            ".//section[contains(@class,'mb-5') and contains(@class, 'mt-5')]",
            ".//div[contains(@class,'container') and contains(@class, 'chapters') and contains(@class, 'chapter-')]",
            ".//*[contains(@id, 'footnote-tooltip-text')]",
            ".//div[@id='chapter-figures']/div/div/div/div",
            ".//div[@id='chapter-figures']/div/div/div",
            ".//div[@id='chapter-figures']/div/div",
            ".//div[@id='chapter-figures']/div",
            ".//div[@id='chapter-figures']//div[@class='row']",
        ]
        return removable_xpaths

    def create_and_add_id(self, id, p, parent, pindex, debug=False):
        pid = None
        match = re.match("h\\d-\\d+-siblings", id)
        if not match:
            if id.startswith("chapter-") or (id.startswith("_idContainer") or id.startswith("footnote")):
                pass
            else:
                if debug:
                    print(f"cannot match {id}")
        else:
            grandparent = parent.getparent()
            grandid = grandparent.get("id")

            match = grandid is not None and re.match(
                "\\d+(\\.\\d+)*|(box|cross-chapter-box|cross-working-group-box)-\\d+(\\.\\d+)*|executive-summary|FAQ \\d+(\\.\\d+)*|references",
                grandid)
            if not match:
                if debug:
                    print(f"grandid does not match {grandid}")
            else:
                pid = f"{grandid}_p{pindex}"
                p.attrib["id"] = pid
        return pid

    @property
    def raw_filename(self):
        return GATSBY_RAW

    @property
    def base_filename(self):
        return GATSBY

    @property
    def cleaned_filename(self):
        return DE_GATSBY

    def raw_to_paras_and_ids(self, topdir, outdir=None):
        globx = f"{topdir}/**/{self.raw_filename}.html"
        infiles = FileLib.posix_glob(globx, recursive=True)
        for infile in infiles:
            htmlx = self.remove_unnecessary_markup(infile)
            if not outdir:
                outdir = Path(infile).parent
                outdir.mkdir(parents=False, exist_ok=True)

            outfile = Path(outdir, f"{self.cleaned_filename}.html")
            HtmlLib.write_html_file(htmlx, outfile, debug=True)
            infile = outfile
            # add ids
            outfile = str(Path(outdir, f"{HTML_WITH_IDS}.html"))
            idfile = str(Path(outdir, f"{ID_LIST}.html"))
            parafile = str(Path(outdir, f"{PARA_LIST}.html"))
            self.add_para_ids_and_make_id_list(infile, idfile=idfile, parafile=parafile, outfile=outfile)

    def analyse_containers(self, container, level, ul, filename=None, debug=False):
        """Part of ToC making"""
        container_xpath = f".//div[contains(@class,'{self.container_levels[level]}')]"
        h_containers = container.xpath(container_xpath)

        texts = []
        for h_container in h_containers:
            self.add_container_infp_to_tree(debug, filename, h_container, level, texts, ul)

    def add_container_infp_to_tree(self, debug, filename, h_container, level, texts, ul):
        if debug:
            print(f"id: {h_container.attrib['id']}")
        h_elems = h_container.xpath(f"./h{level + 1}")
        text = "???" if len(h_elems) == 0 else ''.join(h_elems[0].itertext()).strip()
        if debug:
            print(f"text: {text}")
        texts.append(text)
        li = ET.SubElement(ul, "li")
        a = ET.SubElement(li, "a")
        target_id = h_container.attrib["id"]
        a.attrib["href"] = f"./{filename}#{target_id}"
        span = ET.SubElement(a, "span")
        span.text = text
        ul1 = ET.SubElement(li, "ul")
        if level < len(self.container_levels):
            self.analyse_containers(h_container, level + 1, ul1, filename=filename)

    def make_header_and_nav_ul(self, body):
        """Part of ToC making"""
        header_h1 = body.xpath("div//h1")[0]
        toc_title = header_h1.text
        toc_html, ul = self.make_nav_ul(toc_title)
        return toc_html, ul

    def make_nav_ul(self, toc_title):
        """Part of ToC making"""
        toc_html = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(toc_html)
        toc_div = ET.SubElement(body, "div")
        toc_div.attrib["class"] = "toc"
        toc_div_div = ET.SubElement(toc_div, "div")
        toc_div_span = ET.SubElement(toc_div_div, "span")
        toc_div_span.text = toc_title
        nav = ET.SubElement(toc_div, "nav")
        nav.attrib["role"] = "doc-top"
        ul = ET.SubElement(nav, "ul")
        return toc_html, ul

    def add_ids(self, de_gatsby_file, outdir, assert_exist=False, min_id_sizs=10000, min_html_size=100000,
                min_para_size=100000):
        """adds ids to paras (and possibly sections)
        relies on convention naming
        creates
        * html_with_ids.html
        * id_list.html
        * para_list.html
        :param de_gatsby_file: outputb from gatsby-raw => gatsby => de_gatsby (may change)
        :param outdir: ouput directory
        :param assert_exist: ifg True runs assrt on existence and file_size
        :return:  html_ids_file, idfile, parafile
        """
        html_ids_file = Path(outdir, f"{HTML_WITH_IDS}.html")
        idfile = Path(outdir, f"{ID_LIST}.html")
        parafile = Path(outdir, f"{PARA_LIST}.html")
        self.add_para_ids_and_make_id_list(
            infile=de_gatsby_file, idfile=idfile, outfile=html_ids_file, parafile=parafile)
        if assert_exist:
            abort = False
            FileLib.assert_exist_size(idfile, minsize=min_id_sizs, abort=abort)
            FileLib.assert_exist_size(html_ids_file, minsize=min_html_size, abort=abort)
            FileLib.assert_exist_size(parafile, minsize=min_para_size, abort=abort)
        return html_ids_file, idfile, parafile

    def clean_from_raw(self, htmlx, root_elem):
        div = ET.SubElement(HtmlLib.get_body(htmlx), "div")
        # remove some clutter
        XmlLib.remove_elements(root_elem, xpath="//div[contains(@class, 'col-12')]",
                               new_parent=div, debug=True)
        # remove coloured page
        XmlLib.remove_elements(htmlx, xpath="//div[@data-gatsby-image-wrapper]/div[@aria-hidden='true']",
                               debug=True)


class IPCCArgs(AbstractArgs):
    SECTIONS = "sections"
    VAR = "var"

    AUTHORS = "authors"
    CHAPTER = "chapter"
    DOWNLOAD = "download"
    HELP = "help"
    PDF2HTML = "pdf2html"
    QUERY = "query"
    REPORT = "report"
    SEARCH = "search"
    XPATH = "xpath"

    OPERATIONS = [
        AUTHORS,
        DOWNLOAD,
        PDF2HTML,
        QUERY,
        SEARCH,
        XPATH,
        HELP,
    ]

    pyamihtmlx_dir = Path(__file__).parent
    pyamihtml_dir = pyamihtmlx_dir.parent
    SYMBOL_DICT = {
        "_PYAMIHTMLX": pyamihtmlx_dir,  # top of code
        "_PYAMIHTML": pyamihtml_dir,  # top of repo
        "_TEMP": Path(pyamihtml_dir, "temp"),  # temp tree
        "_QUERY_OUT": Path(pyamihtml_dir, "temp", "queries"),  # output for queries
        "_TEST": Path(pyamihtml_dir, "test"),  # top of test tree
        "_IPCC_REPORTS": Path(pyamihtml_dir, "test", "resources", "ipcc", "cleaned_content"),  # top of IPCC content
        # files
        "_HTML_IDS": "**/html_with_ids.html",
        # XPATHS
        # refs
        "_REFS": "//p[@id and ancestor::*[@id='references']]",  # select references section
        "_NOREFS": "//p[@id and not(ancestor::*[@id='references'])]",  # not selecr references
        "_EXEC_SUMM": "//p[@id and ancestor::*[@id='executive-summary']]",  # executive summaries
        "_FAQ": "//div[h2 and ancestor::*[@id='frequently-asked-questions']]",  # FAQ Q+A
        "_FAQ_Q": "//h2[ancestor::*[@id='frequently-asked-questions']]",  # FAQ Q
        "_FAQ_A": "//p[ancestor::*[@id='frequently-asked-questions']]",  # FAQ A
        "_IMG_DIV": "//div[p[span[img]]]",  # div containing an img

    }

    def __init__(self):
        """arg_dict is set to default"""
        super().__init__()
        self.subparser_arg = "IPCC"

    # class IPCCArgs

    def add_arguments(self):
        """creates adds the arguments for pyami commandline

        """
        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        self.parser.description = textwrap.dedent(
            'Manage and search IPCC resources and other climate stuff. \n'
            '----------------------------------------------------------\n'
            'see pyamihtmlx/IPCC.md'
            '\nExamples:\n'
            'help'
            ''
            'parse foo.pdf and create default HTML'
            f'  pyamihtmlx IPCC --input foo.pdf\n'
            f''

        )
        super().add_arguments()

        self.parser.formatter_class = argparse.RawDescriptionHelpFormatter
        INPUT_HELP = f"input from:\n" \
                     f"   file/s single, multiple, and glob/wildcard (experimental)\n" \
                     f"   directories (needs {self.INFORMAT})\n" \
                     f"   URL/s (must start with 'https:); provide {self.OUTDIR} for output' \n"
        # self.parser.add_argument(f"--{IPCCArgs.INPUT}", nargs="+",
        #                          help=INPUT_HELP)

        CHAPTER_HELP = "IPCC Chapter/s: SPM, TS, ANNEX, Chapter-1...Chapter-99"
        self.parser.add_argument(f"--{IPCCArgs.CHAPTER}", nargs="+",
                                 help=CHAPTER_HELP)

        INFORM_HELP = "input format/s; experimental"
        self.parser.add_argument(f"--{IPCCArgs.INFORMAT}", nargs="+", default="PDF",
                                 help=INFORM_HELP)

        OPERATION_HELP = f"operations from {IPCCArgs.OPERATIONS}"
        self.parser.add_argument(f"--{IPCCArgs.OPERATION}", choices=IPCCArgs.OPERATIONS, nargs="+",
                                 help=OPERATION_HELP)

        QUERY_HELP = "search word/s"
        self.parser.add_argument(f"--{IPCCArgs.QUERY}", nargs="+",
                                 help=QUERY_HELP)

        REPORT_HELP = f"IPCC Reports: lowercase from {REPORTS}"
        self.parser.add_argument(f"--{IPCCArgs.REPORT}", nargs="+",
                                 help=REPORT_HELP)

        XPATH_HELP = "xpath filter (e.g. './/section'"
        self.parser.add_argument(f"--{IPCCArgs.XPATH}", nargs="+",
                                 help=XPATH_HELP)
        return self.parser

    # class IPCCArgs

    def process_args(self, debug=True):
        """runs parsed args
        :return:

        """

        if not self.arg_dict:
            print(f"cannot find self.arg_dict")
            return
        logger.info(f"argdict: {self.arg_dict}")
        print(f"arg_dict: {self.arg_dict}")
        informats = self.arg_dict.get(IPCCArgs.INFORMAT)
        paths = self.get_paths()
        operation = self.get_operation()

        input = self.create_input_files()
        outdir, output = self.create_output_files()

        chapter = self.get_chapters()
        report = self.get_reports()

        kwargs = self.get_kwargs(save_global=True)  # not saved??
        section_regexes = self.get_section_regexes()
        author_roles = self.get_author_roles_nyi()
        query = self.get_query()
        xpath = self.get_xpath()
        if debug:
            if type(input) is list:
                print(f"inputs: {len(input)} > {input[:3]}...")
            else:
                print(f"input: {input}")
            print(f"debug: {debug}")
            print(f"report: {report}")
            print(f"chapter: {chapter}")
            print(f"outdir: {outdir}")
            print(f"output: {output}")
            print(f"kwargs: {kwargs}")
            print(f"query: {query}")
            print(f"xpath: {xpath}")

        logger.info(f"processing {len(paths)} paths")

        if self.process_operation(
                operation,
                outdir=outdir,
                paths=paths,
                section_regexes=section_regexes,
                author_roles=author_roles):
            pass
        elif query is not None:
            if not output:
                print(f"*** no output argument, no search")
            else:
                self.search(input, query=query, xpath=xpath, outfile=output)
        else:
            logger.warning(f"Unknown operation {operation}")

    # class IPCCArgs

    def process_operation(self, operation, outdir=None, paths=None, section_regexes=None, author_roles=None):
        done = True
        if operation == IPCCArgs.DOWNLOAD:
            self.download()
        elif operation == IPCCArgs.PDF2HTML:
            self.convert_pdf2html(outdir, paths, section_regexes)
        elif operation == IPCCArgs.AUTHORS:
            self.extract_authors(author_roles, paths)
        elif operation == IPCCArgs.KWARGS:
            self.get_kwargs(save_global=True)
        else:
            done = False
            return done

    # class IPCCArgs

    def create_output_files(self):
        outdir = self.get_value_lookup_symbol(self.get_outdir, lookup=self.SYMBOL_DICT)
        output = self.get_value_lookup_symbol(self.get_output, lookup=self.SYMBOL_DICT)
        print(f"outdir {outdir} output {output}")

        output_list = self.join_filenames_expand_wildcards(outdir, output)
        if output_list is None:
            print(f"**NO OUTPUT parameter given")
        elif type(output_list) is list and len(output_list) == 1:
            output = output_list[0]
        return outdir, output

    # class IPCCArgs

    def create_input_files(self, debug=False):
        home_dir = Path.home()
        print(f"home {home_dir}")
        indir = self.get_value_lookup_symbol(self.get_indir, lookup=self.SYMBOL_DICT)
        input = self.get_value_lookup_symbol(self.get_input, lookup=self.SYMBOL_DICT)
        input = self.join_filenames_expand_wildcards(indir, input)
        if debug:
            print(f"input {input}")
        return input

    # class IPCCArgs

    def join_filenames_expand_wildcards(self, directory, filename, recursive=True, debug=False):
        """
        joins directory to filename. May or may not contain wildcards. result will be globbed
        Python metacharacters will be used ("**", "?", ".", etc.)
        :param directory: if None, ignored; may contain metacharacters
        :param filenme; if directory is none, fullfile = directory/filename
        :param recursive: recursive globbing (default True)
        """
        if not filename:
            return directory
        if not directory:
            fullfile = filename
        else:
            try:
                fullfile = FileLib.join_dir_and_file_as_posix(directory, filename)
            except Exception as e:
                print(f"failed to join {directory} , {filename} because {e}")
        if debug:
            print(f"fullfile {fullfile}")

        fullfile_list = FileLib.posix_glob(fullfile, recursive=recursive)
        if fullfile_list == []:
            print(f"empty list from {fullfile}")
        return fullfile_list

    # class IPCCArgs

    def get_value_lookup_symbol(self, getter, lookup=None):
        """
        :param getter: function to get command parametr (e.g. get_indir)
        :param lookup: dictionary to substitute underscore variabls

        """
        if not lookup:
            raise ValueError(f"no value for lookup dict")
        value = getter()
        if value and str(value).startswith("_"):
            value1 = lookup.get(value)
            if value1 is None:
                print(f"allowed substitutions {self.lookup.keys()} but found {value}")
                raise ValueError(f"unknown symbol {value}")
            value = value1
        return value

    # class IPCCArgs

    def convert_pdf2html(self, outdir, paths, section_regexes):
        for path in paths:
            HtmlGenerator.create_sections(path, section_regexes, outdir=outdir)

    # class IPCCArgs

    def extract_authors(self, author_roles, paths):
        for path in paths:
            IPCCCommand.extract_authors_and_roles(path, author_roles)

    # class IPCCArgs

    def get_section_regexes(self):
        section_regexes = self.arg_dict.get(IPCCArgs.SECTIONS)
        if not section_regexes:
            section_regexes = IPCCSections.get_section_regexes()
        return section_regexes

    # class IPCCArgs

    def get_kwargs(self, save_global=False, debug=False):
        kwargs = self.arg_dict.get(IPCCArgs.KWARGS)
        if not kwargs and debug:
            print(f"no keywords given")
            return

        kwargs_dict = self.parse_kwargs_to_string(kwargs)
        # print(f"saving kywords to kwargs_dict {kwargs_dict} ; not fully working")
        logger.info(f"kwargs {kwargs_dict}")
        if save_global:
            IPCCCommand.save_args_to_global(kwargs_dict, overwrite=True)
        return kwargs_dict

    # class IPCCArgs

    def get_paths(self):
        inputx = self.arg_dict.get(IPCCArgs.INPUT)
        logger.info(f"input {inputx}")
        paths = IPCCCommand.get_paths(inputx)
        return paths

    def get_chapters(self):
        inputx = self.arg_dict.get(IPCCArgs.CHAPTER)
        chapters = Util.get_list(inputx)
        return chapters

    # class IPCCArgs

    def get_reports(self):
        inputx = self.arg_dict.get(IPCCArgs.REPORT)
        paths = Util.get_list(inputx)
        return paths

    # class IPCCArgs:

    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
        arg_dict = dict()
        arg_dict[IPCCArgs.INFORMAT] = ['PDF']
        return arg_dict

    def get_author_roles_nyi(self):
        pass

    # class IPCCArgs

    def get_query(self):
        # returns a list
        query = self.arg_dict.get(IPCCArgs.QUERY)
        query = Util.get_list(query)
        return query

    # class IPCCArgs

    def get_xpath(self):
        xpath = self._get_value_and_substitute_with_dict(arg=IPCCArgs.XPATH, dikt=self.SYMBOL_DICT)
        return xpath

    # class IPCCArgs

    def _get_value_and_substitute_with_dict(self, arg=None, dikt=None):
        if arg is None:
            return None
        if dikt is None:
            return None
        value = self.arg_dict.get(arg)
        if value and value.startswith("_"):
            value1 = dikt.get(value)
            if value:
                value = value1
        return value

    # class IPCCArgs

    def search(self, inputx, query=None, xpath=None, outfile=None, debug=False):
        if not inputx:
            print(f"no input files for search")
            return
        inputs = Util.get_list(inputx)
        IPCC.create_hit_html_with_ids(inputs, phrases=query, xpath=xpath, outfile=outfile, debug=debug)

    # class IPCCArgs

    def download(self):
        input = self.get_input()
        output = self.get_output()
        outdir = self.get_outdir()

        reports = self.get_reports()
        chapters = self.get_chapters()

        indir = self.get_indir()
        print(f"indir {indir}, input {input}, output {output}, outdir {outdir}")
        print(f"chap {chapters}, report {reports}")
        if not indir or not chapters or not reports:
            logger.error(f"Must give indir/reports/chapters")
            return
        for report in reports:
            chapters = self.get_chapters()
            chapters = self.chapter_wildcards(chapters, report)  # kludge until we get a IPCC python dictionary
            for chapter in chapters:
                wg_url = f"{indir}/{report}/"
                print(f"downloading from: {wg_url}")
                IPCC.download_save_chapter(report, chapter, wg_url, outdir=outdir, sleep=1)

    def chapter_wildcards(self, chapters, report):
        """kludge - we need a dictionary
        """
        if not chapters:
            print(f"no chapters given")
            return []
        if chapters == "Chapter*":
            return ["chapter-{i}" in range(1, 20)]
        return chapters


class IPCCSections:

    @classmethod
    def get_ipcc_regexes(cls, front_back="Table of Contents|Frequently Asked Questions|Executive Summary|References"):
        """
        :param front_back: common section headings (not numbered)
        :return: (section_regex_dict, section_regexes) to manage regexes (largely for IPCC).

        The dict is more powerful but doesn't work properly yet

        """
        return cls.get_section_regexes(), cls.get_section_regex_dict(front_back)

    @classmethod
    def get_section_regexes(cls):
        section_regexes = [
            # C: Adaptation...
            ("section",
             #                f"\s*(?P<id>Table of Contents|Frequently Asked Questions|Executive Summary|References|(?:(?:[A-G]|\d+)[\.:]\d+\s+[A-Z]).*"),
             fr"\s*(?P<id>Table of Contents|Frequently Asked Questions|Executive Summary|References"
             fr"|(?:[A-Z]|\d+)[.:]\d*)\s+[A-Z].*"),
            # 7.1 Introduction
            ("sub_section",
             fr"(?P<id>FAQ \d+\.\d+"
             fr"|(?:\d+\.\d+"
             fr"|[A-Z]\.\d+)"
             fr"\.\d+)"
             fr"\s+[A-Z]*"),  # 7.1.2 subtitle or FAQ 7.1 subtitle D.1.2 Subtitle
            ("sub_sub_section",
             fr"(?P<id>"
             fr"(?:\d+\.\d+\.\d+\.\d+"  # 7.1.2.3 subsubtitle
             fr"|[A-Z]\.\d+\.\d+)"
             fr")\s+[A-Z].*")  # D.1.3
        ]
        return section_regexes

    @classmethod
    def get_section_regex_dict(cls, front_back):
        section_regex_dict = {
            "num_faq": {
                "file_regex": "NEVER.*/spm/.*",  # check this
                "sub_section": fr"(?P<id>FAQ \d+\.\d+)"
            },
            "alpha_sect": {
                "file_regex": ".*(srocc).*/spm/.*",  # check this
                "desc": "sections of form 'A: Foo', 'A.1 Bar', 'A.1.2 'Baz'",
                "section": fr"\s*(?P<id>[A-Z][.:]\s+[A-Z].*)",  # A: Foo
                "sub_section": fr"\s(?P<id>[A-Z]\.\d+\.\d+)\s+[A-Z]*",  # A.1 Bar
                "sub_sub_section": fr"\s(?P<id>[A-Z]\.\d+\.\d+)\s+[A-Z]*"  # A.1.2 Plugh
            },
            "num_sect_old": {
                "file_regex": ".*NEVER.*",
                "desc": "sections of form '1. Introduction', "
                        "subsections '1.2 Bar' "
                        "subsubsections '1.2.3 Plugh'"
                        "subsubsubsections  '1.2.3.4 Xyzzy (may not be any)",
                "section": fr"\s*(?P<id>(?:{front_back}|\s*\d+[.:]?)\s+[A-Z].*",  # A: Foo
                "sub_section": fr"\s(?P<id>\d+\.\d+)\s+[A-Z].*",  # A.1 Bar
                "sub_sub_section": fr"\s(?P<id>\d+\.\d+\.\d+)\s+[A-Z].*"  # A.1.2 Plugh

            },
            "num_sect": {
                "file_regex": ".*/syr/lr.*",
                "desc": "sections of form '1. Introduction', "
                        "subsections '1.2 Bar' "
                        "subsubsections '1.2.3 Plugh'"
                        "subsubsubsections  '1.2.3.4 Xyzzy (may not be any)",
                "section": fr"\s*(?P<id>{front_back})"
                           fr"|Section\s*(?P<id1>\d+):\s*[A-Z].*"
                           fr"|\s*(?P<id2>\d+)\.\s+[A-Z].*",  # A: Foo
                "sub_section": fr"\s*(?P<id>\d+\.\d+)\s+[A-Z].*",  # 1.1 Bar
                "sub_sub_section": fr"\s(?P<id>\d+\.\d+\.\d+)\s+[A-Z].*"  # A.1.2 Plugh

            },
            "num_sect_new": {
                "file_regex": fr"NEW.*/syr/lr.*",
                "sections": {
                    "desc": f"sections of form '1. Introduction', "
                            f"subsections '1.2 Bar' "
                            f"subsubsections '1.2.3 Plugh'"
                            f"subsubsubsections  '1.2.3.4 Xyzzy (may not be any)",
                    "section": {
                        "desc": "sections of form '1. Introduction' ",
                        "regex": fr"\s*(?P<id>{front_back}|\s*\d+[.:]?)\s+[A-Z].*",  # A: Foo
                    },
                    "sub_section": {
                        "desc": "sections of form ''1.2 Bar' ",
                        "regex": fr"\s(?P<id>\d+\.\d+)\s+[A-Z].*",  # A.1 Bar
                    },
                    "sub_sub_section": fr"\s(?P<id>\d+\.\d+\.\d+)\s+[A-Z].*",  # A.1.2 Plugh
                },
                "references": "dummy"

            },
        }
        return section_regex_dict

    @classmethod
    def get_major_section_names(cls):
        return "Table of Contents|Frequently Asked Questions|Executive Summary|References"

    # def xxx(entry):
    #     anchors = entry.xpath(f"{H_A}")
    #     # if len(anchors) != 1:
    #     #     continue
    #     anchor0 = anchors[0]
    #     id = anchor0.get(A_ID)
    #     print(f">>{id}")
    #     spans = entry.xpath(f"{H_SPAN}")
    #     text = " ".join(spans[1:])
    #     href_as = entry.xpath(f"{H_SPAN}/{H_A}")
    #     return href_as

    @classmethod
    def get_body_for_syr_lr(cls, ar6_dir):
        path = Path(ar6_dir, "syr", "lr", "html", "fulltext", "groups_groups.html")
        group_html = ET.parse(str(path))
        body = group_html.xpath("//body")[0]
        return body

    @classmethod
    def create_author_dict_from_sections(cls, body):
        """
        extracts authors and countries from
        <div left="56.64" right="156.14" top="709.44">
          <span ... class="s0">Core Writing Team: </span>
          <span ... class="s1001">Hoesung Lee (Chair), Katherine Calvin (USA), Dipak Dasgupta (India/USA), Gerhard Krinner (France/Germany),
        where there are several labels for author lists ("author_sects")
        """

        # for splitting author/country
        author_re = re.compile(f"\\s*(?P<author>.*\\S)\\s*\\((?P<country>.*\\S)\\).*")
        author_sects = [
            CORE_TEAM,
            EXTENDED_TEAM,
            CONTRIB_AUTHORS,
            REVIEW_EDITORS,
            SCIENTIFIC_STEERING,
            VISUAL_INFORM,
        ]
        author_dict = dict()
        for author_sect in author_sects:
            author_dict[author_sect] = dict()
            text = cls.extract_text_from_following_span(author_sect, body)
            authors = text.split(", ")
            for author in authors:
                author_match = author_re.match(author)
                if author_match:
                    author_name = author_match.group(AUTHOR)
                    country = author_match.group(COUNTRY)
                    author_dict[author_sect][author_name] = country
        return author_dict

    @classmethod
    def extract_text_from_following_span(cls, sect_name, body):
        """extracts text from normal span (1) following bold text (0)
        """
        _div = body.xpath(f"//div[span[contains(., '{sect_name}')]]")
        return _div[0].xpath("./span")[1].text if len(_div) > 0 else None


class IPCCWordpress(IPCCPublisherTool):

    @property
    def raw_filename(self):
        return WORDPRESS_RAW

    @property
    def base_filename(self):
        return WORDPRESS

    @property
    def cleaned_filename(self):
        return DE_WORDPRESS

    def create_and_add_id(self, id, p, parent, pindex, debug=False):
        """ NOT YET FINALISED"""
        pid = None
        # section-2-1-2-block-1
        section_res = [
            "section-\\d+(-\\d+)*-block-\\d+",
            "article-executive-summary-chapter(-\\d+)+-block-\\d+",
            "article-chapter(-\\d+)+-references-block-1",
            "article(-\\d+)+-about-the-chapter-block-\\d+",
            "article(-\\d+)+-block-\\d+",
            "article-frequently-asked-questions-chapter(-\\d+)+-block-\\d+",
        ]
        for section_rex in section_res:
            match = re.match(section_rex, id)
            if match:
                break
        if not match:
            if debug:
                print(f"cannot match |{id}|")
        else:
            if debug:
                print(f"matched id |{id}|")
            if not pindex:
                pindex = parent.index(p)
            pid = f"{id}_p{pindex}"
            p.attrib["id"] = pid
        return pid

    @classmethod
    def get_removable_xpaths(self):
        removable_xpaths = [
            "/html/head/style",
            "/html/head/link",
            "/html/head//button",
            "/html/head/script",

            "/html/body/script",
            "/html/body/header[div[nav]]",
            "/html/body/nav",
            "/html/body/main/nav",
            "/html/body/footer",
            "/html/body/section[@id='chapter-next']",
            "//article[@id='article-chapter-downloads']",
            "//article[@id='article-supplementary-material']",
            "//div[@class='share']",
            # "/html/body//div[@class='nav2'][nav]",
            # "/html/body//div[@class='ref-tooltip'][textarea]",
            # "/html/body//div[@class='share-tooltip']",
            # "/html/body//div[@class='dropdown'][button]",
            # "/html/body//div[@class='section-tooltip']",
            # "/html/body//div[button]",
            # "/html/body//a[button]",
            # "/html/body//span[@class='share-block']",
            # "/html/body//button",
            # "/html/body//div[contains(@class,'related_pages')]",
            # "/html/body//div[@id='gatsby-announcer']",
            # "/html/body//noscript",
            # "/html/body//footer",

        ]
        return removable_xpaths

    def get_pid(self):
        return "PID NYI"

    def clean_from_raw(self, htmlx, root_elem):
        print(f"Wordpress has no clean_from_raw operations")
        return root_elem

