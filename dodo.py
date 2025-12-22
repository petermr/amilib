"""
doit tasks for AR6 IPCC document processing.

This file defines tasks for processing IPCC AR6 documents through
multiple transformation stages with dependency tracking.

Usage:
    doit                    # Run all tasks
    doit list              # List all tasks
    doit info              # Show task details
    doit add_section_ids   # Run specific task
    doit --force           # Force re-run (ignore dependencies)
"""

from pathlib import Path
from doit import create_after

# Base directories
BASE_DIR = Path("test/resources/ipcc/cleaned_content")
SCRIPTS_DIR = Path("scripts")


def get_spm_ts_documents():
    """Get list of all SPM/TS documents."""
    documents = []
    for report in ['wg1', 'wg2', 'wg3']:
        for doc_type in ['summary-for-policymakers', 'technical-summary']:
            doc_dir = BASE_DIR / report / doc_type
            cleaned_file = doc_dir / "de_gatsby.html"
            
            if cleaned_file.exists():
                documents.append({
                    'report': report,
                    'doc_type': doc_type,
                    'doc_dir': doc_dir,
                    'cleaned_file': cleaned_file,
                })
    
    return documents


def get_chapter_documents():
    """Get list of all chapter documents."""
    documents = []
    for report in ['wg1', 'wg2', 'wg3']:
        report_dir = BASE_DIR / report
        if not report_dir.exists():
            continue
        
        for chapter_dir in report_dir.glob("Chapter*"):
            if not chapter_dir.is_dir():
                continue
            
            cleaned_file = chapter_dir / "de_gatsby.html"
            if cleaned_file.exists():
                documents.append({
                    'report': report,
                    'chapter': chapter_dir.name,
                    'doc_dir': chapter_dir,
                    'cleaned_file': cleaned_file,
                })
    
    return documents


def task_add_section_ids():
    """
    Step 1: Add IDs to section containers (h1-container, h2-container, etc.).
    
    This is the first step in the cascading ID addition process.
    Section IDs are extracted from headings and normalized.
    """
    for doc in get_spm_ts_documents() + get_chapter_documents():
        cleaned_file = doc['cleaned_file']
        doc_dir = doc['doc_dir']
        output_file = doc_dir / "html_with_section_ids.html"
        
        # Determine document identifier
        if 'doc_type' in doc:
            doc_id = f"{doc['report']}-{doc['doc_type']}"
        else:
            doc_id = f"{doc['report']}-{doc['chapter']}"
        
        yield {
            'name': f'section-ids-{doc_id}',
            'file_dep': [cleaned_file],
            'targets': [output_file],
            'actions': [
                f'python {SCRIPTS_DIR}/id_processor/add_section_ids.py '
                f'--input {cleaned_file} '
                f'--output {output_file} '
                f'--report {doc["report"]}'
            ],
            'clean': True,
            'verbosity': 2,
        }


@create_after(executed='add_section_ids', target_regex=r'.*html_with_section_ids\.html$')
def task_add_paragraph_ids():
    """
    Step 2: Add IDs to paragraphs (depends on section IDs).
    
    Paragraph IDs are generated based on their parent section container ID.
    Format: {section_id}_p{index}
    """
    for doc in get_spm_ts_documents() + get_chapter_documents():
        doc_dir = doc['doc_dir']
        section_ids_file = doc_dir / "html_with_section_ids.html"
        output_file = doc_dir / "html_with_ids.html"
        
        if not section_ids_file.exists():
            continue
        
        # Determine document identifier
        if 'doc_type' in doc:
            doc_id = f"{doc['report']}-{doc['doc_type']}"
        else:
            doc_id = f"{doc['report']}-{doc['chapter']}"
        
        yield {
            'name': f'para-ids-{doc_id}',
            'file_dep': [section_ids_file],
            'targets': [output_file],
            'actions': [
                f'python {SCRIPTS_DIR}/id_processor/add_paragraph_ids.py '
                f'--input {section_ids_file} '
                f'--output {output_file} '
                f'--report {doc["report"]}'
            ],
            'clean': True,
            'verbosity': 2,
        }


@create_after(executed='add_paragraph_ids', target_regex=r'.*html_with_ids\.html$')
def task_add_nested_div_ids():
    """
    Step 3: Add IDs to nested divs (depends on paragraph IDs).
    
    Nested divs get IDs based on their parent container.
    Format: {parent_id}_{type}_{index}
    """
    for doc in get_spm_ts_documents() + get_chapter_documents():
        doc_dir = doc['doc_dir']
        para_ids_file = doc_dir / "html_with_ids.html"
        output_file = doc_dir / "html_with_all_ids.html"
        
        if not para_ids_file.exists():
            continue
        
        # Determine document identifier
        if 'doc_type' in doc:
            doc_id = f"{doc['report']}-{doc['doc_type']}"
        else:
            doc_id = f"{doc['report']}-{doc['chapter']}"
        
        yield {
            'name': f'nested-div-ids-{doc_id}',
            'file_dep': [para_ids_file],
            'targets': [output_file],
            'actions': [
                f'python {SCRIPTS_DIR}/id_processor/add_nested_div_ids.py '
                f'--input {para_ids_file} '
                f'--output {output_file} '
                f'--report {doc["report"]}'
            ],
            'clean': True,
            'verbosity': 2,
        }


@create_after(executed='add_nested_div_ids', target_regex=r'.*html_with_all_ids\.html$')
def task_generate_id_lists():
    """
    Step 4: Generate ID lists and paragraph lists (depends on all IDs).
    
    Creates:
    - id_list.html: List of all IDs
    - para_list.html: List of all paragraphs with IDs
    """
    for doc in get_spm_ts_documents() + get_chapter_documents():
        doc_dir = doc['doc_dir']
        all_ids_file = doc_dir / "html_with_all_ids.html"
        id_list_file = doc_dir / "id_list.html"
        para_list_file = doc_dir / "para_list.html"
        
        if not all_ids_file.exists():
            continue
        
        # Determine document identifier
        if 'doc_type' in doc:
            doc_id = f"{doc['report']}-{doc['doc_type']}"
        else:
            doc_id = f"{doc['report']}-{doc['chapter']}"
        
        yield {
            'name': f'id-lists-{doc_id}',
            'file_dep': [all_ids_file],
            'targets': [id_list_file, para_list_file],
            'actions': [
                f'python {SCRIPTS_DIR}/id_processor/generate_id_lists.py '
                f'--input {all_ids_file} '
                f'--id-list {id_list_file} '
                f'--para-list {para_list_file}'
            ],
            'clean': True,
            'verbosity': 2,
        }


def task_process_spm_ts_only():
    """
    Process only SPM and TS documents (convenience task).
    """
    return {
        'actions': [
            'doit add_section_ids:section-ids-wg1-summary-for-policymakers',
            'doit add_section_ids:section-ids-wg1-technical-summary',
            'doit add_section_ids:section-ids-wg2-summary-for-policymakers',
            'doit add_section_ids:section-ids-wg2-technical-summary',
            'doit add_section_ids:section-ids-wg3-summary-for-policymakers',
            'doit add_section_ids:section-ids-wg3-technical-summary',
        ],
        'verbosity': 2,
    }


def task_validate_ids():
    """
    Validate that all IDs are unique and properly formatted.
    """
    for doc in get_spm_ts_documents() + get_chapter_documents():
        doc_dir = doc['doc_dir']
        all_ids_file = doc_dir / "html_with_all_ids.html"
        
        if not all_ids_file.exists():
            continue
        
        # Determine document identifier
        if 'doc_type' in doc:
            doc_id = f"{doc['report']}-{doc['doc_type']}"
        else:
            doc_id = f"{doc['report']}-{doc['chapter']}"
        
        yield {
            'name': f'validate-{doc_id}',
            'file_dep': [all_ids_file],
            'actions': [
                f'python {SCRIPTS_DIR}/id_processor/validate_ids.py '
                f'--input {all_ids_file}'
            ],
            'verbosity': 2,
        }



