import re
from sklearn.feature_extraction.text import TfidfVectorizer

# 1: Keyword Extraction (TF-IDF)

def extract_keywords(text: str, top_k: int = 15):
    vec = TfidfVectorizer(stop_words="english", max_features=2000)
    tfidf_matrix = vec.fit_transform([text])
    scores = tfidf_matrix.toarray()[0]
    vocab = vec.get_feature_names_out()

    scored_words = list(zip(vocab, scores))
    scored_words.sort(key=lambda x: x[1], reverse=True)

    return [w for w, s in scored_words[:top_k]]



# Text Normalization

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Skill, tools, and project/experience extraction (rule-based Information Extraction)
def _collect_all_from_rubric(rubric):

    all_skills = set()
    all_tools = set()
    all_projects = set()
    all_certs = set()
    all_roles = set()
    all_majors = set()

    for role_name, cfg in rubric.items():
        # skills
        skills_cfg = cfg.get("skills", {})
        all_skills.update(s.lower() for s in skills_cfg.get("must", []))
        all_skills.update(s.lower() for s in skills_cfg.get("nice", []))

        # tools
        tools_cfg = cfg.get("tools", {})
        all_tools.update(t.lower() for t in tools_cfg.get("core", []))
        all_tools.update(t.lower() for t in tools_cfg.get("optional", []))

        # projects
        sig_cfg = cfg.get("signals", {})
        all_projects.update(p.lower() for p in sig_cfg.get("projects", []))

        # certs
        all_certs.update(c.lower() for c in sig_cfg.get("certifications", []))

        # experience roles
        exp_cfg = cfg.get("experience", {})
        all_roles.update(r.lower() for r in exp_cfg.get("roles", []))

        # majors
        edu_cfg = cfg.get("education", {})
        all_majors.update(m.lower() for m in edu_cfg.get("preferred_majors", []))
        all_majors.update(m.lower() for m in edu_cfg.get("optional_majors", []))

    return {
        "skills": sorted(all_skills),
        "tools": sorted(all_tools),
        "projects": sorted(all_projects),
        "certs": sorted(all_certs),
        "roles": sorted(all_roles),
        "majors": sorted(all_majors),
    }

# Cari frasa / kata kunci sederhana di dalam teks normalized (lowercase).
def _find_phrases(normalized_text: str, phrases):
    found = set()
    for ph in phrases:
        ph = ph.strip().lower()
        # skip kosong
        if not ph:
            continue
        if ph in normalized_text:
            found.add(ph)
    return sorted(found)

# mengambil tahun pengalaman dalam bidang
    # TODO: parsing tahun pakai regex kalau mau lebih serius
    # match ranges seperti "2020-2023", "2019 – 2021", dll
def _extract_experience_years(raw_text: str):
    text = _normalize(raw_text)
    years = 0.0

    # intern signal
    if "intern" in text or "magang" in text:
        years = max(years, 0.5)

    # experience signal (minimal)
    if any(role in text for role in ["data analyst", "data scientist", "data engineer"]):
        years = max(years, 1.0)

    return years

# Mengambil jenjang pendidikan pelamar
def _extract_education_level(raw_text: str):
    text = _normalize(raw_text)

    if "s3" in text or "phd" in text or "doctor" in text:
        return "S3"
    if "s2" in text or "master" in text or "magister" in text:
        return "S2"
    if "s1" in text or "bachelor" in text or "sarjana" in text:
        return "S1"
    if "d3" in text or "diploma" in text:
        return "D3"
    if "sma" in text or "high school" in text:
        return "SMA"
    return "UNKNOWN"

# Mengambil jurusan/prodi
def _extract_education_majors(raw_text: str, all_majors):
    text = _normalize(raw_text)
    return _find_phrases(text, all_majors)



# 2: Build candidate profile - membuat profil dari CV berdasarkan rubrik
def build_profile(raw_text: str, cleaned_text: str, rubric: dict):
    norm_raw = _normalize(raw_text)
    norm_clean = _normalize(cleaned_text)

    vocab = _collect_all_from_rubric(rubric)

    # Skills, tools, projects, certs, roles, majors
    skills_found = _find_phrases(norm_clean, vocab["skills"])
    tools_found = _find_phrases(norm_clean, vocab["tools"])
    projects_found = _find_phrases(norm_clean, vocab["projects"])
    certs_found = _find_phrases(norm_raw, vocab["certs"])  # sering muncul di bagian sertif, tidak selalu ter-lemmatize
    roles_found = _find_phrases(norm_raw, vocab["roles"])
    majors_found = _extract_education_majors(raw_text, vocab["majors"])

    experience_years = _extract_experience_years(raw_text)
    education_level = _extract_education_level(raw_text)

    profile = {
        "skills": skills_found,
        "tools": tools_found,
        "projects": projects_found,
        "certifications": certs_found,
        "experience_years": experience_years,
        "experience_roles": roles_found,
        "education_majors": majors_found,
        "education_level": education_level,
    }

    return profile
