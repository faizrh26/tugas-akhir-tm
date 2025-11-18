import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

# ==============================
# NER Extraction
# ==============================

def extract_entities(text: str) -> Dict[str, List[str]]:
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        label = ent.label_
        if label not in entities:
            entities[label] = []
        entities[label].append(ent.text)
    return entities

# ==============================
# Keyword Extraction using TF-IDF
# ==============================

def extract_keywords(text: str, top_k: int = 15) -> List[str]:
    vec = TfidfVectorizer(stop_words='english', max_features=2000)
    tfidf_matrix = vec.fit_transform([text])
    scores = tfidf_matrix.toarray()[0]
    vocab = vec.get_feature_names_out()

    scored_words = list(zip(vocab, scores))
    scored_words.sort(key=lambda x: x[1], reverse=True)

    return [w for w, s in scored_words[:top_k]]

# ==============================
# Topic Modeling Placeholder
# ==============================

def simple_topic(text: str) -> List[str]:
    # Placeholder logic (nanti bisa diganti LDA)
    tokens = [t.text.lower() for t in nlp(text) if t.is_alpha]
    common = {}
    for tok in tokens:
        common[tok] = common.get(tok, 0) + 1

    sorted_words = sorted(common.items(), key=lambda x: x[1], reverse=True)
    return [w for w, c in sorted_words[:10]]
