"""Base class for stage processors."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class BaseStage(ABC):
    """Base class for all stage processors."""
    
    def __init__(self, registry):
        """
        Initialize stage processor.
        
        Args:
            registry: ComponentRegistry instance
        """
        self.registry = registry
    
    @abstractmethod
    def process(self, component_id: str, component_dir: Path, **kwargs) -> Dict:
        """
        Process a component through this stage.
        
        Args:
            component_id: ID of component to process
            component_dir: Directory containing component files
            **kwargs: Additional stage-specific arguments
            
        Returns:
            Dict with 'success' (bool), 'output_file' (Path), 'error' (str if failed)
        """
        pass
    
    def check_dependencies(self, component_id: str, stage: str) -> bool:
        """Check if dependencies for this stage are met."""
        component = self.registry.get_component(component_id)
        if not component:
            return False
        
        # Define stage dependencies
        dependencies = {
            'pdf_convert': ['download'],
            'clean': ['download', 'pdf_convert'],
            'structure': ['clean'],
            'add_ids': ['structure']
        }
        
        required_stages = dependencies.get(stage, [])
        
        for req_stage in required_stages:
            stage_status = component['stages'].get(req_stage, {})
            if stage_status.get('status') != 'complete':
                return False
        
        return True




