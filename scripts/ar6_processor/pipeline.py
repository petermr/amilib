"""
AR6 Processing Pipeline

Orchestrates component processing through transformation stages.
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.ar6_processor.registry import ComponentRegistry
from scripts.ar6_processor.stage_processors import (
    DownloadStage,
    PDFConvertStage,
    CleanStage,
    StructureStage,
    AddIDsStage
)


class AR6Pipeline:
    """Main pipeline orchestrator for AR6 component processing."""
    
    STAGES = ['download', 'pdf_convert', 'clean', 'structure', 'add_ids']
    
    STAGE_PROCESSORS = {
        'download': DownloadStage,
        'pdf_convert': PDFConvertStage,
        'clean': CleanStage,
        'structure': StructureStage,
        'add_ids': AddIDsStage
    }
    
    def __init__(self, registry: Optional[ComponentRegistry] = None):
        """
        Initialize pipeline.
        
        Args:
            registry: ComponentRegistry instance (creates new if None)
        """
        self.registry = registry or ComponentRegistry()
        self.processors = {}
        for stage, processor_class in self.STAGE_PROCESSORS.items():
            self.processors[stage] = processor_class(self.registry)
    
    def process_component(self, component_id: str, target_stage: Optional[str] = None,
                         force: bool = False, **kwargs) -> Dict:
        """
        Process a component through all stages up to target_stage.
        
        Args:
            component_id: ID of component to process
            target_stage: Final stage to reach (None = all stages)
            force: If True, re-run completed stages
            **kwargs: Additional arguments passed to stage processors
            
        Returns:
            Dict with processing results
        """
        component = self.registry.get_component(component_id)
        if not component:
            return {
                'success': False,
                'error': f'Component {component_id} not found in registry'
            }
        
        component_dir = Path(component['directory'])
        stages_to_run = self.STAGES.copy()
        
        if target_stage:
            if target_stage not in self.STAGES:
                return {
                    'success': False,
                    'error': f'Invalid target stage: {target_stage}'
                }
            stages_to_run = stages_to_run[:self.STAGES.index(target_stage) + 1]
        
        results = {
            'component_id': component_id,
            'stages_processed': [],
            'stages_skipped': [],
            'stages_failed': [],
            'success': True
        }
        
        for stage in stages_to_run:
            stage_status = component['stages'].get(stage, {})
            
            # Skip if already complete (unless force)
            if not force and stage_status.get('status') == 'complete':
                results['stages_skipped'].append({
                    'stage': stage,
                    'reason': 'already complete',
                    'file': stage_status.get('file')
                })
                continue
            
            # Check if stage should be skipped
            if stage_status.get('status') == 'skip':
                results['stages_skipped'].append({
                    'stage': stage,
                    'reason': stage_status.get('reason', 'skipped')
                })
                continue
            
            # Check dependencies
            if not self.processors[stage].check_dependencies(component_id, stage):
                results['stages_failed'].append({
                    'stage': stage,
                    'reason': 'dependencies not met'
                })
                results['success'] = False
                break
            
            # Run stage processor
            print(f"  Processing stage '{stage}' for {component_id}...")
            stage_result = self.processors[stage].process(
                component_id=component_id,
                component_dir=component_dir,
                report=component.get('report'),
                component_name=component.get('component_name'),
                url=component.get('url'),
                **kwargs
            )
            
            if stage_result.get('success'):
                # Update registry
                self.registry.update_stage(component_id, stage, {
                    'status': 'complete',
                    'file': str(stage_result.get('output_file')),
                    'date': datetime.now().isoformat()
                })
                
                results['stages_processed'].append({
                    'stage': stage,
                    'output_file': str(stage_result.get('output_file')),
                    'message': stage_result.get('message', '')
                })
                
                # Refresh component data
                component = self.registry.get_component(component_id)
            else:
                # Check if stage should be skipped (e.g., PDF conversion when no PDF)
                if stage_result.get('skip'):
                    self.registry.update_stage(component_id, stage, {
                        'status': 'skip',
                        'reason': stage_result.get('error', 'skipped')
                    })
                    results['stages_skipped'].append({
                        'stage': stage,
                        'reason': stage_result.get('error', 'skipped')
                    })
                else:
                    results['stages_failed'].append({
                        'stage': stage,
                        'error': stage_result.get('error', 'unknown error')
                    })
                    results['success'] = False
                    break
        
        return results
    
    def get_component_status(self, component_id: str) -> Dict:
        """Get current status of a component."""
        component = self.registry.get_component(component_id)
        if not component:
            return {'error': f'Component {component_id} not found'}
        
        status = {
            'component_id': component_id,
            'report': component['report'],
            'type': component['type'],
            'stages': {}
        }
        
        for stage in self.STAGES:
            stage_info = component['stages'].get(stage, {})
            status['stages'][stage] = {
                'status': stage_info.get('status', 'pending'),
                'file': stage_info.get('file'),
                'date': stage_info.get('date')
            }
        
        return status




