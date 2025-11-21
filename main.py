import input_handler
import prepocessing
import extraction
import scorer

def main():
    # Step 1: INPUT HANDLING
    cv_text = input_handler.load_cv("data/cv_user.pdf")  # bisa diganti ke docx/txt
    interview_answers = input_handler.load_interview_answers("data/jawaban_user.csv")
    rubric = scorer.load_rubric("data/rubrik_penilaian.json")

    # Step 2: PREPROCESSING
    processed_cv = prepocessing.clean_text(cv_text)
    processed_answers = [prepocessing.clean_text(j) for j in interview_answers]

    # Step 3: EXTRACTION
    entities = extraction.extract_entities(processed_cv)
    keywords = extraction.extract_keywords(processed_cv)

     # Step 4: SCORING
    score_result = scorer.score_candidate(keywords, entities, rubric)
    best_role = scorer.recommend_role(score_result)
    
     # Step 5: OUTPUT
    print("===== BEST ROLE RECOMMENDATION =====")
    print(best_role.upper())
    print(score_result)
    
    # Step 3: Output sementara (testing)
    # print("====Cleaned CV====")
    # print(processed_cv[:500])  # preview
    # print("====Cleaned Interview====")
    # for ans in processed_answers:
    #     print(ans[:200])

    # Lanjut ke extraction, scoring, visualisasi di file lain

if __name__ == "__main__":
    main()