# Sure! Below is a sample Streamlit code that provides a file browser to select a directory, locates *.txt files, processes them using your command-line application extract_words, and displays the contents of the output file.
import logging
import os
import re
import streamlit as st
from collections import Counter
from pathlib import Path

from amilib.ami_html import HtmlLib, HtmlUtil

logger = logging.getLogger()


pattern = r'\b(?:[A-Z][a-z]*(?:\s+(?:and|of|in|the|for|to|with|by|on)\s+[A-Z][a-z]*)*)+\b'
stopwords = set([
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
])

def extract_words_from_txt_file(txt_file):
    allmatches = []
    try:
        # Call the command-line application
        if not Path(txt_file).exists():
            raise FileNotFoundError(txt_file)
        with open(txt_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            matchez = re.findall(pattern, line)
            allmatches.extend(matchez)
        return allmatches
    except Exception as e:
        raise e


def remove_stop_words(words):
    words = [w for w in words if len(w) > 1]
    words = [w for w in words if w not in stopwords]
    return words


def extract_words_from_html_file(html_file):
    allmatches = []
    try:
        # Call the command-line application
        if not Path(html_file).exists():
            logger.error(f"file not found {html_file}")
            return allmatches
        htmlx = HtmlLib.parse_html(html_file)
        body = HtmlLib.get_body(htmlx)
        paras = body.xpath(".//p")
        for para in paras:
            text = HtmlUtil.get_text_content(para)
            matches1 = re.findall(pattern, text)
            matches2 = remove_stop_words(matches1)
            allmatches.extend(matches2)
        return allmatches
    except Exception as e:
        raise e


def read_output_file(file):
    with open(file, 'r') as f:
        return f.read()


# Streamlit application
st.title("Phrase Extractor")

# Directory selection
directory = st.text_input("Enter directory path:", "")

if directory and os.path.isdir(directory):
    # List .html files in the directory
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]

    if html_files:
        # selected_file = st.selectbox("Select a .html file:", html_files)
        selected_files = st.multiselect("Select .html files:", html_files)

        if st.button("Extract Words"):
            counter = Counter()
            output_file = os.path.join(directory, f'output.txt')
            for selected_file in selected_files:
                input_file = os.path.join(directory, selected_file)
                matches = extract_words_from_html_file(input_file)
                for match in matches:
                    counter[match] += 1

                # Display the contents of the output file
            with open(output_file, "w") as f:
                most_common = counter.most_common()
                for item in most_common:
                    f.write(f"{item}\n")
            output_content = read_output_file(output_file)
            st.subheader("Output:")
            st.text(output_content)

    else:
        st.warning("No .txt files found in the selected directory.")
else:
    st.warning("Please enter a valid directory path.")
