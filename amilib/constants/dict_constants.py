"""
Constants for AmiDictionary and related functionality.
This centralizes all dictionary-related constants for easier maintenance and imports.
"""

# ===== XML ELEMENT NAMES =====
DICTIONARY = "dictionary"
ENTRY = "entry"
IMAGE = "image"
LINK = "link"
RAW = "raw"
TITLE = "title"

# ===== XML ATTRIBUTE NAMES =====
AMI_ENTRY = "ami_entry"
DESC = "desc"  # description attribute in <dictionary> or <entry>
DEFINITION = "definition"  # one-sentence definition for entry
DESCRIPTION = "description"  # description attribute in <dictionary> or <entry> (often paragraph)
NAME = "name"  # non-lexical name for entry (maybe obsolete)
ROLE = "role"
TERM = "term"  # exact term for entry (includes case and spaces)
WIKIDATA_ID = "wikidataID"  # primary ID for entry where it exists
WIKIDATA_URL = "wikidataURL"  # link to Wikidata entry
TYPE = "type"
VERSION = "version"
WIKIDATA_HITS = "wikidata_hits"  # container for Wikidata lookup hits
WIKIDATA_HIT = "wikidataHit"  # wikidata hit

# ===== EXTERNAL URLS =====
WIKIDATA_SITE = "https://www.wikidata.org/entity/"  # URL of Wikidata site
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/"  # bases of English Wikipedia
WIKIPEDIA_PAGE = "wikipediaPage"  # container for whole Wikipedia page??

# ===== SPECIAL VALUES =====
ANY = "ANY"
UTF_8 = "UTF-8"

# ===== LANGUAGES =====
LANG_UR = "ur"

# ===== DICTIONARY TYPES =====
# These could be moved to a separate file if they grow too large
ACTIVITY = "activity"
COMPOUND = "compound"
COUNTRY = "country"
DISEASE = "disease"
ELEMENT = "elements"
INVASIVE_PLANT = "invasive_plant"
PLANT_GENUS = "plant_genus"
ORGANIZATION = "organization"
PLANT_COMPOUND = "plant_compound"
PLANT = "plant"
PLANT_PART = "plant_part"
SOLVENT = "solvents"

ANIMAL_TEST = "animaltest"
COCHRANE = "cochrane"
COMP_CHEM = "compchem"
CRISPR = "crispr"
CRYSTAL = "crystal"
DISTRIBUTION = "distributions"
DITERPENE = "diterpene"
DRUG = "drugs"
EDGE_MAMMAL = "edgemammals"
CHEM_ELEMENT = "elements"
EPIDEMIC = "epidemic"
ETHICS = "ethics"
EUROFUNDER = "eurofunders"
ILLEGAL_DRUG = "illegaldrugs"
INN = "inn"
INSECTICIDE = "insecticide"
MAGNETISM = "magnetism"
MONOTERPENE = "monoterpene"
NAL = "nal"
NMR = "nmrspectroscopy"
OBESITY = "obesity"
OPTOGENETICS = "optogenetics"
PECTIN = "pectin"
PHOTOSYNTH = "photosynth"
PLANT_DEV = "plantDevelopment"
POVERTY = "poverty"
PROT_STRUCT = "proteinstruct"
PROT_PRED = "protpredict"
REFUGEE = "refugeeUNHCR"
SESQUITERPENE = "sesquiterpene"
STATISTICS = "statistics"
TROPICAL_VIRUS = "tropicalVirus"
WETLANDS = "wetlands"
WILDLIFE = "wildlife" 