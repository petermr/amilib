"""Clean stage processor - removes navigation and unnecessary markup."""
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from test.ipcc_classes import IPCCGatsby, IPCCWordpress, IPCCPublisherTool
from scripts.ar6_processor.stage_processors.base_stage import BaseStage


class CleanStage(BaseStage):
    """Cleans HTML by removing navigation and unnecessary markup."""
    
    def process(self, component_id: str, component_dir: Path, **kwargs) -> Dict:
        """
        Clean HTML file.
        
        Args:
            component_id: Component ID
            component_dir: Directory containing raw HTML
            **kwargs: Additional args
        """
        component = self.registry.get_component(component_id)
        if not component:
            return {'success': False, 'error': f'Component {component_id} not found'}
        
        report = component['report']
        
        # Find input file
        raw_files = list(component_dir.glob("gatsby_raw.html")) + \
                   list(component_dir.glob("wordpress_raw.html")) + \
                   list(component_dir.glob("total_pages.html"))
        
        if not raw_files:
            return {
                'success': False,
                'error': 'No raw HTML file found for cleaning'
            }
        
        raw_file = raw_files[0]
        
        # Determine publisher type
        publisher: IPCCPublisherTool
        if report in ['sr15', 'srocc', 'srccl']:
            publisher = IPCCWordpress()
        else:
            publisher = IPCCGatsby()
        
        try:
            # Clean the HTML
            html_elem = publisher.remove_unnecessary_markup(str(raw_file))
            
            if html_elem is None:
                return {
                    'success': False,
                    'error': 'Cleaning produced None HTML element'
                }
            
            # Write cleaned file
            cleaned_filename = f"de_{publisher.base_filename}.html"
            output_file = component_dir / cleaned_filename
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            from amilib.ami_html import HtmlLib
            HtmlLib.write_html_file(html_elem, str(output_file), debug=True)
            
            return {
                'success': True,
                'output_file': output_file,
                'message': f'Cleaned HTML written to {output_file}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Cleaning failed: {str(e)}'
            }




