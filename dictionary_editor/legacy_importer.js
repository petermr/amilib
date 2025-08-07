/**
 * Legacy Dictionary Importer
 * 
 * This module handles importing legacy XML dictionaries and converting them
 * to the new JSON format used by the dictionary editor.
 * 
 * Supported formats:
 * - XML dictionaries (amilib format)
 * - HTML dictionaries (with role="ami_dictionary")
 * - Plain text word lists
 * - CSV word lists
 */

class LegacyDictionaryImporter {
    constructor() {
        this.supportedFormats = {
            'xml': this.parseXMLDictionary,
            'html': this.parseHTMLDictionary,
            'txt': this.parseTextDictionary,
            'csv': this.parseCSVDictionary
        };
    }

    /**
     * Main import function - detects format and parses accordingly
     * @param {File} file - The file to import
     * @param {string} filename - Optional filename for metadata
     * @returns {Promise<Object>} - Parsed dictionary in JSON format
     */
    async importDictionary(file, filename = null) {
        const extension = this.getFileExtension(file.name);
        const parser = this.supportedFormats[extension];
        
        if (!parser) {
            throw new Error(`Unsupported file format: ${extension}`);
        }

        try {
            const content = await this.readFileAsText(file);
            const dictionary = await parser.call(this, content, filename || file.name);
            return this.validateAndEnhanceDictionary(dictionary);
        } catch (error) {
            throw new Error(`Failed to import dictionary: ${error.message}`);
        }
    }

    /**
     * Parse XML dictionary (amilib format)
     * @param {string} content - XML content
     * @param {string} filename - Original filename
     * @returns {Object} - Parsed dictionary
     */
    parseXMLDictionary(content, filename) {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(content, 'text/xml');
        
        // Check for parsing errors
        const parseError = xmlDoc.querySelector('parsererror');
        if (parseError) {
            throw new Error('Invalid XML format');
        }

        const dictionary = xmlDoc.querySelector('dictionary');
        if (!dictionary) {
            throw new Error('No dictionary element found in XML');
        }

        // Extract metadata
        const metadata = this.extractXMLMetadata(dictionary, filename);
        
        // Extract entries
        const entries = this.extractXMLEntries(dictionary);

        return {
            metadata,
            entries
        };
    }

    /**
     * Parse HTML dictionary (with role="ami_dictionary")
     * @param {string} content - HTML content
     * @param {string} filename - Original filename
     * @returns {Object} - Parsed dictionary
     */
    parseHTMLDictionary(content, filename) {
        const parser = new DOMParser();
        const htmlDoc = parser.parseFromString(content, 'text/html');
        
        const dictionaryDiv = htmlDoc.querySelector('div[role="ami_dictionary"]');
        if (!dictionaryDiv) {
            throw new Error('No dictionary div with role="ami_dictionary" found');
        }

        // Extract metadata
        const metadata = this.extractHTMLMetadata(dictionaryDiv, filename);
        
        // Extract entries
        const entries = this.extractHTMLEntries(dictionaryDiv);

        return {
            metadata,
            entries
        };
    }

    /**
     * Parse plain text dictionary (one word per line)
     * @param {string} content - Text content
     * @param {string} filename - Original filename
     * @returns {Object} - Parsed dictionary
     */
    parseTextDictionary(content, filename) {
        const lines = content.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0 && !line.startsWith('#'));

        const entries = lines.map((term, index) => ({
            id: `entry_${index + 1}`,
            term: term,
            definition: `Definition for ${term}`,
            description: '',
            synonyms: [],
            examples: [],
            category: '',
            tags: [],
            references: [],
            wikidata_id: '',
            wikipedia_url: ''
        }));

        const metadata = {
            title: this.extractTitleFromFilename(filename),
            filename: filename,
            version: '1.0.0',
            description: `Imported from text file: ${filename}`,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            author: 'Legacy Importer',
            language: 'en',
            source_format: 'text'
        };

        return {
            metadata,
            entries
        };
    }

    /**
     * Parse CSV dictionary
     * @param {string} content - CSV content
     * @param {string} filename - Original filename
     * @returns {Object} - Parsed dictionary
     */
    parseCSVDictionary(content, filename) {
        const lines = content.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0);

        if (lines.length === 0) {
            throw new Error('Empty CSV file');
        }

        // Parse CSV (simple comma-separated, no escaping for now)
        const entries = [];
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const entry = {
                id: `entry_${i}`,
                term: '',
                definition: '',
                description: '',
                synonyms: [],
                examples: [],
                category: '',
                tags: [],
                references: [],
                wikidata_id: '',
                wikipedia_url: ''
            };

            // Map CSV columns to entry fields
            headers.forEach((header, index) => {
                const value = values[index] || '';
                switch (header) {
                    case 'term':
                    case 'word':
                    case 'name':
                        entry.term = value;
                        break;
                    case 'definition':
                    case 'def':
                    case 'description':
                        entry.definition = value;
                        break;
                    case 'synonyms':
                        entry.synonyms = value ? value.split(';').map(s => s.trim()) : [];
                        break;
                    case 'category':
                        entry.category = value;
                        break;
                    case 'tags':
                        entry.tags = value ? value.split(';').map(s => s.trim()) : [];
                        break;
                    case 'wikidata_id':
                    case 'wikidata':
                        entry.wikidata_id = value;
                        break;
                    case 'wikipedia_url':
                    case 'wikipedia':
                        entry.wikipedia_url = value;
                        break;
                }
            });

            if (entry.term) {
                entries.push(entry);
            }
        }

        const metadata = {
            title: this.extractTitleFromFilename(filename),
            filename: filename,
            version: '1.0.0',
            description: `Imported from CSV file: ${filename}`,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            author: 'Legacy Importer',
            language: 'en',
            source_format: 'csv'
        };

        return {
            metadata,
            entries
        };
    }

    /**
     * Extract metadata from XML dictionary
     * @param {Element} dictionary - Dictionary element
     * @param {string} filename - Original filename
     * @returns {Object} - Metadata object
     */
    extractXMLMetadata(dictionary, filename) {
        const title = dictionary.getAttribute('title') || this.extractTitleFromFilename(filename);
        const version = dictionary.getAttribute('version') || '1.0.0';
        
        // Look for desc element
        const descElement = dictionary.querySelector('desc');
        const description = descElement ? descElement.textContent : `Imported from XML: ${filename}`;

        return {
            title: title,
            filename: filename,
            version: version,
            description: description,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            author: 'Legacy Importer',
            language: 'en',
            source_format: 'xml'
        };
    }

    /**
     * Extract entries from XML dictionary
     * @param {Element} dictionary - Dictionary element
     * @returns {Array} - Array of entry objects
     */
    extractXMLEntries(dictionary) {
        const entryElements = dictionary.querySelectorAll('entry');
        const entries = [];

        entryElements.forEach((entryElement, index) => {
            const entry = {
                id: `entry_${index + 1}`,
                term: entryElement.getAttribute('term') || entryElement.getAttribute('name') || '',
                definition: '',
                description: '',
                synonyms: [],
                examples: [],
                category: '',
                tags: [],
                references: [],
                wikidata_id: '',
                wikipedia_url: ''
            };

            // Extract additional attributes
            if (entryElement.getAttribute('wikidataID')) {
                entry.wikidata_id = entryElement.getAttribute('wikidataID');
            }
            if (entryElement.getAttribute('wikidataURL')) {
                entry.wikipedia_url = entryElement.getAttribute('wikidataURL');
            }

            // Extract child elements
            const descElement = entryElement.querySelector('desc');
            if (descElement) {
                entry.description = descElement.textContent;
            }

            const definitionElement = entryElement.querySelector('definition');
            if (definitionElement) {
                entry.definition = definitionElement.textContent;
            }

            // Extract synonyms from raw elements
            const rawElements = entryElement.querySelectorAll('raw');
            rawElements.forEach(raw => {
                if (raw.getAttribute('type') === 'synonym') {
                    entry.synonyms.push(raw.textContent);
                }
            });

            // Only add entries with terms
            if (entry.term) {
                entries.push(entry);
            }
        });

        return entries;
    }

    /**
     * Extract metadata from HTML dictionary
     * @param {Element} dictionaryDiv - Dictionary div element
     * @param {string} filename - Original filename
     * @returns {Object} - Metadata object
     */
    extractHTMLMetadata(dictionaryDiv, filename) {
        const title = dictionaryDiv.getAttribute('title') || this.extractTitleFromFilename(filename);
        
        return {
            title: title,
            filename: filename,
            version: '1.0.0',
            description: `Imported from HTML: ${filename}`,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            author: 'Legacy Importer',
            language: 'en',
            source_format: 'html'
        };
    }

    /**
     * Extract entries from HTML dictionary
     * @param {Element} dictionaryDiv - Dictionary div element
     * @returns {Array} - Array of entry objects
     */
    extractHTMLEntries(dictionaryDiv) {
        const entryElements = dictionaryDiv.querySelectorAll('div[role="ami_entry"]');
        const entries = [];

        entryElements.forEach((entryElement, index) => {
            const entry = {
                id: entryElement.getAttribute('id') || `entry_${index + 1}`,
                term: '',
                definition: '',
                description: '',
                synonyms: [],
                examples: [],
                category: '',
                tags: [],
                references: [],
                wikidata_id: '',
                wikipedia_url: ''
            };

            // Extract term from the specific HTML structure
            // Look for pattern: <span>Term:</span><span>actual_term</span>
            const termSpans = entryElement.querySelectorAll('span');
            for (let i = 0; i < termSpans.length - 1; i++) {
                if (termSpans[i].textContent.trim() === 'Term:') {
                    entry.term = termSpans[i + 1].textContent.trim();
                    break;
                }
            }

            // If term not found in spans, try alternative patterns
            if (!entry.term) {
                // Try to find term in any span that might contain it
                const allSpans = entryElement.querySelectorAll('span');
                for (const span of allSpans) {
                    const text = span.textContent.trim();
                    if (text && text !== 'Term:' && !text.includes('Term:')) {
                        entry.term = text;
                        break;
                    }
                }
            }

            // Extract definition from paragraph with class "wpage_first_para"
            const definitionPara = entryElement.querySelector('p.wpage_first_para');
            if (definitionPara) {
                entry.definition = definitionPara.textContent.trim();
                entry.description = definitionPara.innerHTML; // Keep HTML for rich content
            } else {
                // Fallback: extract all text content excluding the term
                const textContent = entryElement.textContent.trim();
                if (textContent && textContent !== entry.term) {
                    entry.description = textContent;
                    entry.definition = textContent;
                }
            }

            // Only add entries with terms
            if (entry.term) {
                entries.push(entry);
            }
        });

        return entries;
    }

    /**
     * Validate and enhance imported dictionary
     * @param {Object} dictionary - Raw dictionary object
     * @returns {Object} - Enhanced dictionary
     */
    validateAndEnhanceDictionary(dictionary) {
        // Ensure required fields exist
        if (!dictionary.metadata) {
            dictionary.metadata = {};
        }
        if (!dictionary.entries) {
            dictionary.entries = [];
        }

        // Set default metadata if missing
        const metadata = dictionary.metadata;
        if (!metadata.title) {
            metadata.title = 'Imported Dictionary';
        }
        if (!metadata.version) {
            metadata.version = '1.0.0';
        }
        if (!metadata.created) {
            metadata.created = new Date().toISOString();
        }
        metadata.modified = new Date().toISOString();

        // Validate and enhance entries
        dictionary.entries = dictionary.entries.map((entry, index) => {
            // Ensure entry has required fields
            if (!entry.id) {
                entry.id = `entry_${index + 1}`;
            }
            if (!entry.term) {
                entry.term = `Entry ${index + 1}`;
            }
            if (!entry.definition) {
                entry.definition = `Definition for ${entry.term}`;
            }

            // Ensure arrays exist
            if (!Array.isArray(entry.synonyms)) entry.synonyms = [];
            if (!Array.isArray(entry.examples)) entry.examples = [];
            if (!Array.isArray(entry.tags)) entry.tags = [];
            if (!Array.isArray(entry.references)) entry.references = [];

            // Ensure string fields exist
            if (!entry.description) entry.description = '';
            if (!entry.category) entry.category = '';
            if (!entry.wikidata_id) entry.wikidata_id = '';
            if (!entry.wikipedia_url) entry.wikipedia_url = '';

            return entry;
        });

        return dictionary;
    }

    /**
     * Extract title from filename
     * @param {string} filename - Original filename
     * @returns {string} - Extracted title
     */
    extractTitleFromFilename(filename) {
        if (!filename) return 'Imported Dictionary';
        
        // Remove extension and convert to title case
        const name = filename.replace(/\.[^/.]+$/, '');
        return name
            .replace(/[_-]/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Get file extension
     * @param {string} filename - Filename
     * @returns {string} - File extension
     */
    getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    /**
     * Read file as text
     * @param {File} file - File to read
     * @returns {Promise<string>} - File content
     */
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    /**
     * Get supported file extensions
     * @returns {Array} - Array of supported extensions
     */
    getSupportedExtensions() {
        return Object.keys(this.supportedFormats);
    }

    /**
     * Get file filter string for file input
     * @returns {string} - File filter string
     */
    getFileFilter() {
        const extensions = this.getSupportedExtensions();
        return extensions.map(ext => `.${ext}`).join(',');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LegacyDictionaryImporter;
} else {
    // Browser environment
    window.LegacyDictionaryImporter = LegacyDictionaryImporter;
}
