import os
import docx2txt
import PyPDF2
import csv
import pandas as pd

def load_cv(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return docx2txt.process(file_path)
    elif ext == ".txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type!")

def load_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def load_interview_answers(file_path):
    # format .csv: id_user, pertanyaan, jawaban
    df = pd.read_csv(file_path)
    return df['jawaban'].tolist()

def load_rubric(file_path):
    # format .csv: job, label, kata_kunci, bobot
    return pd.read_csv(file_path)