"""
Component Registry for AR6 Processing

Tracks AR6 components and their processing stage status.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.resources import Resources
from test.ipcc_constants import WG1_URL, WG2_URL, WG3_URL, SYR_URL


class ComponentRegistry:
    """Registry of AR6 components and their processing status."""
    
    STAGES = ['download', 'pdf_convert', 'clean', 'structure', 'add_ids']
    
    def __init__(self, registry_file: Optional[Path] = None):
        """
        Initialize registry.
        
        Args:
            registry_file: Path to registry JSON file. If None, uses default location.
        """
        if registry_file is None:
            registry_file = Path(Resources.TEMP_DIR, "ar6_processor", "registry.json")
        
        self.registry_file = registry_file
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.components: Dict[str, Dict] = {}
        self.load()
    
    def load(self):
        """Load registry from file."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                self.components = data.get('components', {})
        else:
            self.components = {}
            self._initialize_from_filesystem()
    
    def save(self):
        """Save registry to file."""
        data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'components': self.components
        }
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_from_filesystem(self):
        """Scan filesystem and initialize registry with existing components."""
        base_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")
        
        if not base_dir.exists():
            return
        
        # Scan for existing components
        for report_dir in base_dir.iterdir():
            if not report_dir.is_dir():
                continue
            
            report = report_dir.name
            
            # Scan chapters
            for chapter_dir in report_dir.glob("Chapter*"):
                component_id = f"{report}-{chapter_dir.name.lower()}"
                self._register_from_directory(component_id, report, "chapter", chapter_dir)
            
            # Scan SPM/TS
            for section_type in ["summary-for-policymakers", "technical-summary"]:
                section_dir = report_dir / section_type
                if section_dir.exists():
                    component_id = f"{report}-{section_type.replace('-', '_')}"
                    self._register_from_directory(component_id, report, section_type.replace('-', '_'), section_dir)
            
            # Scan annexes
            for annex_dir in report_dir.glob("annex-*"):
                component_id = f"{report}-{annex_dir.name}"
                annex_type = "glossary" if "glossary" in annex_dir.name else "acronyms"
                self._register_from_directory(component_id, report, "annex", annex_dir, annex_type=annex_type)
            
            # Scan cross-chapter boxes (WG2)
            if report == "wg2":
                for ccp_dir in report_dir.glob("CrossChapters/ccp*"):
                    component_id = f"{report}-{ccp_dir.name}"
                    self._register_from_directory(component_id, report, "cross_chapter_box", ccp_dir)
    
    def _register_from_directory(self, component_id: str, report: str, component_type: str, 
                                 directory: Path, annex_type: Optional[str] = None):
        """Register a component from filesystem directory."""
        if component_id in self.components:
            return  # Already registered
        
        component = {
            'id': component_id,
            'report': report,
            'type': component_type,
            'directory': str(directory),
            'stages': {}
        }
        
        if annex_type:
            component['annex_type'] = annex_type
        
        # Check stage completion
        for stage in self.STAGES:
            status = self._check_stage_status(stage, directory)
            component['stages'][stage] = status
        
        self.components[component_id] = component
    
    def _check_stage_status(self, stage: str, directory: Path) -> Dict:
        """Check if a stage has been completed."""
        status = {
            'status': 'pending',
            'file': None,
            'date': None
        }
        
        if stage == 'download':
            # Check for raw files
            for pattern in ['gatsby_raw.html', 'wordpress_raw.html', '*.pdf']:
                files = list(directory.glob(pattern))
                if files:
                    status['status'] = 'complete'
                    status['file'] = str(files[0])
                    if files[0].stat().st_mtime:
                        status['date'] = datetime.fromtimestamp(files[0].stat().st_mtime).isoformat()
                    break
        
        elif stage == 'pdf_convert':
            # Check for PDF conversion output
            if list(directory.glob("total_pages.html")) or list(directory.glob("page_*.html")):
                status['status'] = 'complete'
                status['file'] = str(list(directory.glob("total_pages.html"))[0] if list(directory.glob("total_pages.html")) else list(directory.glob("page_*.html"))[0])
            elif not list(directory.glob("*.pdf")):
                # No PDF source, skip this stage
                status['status'] = 'skip'
                status['reason'] = 'No PDF source'
        
        elif stage == 'clean':
            # Check for cleaned files
            for pattern in ['de_gatsby.html', 'de_wordpress.html']:
                files = list(directory.glob(pattern))
                if files:
                    status['status'] = 'complete'
                    status['file'] = str(files[0])
                    if files[0].stat().st_mtime:
                        status['date'] = datetime.fromtimestamp(files[0].stat().st_mtime).isoformat()
                    break
        
        elif stage == 'structure':
            # Check if cleaned file exists (structure is implicit in clean stage for now)
            if list(directory.glob("de_*.html")):
                status['status'] = 'complete'
                status['file'] = str(list(directory.glob("de_*.html"))[0])
            else:
                status['status'] = 'pending'
        
        elif stage == 'add_ids':
            # Check for html_with_ids.html
            id_file = directory / "html_with_ids.html"
            if id_file.exists():
                status['status'] = 'complete'
                status['file'] = str(id_file)
                if id_file.stat().st_mtime:
                    status['date'] = datetime.fromtimestamp(id_file.stat().st_mtime).isoformat()
        
        return status
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get component by ID."""
        return self.components.get(component_id)
    
    def get_components(self, report: Optional[str] = None, 
                      component_type: Optional[str] = None) -> List[Dict]:
        """Get filtered list of components."""
        components = list(self.components.values())
        
        if report:
            components = [c for c in components if c['report'] == report]
        
        if component_type:
            components = [c for c in components if c['type'] == component_type]
        
        return components
    
    def update_stage(self, component_id: str, stage: str, status: Dict):
        """Update stage status for a component."""
        if component_id not in self.components:
            raise ValueError(f"Component {component_id} not found")
        
        if stage not in self.STAGES:
            raise ValueError(f"Invalid stage: {stage}")
        
        self.components[component_id]['stages'][stage] = status
        self.save()
    
    def add_component(self, component_id: str, report: str, component_type: str,
                     directory: Path, url: Optional[str] = None, **kwargs):
        """Add a new component to registry."""
        component = {
            'id': component_id,
            'report': report,
            'type': component_type,
            'directory': str(directory),
            'stages': {}
        }
        
        if url:
            component['url'] = url
        
        for key, value in kwargs.items():
            component[key] = value
        
        # Initialize all stages as pending
        for stage in self.STAGES:
            component['stages'][stage] = {'status': 'pending'}
        
        self.components[component_id] = component
        self.save()
    
    def get_missing_components(self) -> List[Dict]:
        """Get list of components that need to be added to registry."""
        # This would scan the manifest and compare with registry
        # For now, return empty list
        return []




