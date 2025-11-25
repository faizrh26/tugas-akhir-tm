# main.py

from pipeline import process_cv

def main():
    file_path = "data/user_cv.txt"
    result = process_cv(file_path)

    print("Job Role Recommendation")
    print(result["best_role"].upper())
    print()
    print("Raw scores:", result["score_result"]["raw_scores"])
    print("Percent   :", result["score_result"]["percent"])
    print("Recommendation(s) are based on program reading on CV.")
    print("\n=== Feedback (candidate) ===")
    print(result["feedback"]["for_candidate"]["summary"])


if __name__ == "__main__":
    main()
