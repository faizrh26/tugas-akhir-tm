import os
import fitz
import re
import spacy

def load_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def load_cv(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext != ".pdf":
        raise ValueError("Only PDF CV files are supported.")

    return load_pdf(path)

nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+.,/%()\n -]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_and_lemmatize(text):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return tokens


def preprocess(text):
    cleaned = clean_text(text)
    tokens = tokenize_and_lemmatize(cleaned)
    return tokens

#Ujicoba
cv_pdf = "Alice Clark CV.pdf"  
raw_text = load_pdf(cv_pdf)
print("Raw length:", len(raw_text))
print(raw_text[:300])

tokens = preprocess(raw_text)
print("Total tokens:", len(tokens))
print(tokens)