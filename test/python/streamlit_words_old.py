# Sure! Below is a sample Streamlit code that provides a file browser to select a directory, locates *.txt files, processes them using your command-line application extract_words, and displays the contents of the output file.
import logging
import os
import re
import streamlit as st
from collections import Counter
from pathlib import Path

from amilib.ami_html import HtmlLib, HtmlUtil

logger = logging.getLogger()

ONE_OR_MORE_CAPITALS = r'\b(?:[A-Z][a-z]*(?:\s+(?:and|of|in|the|for|to|with|by|on)\s+[A-Z][a-z]*)*)+\b'
stopwords = {[
    "Although",
    "An",
    "As",
    "Box",
    "By",
    "Chapter",
    "Each",
    "Figure",
    "For",
    "From",
    "In",
    "It",
    "Journal",
    "Many",
    "No",
    "On",
    "Other",
    "Section",
    "Since",
    "Such",
    "Some",
    "Table",
    "The",
    "There",
    "They",
    "This",
    "To",
    "We",
    "What",
    "With",
]}

class WordFinder():

    def __init__(self):
        self.pattern = ONE_OR_MORE_CAPITALS
        self.words = []

    @staticmethod
    def extract_words_from_txt_file(txt_file):
        # Call the command-line application
        if not Path(txt_file).exists():
            raise FileNotFoundError(txt_file)
        with open(txt_file, "r") as f:
            lines = f.readlines()

        words = match_words(lines)
        return words


    def match_words(self, lines):
        allmatches = []
        for line in lines:
            matchez = re.findall(self.pattern, line)
            allmatches.extend(matchez)
        return allmatches


    def remove_stop_words(words):
        words = [w for w in words if len(w) > 1]
        words = [w for w in words if w not in stopwords]
        return words


    def extract_words_from_html_file(html_file, xpath=".//p"):
        allmatches = []
        if not Path(html_file).exists():
            logger.error(f"file not found {html_file}")
            return allmatches
        htmlx = HtmlLib.parse_html(html_file)
        body = HtmlLib.get_body(htmlx)
        paras = body.xpath(xpath)
        match_paras(allmatches, paras)
        return allmatches


    def match_paras(allmatches, paras):
        for para in paras:
            text = HtmlUtil.get_text_content(para)
            matches1 = re.findall(self.pattern, text)
            matches2 = remove_stop_words(matches1)
            allmatches.extend(matches2)


    def read_output_file(file):
        with open(file, 'r') as f:
            return f.read()


    def setup_files():
        st.title("Phrase Extractor")
        directory = st.text_input("Enter input directory path:", "")
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"not directory {directory}")
        html_files = [f for f in os.listdir(directory) if f.endswith('.html')]
        if not html_files:
            raise ValueError("no files")
        files = st.multiselect("Select .html files:", html_files)
        return files


    def extract_words(output_directory, files, patternx):
        counter = ceate_counter_from_files(files, patternx)
        with open(output_file, "w", encoding="UTF-8") as f:
            most_common = counter.most_common()
            for item in most_common:
                f.write(f"{item}\n")
        output_content = read_output_file(output_file)
        st.subheader("Output:")
        st.text(output_content)


    def ceate_counter_from_files(directory, patternx):
        counter = Counter()
        for selected_file in selected_files:
            input_file = os.path.join(directory, selected_file)
            matches = extract_words_from_html_file(input_file, patternx)
            for match in matches:
                counter[match] += 1

            # Display the contents of the output file
        return counter

word_finder = WordFinder()
selected_files = word_finder.setup_files()
output_file = os.path.join(output_dir, f'output.txt')
if st.button("Extract Words"):
    pattern = ONE_OR_MORE_CAPITALS
    extract_words(output_dir, selected_files, pattern)
