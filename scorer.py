import json
from typing import Dict, List

# ======================================
# Load rubric (CSV/JSON optional)
# ======================================

def load_rubric(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".json"):
            return json.load(f)
        else:
            raise ValueError("Rubric format not supported yet (use JSON)")

# ======================================
# Scoring function
# ======================================

def score_candidate(keywords: List[str], entities: Dict[str, List[str]], rubric: Dict) -> Dict:
    scores = {"data_scientist": 0, "data_analyst": 0, "data_engineer": 0}

    # Combine all extracted text features
    flat_entities = []
    for ent_list in entities.values():
        flat_entities.extend(ent_list)

    all_tokens = set([w.lower() for w in keywords] + [e.lower() for e in flat_entities])

    # Scoring logic
    for role, rules in rubric.items():
        for keyword, weight in rules.items():
            if keyword.lower() in all_tokens:
                scores[role] += weight

    # Also compute percentage
    max_scores = {role: sum(rubric[role].values()) for role in rubric}
    percent = {
        role: round((scores[role] / max_scores[role]) * 100, 2)
        for role in rubric
    }

    return {"raw_scores": scores, "percent": percent}

# ======================================
# Utility: pick best recommendation
# ======================================

def recommend_role(score_result: Dict) -> str:
    percent = score_result["percent"]
    best_role = max(percent, key=percent.get)
    return best_role
