#!/usr/bin/env python3
"""
AR6 Incremental Processing System - Command Line Interface

A make-like system for processing AR6 IPCC components through transformation stages.
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from scripts.ar6_processor.registry import ComponentRegistry
    from scripts.ar6_processor.pipeline import AR6Pipeline
    from scripts.ar6_processor.batch_processor import BatchProcessor
except ImportError as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AR6 Incremental Processing System - Process IPCC components through transformation stages'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process components')
    process_parser.add_argument('--component-id', help='Process specific component ID')
    process_parser.add_argument('--component-ids', nargs='+', help='Process multiple component IDs')
    process_parser.add_argument('--report', choices=['wg1', 'wg2', 'wg3', 'syr'], help='Filter by report')
    process_parser.add_argument('--component-type', choices=['chapter', 'spm', 'ts', 'annex', 'cross_chapter_box'],
                               help='Filter by component type')
    process_parser.add_argument('--target-stage', choices=['download', 'pdf_convert', 'clean', 'structure', 'add_ids'],
                               help='Final stage to reach')
    process_parser.add_argument('--force', action='store_true', help='Force re-run completed stages')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show component status')
    status_parser.add_argument('--component-id', help='Show status for specific component')
    status_parser.add_argument('--report', choices=['wg1', 'wg2', 'wg3', 'syr'], help='Filter by report')
    status_parser.add_argument('--component-type', choices=['chapter', 'spm', 'ts', 'annex', 'cross_chapter_box'],
                              help='Filter by component type')
    status_parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    
    # Registry command
    registry_parser = subparsers.add_parser('registry', help='Manage registry')
    registry_parser.add_argument('--scan', action='store_true', help='Scan filesystem and update registry')
    registry_parser.add_argument('--list', action='store_true', help='List all components')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    registry = ComponentRegistry()
    pipeline = AR6Pipeline(registry)
    batch_processor = BatchProcessor(registry, pipeline)
    
    if args.command == 'process':
        if args.component_id:
            # Process single component
            result = pipeline.process_component(
                component_id=args.component_id,
                target_stage=args.target_stage,
                force=args.force
            )
            print_result(result)
        else:
            # Process batch
            result = batch_processor.process_batch(
                component_ids=args.component_ids,
                report=args.report,
                component_type=args.component_type,
                target_stage=args.target_stage,
                force=args.force
            )
            print_batch_result(result)
    
    elif args.command == 'status':
        if args.component_id:
            # Show single component status
            status = pipeline.get_component_status(args.component_id)
            print_component_status(status)
        elif args.summary:
            # Show summary
            summary = batch_processor.get_status_summary(
                report=args.report,
                component_type=args.component_type
            )
            print_summary(summary)
        else:
            # List components
            components = registry.get_components(report=args.report, component_type=args.component_type)
            print(f"\nFound {len(components)} components:")
            for comp in components:
                print(f"  {comp['id']}: {comp['report']}/{comp['type']}")
    
    elif args.command == 'registry':
        if args.scan:
            registry._initialize_from_filesystem()
            registry.save()
            print(f"Registry updated: {len(registry.components)} components")
        elif args.list:
            components = registry.get_components()
            print(f"\nRegistry contains {len(components)} components:")
            for comp in sorted(components, key=lambda x: x['id']):
                print(f"  {comp['id']}: {comp['report']}/{comp['type']}")


def print_result(result: dict):
    """Print single component processing result."""
    print(f"\n{'='*80}")
    print(f"Component: {result.get('component_id')}")
    print(f"Success: {result.get('success')}")
    
    if result.get('stages_processed'):
        print(f"\nStages Processed ({len(result['stages_processed'])}):")
        for stage_info in result['stages_processed']:
            print(f"  ✓ {stage_info['stage']}: {stage_info.get('output_file', '')}")
    
    if result.get('stages_skipped'):
        print(f"\nStages Skipped ({len(result['stages_skipped'])}):")
        for stage_info in result['stages_skipped']:
            print(f"  ⊘ {stage_info['stage']}: {stage_info.get('reason', '')}")
    
    if result.get('stages_failed'):
        print(f"\nStages Failed ({len(result['stages_failed'])}):")
        for stage_info in result['stages_failed']:
            print(f"  ✗ {stage_info['stage']}: {stage_info.get('error', stage_info.get('reason', ''))}")
    
    print(f"{'='*80}\n")


def print_batch_result(result: dict):
    """Print batch processing result."""
    print(f"\n{'='*80}")
    print(f"Batch Processing Results")
    print(f"  Total: {result['total']}")
    print(f"  Processed: {len(result['processed'])}")
    print(f"  Failed: {len(result['failed'])}")
    
    if result['failed']:
        print(f"\nFailed Components:")
        for failed in result['failed']:
            print(f"  ✗ {failed['component_id']}: {failed.get('error', 'unknown')}")
    
    print(f"{'='*80}\n")


def print_component_status(status: dict):
    """Print component status."""
    print(f"\n{'='*80}")
    print(f"Component: {status.get('component_id')}")
    print(f"Report: {status.get('report')}")
    print(f"Type: {status.get('type')}")
    print(f"\nStage Status:")
    for stage, stage_info in status.get('stages', {}).items():
        status_symbol = {
            'complete': '✓',
            'pending': '○',
            'skip': '⊘'
        }.get(stage_info.get('status', 'pending'), '?')
        print(f"  {status_symbol} {stage}: {stage_info.get('status', 'pending')}")
        if stage_info.get('file'):
            print(f"      File: {stage_info['file']}")
    print(f"{'='*80}\n")


def print_summary(summary: dict):
    """Print status summary."""
    print(f"\n{'='*80}")
    print(f"Status Summary")
    print(f"  Total Components: {summary['total']}")
    print(f"\nBy Status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")
    print(f"\nBy Stage:")
    for stage, stage_counts in summary['by_stage'].items():
        print(f"  {stage}:")
        for status, count in stage_counts.items():
            if count > 0:
                print(f"    {status}: {count}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()

