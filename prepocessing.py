import spacy
import string

# Pakai model spacy bahasa Indonesia kalau user data dalam Bahasa Indonesia, kalau English: 'en_core_web_sm'
# Kalau belum install, run di terminal: python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

STOPWORDS = set(spacy.lang.en.stop_words.STOP_WORDS)  # Kalau Indo ganti stopword Indo

def clean_text(text):
    # Lowercase
    text = text.lower()
    # Remove punctuation, angka, dll
    text = "".join([char for char in text if char not in string.punctuation and not char.isdigit()])
    # Proses NLP: tokenisasi, stopword removal, lemmatization
    doc = nlp(text)
    result = []
    for token in doc:
        if (token.text not in STOPWORDS) and (token.is_alpha):
            result.append(token.lemma_)
    return " ".join(result)