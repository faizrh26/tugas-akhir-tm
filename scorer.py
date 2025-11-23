import json


# Load rubric for scoring (JSON)

def load_rubric(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Scoring module – based on candidate profile and rubric
# 1st Module – based on candidate experience year(s)
def _score_experience(candidate, role_rubric):
    years = candidate.get("experience_years", 0.0)
    pref_years = role_rubric["experience"].get("pref_years", 1) or 1

    # penilaian berdasarkan pengalaman, minimal 1 tahun
    score = min(years / pref_years, 1.0) # 0 tahun = 0, 1/2 tahun = 0.5, 1 tahun dst = 1

    return score

# Module 2nd – based education (Uni Major)
def _score_education(candidate, role_rubric):
    majors = [m.lower() for m in candidate.get("education_majors", [])]
    level = (candidate.get("education_level") or "").upper()

    edu_cfg = role_rubric["education"]
    preferred = [m.lower() for m in edu_cfg.get("preferred_majors", [])]
    optional = [m.lower() for m in edu_cfg.get("optional_majors", [])]
    min_level = (edu_cfg.get("min_level") or "").upper()

    
    if any(m in " ".join(majors) for m in preferred):
        major_score = 1.0
    elif any(m in " ".join(majors) for m in optional):
        major_score = 0.6
    else:
        major_score = 0.3  # jurusan tidak 'relevan', tapi tidak bernilai 0

    # Level check (sederhana banget)
    level_order = ["SMA", "D3", "S1", "S2", "S3"]
    try:
        idx_level = level_order.index(level) if level in level_order else -1
        idx_min = level_order.index(min_level) if min_level in level_order else 2  # default S1
        if idx_level >= idx_min:
            level_score = 1.0
        else:
            level_score = 0.5
    except ValueError:
        level_score = 0.5

    # Kombinasikan secara sederhana
    return (major_score * 0.7) + (level_score * 0.3)

# 3rd Module - based on Skills
def _score_skills(candidate, role_rubric):
    cand_skills = set(s.lower() for s in candidate.get("skills", []))
    cand_tools = set(t.lower() for t in candidate.get("tools", []))

    skills_cfg = role_rubric["skills"]
    tools_cfg = role_rubric["tools"]

    must = [s.lower() for s in skills_cfg.get("must", [])]
    nice = [s.lower() for s in skills_cfg.get("nice", [])]

    core_tools = [t.lower() for t in tools_cfg.get("core", [])]
    opt_tools = [t.lower() for t in tools_cfg.get("optional", [])]

    # Must skills: skill yang harusnya dimiliki di bidang tersebut
    if must:
        must_hit = sum(1 for s in must if s in cand_skills)
        skills_must_score = must_hit / len(must)
    else:
        skills_must_score = 0.0

    # Nice skills: Skill yang nice-to-have di industri DA/DS/DE
    if nice:
        nice_hit = sum(1 for s in nice if s in cand_skills)
        skills_nice_score = nice_hit / len(nice)
    else:
        skills_nice_score = 0.0

    # Tools (gabungan core + optional, tapi core lebih penting)
    # Core : tools yang sering dipakai di industri tsb
    tool_core_score = (sum(1 for t in core_tools if t in cand_tools) / len(core_tools)) if core_tools else 0.0 
    # Optional : tools yang tidak sesering itu dipakai di industri, tapi masih cukup umum
    tool_opt_score = (sum(1 for t in opt_tools if t in cand_tools) / len(opt_tools)) if opt_tools else 0.0

    # Gabungkan tools (0.7 * Core Tools + 0.3 * Optional Tools )
    tools_score = (0.7 * tool_core_score) + (0.3 * tool_opt_score)

    return skills_must_score, skills_nice_score, tools_score

# 4th Module - based on projects and certifications
def _score_signals(candidate, role_rubric):
    cand_projects = set(p.lower() for p in candidate.get("projects", []))
    cand_certs = set(c.lower() for c in candidate.get("certifications", []))

    sig_cfg = role_rubric["signals"]
    proj_keys = [p.lower() for p in sig_cfg.get("projects", [])]
    cert_keys = [c.lower() for c in sig_cfg.get("certifications", [])]

    proj_score = (sum(1 for p in proj_keys if p in cand_projects) / len(proj_keys)) if proj_keys else 0.0
    cert_score = (sum(1 for c in cert_keys if c in cand_certs) / len(cert_keys)) if cert_keys else 0.0

    # gabung project + cert
    signals_score = (0.6 * proj_score) + (0.4 * cert_score)
    return signals_score

# Final module - final weighting based on rubric (0.4, 0.4, 0.1, 0.1) 
def _score_one_role(candidate, role_name, role_rubric):
    w = role_rubric["weights"]

    skills_must_score, skills_nice_score, tools_score = _score_skills(candidate, role_rubric)
    experience_score = _score_experience(candidate, role_rubric)
    education_score = _score_education(candidate, role_rubric)
    signals_score = _score_signals(candidate, role_rubric)

    # Tools bisa dianggap bagian dari skills_nice, atau kita treat sebagai boost kecil
    combined_skills_nice = min(1.0, (skills_nice_score * 0.7 + tools_score * 0.3))

    total = (
        w.get("skills_must", 0) * skills_must_score +
        w.get("skills_nice", 0) * combined_skills_nice +
        w.get("experience", 0) * experience_score +
        w.get("education", 0) * education_score +
        w.get("signals", 0) * signals_score
    )

    return {
        "total": round(float(total), 4),
        "skills_must": round(float(skills_must_score), 4),
        "skills_nice": round(float(skills_nice_score), 4),
        "tools": round(float(tools_score), 4),
        "experience": round(float(experience_score), 4),
        "education": round(float(education_score), 4),
        "signals": round(float(signals_score), 4),
    }

# Prepare the scoring result for use (raw score, percent, and role(s) details)
def score_candidate(candidate_profile, rubric):

    raw_scores = {}
    percent = {}
    details = {}

    for role_name, role_rubric in rubric.items():
        role_detail = _score_one_role(candidate_profile, role_name, role_rubric)
        total = role_detail["total"]
        raw_scores[role_name] = total  # 0.0 - 1.0
        percent[role_name] = round(total * 100, 2)
        details[role_name] = role_detail

    return {
        "raw_scores": raw_scores,
        "percent": percent,
        "details": details,
    }

# Merekomendasikan role berdasarkan hasil perhitungan diatas
def recommend_role(score_result):
    percent = score_result["percent"]
    best_role = max(percent, key=percent.get) if percent else None
    return best_role
