import input_handler
import preprocessing

def main():
    # Step 1: INPUT HANDLING
    cv_text = input_handler.load_cv("data/cv_user.pdf")  # bisa diganti ke docx/txt
    interview_answers = input_handler.load_interview_answers("data/jawaban_user.csv")
    rubric = input_handler.load_rubric("data/rubrik_penilaian.csv")

    # Step 2: PREPROCESSING
    processed_cv = preprocessing.clean_text(cv_text)
    processed_answers = [preprocessing.clean_text(j) for j in interview_answers]

    # Step 3: Output sementara (testing)
    print("====Cleaned CV====")
    print(processed_cv[:500])  # preview
    print("====Cleaned Interview====")
    for ans in processed_answers:
        print(ans[:200])

    # Lanjut ke extraction, scoring, visualisasi di file lain

if __name__ == "__main__":
    main()