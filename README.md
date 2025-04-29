# amilib

Library to support downloading and analysis of documents, mainly from Open Access repositories, from 
published scholarly articles, or from authoritative sites such as UN IPCC or UNFCCC. The current version 2024-12-01 includes entry points but the longer term plan is to integrate with [docanalysis](https://github.com/petermr/docanalysis) and [pygetpapers](https://github.com/petermr/pygetpapers). That will give a onestop toolset for downloading Open Access articles/reports in bulk, making them semantic , and analysing them with NLP and AI/ML methods.

# components and tests

`amilib` is written as a set of libraries developed by test-driven-development (TDD). The main strategy is to tackle a real download/transform/analyse problem as a series of tests, and then abstract the tests into the library. The tests therefore act as a guide to functionality and simple how-tos. During development the libraries can be accessed through the command-line (`argparse`) and this is the current normal approach. (However we plan to move the main entry points for most users to `docanalysis`).

# main sub-libraries

This represents functionality at 2024-12-02. There are about non-trivial 1000 methods.

|Module|Function  |
|-------|----  |
|[amilib/ami_args.py](amilib/ami_args.py)|Abstract class for argparse option  |
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


# commands and subcommands

`amilib` has an `argparse` dommand-set and 4 sub-command-sets. These exercise most of the functionality and are used by the community for many purposes. However it makes more sense to move some of the entry-points to `docanalysis` and this will occur gradually.

## top-level command

This is really only a placeholder.

```
amilib --help
usage: amilib [-h] [-v] {DICT,PDF,HTML,SEARCH} ...

pyamihtml: create, manipulate, use CProject 
----------------------------------------

amilib is a set of problem-independent methods to support document retrieval and analysis
The subcommands:

  DICT <options>      # create and edit Ami Dictionaries
  HTML <options>      # create/edit HTML
  PDF <options>       # convert PDF into HTML and images
  SEARCH <options>    # search and index documents

After installation, run 
  amilib <subcommand> <options>

Examples (# foo is a comment):
  amilib        # runs help
  amilib -h     # runs help
  amilib PDF -h # runs PDF help
  amilib PDF --infile foo.pdf --outdir bar/ # converts PDF to HTML

----------------------------------------

positional arguments:
  {DICT,PDF,HTML,SEARCH}
                        subcommands

options:
  -h, --help            show this help message and exit
  -v, --version         show version 0.3.0

run:
        pyamihtmlx <subcommand> <args>
          where subcommand is in   {DICT, HTML,PDF, SEARCH} and args depend on subcommand
        
```


### `amilib DICT`

`amilib DICT` is used to make and maintain dictionaries.
```
amilib DICT --help

usage: amilib DICT [-h] [--description {wikipedia,wiktionary,wikidata} [{wikipedia,wiktionary,wikidata} ...]] [--dict DICT]
                   [--inpath INPATH [INPATH ...]] [--figures [{None,wikipedia,wikidata} ...]] [--operation {create,edit,markup,validate}]
                   [--outpath OUTPATH [OUTPATH ...]] [--synonym SYNONYM [SYNONYM ...]] [--title TITLE] [--validate]
                   [--wikidata [WIKIDATA ...]] [--wikipedia [WIKIPEDIA ...]] [--wiktionary [WIKTIONARY ...]] [--words [WORDS ...]]

AMI dictionary creation, validation, editing

options:
  -h, --help            show this help message and exit
  --description {wikipedia,wiktionary,wikidata} [{wikipedia,wiktionary,wikidata} ...]
                        add extended description tp dict from one or more of these
  --dict DICT           path for dictionary (existing = edit; new = create (type depends on suffix *.xml or *.html)
  --inpath INPATH [INPATH ...]
                        path for input file(s)
  --figures [{None,wikipedia,wikidata} ...]
                        sources for figures: 'wikipedia' uses infobox or first thumbnail, wikidata uses first figure
  --operation {create,edit,markup,validate}
                        operation: 'create' needs 'words' 'edit' needs 'inpath' 'markup' need 'inpath' and 'outpath` (move to search?)
                        'validate' requires 'inpath' default = 'create
  --outpath OUTPATH [OUTPATH ...]
                        output file
  --synonym SYNONYM [SYNONYM ...]
                        add sysnonyms (from Wikidata) for terms (NYI)
  --title TITLE         internal title for dictionary, normally same as stem of dictionary file
  --validate            validate dictionary; DEPRECATED use '--operation validate'
  --wikidata [WIKIDATA ...]
                        DEPRECATED use --description wikidata add WikidataIDs (NYI)
  --wikipedia [WIKIPEDIA ...]
                        add Wikipedia link/s; DEPRECATED use '--description wikipedia'
  --wiktionary [WIKTIONARY ...]
                        add Wiktionary output as html (may be messy); DEPRECATED use '--description wiktionary'
  --words [WORDS ...]   path/file with words or list of words to create dictionaray

Examples: DICT --words wordsfile --dict dictfile --description wikipedia # creates dictionary from wordsfile and adds wikipedia info
```

### `amilib HTML`

creates, manages, transforms HTML

```
amilib HTML --help
INFO amix.py:546:***** amilib VERSION 0.3.0 *****
INFO:amilib.amix:***** amilib VERSION 0.3.0 *****
INFO amix.py:170:command: ['HTML', '--help']
INFO:amilib.amix:command: ['HTML', '--help']
usage: amilib HTML [-h] [--annotate] [--color COLOR] [--dict DICT] [--inpath INPATH] [--outpath OUTPATH] [--outdir OUTDIR]

HTML editing, analysing annotation

options:
  -h, --help         show this help message and exit
  --annotate         annotate HTML file with dictionary
  --color COLOR      colour for annotation
  --dict DICT        dictionary for annotation
  --inpath INPATH    input html file
  --outpath OUTPATH  output html file
  --outdir OUTDIR    output directory
```

### `amilib PDF`

Converts PDF to structured HTML. Heuristic.

```
amilib PDF --help
INFO amix.py:546:***** amilib VERSION 0.3.0 *****
INFO:amilib.amix:***** amilib VERSION 0.3.0 *****
INFO amix.py:170:command: ['PDF', '--help']
INFO:amilib.amix:command: ['PDF', '--help']
usage: amilib PDF [-h] [--debug {words,lines,rects,curves,images,tables,hyperlinks,texts,annots}] [--flow FLOW] [--footer FOOTER]
                  [--header HEADER] [--imagedir IMAGEDIR] [--indir INDIR] [--inform INFORM [INFORM ...]] [--inpath INPATH]
                  [--infile INFILE] [--instem INSTEM] [--maxpage MAXPAGE] [--offset OFFSET] [--outdir OUTDIR] [--outpath OUTPATH]
                  [--outstem OUTSTEM] [--outform OUTFORM] [--pdf2html {pdfminer,pdfplumber}] [--pages PAGES [PAGES ...]]
                  [--resolution RESOLUTION] [--template TEMPLATE]

PDF tools. 
----------
Typically reads one or more PDF files and converts to HTML
can clip parts of page, select page ranges, etc.

Examples:
  * PDF --help

options:
  -h, --help            show this help message and exit
  --debug {words,lines,rects,curves,images,tables,hyperlinks,texts,annots}
                        debug these during parsing (NYI)
  --flow FLOW           create flowing HTML, e.g. join lines, pages (heuristics)
  --footer FOOTER       bottom margin (clip everythimg above)
  --header HEADER       top margin (clip everything below
  --imagedir IMAGEDIR   output images to imagedir
  --indir INDIR         input directory (might be calculated from inpath)
  --inform INFORM [INFORM ...]
                        input formats (might be calculated from inpath)
  --inpath INPATH       input file or (NYI) url; might be calculated from dir/stem/form
  --infile INFILE       input file (synonym for inpath)
  --instem INSTEM       input stem (e.g. 'fulltext'); maybe calculated from 'inpath`
  --maxpage MAXPAGE     maximum number of pages (will be deprecated, use 'pages')
  --offset OFFSET       number of pages before numbers page 1, default=0
  --outdir OUTDIR       output directory
  --outpath OUTPATH     output path (can be calculated from dir/stem/form)
  --outstem OUTSTEM     output stem
  --outform OUTFORM     output format
  --pdf2html {pdfminer,pdfplumber}
                        convert PDF to html
  --pages PAGES [PAGES ...]
                        reads '_2 4_6 8 11_' as 1-2, 4-6, 8, 11-end ; all ranges inclusive (not yet debugged)
  --resolution RESOLUTION
                        resolution of output images (if imagedir)
  --template TEMPLATE   file to parse specific type of document (NYI)

```

### `amilib SEARCH`

Searches and annotates HTML documents

```
amilib SEARCH --help
usage: amilib SEARCH [-h] [--debug DEBUG] [--dict DICT] [--inpath INPATH [INPATH ...]]
                     [--operation {annotate,index,no_input_styles} [{annotate,index,no_input_styles} ...]]
                     [--outpath OUTPATH [OUTPATH ...]] [--title TITLE]

SEARCH tools. 
----------
Search documents and corpora and make indexes and maybe knowledge graphs.Not yet finished.

Examples:
  * SEARCH --help

options:
  -h, --help            show this help message and exit
  --debug DEBUG         debug these during parsing (NYI)
  --dict DICT           path for dictionary *.xml or *.html)
  --inpath INPATH [INPATH ...]
                        path for input file(s)
  --operation {annotate,index,no_input_styles} [{annotate,index,no_input_styles} ...]
                        operation: 'no_input_styles' needs 'inpath ; remove styles from inpath 'annotate' needs 'inpath and dict';
                        annotates words/phrases 'index' needs 'inpath' optionally outpath (NYI) default = annotate
  --outpath OUTPATH [OUTPATH ...]
                        output file
  --title TITLE         internal title for dictionary, normally same as stem of dictionary file

```


