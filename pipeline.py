# pipeline.py

import input_handler
import prepocessing
import extraction
import scorer

Rubrik_penilaian = "data/rubrik_penilaian.json"


def process_cv(file_path):

    # 1. LOAD CV
    cv_text = input_handler.load_cv(file_path)

    # 2. PREPROCESSING
    cleaned_text = prepocessing.clean_text(cv_text)

    # 3. EXTRACTION
    entities = extraction.extract_entities(cv_text)       # NER
    keywords = extraction.extract_keywords(cleaned_text)  # TF-IDF

    # 4. SCORING
    rubric = scorer.load_rubric(Rubrik_penilaian)
    score_result = scorer.score_candidate(keywords, entities, rubric)
    best_role = scorer.recommend_role(score_result)

    # 5. Return full detail
    return {
        "best_role": best_role,
        "score_result": score_result,
        "entities": entities,
        "keywords": keywords,
        "raw_text": cv_text,
        "cleaned_text": cleaned_text
    }
