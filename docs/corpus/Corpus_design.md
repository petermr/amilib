Based on my exploration of the existing AmiCorpus code, here's my PLAN for Task 1 (NO CODE):
Current AmiCorpus Analysis
Existing Structure:
corpus_module/ - Standalone corpus module with:
corpus.py - Main AmiCorpus and AmiCorpusContainer classes
query.py - CorpusQuery class for search queries
search.py - CorpusSearch class for brute-force searching
__init__.py - Module exports
amilib/ami_corpus.py - Older version with similar functionality
Current Capabilities:
Hierarchical directory management via AmiCorpusContainer
File globbing and discovery with globstr patterns
Brute-force search across HTML files with phrase matching
Query management with CorpusQuery objects
Results visualization with DataTables HTML generation
EUPMC integration for scientific papers
Missing Transformation Tracking:
No schema for tracking foo.xml → foo.xml.html transformations
No version control for transformations
No metadata about transformation types and timestamps
Proposed Enhancement Plan
1.1 Transformation Schema Design
JSON/YAML metadata files to track original → transformed mappings
Transformation registry with timestamps, types, and parameters
File suffix mapping (e.g., .xml → .xml.html, .pdf → .pdf.txt)
1.2 Corpus Structure Enhancement
Extend AmiCorpus to include transformation tracking
Add transformation metadata to AmiCorpusContainer
Create transformation history for each document
1.3 Graphviz Diagram Plans
State diagrams: Show current corpus structure and relationships
Transformation flow diagrams: Document processing pipeline
Relationship diagrams: Original ↔ transformed file connections
1.4 Test Planning
Unit tests for transformation tracking
Integration tests for corpus creation with transformations
Visualization tests for graphviz diagram generation
Performance tests for brute-force search on larger corpora
1.5 Integration Strategy
Extend existing corpus_module rather than replace
Maintain backward compatibility with current AmiCorpus usage
Add transformation capabilities as optional features
Use existing file patterns and directory structures
1.6 Key Design Decisions
File-based transformation tracking (JSON metadata files)
Suffix-based transformation identification (e.g., .xml.html)
Hierarchical transformation history (multiple transformations per file)
Brute-force search across both original and transformed files
This approach builds on the existing solid foundation while adding the transformation tracking capabilities needed for the complex project workflow.
Is this plan aligned with your vision for Task 1?
YES.
STYLE: Where possible define transformations in external files (YAML, JSON, XML, etc.) rather than internally. This allows non coders to understand the logic and change it for different applications

EXCELLENT STYLE RULE!
This is a crucial design principle that I will follow throughout the project:
External Transformation Definition Strategy
1.1.1 Transformation Configuration Files
YAML/JSON schemas for transformation definitions
XML transformation rules for complex document processing
Configuration files that non-coders can read and modify
Template-based approaches for common transformation patterns
1.1.2 Benefits of External Configuration
Non-coder accessibility - Business users can understand and modify logic
Application flexibility - Different transformation rules for different use cases
Version control - Transformation logic tracked separately from code
Reusability - Same transformation rules across different corpora
Maintainability - Changes without code deployment
1.1.3 Proposed External File Structure
Apply to IPCC_AR6_WGI...
json
1.1.4 Configuration File Examples
Transformation rules in YAML (readable by non-coders)
File suffix mappings in JSON (easy to modify)
Search patterns in external config files
Corpus metadata in human-readable formats
1.1.5 Implementation Approach
Configuration-driven design - Code reads external files
Validation schemas - Ensure configuration correctness
Default configurations - Sensible defaults with override capability
Documentation - Clear examples for non-coders
This style rule will be applied to all transformation logic throughout the project, making the system accessible to both technical and non-technical users.
Should I proceed with designing the external configuration file structures for Task 1?
YES.
CORPUS: Input can come from:
* searches of remote repositories (europepmc, biorxiv, redalyc, scielo, and others)
* heterogeneous manually created collections (e.g user saves current reading) 

EXCELLENT! This expands the corpus scope significantly. Let me plan the external configuration structure to handle these diverse input sources:
1.1.6 External Configuration for Multi-Source Corpora
1.1.6.1 Repository Configuration Files
Apply to IPCC_AR6_WGI...
/
1.1.6.2 Repository Configuration Structure
repositories/europepmc.yaml:
Apply to IPCC_AR6_WGI...
"
1.1.6.3 Manual Collection Configuration
repositories/local_collection.json:
Apply to IPCC_AR6_WGI...
}
1.1.6.4 Unified Corpus Configuration
schemas/corpus_metadata.yaml:
Apply to IPCC_AR6_WGI...
"
1.1.6.5 Benefits for Non-Coders
Repository selection - Choose sources without coding
Query modification - Change search terms in YAML/JSON
Transformation customization - Adjust processing steps
Metadata mapping - Define field mappings for different sources
Pipeline configuration - Modify processing workflow
1.1.6.6 Implementation Strategy
Repository adapters - Code reads external configs
Unified interface - Same corpus API regardless of source
Validation - Schema validation for all config files
Documentation - Clear examples for each repository type
Extensibility - Easy to add new repositories via config
This approach allows users to:
Mix sources (EUPMC + local files + BioRxiv)
Customize transformations per repository
Modify search parameters without code changes
Add new repositories via configuration files
Should I proceed with designing the repository adapter interfaces and transformation pipeline configuration?
I wrote several declarative files for editing HTML files which I think relate to IPCC. They contained instructions such as remove_empty_elements. Please see if you can find these and comment on the structire.

I think these are in HTMLEditor

I  am getting:
 Connection failed. If the problem persists, please check your internet connection or VPN 
but my internet seems stable. 

Please save the current design in docs/*.md so you can read it in the future

