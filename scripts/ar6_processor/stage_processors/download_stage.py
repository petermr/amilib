"""Download stage processor - downloads components from IPCC website."""
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from test.ipcc_classes import IPCC
from scripts.ar6_processor.stage_processors.base_stage import BaseStage


class DownloadStage(BaseStage):
    """Downloads components from IPCC website."""
    
    def process(self, component_id: str, component_dir: Path, **kwargs) -> Dict:
        """
        Download component from IPCC website.
        
        Args:
            component_id: Component ID (e.g., 'wg1-chapter01')
            component_dir: Output directory
            **kwargs: Additional args (report, component_name, url)
        """
        component = self.registry.get_component(component_id)
        if not component:
            return {'success': False, 'error': f'Component {component_id} not found'}
        
        report = kwargs.get('report') or component['report']
        component_name = kwargs.get('component_name') or component_id.split('-', 1)[1]
        url = kwargs.get('url') or component.get('url')
        
        if not url:
            # Construct URL from report and component name
            from test.ipcc_constants import WG1_URL, WG2_URL, WG3_URL, SYR_URL
            base_urls = {
                'wg1': WG1_URL,
                'wg2': WG2_URL,
                'wg3': WG3_URL,
                'syr': SYR_URL
            }
            base_url = base_urls.get(report)
            if not base_url:
                return {'success': False, 'error': f'Unknown report: {report}'}
            
            # Construct URL based on component type
            if component['type'] == 'chapter':
                url = f"{base_url}chapter/{component_name}/"
            elif component['type'] == 'spm':
                url = f"{base_url}downloads/report/IPCC_AR6_{report.upper()}_SPM.pdf"
            elif component['type'] == 'ts':
                url = f"{base_url}downloads/report/IPCC_AR6_{report.upper()}_TS.pdf"
            elif component['type'] == 'annex':
                # Annex URLs vary, try common patterns
                url = f"{base_url}downloads/report/IPCC_AR6_{report.upper()}_{component_name}.pdf"
        
        component_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use existing IPCC download method
            IPCC.download_save_chapter(
                report=report,
                chap=component_name,
                wg_url=url,
                outdir=component_dir.parent,
                sleep=1
            )
            
            # Check if file was downloaded
            raw_files = list(component_dir.glob("gatsby_raw.html")) + \
                       list(component_dir.glob("wordpress_raw.html")) + \
                       list(component_dir.glob("*.pdf"))
            
            if raw_files:
                return {
                    'success': True,
                    'output_file': raw_files[0],
                    'message': f'Downloaded to {raw_files[0]}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Download completed but no output file found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }





