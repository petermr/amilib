import json
from pathlib import Path
import lxml.etree as ET

from amilib.xml_lib import HtmlLib


class EPMCMetadata:
    """

    """


    def __init__(self):
        self.pmcid = None
        self.doi = None
        self.title = None
        self.author_string = None
        self.journal_info = None
        self.pub_year = None
        self.page_info = None
        self.abstract_text = None

    def __str__(self):
        s = ""
        s = _add_str(s, self.pmcid)
        s = _add_str(s, self.doi)
        s = _add_str(s, self.title)
        s = _add_str(s, self.author_string)
        s = _add_str(s, self.journal_info)
        s = _add_str(s, self.pub_year)
        s = _add_str(s, self.page_info)
        s = _add_str(s, self.abstract_text)
        return s

    @classmethod
    def create_metadata_from_json(cls, jsonx):
        if jsonx is not None:
            metadata = EPMCMetadata()
            metadata.pmcid = jsonx.get(EPMCBib.PMCID)
            metadata.doi = jsonx.get(EPMCBib.DOI)
            metadata.title = jsonx.get(EPMCBib.TITLE)
            metadata.author_string = jsonx.get(EPMCBib.AUTHOR_STRING)
            metadata.abstract_text = jsonx.get(EPMCBib.ABSTRACT_TEXT)
            jinf = jsonx.get(EPMCBib.JOURNAL_INFO)
            metadata.page_info = jsonx.get(EPMCBib.PAGE_INFO)
            metadata.journal_info = JournalInfo.read_json(jinf)

            return metadata


    def create_bib_list_element(self, ul):
        """
        creates and adds a <li> with the bibliographic info
        restylable through CSS
        :param ul: parent ul
        :return: the li
        """
        if ul is None:
            return None
        li = ET.SubElement(ul, "li")
        self.add_pmcid_span(li)
        self.add_author_span(li)
        self.add_title_span(li)

        self.add_journal_info_span(li)
        self.add_page_span(li)
        self.add_doi_span(li)
        self.add_abstract_span(li)

        return li

    def add_pmcid_span(self, li):
        if self.pmcid is not None:
            span = ET.SubElement(li, "span")
            span.attrib["class"] = "pmcid"
            span.text = " " + self.pmcid + ", "

    def add_author_span(self, li):
        if self.author_string is not None:
            span = ET.SubElement(li, "span")
            span.attrib["class"] = "author_string"
            span.text = " " + self.author_string + ", "

    def add_title_span(self, li):
        if self.title is not None:
            span = ET.SubElement(li, "span")
            span.attrib["class"] = "title"
            span.text = ' "' + self.title + '", '

    def add_year_span(self, li):
        if self.pub_year is not None:
            span = ET.SubElement(li, "span")
            span.attrib["class"] = "pub_year"
            span.text = " YR (" + self.pub_year + "), "

    def add_page_span(self, li):
        if self.page_info is not None:
            span = ET.SubElement(li, "span")
            span.attrib["class"] = "page_info"
            span.text = "PI " + self.page_info + ", "

    def add_abstract_span(self, li):
        if self.abstract_text is not None:
            span = ET.SubElement(li, "span")
            span.attrib["class"] = "abstract_text"
            span.text = " " + f"Abstract: {len(self.abstract_text.split())} words" + ", "
            span.attrib["title"] = self.abstract_text

    def add_doi_span(self, li):
        if self.doi is not None:
            aa = ET.SubElement(li, "a")
            aa.text = " DOI: " + self.doi + ", "
            aa.attrib["href"] = f"https://doi.org/{self.doi}"


    def add_journal_info_span(self, li):
        if self.journal_info is not None:
            self.journal_info.add_spans(li)



class EPMCBib:
    """
        # all_cols = [id,source,pmid,pmcid,fullTextIdList,doi,title,authorString,authorList,authorIdList,
        # dataLinksTagsList,journalInfo,pubYear,pageInfo,abstractText,affiliation,publicationStatus,language,
        # pubModel,pubTypeList,grantsList,keywordList,fullTextUrlList,isOpenAccess,inEPMC,inPMC,hasPDF,
        # hasBook,hasSuppl,citedByCount,hasData,hasReferences,hasTextMinedTerms,hasDbCrossReferences,hasLabsLinks,
        # license,hasEvaluations,authMan,epmcAuthMan,nihAuthMan,hasTMAccessionNumbers,tmAccessionTypeList,
        # dateOfCreation,firstIndexDate,fullTextReceivedDate,dateOfRevision,electronicPublicationDate,
        # firstPublicationDate,subsetList,commentCorrectionList,meshHeadingList,dateOfCompletion,manuscriptId,
        # embargoDate,chemicalList]
    """
    """
{
	"papers": {
		"PMC11193050": {
			"downloaded": true,
			"pdfdownloaded": true,
			"jsondownloaded": true,
			"csvmade": false,
			"htmlmade": false,
			"id": "38912110",
			"source": "MED",
			"pmid": "38912110",
			"pmcid": "PMC11193050",
			"fullTextIdList": {
				"fullTextId": "PMC11193050"
			},
			"doi": "10.3897/bdj.12.e120304",
			"title": "Towards computable taxonomic knowledge: Leveraging nanopublications for sharing new synonyms in the Madagascan genus <i>Helictopleurus</i> (Coleoptera, Scarabaeinae).",
			"authorString": "Rossini M, Montanaro G, Montreuil O, Tarasov S.",
			"authorList": {
				"author": [
					{
						"fullName": "Rossini M",
						"firstName": "Michele",
						"lastName": "Rossini",
						"initials": "M",
						"authorId": {
							"@type": "ORCID",
							"#text": "0000-0002-1938-6105"
						},
						"authorAffiliationDetailsList": {
							"authorAffiliation": [
								{
									"affiliation": "Finnish Museum of Natural History (LUOMUS), University of Helsinki, Helsinki, Finland Finnish Museum of Natural History (LUOMUS), University of Helsinki Helsinki Finland."
								},
								{
									"affiliation": "Department of Agronomy, Food, Natural resources, Animals and Environment (DAFNAE), University of Padova, Padova, Italy Department of Agronomy, Food, Natural resources, Animals and Environment (DAFNAE), University of Padova Padova Italy."
								}
							]
						}
					},
					...
								"authorIdList": {
				"authorId": [
					{
						"@type": "ORCID",
						"#text": "0000-0001-5237-2330"
					},
					...
					
				]
			},
			...
						"dataLinksTagsList": {
				"dataLinkstag": "altmetrics"
			},
			"journalInfo": {
				"volume": "12",
				"journalIssueId": "3697827",
				"dateOfPublication": "2024",
				"monthOfPublication": "0",
				"yearOfPublication": "2024",
				"printPublicationDate": "2024-01-01",
				"journal": {
					"title": "Biodiversity data journal",
					"ISOAbbreviation": "Biodivers Data J",
					"medlineAbbreviation": "Biodivers Data J",
					"NLMid": "101619899",
					"ISSN": "1314-2828",
					"ESSN": "1314-2828"
				}
			},
			"pubYear": "2024",
			"pageInfo": "e120304",
			"abstractText": "<h4>Background</h4>Numerous taxonomic studies have focused on the dung beetle genus <i>Helictopleurus</i> d'Orbigny, 1915, endemic to Madagascar. However, this genus stilll needs a thorough revision. Semantic technologies, such as nanopublications, hold the potential to enhance taxonomy by transforming how data are published and analysed. This paper evaluates the effectiveness of nanopublications in establishing synonyms within the genus <i>Helictopleurus</i>.<h4>New information</h4>In this study, we identify four new synonyms within <i>Helictopleurus</i>: <i>H.rudicollis</i> (Fairmaire, 1898) = <i>H.hypocrita</i> Balthasar, 1941 <b>syn. nov.</b>; <i>H.vadoni</i> Lebis, 1960 = <i>H.perpunctatus</i> Balthasar, 1963 <b>syn. nov.</b>; <i>H.halffteri</i> Balthasar, 1964 = <i>H.dorbignyi</i> Montreuil, 2005 <b>syn. nov.</b>; <i>H.clouei</i> (Harold, 1869) = <i>H.gibbicollis</i> (Fairmaire, 1895) <b>syn. nov.</b> <i>Helictopleurus</i> may have a significantly larger number of synonyms than currently known, indicating potentially inaccurate estimates about its recent extinction.We also publish the newly-established synonyms as nanopublications, which are machine-readable data snippets accessible online. Additionally, we explore the utility of nanopublications in taxonomy and demonstrate their practical use with an example query for data extraction.",
			"affiliation": "Finnish Museum of Natural History (LUOMUS), University of Helsinki, Helsinki, Finland Finnish Museum of Natural History (LUOMUS), University of Helsinki Helsinki Finland.",
			"publicationStatus": "epublish",
			"language": "eng",
			"pubModel": "Electronic-eCollection",
			"pubTypeList": {
				"pubType": [
					"research-article",
					"Journal Article"
				]
			},
			"keywordList": {
				"keyword": [
					"Taxonomy",
					"Extinction",
					"Nomenclature",
					"Madagascar",
					"Ontology",
					"Dung Beetles",
					"Sparql",
					"Machine-readable Data"
				]
			},
			"fullTextUrlList": {
				"fullTextUrl": [
					{
						"availability": "Subscription required",
						"availabilityCode": "S",
						"documentStyle": "doi",
						"site": "DOI",
						"url": "https://doi.org/10.3897/BDJ.12.e120304"
					},
					{
						"availability": "Open access",
						"availabilityCode": "OA",
						"documentStyle": "html",
						"site": "Europe_PMC",
						"url": "https://europepmc.org/articles/PMC11193050"
					},
					{
						"availability": "Open access",
						"availabilityCode": "OA",
						"documentStyle": "pdf",
						"site": "Europe_PMC",
						"url": "https://europepmc.org/articles/PMC11193050?pdf=render"
					}
				]
			},
			"isOpenAccess": "Y",
			"inEPMC": "Y",
			"inPMC": "N",
			"hasPDF": "Y",
			"hasBook": "N",
			"hasSuppl": "Y",
			"citedByCount": "0",
			"hasData": "Y",
			"hasReferences": "Y",
			"hasTextMinedTerms": "Y",
			"hasDbCrossReferences": "N",
			"hasLabsLinks": "Y",
			"license": "cc by",
			"hasEvaluations": "N",
			"authMan": "N",
			"epmcAuthMan": "N",
			"nihAuthMan": "N",
			"hasTMAccessionNumbers": "N",
			"dateOfCreation": "2024-06-24",
			"firstIndexDate": "2024-06-25",
			"fullTextReceivedDate": "2024-06-24",
			"dateOfRevision": "2024-06-25",
			"electronicPublicationDate": "2024-06-14",
			"firstPublicationDate": "2024-06-14"
		},

    """
    INT = "int"
    LIST = "list"
    ORDERED_DICT = "OrderedDict"
    STR = "str"

    PMCID = 'pmcid'
    DOI = 'doi'
    TITLE = 'title'
    AUTHOR_STRING = 'authorString'
    ABSTRACT_TEXT = 'abstractText'
    JOURNAL_INFO = 'journalInfo'
    PUB_YEAR = 'pubYear'
    PAGE_INFO = 'pageInfo'

    FORMATS = {
        PMCID: STR,
        DOI: STR,
        TITLE: STR,
        AUTHOR_STRING: LIST,
        JOURNAL_INFO: ORDERED_DICT,
        PUB_YEAR: INT,
        PAGE_INFO: STR,
    }

    COMMON = [
        'pmcid',
        'doi',
        'title',
        'authorString',
        'journalInfo',
        'pubYear',
        'pageInfo'
    ]

    def __init__(self):
        self.infile = None
        self.bib_json = None
        self.papers = []

    def read_bib_json(self, infile):
        """
        :param infile: input json
        """
        assert Path(infile).exists(), f"JSON file {infile} must exist"
        self.infile = infile
        with open(infile, "r") as f:
            self.bib_json = json.load(f)
        if self.bib_json is None:
            print(f"No bib_json")
            return None
        papers = self.bib_json.get("papers")
        assert papers is not None, f"must have 'papers'"
        print(f"read {len(papers)} papers")

        for paper in papers:
            paper_value = papers.get(paper)
            epmc_paper = EPMCMetadata.create_metadata_from_json(paper_value)

            self.papers.append(epmc_paper)




    def create_html_json(self):
        """

        """
        htmlx = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(htmlx)
        ul = ET.SubElement(body, "ul")
        for epmc_paper in self.papers:
            # print(f"paper {epmc_paper}")
            epmc_paper.create_bib_list_element(ul)

        return htmlx


    @classmethod
    def add_span(cls, row, line_span, name, start="", end = ""):
        val = row.get(name)
        if val is not None:
            el = ET.SubElement(line_span, "span")
            el.text = start + str(val)
            el.tail = end


def _add_str(s, value):
    if value is not None:
        s += str(value) + "\n"
    return s


class JournalInfo:
    """
    OrderedDict([('volume', '9'), ('journalIssueId', '3560901'), ('dateOfPublication', '2023'),
    ('monthOfPublication', '0'), ('yearOfPublication', '2023'), ('printPublicationDate', '2023-01-01'),
    ('NLMid', '101660598'), ('ISSN', '2167-9843'), ('ESSN', '2376-5992')])
    """
    JOURNAL = 'journal'
    JOURNAL_INFO = 'journalInfo'
    VOLUME = 'volume'  # int
    ISSUE = 'issue'
    JOURNAL_ISSUE_ID = 'journalIssueId'
    DATE_OF_PUBLICATION = 'dateOfPublication'
    MONTH_OF_PUBLICATION = 'monthOfPublication'
    YEAR_OF_PUBLICATION = 'yearOfPublication'  # int
    PRINT_PUBLICATION_DATE = 'printPublicationDate'  # yyyy-mm-dd '2023-01-01'),
    NLM_ID = 'NLMid'  # str
    ISSN = 'ISSN'  # dddd-dddd,
    ESSN = 'ESSN'  # dddd-dddd,
    TITLE = "title"
    ISO_ABB = "ISOAbbreviation"
    MEDLINE_ABB = "medlineAbbreviation"

    def __init__(self):
        self.vol = None
        self.jissue_id = None
        self.pub_date = None
        self.month_pub = None
        self.year_pub = None
        self.print_pub_date = None
        self.nlm_id = None
        self.issn = None
        self.essn = None

        self.journal_title = None
        self.volume = None
        self.issue = None
        self.iso_abbrev = None
        self.medline_abbrev = None

        self.volume = None
        self.issue = None
        """
        "journal": {
					"title": "Biodiversity data journal",
					"ISOAbbreviation": "Biodivers Data J",
					"medlineAbbreviation": "Biodivers Data J",
					"NLMid": "101619899",
					"ISSN": "1314-2828",
					"ESSN": "1314-2828"
		"""

    def __str__(self):
        pass

        s = ""
        s = _add_str(s, self.pub_date)
        s = _add_str(s, self.year_pub)
        s = _add_str(s, self.journal_title)
        s = _add_str(s, self.iso_abbrev)
        s = _add_str(s, self.medline_abbrev)

        return s

    def add_spans(self, li):
        self.add_volume_issue_span(li)
        self.add_year_pub(li)
        self.add_journal_title(li)


    def get_html_span(cls, row):
        pass

    @classmethod
    def read_json(cls, jinfo_value):
        """
        "journalInfo": {
        "volume": "12",
        "journalIssueId": "3697827",
        "dateOfPublication": "2024",
        "monthOfPublication": "0",
        "yearOfPublication": "2024",
        "printPublicationDate": "2024-01-01",
        "journal": {
            "title": "Biodiversity data journal",
            "ISOAbbreviation": "Biodivers Data J",
            "medlineAbbreviation": "Biodivers Data J",
            "NLMid": "101619899",
            "ISSN": "1314-2828",
            "ESSN": "1314-2828"
        }
    },

        """
        if jinfo_value is not None:
            j_info = JournalInfo()
            j_info.value = jinfo_value
            j_info.volume = jinfo_value.get(JournalInfo.VOLUME)
            j_info.issue = jinfo_value.get(JournalInfo.ISSUE)
            j_info.year_pub = jinfo_value.get(JournalInfo.YEAR_OF_PUBLICATION)
            j_info.journal = jinfo_value.get(JournalInfo.JOURNAL)
            if j_info.journal is not None:
                j_info.journal_title = j_info.journal.get(JournalInfo.TITLE)
                j_info.iso_abbrev = j_info.journal.get(JournalInfo.ISO_ABB)
                j_info.medline_abbrev = j_info.journal.get(JournalInfo.MEDLINE_ABB)
            return j_info


    def add_volume_issue_span(self, li):
        if self.volume is not None:
            span = ET.SubElement(li, "span")
            b = ET.SubElement(span, "b")
            b.text = " " + str(self.volume)
            if self.issue is not None:
                b.text += "(" + str(self.issue) + ")"
            b.text += " "


    def add_year_pub(self, li):
        if self.year_pub is not None:
            span = ET.SubElement(li, "span")
            span.text = " (" + str(self.year_pub) + "): "

    def add_journal_title(self, li):
        if self.journal_title is not None:
            span = ET.SubElement(li, "span")
            ital = ET.SubElement(span, "i")
            ital.text = " " + str(self.journal_title) + ", "



