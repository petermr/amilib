#!/usr/bin/env python3
"""
Script to incrementally add Wikidata IDs to encyclopedia entries.

This script processes entries in batches, allowing for incremental progress
on slow or fragile network connections. It saves intermediate results after
each batch, so progress is preserved even if the script is interrupted.

Usage:
    python scripts/add_wikidata_ids.py input.html output.html [options]

Options:
    --batch-size N      Number of IDs to lookup per batch (default: 20)
    --delay SECONDS     Delay between requests in seconds (default: 0.1)
    --max-ids N         Maximum total IDs to lookup (default: None, process all)
    --resume            Resume from existing output file if it exists
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import amilib
sys.path.insert(0, str(Path(__file__).parent.parent))

from amilib.ami_encyclopedia import AmiEncyclopedia
from amilib.util import Util

logger = Util.get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Incrementally add Wikidata IDs to encyclopedia entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input encyclopedia HTML file'
    )
    
    parser.add_argument(
        'output_file',
        type=Path,
        help='Output encyclopedia HTML file (will be saved incrementally)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=20,
        help='Number of IDs to lookup per batch (default: 20)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between requests in seconds (default: 0.1)'
    )
    
    parser.add_argument(
        '--max-ids',
        type=int,
        default=None,
        help='Maximum total IDs to lookup (default: None, process all)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from existing output file if it exists'
    )
    
    parser.add_argument(
        '--title',
        type=str,
        default=None,
        help='Title for the encyclopedia (default: extracted from input file)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.exists():
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Create output directory if needed
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load encyclopedia
    logger.info(f"Loading encyclopedia from: {args.input_file}")
    
    # Determine if we should resume from existing output
    if args.resume and args.output_file.exists():
        logger.info(f"Resuming from existing output file: {args.output_file}")
        encyclopedia = AmiEncyclopedia(title=args.title or "Encyclopedia")
        encyclopedia.create_from_html_file(args.output_file)
    else:
        # Load from input file
        encyclopedia = AmiEncyclopedia(title=args.title or "Encyclopedia")
        encyclopedia.create_from_html_file(args.input_file)
    
    # Count initial state
    total_entries = len(encyclopedia.entries)
    entries_with_id = sum(
        1 for entry in encyclopedia.entries
        if entry.get('wikidata_id') and 
        entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id')
    )
    entries_missing_id = total_entries - entries_with_id
    
    logger.info(f"Encyclopedia loaded: {total_entries} total entries")
    logger.info(f"  - {entries_with_id} already have Wikidata IDs")
    logger.info(f"  - {entries_missing_id} need Wikidata IDs")
    
    if entries_missing_id == 0:
        logger.info("All entries already have Wikidata IDs. Nothing to do.")
        return
    
    # Process in batches
    logger.info(f"\nStarting incremental batch processing:")
    logger.info(f"  - Batch size: {args.batch_size} IDs per batch")
    logger.info(f"  - Delay: {args.delay} seconds between requests")
    if args.max_ids:
        logger.info(f"  - Maximum IDs to lookup: {args.max_ids}")
    logger.info(f"  - Output file: {args.output_file}")
    logger.info("")
    
    # Track total progress
    total_ids_looked_up = 0
    batch_number = 0
    all_stats = {
        "entries_with_wikidata_id_before": entries_with_id,
        "entries_successfully_found": 0,
        "entries_failed_lookup": 0,
        "entries_skipped_already_have_id": 0,
        "entries_skipped_no_wikipedia": 0,
        "entries_skipped_ambiguous": 0,
    }
    
    # Process in batches until all entries have IDs or max_ids reached
    while True:
        # Count current state
        current_with_id = sum(
            1 for entry in encyclopedia.entries
            if entry.get('wikidata_id') and 
            entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id')
        )
        current_missing = total_entries - current_with_id
        
        # Check if we're done
        if current_missing == 0:
            logger.info("All entries now have Wikidata IDs!")
            break
        
        # Check if we've reached max_ids limit
        if args.max_ids and total_ids_looked_up >= args.max_ids:
            logger.info(f"Reached maximum IDs limit ({args.max_ids})")
            break
        
        # Calculate how many to process in this batch
        remaining_limit = args.max_ids - total_ids_looked_up if args.max_ids else None
        batch_max_ids = min(args.batch_size, current_missing)
        if remaining_limit:
            batch_max_ids = min(batch_max_ids, remaining_limit)
        
        batch_number += 1
        logger.info(f"\n{'=' * 60}")
        logger.info(f"BATCH {batch_number}")
        logger.info(f"{'=' * 60}")
        logger.info(f"Processing up to {batch_max_ids} entries...")
        logger.info(f"Progress: {current_with_id}/{total_entries} entries have Wikidata IDs ({current_with_id/total_entries*100:.1f}%)")
        logger.info(f"Remaining: {current_missing} entries need IDs")
        
        # Lookup Wikidata IDs for this batch
        try:
            batch_stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(
                max_ids=batch_max_ids,
                output_file=args.output_file,
                delay_seconds=args.delay
            )
            
            # Accumulate stats
            all_stats["entries_successfully_found"] += batch_stats.get("entries_successfully_found", 0)
            all_stats["entries_failed_lookup"] += batch_stats.get("entries_failed_lookup", 0)
            all_stats["entries_skipped_already_have_id"] += batch_stats.get("entries_skipped_already_have_id", 0)
            all_stats["entries_skipped_no_wikipedia"] += batch_stats.get("entries_skipped_no_wikipedia", 0)
            all_stats["entries_skipped_ambiguous"] += batch_stats.get("entries_skipped_ambiguous", 0)
            
            total_ids_looked_up += batch_stats.get("entries_looked_up", 0)
            found_in_batch = batch_stats.get("entries_successfully_found", 0)
            
            logger.info(f"Batch {batch_number} complete:")
            logger.info(f"  - Looked up: {batch_stats.get('entries_looked_up', 0)} entries")
            logger.info(f"  - Successfully found: {found_in_batch} Wikidata IDs")
            logger.info(f"  - Failed: {batch_stats.get('entries_failed_lookup', 0)} lookups")
            logger.info(f"  - Saved to: {args.output_file}")
            
            # If no IDs were found in this batch, we might be stuck
            if found_in_batch == 0 and batch_stats.get("entries_looked_up", 0) > 0:
                logger.warning("No IDs found in this batch. Remaining entries may not have Wikipedia pages.")
                # Continue anyway - might be network issues
            
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user. Saving current progress...")
            try:
                encyclopedia.save_wiki_normalized_html(args.output_file)
                logger.info(f"Progress saved to: {args.output_file}")
            except Exception as e:
                logger.error(f"Failed to save progress: {e}")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in batch {batch_number}: {e}")
            logger.info("Saving current progress before continuing...")
            try:
                encyclopedia.save_wiki_normalized_html(args.output_file)
                logger.info(f"Progress saved to: {args.output_file}")
            except Exception as save_error:
                logger.error(f"Failed to save progress: {save_error}")
            # Continue with next batch
            continue
    
    # Final summary
    final_with_id = sum(
        1 for entry in encyclopedia.entries
        if entry.get('wikidata_id') and 
        entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id')
    )
    final_missing = total_entries - final_with_id
    
    logger.info("\n" + "=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total entries: {total_entries}")
    logger.info(f"Entries with Wikidata ID (before): {all_stats['entries_with_wikidata_id_before']}")
    logger.info(f"Entries with Wikidata ID (after): {final_with_id}")
    logger.info(f"Entries still missing: {final_missing}")
    logger.info(f"Total batches processed: {batch_number}")
    logger.info(f"Total IDs looked up: {total_ids_looked_up}")
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  - Successfully found: {all_stats['entries_successfully_found']} Wikidata IDs")
    logger.info(f"  - Failed lookups: {all_stats['entries_failed_lookup']}")
    logger.info(f"  - Skipped (already have ID): {all_stats['entries_skipped_already_have_id']}")
    logger.info(f"  - Skipped (no Wikipedia): {all_stats['entries_skipped_no_wikipedia']}")
    logger.info(f"  - Skipped (ambiguous): {all_stats['entries_skipped_ambiguous']}")
    logger.info("")
    logger.info(f"Final encyclopedia saved to: {args.output_file}")
    
    # Save final version
    try:
        encyclopedia.save_wiki_normalized_html(args.output_file)
        logger.info("Final encyclopedia saved successfully")
    except Exception as e:
        logger.error(f"Failed to save final encyclopedia: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

