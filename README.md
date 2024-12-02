# amilib

Library to support downloading and analysis of documents, mainly from Open Access repositories, from 
published scholarly articles, or from authoritative sites such as UN IPCC or UNFCCC. The current version 2024-12-01 includes entry points but the longer term plan is to integrate with [docanalysis](https://github.com/petermr/docanalysis) and [pygetpapers](https://github.com/petermr/pygetpapers). That will give a onestop toolset for downloading Open Access articles/reports in bulk, making them semantic , and analysing them with NLP and AI/ML methods.

# components and tests

`amilib` is written as a set of libraries developed by test-driven-development (TDD). The main strategy is to tackle a real download/transform/analyse problem as a series of tests, and then abstract the tests into the library. The tests therefore act as a guide to functionality and simple how-tos. During development the libraries can be accessed through the command-line (`argparse`) and this is the current normal approach. (However we plan to move the main entry points for most users to `docanalysis`).

# main sub-libraries

This represents functionality at 2024-12-02:

|Module|Function  |
|-------|----  |
|ami_args.py|Abstract class for argparse option  |
|ami_bib.py|Bibliographic support  |
|ami_corpus.py|create, normalize, search, tranform a corpus  |
|ami_csv.py|CSV utilities  |
|ami_dict.py| Ami Dictionary|
|ami_graph.py| (stub)  |
|ami_html.py|large collection for manipulating HTML  |
|ami_integrate.py| miscellaneous conversions |
|ami_nlp.py| (stubs) |
|ami_pdf_libs.py|large PDF2HTML , includes pdfplumber |
|ami_svg.py| (stub) mainly convenience routiines |
|ami_util.py| lowlevel numeric/geom utilities |
|amidriver.py| headless browser |
|amix.py|  entry point for amilib main |
|bbox.py| bounding box manipulation |
|constants.py| (stub) |
|dict_args.py| dictionary options in argparse |
|file_lib.py| file utilities |
|headless_lib.py|  messy utility routines (may be obsolete)|
|html_args.py| HTML options in argparse |
|html_extra.py| stub obsolete? |
|html_generator.py|  messy ?obsolete|
|html_marker.py| markup HTML (messy) |
|pdf_args.py|  PDF options in argprase|
|search_args.py| search options in argparse |
|util.py| many scattered utilities |
|wikimedia.py| download and conversion of Wikimedia|
|xml_lib.py| convenience routies (lxml wrappers)|



