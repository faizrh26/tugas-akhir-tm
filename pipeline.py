import input_handler
import prepocessing
import extraction
import scorer

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

    return {
        "best_role": best_role,
        "score_result": score_result,
        "profile": profile,
        "keywords": keywords,
        "raw_text": cv_text,
        "cleaned_text": cleaned_text,
    }


if __name__ == "__main__":
    # contoh manual
    result = process_cv("data/user_cv.txt")
    print("===== BEST ROLE =====")
    print(result["best_role"])
    print("Scores:", result["score_result"])
