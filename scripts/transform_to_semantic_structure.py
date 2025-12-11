"""
Transform all glossary/acronym files to semantic structure with role-based divs.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.glossary_processor.semantic_structure_transformer import SemanticStructureTransformer
from amilib.util import Util

logger = Util.get_logger(__name__)


# Define all glossary/acronym files
FILES = [
    {
        "report": "wg1",
        "annex": "annex-i-glossary",
        "entry_type": "glossary",
        "input": "test/resources/ipcc/cleaned_content/wg1/annex-i-glossary/annex-i-glossary.html",
        "output": "test/resources/ipcc/cleaned_content/wg1/annex-i-glossary/semantic.html"
    },
    {
        "report": "wg1",
        "annex": "annex-ii-acronyms",
        "entry_type": "acronym",
        "input": "test/resources/ipcc/cleaned_content/wg1/annex-ii-acronyms/annex-ii-acronyms.html",
        "output": "test/resources/ipcc/cleaned_content/wg1/annex-ii-acronyms/semantic.html"
    },
    {
        "report": "wg3",
        "annex": "annex-i-glossary",
        "entry_type": "glossary",
        "input": "test/resources/ipcc/cleaned_content/wg3/annex-i-glossary/annex-i-glossary.html",
        "output": "test/resources/ipcc/cleaned_content/wg3/annex-i-glossary/semantic.html"
    },
    {
        "report": "wg3",
        "annex": "annex-vi-acronyms",
        "entry_type": "acronym",
        "input": "test/resources/ipcc/cleaned_content/wg3/annex-vi-acronyms/annex-vi-acronyms.html",
        "output": "test/resources/ipcc/cleaned_content/wg3/annex-vi-acronyms/semantic.html"
    },
    {
        "report": "syr",
        "annex": "annex-i-glossary",
        "entry_type": "glossary",
        "input": "test/resources/ipcc/cleaned_content/syr/annex-i-glossary/annex-i-glossary.html",
        "output": "test/resources/ipcc/cleaned_content/syr/annex-i-glossary/semantic.html"
    },
    {
        "report": "syr",
        "annex": "annex-ii-acronyms",
        "entry_type": "acronym",
        "input": "test/resources/ipcc/cleaned_content/syr/annex-ii-acronyms/annex-ii-acronyms.html",
        "output": "test/resources/ipcc/cleaned_content/syr/annex-ii-acronyms/semantic.html"
    }
]


def main():
    """Transform all files."""
    transformer = SemanticStructureTransformer(use_dl=False)
    
    results = []
    for file_info in FILES:
        input_path = Path(file_info["input"])
        output_path = Path(file_info["output"])
        
        if not input_path.exists():
            logger.warning(f"Input file not found: {input_path}")
            results.append((file_info["report"], file_info["annex"], False, "Input file not found"))
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {file_info['report']} / {file_info['annex']}")
        logger.info(f"{'='*60}")
        
        success = transformer.transform_html(
            input_path,
            output_path,
            file_info["report"],
            file_info["annex"],
            file_info["entry_type"]
        )
        
        results.append((file_info["report"], file_info["annex"], success, ""))
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TRANSFORMATION SUMMARY")
    logger.info(f"{'='*60}")
    
    successful = sum(1 for _, _, success, _ in results if success)
    total = len(results)
    
    for report, annex, success, error in results:
        status = "✅" if success else "❌"
        logger.info(f"{status} {report} / {annex}")
        if error:
            logger.info(f"   Error: {error}")
    
    logger.info(f"\n✅ Successfully transformed: {successful}/{total}")
    logger.info(f"❌ Failed: {total - successful}/{total}")


if __name__ == '__main__':
    main()

