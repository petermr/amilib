"""
Batch Processor for AR6 Components

Processes multiple components in batch with filtering options.
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.ar6_processor.registry import ComponentRegistry
from scripts.ar6_processor.pipeline import AR6Pipeline


class BatchProcessor:
    """Batch processor for multiple AR6 components."""
    
    def __init__(self, registry: Optional[ComponentRegistry] = None,
                 pipeline: Optional[AR6Pipeline] = None):
        """
        Initialize batch processor.
        
        Args:
            registry: ComponentRegistry instance
            pipeline: AR6Pipeline instance
        """
        self.registry = registry or ComponentRegistry()
        self.pipeline = pipeline or AR6Pipeline(self.registry)
    
    def process_batch(self, component_ids: Optional[List[str]] = None,
                     report: Optional[str] = None,
                     component_type: Optional[str] = None,
                     target_stage: Optional[str] = None,
                     force: bool = False,
                     **kwargs) -> Dict:
        """
        Process multiple components in batch.
        
        Args:
            component_ids: List of specific component IDs (None = all matching filter)
            report: Filter by report (wg1, wg2, wg3, syr)
            component_type: Filter by type (chapter, spm, ts, annex, cross_chapter_box)
            target_stage: Final stage to reach
            force: If True, re-run completed stages
            **kwargs: Additional arguments passed to stage processors
            
        Returns:
            Dict with batch processing results
        """
        # Get components to process
        if component_ids:
            components = [self.registry.get_component(cid) for cid in component_ids]
            components = [c for c in components if c is not None]
        else:
            components = self.registry.get_components(report=report, component_type=component_type)
        
        if not components:
            return {
                'success': False,
                'error': 'No components found matching criteria'
            }
        
        results = {
            'total': len(components),
            'processed': [],
            'failed': [],
            'skipped': []
        }
        
        print(f"\n{'='*80}")
        print(f"Processing {len(components)} components")
        if target_stage:
            print(f"Target stage: {target_stage}")
        print(f"{'='*80}\n")
        
        for i, component in enumerate(components, 1):
            component_id = component['id']
            print(f"[{i}/{len(components)}] Processing: {component_id}")
            
            result = self.pipeline.process_component(
                component_id=component_id,
                target_stage=target_stage,
                force=force,
                **kwargs
            )
            
            if result['success']:
                results['processed'].append({
                    'component_id': component_id,
                    'stages_processed': len(result['stages_processed']),
                    'stages_skipped': len(result['stages_skipped'])
                })
            else:
                results['failed'].append({
                    'component_id': component_id,
                    'error': result.get('error', 'unknown error'),
                    'failed_stage': result.get('stages_failed', [{}])[0].get('stage') if result.get('stages_failed') else None
                })
        
        results['success'] = len(results['failed']) == 0
        
        print(f"\n{'='*80}")
        print(f"Batch Processing Complete")
        print(f"  Total: {results['total']}")
        print(f"  Processed: {len(results['processed'])}")
        print(f"  Failed: {len(results['failed'])}")
        print(f"{'='*80}\n")
        
        return results
    
    def get_status_summary(self, report: Optional[str] = None,
                          component_type: Optional[str] = None) -> Dict:
        """Get status summary for filtered components."""
        components = self.registry.get_components(report=report, component_type=component_type)
        
        summary = {
            'total': len(components),
            'by_stage': {},
            'by_status': {'complete': 0, 'pending': 0, 'skip': 0}
        }
        
        for stage in AR6Pipeline.STAGES:
            summary['by_stage'][stage] = {
                'complete': 0,
                'pending': 0,
                'skip': 0
            }
        
        for component in components:
            all_complete = True
            for stage in AR6Pipeline.STAGES:
                stage_status = component['stages'].get(stage, {}).get('status', 'pending')
                summary['by_stage'][stage][stage_status] = summary['by_stage'][stage].get(stage_status, 0) + 1
                
                if stage_status != 'complete' and stage_status != 'skip':
                    all_complete = False
            
            if all_complete:
                summary['by_status']['complete'] += 1
            else:
                summary['by_status']['pending'] += 1
        
        return summary




