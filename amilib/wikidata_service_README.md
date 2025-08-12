# Wikidata Service Module

## Overview

The `WikidataService` module provides clean, simple interfaces for Wikidata operations using the existing amilib wikimedia functionality. It's designed to be used by the Dictionary Editor and other applications that need to enrich terms with structured Wikidata data.

## Features

- **Entity Search**: Search for Wikidata entities by term
- **Property Retrieval**: Get entity properties and values
- **Description & Aliases**: Extract entity descriptions and alternative names
- **Wikipedia Links**: Get Wikipedia page links for entities
- **Comprehensive Summaries**: Get complete entity information
- **Term Enrichment**: Enrich dictionary terms with Wikidata data
- **Batch Processing**: Process multiple terms efficiently
- **QID Validation**: Validate Wikidata entity IDs
- **Language Support**: Multi-language support (default: English)

## Installation

The module is part of amilib and requires the following dependencies:
- `requests` for HTTP operations
- `lxml` for XML/HTML parsing
- `SPARQLWrapper` for SPARQL queries

## Quick Start

### Basic Usage

```python
from amilib.wikidata_service import WikidataService

# Initialize the service
service = WikidataService()

# Search for an entity
results = service.search_entity("Douglas Adams")

# Enrich a term
enrichment = service.enrich_term("climate change")

# Get entity summary
summary = service.get_entity_summary("Q42")
```

### Convenience Functions

```python
from amilib.wikidata_service import (
    search_wikidata_entity,
    get_wikidata_entity_summary,
    enrich_term_with_wikidata
)

# Quick searches
entities = search_wikidata_entity("acetone")
summary = get_wikidata_entity_summary("Q42")
enrichment = enrich_term_with_wikidata("climate change")
```

## API Reference

### WikidataService Class

#### Constructor

```python
WikidataService(language: str = 'en')
```

- **language**: Language code for Wikidata operations (default: 'en')

#### Methods

##### `search_entity(term: str, max_results: int = 5) -> List[Dict[str, Any]]`

Search for Wikidata entities by term.

**Parameters:**
- **term**: Search term
- **max_results**: Maximum number of results to return

**Returns:**
List of entity dictionaries with:
- `id`: Wikidata entity ID (Q-number)
- `description`: Entity description
- `label`: Entity label
- `match_type`: Type of match ('exact', 'primary', 'secondary')
- `confidence`: Confidence score (0.0 to 1.0)

**Example:**
```python
results = service.search_entity("Douglas Adams")
# Returns: [{'id': 'Q42', 'description': 'English writer and humorist', ...}]
```

##### `get_entity_properties(qid: str) -> Dict[str, Any]`

Get properties and values for a Wikidata entity.

**Parameters:**
- **qid**: Wikidata entity ID (e.g., 'Q12345')

**Returns:**
Dictionary mapping property names to lists of values.

**Example:**
```python
properties = service.get_entity_properties("Q42")
# Returns: {'instance of': [{'type': 'entity', 'id': 'Q5', 'value': 'Q5'}], ...}
```

##### `get_entity_description(qid: str) -> Optional[str]`

Get the description of a Wikidata entity.

**Parameters:**
- **qid**: Wikidata entity ID

**Returns:**
Entity description or None if not found.

**Example:**
```python
description = service.get_entity_description("Q42")
# Returns: "English writer and humorist"
```

##### `get_entity_aliases(qid: str) -> List[str]`

Get aliases (alternative names) for a Wikidata entity.

**Parameters:**
- **qid**: Wikidata entity ID

**Returns:**
List of aliases.

**Example:**
```python
aliases = service.get_entity_aliases("Q42")
# Returns: ["Douglas Noël Adams", "DNA", ...]
```

##### `get_wikipedia_links(qid: str, languages: Optional[List[str]] = None) -> Dict[str, str]`

Get Wikipedia page links for a Wikidata entity.

**Parameters:**
- **qid**: Wikidata entity ID
- **languages**: List of language codes (default: ['en'])

**Returns:**
Dictionary mapping language codes to Wikipedia page titles.

**Example:**
```python
links = service.get_wikipedia_links("Q42")
# Returns: {'en': 'Douglas_Adams', 'es': 'Douglas_Adams', ...}
```

##### `get_entity_summary(qid: str) -> Dict[str, Any]`

Get a comprehensive summary of a Wikidata entity.

**Parameters:**
- **qid**: Wikidata entity ID

**Returns:**
Dictionary containing entity summary information:
- `id`: Entity ID
- `label`: Entity label
- `description`: Entity description
- `aliases`: List of aliases
- `properties`: Entity properties
- `wikipedia_links`: Wikipedia page links
- `type`: Entity type

**Example:**
```python
summary = service.get_entity_summary("Q42")
# Returns comprehensive entity information
```

##### `enrich_term(term: str) -> Dict[str, Any]`

Enrich a term with Wikidata information.

**Parameters:**
- **term**: Term to enrich

**Returns:**
Dictionary containing enriched information:
- `term`: Original term
- `wikidata`: Wikidata data (or None if not found)
- `enrichment_status`: Status of enrichment

**Example:**
```python
enrichment = service.enrich_term("Douglas Adams")
# Returns: {'term': 'Douglas Adams', 'wikidata': {...}, 'enrichment_status': 'success'}
```

##### `batch_enrich_terms(terms: List[str]) -> List[Dict[str, Any]]`

Enrich multiple terms in batch.

**Parameters:**
- **terms**: List of terms to enrich

**Returns:**
List of enrichment results.

**Example:**
```python
terms = ["Douglas Adams", "climate change", "acetone"]
results = service.batch_enrich_terms(terms)
# Returns list of enrichment results for each term
```

##### `validate_qid(qid: str) -> bool`

Validate if a string is a valid Wikidata QID.

**Parameters:**
- **qid**: String to validate

**Returns:**
True if valid QID, False otherwise.

**Example:**
```python
is_valid = service.validate_qid("Q42")  # True
is_valid = service.validate_qid("invalid")  # False
```

##### `clear_cache()`

Clear the internal cache.

**Example:**
```python
service.clear_cache()
```

## Data Structures

### Entity Search Result

```python
{
    'id': 'Q42',
    'description': 'English writer and humorist',
    'label': 'Douglas Adams',
    'match_type': 'exact',
    'confidence': 1.0
}
```

### Entity Properties

```python
{
    'instance of': [
        {
            'type': 'entity',
            'id': 'Q5',
            'value': 'Q5'
        }
    ],
    'date of birth': [
        {
            'type': 'time',
            'value': '+1952-03-11T00:00:00Z'
        }
    ]
}
```

### Term Enrichment Result

```python
{
    'term': 'Douglas Adams',
    'wikidata': {
        'id': 'Q42',
        'description': 'English writer and humorist',
        'label': 'Douglas Adams',
        'confidence': 1.0,
        'summary': {
            'id': 'Q42',
            'label': 'Douglas Adams',
            'description': 'English writer and humorist',
            'aliases': ['Douglas Noël Adams', 'DNA'],
            'properties': {...},
            'wikipedia_links': {'en': 'Douglas_Adams'},
            'type': 'human'
        }
    },
    'enrichment_status': 'success'
}
```

## Error Handling

The service includes comprehensive error handling:

- **Network Errors**: Gracefully handles network failures
- **Invalid QIDs**: Returns empty results for invalid entity IDs
- **Missing Data**: Returns None or empty lists for missing information
- **API Limits**: Respects Wikidata API rate limits

## Performance Considerations

- **Caching**: Internal caching for repeated requests
- **Batch Processing**: Efficient processing of multiple terms
- **Fallback Methods**: Multiple data sources for reliability
- **Rate Limiting**: Built-in respect for API limits

## Examples

See `examples/wikidata_service_example.py` for comprehensive usage examples.

## Testing

Run the tests with:

```bash
python -m pytest test/test_wikimedia.py::WikidataServiceTest -v
```

## Integration with Dictionary Editor

The Wikidata service is designed to integrate seamlessly with the Dictionary Editor:

1. **Enrich Button**: Add "Enrich from Wikidata" button to entry forms
2. **Auto-fill**: Populate entry fields with Wikidata data
3. **Validation**: Validate Wikidata IDs entered by users
4. **Batch Operations**: Enrich multiple entries simultaneously

## Future Enhancements

- **SPARQL Queries**: Advanced query capabilities
- **Property Filtering**: Filter properties by type or value
- **Relationship Mapping**: Map entity relationships
- **Image Integration**: Extract and link entity images
- **Multi-language Support**: Enhanced language handling

## Contributing

When contributing to the Wikidata service:

1. Follow the existing code style
2. Add comprehensive tests for new functionality
3. Update this documentation
4. Ensure error handling is robust
5. Test with various entity types and edge cases

## License

This module is part of amilib and follows the same license terms.

