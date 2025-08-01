#!/usr/bin/env python3
"""
Create flat text version of IPCC glossary
"""

import csv
from pathlib import Path
from bs4 import BeautifulSoup

def main():
    input_file = Path("temp", "ipcc_glossary_wordlist.csv")
    output_file = Path("temp", "ipcc_glossary_flat.csv")
    
    print(f"📖 Reading: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
            writer = csv.writer(out_f, delimiter='\t')
            writer.writerow(['term', 'definition', 'link_to_glossary_entry', 'link_to_wikipedia'])
            
            for row in reader:
                term = row['term'].strip()
                html_definition = row['definition'].strip()
                link = row['link_to_glossary_entry'].strip()
                wiki_link = row['link_to_wikipedia'].strip()
                
                # Extract plain text from HTML
                soup = BeautifulSoup(html_definition, 'html.parser')
                flat_definition = soup.get_text().strip()
                
                writer.writerow([term, flat_definition, link, wiki_link])
    
    print(f"✅ Created: {output_file}")
    print("Please check the new file.")

if __name__ == "__main__":
    main() 