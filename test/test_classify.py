import unittest

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder
import numpy as np

from test.test_all import AmiAnyTest


class TestClassify(AmiAnyTest):

    def test_example_classifier(self):

        """
     ** section
        classification **
        for scientific articles in XML format using ** scikit-learn ** and ** BeautifulSoup **.

        ### 🔧 What this script does:
        - Parses the    XML    to    extract    section    texts.
        - Uses    labeled    training    sections to    train a    classifier(e.g., logistic regression).
        - Predicts the    category    of    each    unlabeled    section.
        - Outputs    both    the    predicted ** label ** and a ** confidence
        score **   for each section.

        ---
        """


        def extract_sections(xml_path):
            """Extracts sections and their titles/content from a PMC XML file."""
            with open(xml_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "lxml")

            sections = []
            for sec in soup.find_all("sec"):
                title = sec.title.get_text(strip=True) if sec.title else ""
                paragraphs = " ".join(p.get_text(strip=True) for p in sec.find_all("p"))
                full_text = f"{title} {paragraphs}".strip()
                if full_text:
                    sections.append({"title": title, "text": full_text, "xml": sec})
            return sections

        def train_classifier(training_sections):
            """Train a classifier using labeled section data."""
            texts = [section["text"] for section in training_sections]
            labels = [section["label"] for section in training_sections]

            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(labels)

            pipeline = make_pipeline(
                TfidfVectorizer(ngram_range=(1, 2), stop_words="english"),
                LogisticRegression(max_iter=1000)
            )
            pipeline.fit(texts, y)
            return pipeline, label_encoder

        def classify_sections(classifier, label_encoder, sections):
            """Classify unlabeled sections and return predictions with confidence."""
            texts = [section["text"] for section in sections]
            probas = classifier.predict_proba(texts)
            predictions = classifier.predict(texts)

            results = []
            for i, section in enumerate(sections):
                label = label_encoder.inverse_transform([predictions[i]])[0]
                confidence = np.max(probas[i])
                results.append({
                    "title": section["title"],
                    "text": section["text"],
                    "predicted_label": label,
                    "confidence": confidence
                })
            return results

    # ==== Example usage ====


        # Training data: list of dicts with "text" and "label"
        training_data = [
            {"text": "In this study, we aim to investigate the role of...", "label": "introduction"},
            {"text": "We used a randomized control trial with 200 participants...", "label": "methods"},
            {"text": "The results showed a significant difference in...", "label": "results"},
            {"text": "This suggests that the treatment is effective...", "label": "discussion"},
            # Add more labeled sections from other categories
        ]

        # Load training data into sections format
        training_sections = [{"text": item["text"], "label": item["label"]} for item in training_data]

        # Train the classifier
        clf, encoder = train_classifier(training_sections)

        # Load unlabeled XML file
        xml_file_path = "example_article.xml"  # Replace with your file path
        unlabeled_sections = extract_sections(xml_file_path)

        # Classify sections
        classified = classify_sections(clf, encoder, unlabeled_sections)

        # Print results
        for sec in classified:
            print(f"Title: {sec['title']}")
            print(f"Predicted Label: {sec['predicted_label']} (Confidence: {sec['confidence']:.2f})")
            print("-" * 60)

        ### 📝 Notes:
        """
        - You’ll    need    to    customize the    `training_data`with your labeled examples.
        - This    example    uses ** logistic regression ** for simplicity.You could swap it 
        for other models 
        (e.g., SVM, RandomForest, or even fine-tuned transformers like `scibert` if you're 
        okay with more complexity).
        - Confidence is calculated as the max probability across all class predictions.
    
        ---
    
        """



if __name__ == '__main__':
    unittest.main()
