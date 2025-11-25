import input_handler
import prepocessing
import extraction
import scorer
from feedback import build_feedback

RUBRIC_PATH = "data/rubrik_penilaian.json"


def process_cv(file_path: str):
    # Load CV
    cv_text = input_handler.load_cv(file_path)

    # Preprocessing
    cleaned_text = prepocessing.clean_text(cv_text)

    # Load rubric
    rubric = scorer.load_rubric(RUBRIC_PATH)

    # Build candidate profile
    profile = extraction.build_profile(cv_text, cleaned_text, rubric)

    # Scoring
    score_result = scorer.score_candidate(profile, rubric)
    best_role = scorer.recommend_role(score_result)

    # Optional: keywords for UI / debugging
    keywords = extraction.extract_keywords(cleaned_text)

    # Build feedback (pakai best_role dari sini)
    feedback = build_feedback(best_role, score_result, profile, rubric)

    return {
        "best_role": best_role,
        "score_result": score_result,
        "profile": profile,
        "keywords": keywords,
        "raw_text": cv_text,
        "cleaned_text": cleaned_text,
        "feedback": feedback,
    }
