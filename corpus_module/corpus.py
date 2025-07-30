"""
Core corpus management functionality.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from collections import defaultdict
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import fitz  # PyMuPDF
from keybert import KeyBERT

logger = logging.getLogger(__name__)

# Constants
DATATABLES_HTML = "datatables.html"
SAVED_CONFIG_INI = "saved_config.ini"
HTML_WITH_IDS = "html_with_ids"
EUPMC_RESULTS_JSON = "eupmc_result.json"
TABLE_HITS_SUFFIX = "table_hits.html"


class AmiCorpus:
    """
    Main corpus management class supporting hierarchical directory structures.
    """

    def __init__(self,
                 topdir: Optional[Union[str, Path]] = None,
                 infiles: Optional[List[Union[str, Path]]] = None,
                 globstr: Optional[str] = None,
                 outfile: Optional[Union[str, Path]] = None,
                 make_descendants: bool = False,
                 mkdir: bool = False,
                 **kwargs):
        """
        Create new corpus with optional input data.
        
        Args:
            topdir: Input directory with files/subdirs as possible corpus components
            infiles: List of files to use (alternative to globstr)
            globstr: Create infiles using globbing under topdir (requires topdir)
            outfile: Output file path
            mkdir: Make topdir if doesn't exist (default=False)
            make_descendants: Makes AmiCorpusContainers for directories on tree
            **kwargs: Dict of per-corpus user-specified properties
        """
        self.topdir = Path(topdir) if topdir else None
        if self.topdir and not self.topdir.is_dir():
            if mkdir:
                self.topdir.mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(f"AmiCorpus() requires valid directory {self.topdir}")

        self.container_by_file = dict()
        # rootnode
        self.ami_container = self.create_corpus_container(
            self.topdir, make_descendants=make_descendants, mkdir=mkdir)
        self.infiles = infiles
        self.outfile = Path(outfile) if outfile else None
        self.globstr = globstr
        self.corpus_queries = dict()
        self.search_html = None
        self.eupmc_results = None
        self._make_infiles()
        self._make_outfile()

        self.make_special(kwargs)

    def __str__(self):
        """String representation of corpus."""
        values = []
        for key in self.corpus_queries.keys():
            value = self.corpus_queries.get(key)
            values.append(value)

        s = f"""AmiCorpus:
topdir:  {self.topdir}
globstr: {self.globstr}
infiles: {len(self.infiles) if self.infiles else 0}
outfile: {self.outfile}
"""
        s += "QUERIES"
        for (key, value) in self.corpus_queries.items():
            s += f"""
            {key}:
            {value.__str__()}
            """
        return s

    def _make_infiles(self):
        """Create infiles list from globstr if not provided."""
        if self.infiles:
            logger.info(f"taking infiles from list")
        else:
            if self.topdir and self.globstr:
                self.infiles = self._posix_glob(f"{self.topdir}/{self.globstr}", recursive=True)
        if self.infiles is None:
            logger.error(f"self.infiles is None")
            return
        logger.info(f"inputting {len(self.infiles)} files")
        return self.infiles

    def create_corpus_container(self, file: Optional[Union[str, Path]], 
                               bib_type: str = "None", make_descendants: bool = False, 
                               mkdir: bool = False):
        """
        Create container as child of self.
        
        Args:
            file: File or dir contained by container
            bib_type: Type of container
            make_descendants: Whether to create descendant containers
            mkdir: Whether to create directory if it doesn't exist
            
        Returns:
            AmiCorpusContainer instance
        """
        if file is None:
            logger.error("Container has no file")
            return None

        container = AmiCorpusContainer(self, file)
        container.bib_type = bib_type
        if not Path(file).exists() and mkdir:
            Path(file).mkdir(parents=True, exist_ok=True)
        if make_descendants:
            self.make_descendants(file)
        return container

    @property
    def root_dir(self):
        """Get root directory of corpus."""
        return self.ami_container.file if self.ami_container else None

    def make_descendants(self, file: Optional[Union[str, Path]] = None):
        """
        Creates AmiCorpusContainers for directory tree.
        
        Args:
            file: Directory to process (defaults to root_dir)
        """
        if file is None:
            file = self.root_dir
        if file is None or not Path(file).is_dir():
            logger.error(f"Cannot make file children for {file}")
            return
        files = self._get_children(file)
        for f in files:
            container = AmiCorpusContainer(self, f)
            container.make_descendants()

    def make_special(self, kwargs: Dict[str, Any]):
        """Manage repository specific functionality."""
        if "eupmc" in kwargs:
            self.eupmc_results = kwargs["eupmc"]

    @classmethod
    def make_datatables(cls, indir: Union[str, Path], outdir: Optional[Union[str, Path]] = None, 
                       outfile_h: Optional[Union[str, Path]] = None):
        """
        Create a JQuery DataTables HTML file from an AmiCorpus.
        
        Args:
            indir: Directory with corpus (normally created by pygetpapers)
            outdir: Output directory for datatables (if omitted uses indir)
            outfile_h: The HTML file created (may be changed)
        """
        if indir is None:
            logger.warning("No indir")
            return
        if outdir is None:
            outdir = indir
        if outfile_h is None:
            outfile_h = Path(outdir) / DATATABLES_HTML
            
        config_ini = Path(indir) / SAVED_CONFIG_INI
        Path(outdir).mkdir(parents=True, exist_ok=True)
        datatables = True
        epmc_infile = Path(indir) / EUPMC_RESULTS_JSON
        
        if epmc_infile.exists():
            cls.read_json_create_write_html_table(
                epmc_infile, outfile_h, wanted_keys=None, datatables=datatables,
                table_id=None, config_ini=config_ini)
            return
            
        # Try alternative filename
        infile = Path(indir) / EUPMC_RESULTS_JSON
        if infile.exists():
            cls.read_json_create_write_html_table(
                infile, outfile_h, wanted_keys=None, datatables=datatables, 
                table_id=None, config_ini=config_ini)
            return

    @classmethod
    def read_json_create_write_html_table(cls, infile: Union[str, Path], outfile_h: Union[str, Path],
                                         wanted_keys: Optional[List[str]] = None, datatables: bool = True,
                                         table_id: Optional[str] = None, config_ini: Optional[Union[str, Path]] = None):
        """
        Read JSON data and create HTML table.
        
        Args:
            infile: Input JSON file
            outfile_h: Output HTML file
            wanted_keys: Keys to include in table
            datatables: Whether to enable DataTables
            table_id: Table ID
            config_ini: Config file path
        """
        # This would need to be implemented based on the original functionality
        # For now, we'll create a basic implementation
        logger.info(f"Creating HTML table from {infile} to {outfile_h}")
        
        # Read JSON data
        with open(infile, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Create simple HTML table
        if datatables:
            from datatables_module import Datatables
            htmlx, tbody = Datatables.create_table(
                labels=list(data[0].keys()) if data else [], 
                table_id=table_id or "corpus_table"
            )
            
            # Add data rows
            for row in data:
                tr = tbody.makeelement("tr")
                for value in row.values():
                    td = tr.makeelement("td")
                    td.text = str(value)
                    tr.append(td)
                tbody.append(tr)
                
            # Write to file
            with open(outfile_h, 'w', encoding='utf-8') as f:
                f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))

    def list_files(self, globstr: str) -> List[Path]:
        """
        Find files in corpus starting at root_dir.
        
        Args:
            globstr: Glob pattern to match files
            
        Returns:
            List of matching file paths
        """
        if globstr and self.root_dir:
            return self._posix_glob(str(self.root_dir / globstr), recursive=True)
        return []

    def create_datatables_html_with_filenames(self, html_glob: str, labels: List[str], 
                                            table_id: str, outpath: Optional[Union[str, Path]] = None, 
                                            debug: bool = True):
        """
        Create DataTables HTML with filenames.
        
        Args:
            html_glob: Glob string to find HTML files
            labels: Column labels
            table_id: Table ID
            outpath: Output path
            debug: Enable debug logging
            
        Returns:
            HTML document
        """
        html_files = sorted(self.list_files(globstr=html_glob))
        
        from datatables_module import Datatables
        self.datables_html, tbody = Datatables._create_html_for_datatables(labels, table_id)

        for html_file in html_files:
            if outpath:
                offset = self._get_relative_path(html_file, Path(outpath).parent, walk_up=True)
            else:
                offset = html_file.name
                
            tr = tbody.makeelement("tr")
            td = tr.makeelement("td")
            a = td.makeelement("a")
            a.attrib["href"] = str(offset)
            a.text = str(offset)
            td.append(a)
            tr.append(td)
            tbody.append(tr)

        if outpath:
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(ET.tostring(self.datables_html, encoding='unicode', pretty_print=True))

        return self.datables_html

    def make_infiles(self, maxfiles: int = 999999999) -> List[Path]:
        """
        Create infiles list from globstr.
        
        Args:
            maxfiles: Maximum number of files to include
            
        Returns:
            List of file paths
        """
        if self.globstr:
            self.infiles = self._posix_glob(self.globstr, recursive=True)[:maxfiles]
        return self.infiles

    def _make_outfile(self):
        """Create output file path if not provided."""
        if not self.outfile:
            pass  # Implementation depends on specific requirements

    def get_or_create_corpus_query(self, query_id: str, phrasefile: Optional[Union[str, Path]] = None,
                                  phrases: Optional[List[str]] = None, outfile: Optional[Union[str, Path]] = None):
        """
        Retrieve query by query_id. If not found, create new one.
        
        Args:
            query_id: Unique ID of query
            phrasefile: File containing phrases
            phrases: List of phrases
            outfile: Output file for results
            
        Returns:
            CorpusQuery instance
        """
        corpus_query = self.corpus_queries.get(query_id)
        if not corpus_query:
            corpus_query = CorpusQuery(
                query_id=query_id,
                phrasefile=phrasefile,
                phrases=phrases,
                outfile=outfile)
            self.corpus_queries[query_id] = corpus_query
            corpus_query.corpus = self

        return corpus_query

    def search_files_with_queries(self, query_ids: Union[str, List[str]], debug: bool = True) -> Dict[str, Any]:
        """
        Run queries. Assumes queries have been loaded and are recallable by ID.
        
        Args:
            query_ids: Single or list of query IDs
            debug: Enable debug logging
            
        Returns:
            Dictionary mapping query IDs to HTML results
        """
        html_by_query_id = dict()
        if isinstance(query_ids, str):
            query_ids = [query_ids]
        elif not isinstance(query_ids, list):
            raise ValueError(f"queries requires id/s as list or str, found {type(query_ids)}")
            
        for query_id in query_ids:
            query = self.corpus_queries.get(query_id)
            if query is None:
                logger.error(f"cannot find query: {query_id}")
                continue
            logger.debug(f"outfile==> {query.outfile}")
            
            # This would need to be implemented based on the search functionality
            # For now, we'll create a placeholder
            logger.info(f"Running query: {query_id}")
            
        return html_by_query_id

    def ingest_files(self, source_dir: Union[str, Path], file_pattern: str = "*", 
                    target_container: str = "files", file_type: str = "unknown") -> List[Path]:
        """
        Ingest files from source directory into corpus using AmiCorpus methods.
        
        Args:
            source_dir: Directory containing files to ingest
            file_pattern: Glob pattern to match files (default: "*" for all files)
            target_container: Name of container to ingest into (default: "files")
            file_type: Type of files being ingested (default: "unknown")
            
        Returns:
            List of paths to ingested files
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_path}")
        
        # Find files matching pattern
        files_to_ingest = list(source_path.glob(file_pattern))
        if not files_to_ingest:
            logger.warning(f"No files found matching pattern '{file_pattern}' in {source_path}")
            return []
        
        # Get or create target container
        target_container_obj = None
        for container in self.ami_container.child_containers:
            if container.file.name == "data":
                for child in container.child_containers:
                    if child.file.name == target_container:
                        target_container_obj = child
                        break
                break
        
        if not target_container_obj:
            # Create data container if it doesn't exist
            data_container = self.ami_container.create_corpus_container("data", bib_type="bagit_data", mkdir=True)
            target_container_obj = data_container.create_corpus_container(target_container, bib_type=file_type, mkdir=True)
        
        # Ingest files
        ingested_files = []
        for source_file in files_to_ingest:
            if source_file.is_file():
                try:
                    # Create document in corpus using AmiCorpus method
                    dest_path = target_container_obj.create_document(source_file.name)
                    
                    # Copy file content
                    import shutil
                    shutil.copy2(source_file, dest_path)
                    
                    ingested_files.append(dest_path)
                    logger.info(f"Ingested: {source_file.name} -> {dest_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to ingest {source_file.name}: {e}")
        
        logger.info(f"Ingestion complete: {len(ingested_files)} files ingested")
        return ingested_files

    def extract_significant_phrases(self, file_pattern: str = "*.pdf", 
                                   min_tfidf_score: float = 0.1,
                                   max_phrases: int = 100,
                                   min_word_length: int = 3) -> List[Dict[str, Any]]:
        """
        Extract significant phrases using TF-IDF analysis.
        
        Args:
            file_pattern: Glob pattern for files to process (e.g., "*.pdf", "*.xml.html")
            min_tfidf_score: Minimum TF-IDF score threshold
            max_phrases: Maximum number of phrases to return
            min_word_length: Minimum word length to consider
            
        Returns:
            List of phrase dictionaries with TF-IDF scores and metadata
        """
        logger.info(f"Extracting significant phrases from files matching '{file_pattern}'")
        
        # Find the files container
        files_container = None
        for container in self.ami_container.child_containers:
            if container.file.name == "data":
                for child in container.child_containers:
                    if child.file.name == "files":
                        files_container = child
                        break
                break
        
        if not files_container:
            raise ValueError("No 'data/files' container found in corpus")
        
        # Get files matching pattern
        files_to_process = list(files_container.file.glob(file_pattern))
        if not files_to_process:
            logger.warning(f"No files found matching pattern '{file_pattern}' in {files_container.file}")
            return []
        
        logger.info(f"Processing {len(files_to_process)} files for TF-IDF analysis")
        
        # Extract text from files
        documents = []
        file_names = []
        
        for file_path in files_to_process:
            try:
                text = self._extract_text_from_file(file_path)
                if text and len(text.strip()) > 0:
                    documents.append(text)
                    file_names.append(file_path.name)
                    logger.debug(f"Extracted text from {file_path.name} ({len(text)} characters)")
                else:
                    logger.warning(f"No text extracted from {file_path.name}")
            except Exception as e:
                logger.error(f"Error extracting text from {file_path.name}: {e}")
                continue
        
        if not documents:
            logger.error("No documents with text content found")
            return []
        
        # Perform TF-IDF analysis
        phrases = self._perform_tfidf_analysis(documents, file_names, min_tfidf_score, 
                                             max_phrases, min_word_length)
        
        logger.info(f"Extracted {len(phrases)} significant phrases")
        return phrases

    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from a file based on its type."""
        if file_path.suffix.lower() == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.html', '.htm', '.xml']:
            return self._extract_text_from_html(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            return self._extract_text_from_text(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return ""

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file using PyMuPDF."""
        try:
            doc = fitz.open(str(file_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""

    def _extract_text_from_html(self, file_path: Path) -> str:
        """Extract text from HTML/XML file."""
        try:
            from lxml import html
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = html.fromstring(content)
            return tree.text_content()
        except Exception as e:
            logger.error(f"Error extracting text from HTML {file_path}: {e}")
            return ""

    def _extract_text_from_text(self, file_path: Path) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error extracting text from text file {file_path}: {e}")
            return ""

    def _perform_tfidf_analysis(self, documents: List[str], file_names: List[str],
                               min_tfidf_score: float, max_phrases: int, 
                               min_word_length: int) -> List[Dict[str, Any]]:
        """Perform TF-IDF analysis on documents."""
        # Custom stop words - combine sklearn's stop words with additional ones
        custom_stop_words = list(ENGLISH_STOP_WORDS)
        custom_stop_words.extend([
            'said', 'will', 'one', 'may', 'would', 'could', 'should',
            # URL artifacts
            'https', 'http', 'www', 'org', 'com', 'edu', 'gov', 'uk', 'us',
            # Common artifacts
            'pdf', 'html', 'xml', 'txt', 'doc', 'docx'
        ])
        
        # Configure TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            lowercase=True,  # Case-insensitive
            stop_words=custom_stop_words,
            min_df=1,  # Include terms that appear in at least 1 document
            max_df=0.95,  # Exclude terms that appear in more than 95% of documents
            token_pattern=r'\b[a-zA-Z]{%d,}\b(?!\.[a-z]{2,})' % min_word_length,  # Words with min_word_length+ chars, exclude file extensions
            ngram_range=(1, 2),  # Single words and bigrams
            max_features=max_phrases * 2  # Get more features than needed for filtering
        )
        
        # Fit and transform documents
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate average TF-IDF scores across all documents
        avg_tfidf_scores = tfidf_matrix.mean(axis=0).A1
        
        # Create phrase list with scores and document information
        phrases = []
        for i, (phrase, score) in enumerate(zip(feature_names, avg_tfidf_scores)):
            if score >= min_tfidf_score:
                # Find which documents contain this phrase
                doc_indices = tfidf_matrix[:, i].nonzero()[0]
                doc_names = [file_names[j] for j in doc_indices]
                
                phrases.append({
                    "phrase": phrase,
                    "tfidf_score": float(score),
                    "frequency": int(tfidf_matrix[:, i].sum()),
                    "documents": doc_names,
                    "wikipedia_url": None,
                    "definition": None
                })
        
        # Sort by TF-IDF score (descending) and limit to max_phrases
        phrases.sort(key=lambda x: x["tfidf_score"], reverse=True)
        phrases = phrases[:max_phrases]
        
        return phrases

    def extract_significant_phrases_keybert(self, file_pattern: str = "*.pdf", 
                                          max_phrases: int = 200,
                                          min_word_length: int = 3,
                                          diversity: float = 0.7) -> List[Dict[str, Any]]:
        """
        Extract significant phrases using KeyBERT (BERT-based keyphrase extraction).
        
        Args:
            file_pattern: Glob pattern for files to process (e.g., "*.pdf", "*.xml.html")
            max_phrases: Maximum number of phrases to return
            min_word_length: Minimum word length to consider
            diversity: Diversity parameter for KeyBERT (0.0-1.0, higher = more diverse)
            
        Returns:
            List of phrase dictionaries with KeyBERT scores and metadata
        """
        logger.info(f"Extracting significant phrases using KeyBERT from files matching '{file_pattern}'")
        
        # Find the files container
        files_container = None
        for container in self.ami_container.child_containers:
            if container.file.name == "data":
                for child in container.child_containers:
                    if child.file.name == "files":
                        files_container = child
                        break
                break
        
        if not files_container:
            raise ValueError("No 'data/files' container found in corpus")
        
        # Get files matching pattern
        files_to_process = list(files_container.file.glob(file_pattern))
        if not files_to_process:
            logger.warning(f"No files found matching pattern '{file_pattern}' in {files_container.file}")
            return []
        
        logger.info(f"Processing {len(files_to_process)} files for KeyBERT analysis")
        
        # Extract text from files
        documents = []
        file_names = []
        
        for file_path in files_to_process:
            try:
                text = self._extract_text_from_file(file_path)
                if text and len(text.strip()) > 0:
                    documents.append(text)
                    file_names.append(file_path.name)
                    logger.debug(f"Extracted text from {file_path.name} ({len(text)} characters)")
                else:
                    logger.warning(f"No text extracted from {file_path.name}")
            except Exception as e:
                logger.error(f"Error extracting text from {file_path.name}: {e}")
                continue
        
        if not documents:
            logger.error("No documents with text content found")
            return []
        
        # Perform KeyBERT analysis
        phrases = self._perform_keybert_analysis(documents, file_names, max_phrases, 
                                               min_word_length, diversity)
        
        logger.info(f"Extracted {len(phrases)} significant phrases using KeyBERT")
        return phrases

    def _perform_keybert_analysis(self, documents: List[str], file_names: List[str],
                                max_phrases: int, min_word_length: int, 
                                diversity: float) -> List[Dict[str, Any]]:
        """Perform KeyBERT analysis on documents."""
        # Initialize KeyBERT
        kw_model = KeyBERT()
        
        # Combine all documents for analysis
        combined_text = " ".join(documents)
        
        # Extract keyphrases using KeyBERT
        keyphrases = kw_model.extract_keywords(
            combined_text,
            keyphrase_ngram_range=(1, 2),  # Single words and bigrams
            stop_words='english',
            use_maxsum=True,  # Use MaxSum algorithm for diversity
            nr_candidates=max_phrases * 2,  # Get more candidates than needed
            diversity=diversity
        )
        
        # Create phrase list with scores and document information
        phrases = []
        for phrase, score in keyphrases:
            # Filter by minimum word length
            words = phrase.split()
            if all(len(word) >= min_word_length for word in words):
                # Find which documents contain this phrase (case-insensitive)
                doc_names = []
                for i, doc in enumerate(documents):
                    if phrase.lower() in doc.lower():
                        doc_names.append(file_names[i])
                
                phrases.append({
                    "phrase": phrase,
                    "keybert_score": float(score),
                    "frequency": len(doc_names),
                    "documents": doc_names,
                    "wikipedia_url": None,
                    "definition": None
                })
        
        return phrases

    # Utility methods
    def _posix_glob(self, pattern: str, recursive: bool = False) -> List[Path]:
        """Glob files using POSIX-style patterns."""
        return list(Path(".").glob(pattern))

    def _get_children(self, directory: Union[str, Path]) -> List[Path]:
        """Get child files/directories of a directory."""
        return list(Path(directory).iterdir())

    def _get_relative_path(self, file_path: Path, base_path: Path, walk_up: bool = False) -> str:
        """Get relative path from base path."""
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return str(file_path)


class AmiCorpusContainer:
    """
    Container for corpus components (files or directories).
    """

    def __init__(self, ami_corpus: AmiCorpus, file: Union[str, Path], 
                 bib_type: str = "unknown", mkdir: bool = False, exist_ok: bool = True):
        """
        Create corpus container for directory-structured corpus.
        
        Args:
            ami_corpus: Corpus to which this belongs
            file: File/directory on filesystem
            bib_type: Type of container (e.g., report)
            mkdir: Whether to create directory
            exist_ok: Whether to allow existing directory
        """
        if not isinstance(ami_corpus, AmiCorpus):
            raise ValueError(f"ami_corpus has wrong type {type(ami_corpus)}")
            
        self.ami_corpus = ami_corpus
        self.file = Path(file)
        self.ami_corpus.container_by_file[self.file] = self
        
        if not file:
            logger.error(f"No file argument")
            return None
            
        self.bib_type = bib_type
        self.child_container_list = []
        self.child_document_list = []

    @property
    def child_containers(self) -> List['AmiCorpusContainer']:
        """Get child containers."""
        child_containers = []
        if self.ami_corpus and self.file and self.file.is_dir():
            child_nodes = self.ami_corpus._get_children(self.file)
            for child_node in child_nodes:
                child_container = AmiCorpusContainer(self.ami_corpus, child_node)
                child_container.bib_type = "" if child_node.is_dir() else "file"
                child_containers.append(child_container)
        return child_containers

    def create_corpus_container(self, filename: str, bib_type: str = "unknown", 
                               make_descendants: bool = False, mkdir: bool = False):
        """
        Create a child container and optionally its actual directory.
        
        Args:
            filename: Name of the container
            bib_type: Type of container
            make_descendants: Whether to create descendants
            mkdir: Whether to create directory
            
        Returns:
            AmiCorpusContainer instance
        """
        if not filename:
            logger.error("filename is None")
            return None
            
        path = self.file / filename
        if mkdir and not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        else:
            if not path.is_dir():
                logger.error(f"{path} exists but is not a directory")
                return None
                
        corpus_container = AmiCorpusContainer(self.ami_corpus, path, bib_type=bib_type, mkdir=mkdir)
        self.child_container_list.append(corpus_container)
        return corpus_container

    def create_document(self, filename: str, text: Optional[str] = None, type: str = "unknown") -> Path:
        """
        Create document file with name and self as parent.
        
        Args:
            filename: Name of the document
            text: Content of the document
            type: Type of document
            
        Returns:
            Path to created document
        """
        document_file = self.file / filename
        document_file.touch()
        if text:
            with open(document_file, "w", encoding="UTF-8") as f:
                f.write(text)

        self.child_document_list.append(document_file)
        return document_file

    def make_descendants(self):
        """Create descendant containers if this is a directory."""
        if self.file and self.file.is_dir():
            self.ami_corpus.make_descendants(self.file) 