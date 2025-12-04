# Add Wikidata IDs to Encyclopedia

## Overview

The `add_wikidata_ids.py` script incrementally adds Wikidata IDs to encyclopedia entries. It's designed for processing large encyclopedias (e.g., 400+ entries) on slow or fragile network connections.

## Features

- **Incremental Processing**: Processes entries in small batches (default: 20 IDs per batch)
- **Progress Preservation**: Saves intermediate results after each batch, so progress is preserved if interrupted
- **Resume Support**: Can resume from an existing output file
- **Rate Limiting**: Configurable delay between requests to avoid overwhelming slow connections
- **Progress Tracking**: Detailed logging of progress and statistics

## Usage

### Basic Usage

```bash
python scripts/add_wikidata_ids.py input.html output.html
```

This will:
- Load the encyclopedia from `input.html`
- Process entries in batches of 20 IDs
- Save progress to `output.html` after each batch
- Use a 0.1 second delay between requests

### Custom Batch Size

For slower connections, use smaller batches:

```bash
python scripts/add_wikidata_ids.py input.html output.html --batch-size 10
```

### Custom Delay

For very slow or fragile connections, increase the delay:

```bash
python scripts/add_wikidata_ids.py input.html output.html --delay 0.5
```

### Limit Total IDs

To process only a subset of entries (useful for testing):

```bash
python scripts/add_wikidata_ids.py input.html output.html --max-ids 50
```

### Resume from Existing File

If the script was interrupted, resume from the existing output:

```bash
python scripts/add_wikidata_ids.py input.html output.html --resume
```

Note: When using `--resume`, the script will load from `output.html` instead of `input.html`.

### Complete Example

For a 400-entry encyclopedia on a slow connection:

```bash
python scripts/add_wikidata_ids.py \
    large_encyclopedia.html \
    large_encyclopedia_with_ids.html \
    --batch-size 20 \
    --delay 0.2 \
    --title "My Encyclopedia"
```

## How It Works

1. **Load Encyclopedia**: Loads entries from the input HTML file
2. **Classify Entries**: Uses classification system to skip entries that already have IDs or can't be processed
3. **Batch Processing**: 
   - Processes entries in small batches
   - Looks up Wikidata IDs from Wikipedia pages
   - Gets Wikidata categories for newly found IDs
4. **Save Progress**: After each batch, saves the updated encyclopedia
5. **Repeat**: Continues until all entries have IDs or max_ids limit reached

## Output

The script provides detailed progress information:

- Initial state (how many entries have/need IDs)
- Progress for each batch
- Final summary with statistics

Example output:
```
Encyclopedia loaded: 400 total entries
  - 50 already have Wikidata IDs
  - 350 need Wikidata IDs

Starting incremental batch processing:
  - Batch size: 20 IDs per batch
  - Delay: 0.1 seconds between requests
  - Output file: output.html

============================================================
BATCH 1
============================================================
Processing up to 20 entries...
Progress: 50/400 entries have Wikidata IDs (12.5%)
Remaining: 350 entries need IDs
Batch 1 complete:
  - Looked up: 20 entries
  - Successfully found: 18 Wikidata IDs
  - Failed: 2 lookups
  - Saved to: output.html

[... continues with more batches ...]

============================================================
PROCESSING COMPLETE
============================================================
Total entries: 400
Entries with Wikidata ID (before): 50
Entries with Wikidata ID (after): 385
Entries still missing: 15
Total batches processed: 18
```

## Error Handling

- **Network Errors**: The script continues processing even if individual lookups fail
- **Interruptions**: Press Ctrl+C to safely interrupt - current progress will be saved
- **Resume**: Use `--resume` flag to continue from where you left off

## Tips

1. **Start Small**: Test with `--max-ids 20` first to verify everything works
2. **Monitor Progress**: Watch the output to see how many IDs are being found
3. **Adjust Batch Size**: Smaller batches (10-15) are safer for very slow connections
4. **Increase Delay**: If you see many failures, try `--delay 0.5` or higher
5. **Resume Often**: If connection is unstable, run in smaller chunks with `--max-ids` and resume

## Requirements

- Python 3.7+
- amilib package (installed in the workspace)
- Internet connection for Wikidata/Wikipedia lookups

