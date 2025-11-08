# IPCC Chapter Annotation Script Summary

## Overview

Created a comprehensive prototype script for annotating IPCC HTML chapters with keyphrase hyperlinks. The script supports both CSV keyword files from GitHub and AmiDictionary format, with explicit URLs and filenames for all chapters.

## Files Created

### 1. Main Script: `markup_ipcc_chapters_with_keywords.py`
- **Purpose**: Annotate IPCC HTML chapters with keyphrase hyperlinks
- **Features**:
  - Supports both CSV and AmiDictionary keyword sources
  - Explicit chapter mapping with names, URLs, and filenames
  - Batch processing of multiple chapters
  - GitHub integration for keyword loading
  - Comprehensive error handling and logging
  - Follows amilib style guide

### 2. Test Script: `test_ipcc_annotation.py`
- **Purpose**: Test the annotation functionality
- **Features**:
  - Tests both CSV and dictionary annotation methods
  - Demonstrates basic usage
  - Provides test results summary

### 3. Configuration File: `ipcc_annotation_config.json`
- **Purpose**: Configuration template for annotation settings
- **Features**:
  - Chapter information mapping
  - Default settings
  - Dictionary source configurations

## Key Features

### Explicit Chapter Information
All 12 IPCC WG1 chapters are mapped with:
- **Chapter names**: Full descriptive titles
- **CSV filenames**: Explicit filenames (e.g., `Chapter_1_keywords.csv`)
- **GitHub URLs**: Direct links to keyword files
- **HTML filenames**: Target HTML files for annotation

### Output Directory Structure
- **Default output**: `temp/annotate/keyphrases/`
- **CSV annotated**: `temp/annotate/keyphrases/csv_annotated/`
- **Dictionary annotated**: `temp/annotate/keyphrases/dict_annotated/`

### File Naming Convention
- **HTML output**: `Chapter01_Framing_Context_and_Methods_annotated.html`
- **Statistics**: `Chapter01_Framing_Context_and_Methods_stats.json`

## Usage Examples

### Basic Usage
```bash
# Process Chapter 1 with CSV keywords
python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv

# Process multiple chapters
python markup_ipcc_chapters_with_keywords.py --chapter 1,2,3 --keywords csv

# Process all chapters
python markup_ipcc_chapters_with_keywords.py --all-chapters --keywords csv
```

### Advanced Usage
```bash
# Use custom directories
python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv \
  --chapter-dir /path/to/chapters --output-dir /path/to/output

# Use dictionary source
python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords dictionary \
  --dict-path /path/to/dictionary.xml

# Enable verbose logging
python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv --verbose
```

## Chapter Information

| Chapter | Name | CSV Filename | GitHub URL |
|---------|------|--------------|------------|
| 1 | Framing, Context and Methods | Chapter_1_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_1_keywords.csv) |
| 2 | Changing State of the Climate System | Chapter_2_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_2_keywords.csv) |
| 3 | Human Influence on the Climate System | Chapter_3_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_3_keywords.csv) |
| 4 | Future Global Climate: Scenario-based Projections and Near-term Information | Chapter_4_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_4_keywords.csv) |
| 5 | Global Carbon and other Biogeochemical Cycles and Feedbacks | Chapter_5_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_5_keywords.csv) |
| 6 | Short-lived Climate Forcers | Chapter_6_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_6_keywords.csv) |
| 7 | The Earth's Energy Budget, Climate Feedbacks, and Climate Sensitivity | Chapter_7_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_7_keywords.csv) |
| 8 | Water Cycle Changes | Chapter_8_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_8_keywords.csv) |
| 9 | Ocean, Cryosphere and Sea Level Change | Chapter_9_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_9_keywords.csv) |
| 10 | Linking Global to Regional Climate Change | Chapter_10_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_10_keywords.csv) |
| 11 | Weather and Climate Extreme Events in a Changing Climate | Chapter_11_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_11_keywords.csv) |
| 12 | Climate Change Information for Regional Impact and for Risk Assessment | Chapter_12_keywords.csv | [Link](https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_12_keywords.csv) |

## Integration with Amilib

The script leverages existing amilib functionality:
- **HtmlLib**: HTML processing and hyperlink insertion
- **AmiDictionary**: Dictionary management and markup
- **Util**: Logging and utility functions
- **Style Guide Compliance**: Follows established patterns

## Next Steps

1. **Test with real data**: Run the script with actual IPCC chapters
2. **Extend to other working groups**: Add WG2 and WG3 chapters
3. **Enhance keyword processing**: Improve CSV parsing and validation
4. **Add more output formats**: Support for different annotation styles
5. **Create batch processing**: Automated processing of all chapters

## Dependencies

- Python 3.7+
- lxml (HTML processing)
- requests (GitHub API access)
- amilib (core functionality)

## Documentation

- **README**: Updated with new script information
- **Help**: Comprehensive command-line help
- **Examples**: Multiple usage scenarios
- **Configuration**: JSON configuration template

































