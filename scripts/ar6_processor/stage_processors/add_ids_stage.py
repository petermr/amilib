"""Add IDs stage processor - adds semantic IDs to HTML."""
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from test.ipcc_classes import IPCCGatsby, IPCCWordpress, IPCCPublisherTool
from scripts.ar6_processor.stage_processors.base_stage import BaseStage


class AddIDsStage(BaseStage):
    """Adds semantic IDs to paragraphs and sections."""
    
    def process(self, component_id: str, component_dir: Path, **kwargs) -> Dict:
        """
        Add semantic IDs to HTML.
        
        Args:
            component_id: Component ID
            component_dir: Directory containing structured HTML
            **kwargs: Additional args
        """
        component = self.registry.get_component(component_id)
        if not component:
            return {'success': False, 'error': f'Component {component_id} not found'}
        
        report = component['report']
        
        # Find cleaned file
        cleaned_files = list(component_dir.glob("de_*.html"))
        if not cleaned_files:
            return {
                'success': False,
                'error': 'No cleaned HTML file found for ID addition'
            }
        
        cleaned_file = cleaned_files[0]
        
        # Determine publisher type
        publisher: IPCCPublisherTool
        if report in ['sr15', 'srocc', 'srccl']:
            publisher = IPCCWordpress()
        else:
            publisher = IPCCGatsby()
        
        try:
            # Add IDs using existing method
            html_ids_file, idfile, parafile = publisher.add_ids(
                de_gatsby_file=str(cleaned_file),
                outdir=str(component_dir),
                assert_exist=False,
                min_id_sizs=10,
                min_para_size=10
            )
            
            return {
                'success': True,
                'output_file': Path(html_ids_file),
                'id_list_file': Path(idfile),
                'para_list_file': Path(parafile),
                'message': f'IDs added: {html_ids_file}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'ID addition failed: {str(e)}'
            }




