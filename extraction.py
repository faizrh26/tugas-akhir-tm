import re
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

# ============================================================
# SECTION HEADERS (ATS-style CV detection)
# ============================================================

SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "career experience"
    ],
    "education": [
        "education", "academic background", "academic history", "qualifications"
    ],
    "skills": [
        "skills", "technical skills", "core skills", "skills & abilities"
    ],
    "projects": [
        "projects", "project experience", "relevant projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "licences"
    ],
    "summary": [
        "summary", "profile", "professional summary", "about me"
    ]
}

UNIVERSITY_KEYWORDS = [
    "university", "universitas", "institute", "institut",
    "polytechnic", "politeknik", "college", "school of",
    "sekolah tinggi"
]

MONTHS = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]


# ============================================================
# TF-IDF keywords (for word cloud / display only)
# ============================================================

def extract_keywords(text, top_k=20):
    if not text:
        return []
    vec = TfidfVectorizer(stop_words="english", max_features=2000)
    tfidf = vec.fit_transform([text]).toarray()[0]
    vocab = vec.get_feature_names_out()
    pairs = list(zip(vocab, tfidf))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return [w for w, s in pairs[:top_k]]


# ============================================================
# Normalize helper
# ============================================================

def _norm(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


# ============================================================
# SECTION PARSER — identify segments of CV
# ============================================================

def parse_sections(raw_text: str):
    """
    Pisahkan CV menjadi bagian-bagian ATS:
    experience, education, skills, projects, certifications, summary, other.
    """
    lines = raw_text.splitlines()
    sections = {k: "" for k in SECTION_HEADERS}
    sections["other"] = ""

    current = "other"

    for line in lines:
        clean = line.strip()
        low = clean.lower()

        # cek apakah line ini header section
        found = None
        for sec, headers in SECTION_HEADERS.items():
            for h in headers:
                if low.startswith(h):
                    found = sec
                    break
            if found:
                break

        # update current section
        if found:
            current = found
            continue

        # append line ke section aktif
        sections[current] += clean + "\n"

    return sections


# ============================================================
# EXPERIENCE EXTRACTION (V4 mid-year assumption)
# ============================================================

def extract_experience_years(section_text):
    """
    Hitung estimasi pengalaman kerja dengan akurasi lebih tinggi.
    - Menggunakan mid-year assumption jika hanya tahun
    - Memahami rentang '2020–2022', '2020 – Present'
    - Fallback: intern → 0.5 tahun, role → 1 tahun
    """

    text = section_text.lower()
    current_year = datetime.datetime.now().year
    total_years = 0.0

    # 1) Rentang tahun lengkap
    year_ranges = re.findall(
        r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current|now)",
        text
    )

    for start_str, end_str in year_ranges:
        start_year = int(start_str)

        if end_str in ["present", "current", "now"]:
            end_year = current_year
        else:
            end_year = int(end_str)

        start_float = start_year + 0.5
        end_float = end_year + 0.5

        span = end_float - start_float
        if span > 0:
            total_years += min(span, 10.0)

    # 2) SINGLE YEAR ONLY
    single_years = re.findall(r"\b(20\d{2})\b", text)

    used_years = set(start for start, _ in year_ranges)
    used_years.update(end for _, end in year_ranges if end.isdigit())

    for yr_str in single_years:
        yr = int(yr_str)
        if yr not in used_years:
            if "intern" in text:
                total_years += 0.5
            elif any(r in text for r in ["data analyst", "data scientist", "data engineer"]):
                total_years += 1.0
            else:
                total_years += 0.5

    # 3) fallback total
    if total_years == 0:
        if "intern" in text:
            return 0.5
        if any(r in text for r in ["data analyst", "data scientist", "data engineer"]):
            return 1.0

    return round(total_years, 2)


def extract_experience_roles(section_text, role_keywords):
    roles = []
    low = section_text.lower()

    # roles dari rubric
    for r in role_keywords:
        if r in low:
            roles.append(r)

    # Job Title Capitalized
    caps = re.findall(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})\b", section_text)
    for c in caps:
        if any(r in c.lower() for r in role_keywords):
            roles.append(c)

    return list(sorted(set(roles)))


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education_level(section_text):
    t = section_text.lower()

    if any(k in t for k in ["phd", "doctor", "s3"]):
        return "S3"
    if any(k in t for k in ["msc", "m.sc", "magister", "master", "s2"]):
        return "S2"
    if any(k in t for k in ["bsc", "b.sc", "bachelor", "sarjana", "s1"]):
        return "S1"
    if any(k in t for k in ["d3", "diploma", "associate"]):
        return "D3"
    if any(k in t for k in ["sma", "smk", "high school"]):
        return "SMA"

    return "UNKNOWN"


def extract_education_institution(section_text):
    inst = []
    for line in section_text.splitlines():
        low = line.lower()
        if any(k in low for k in UNIVERSITY_KEYWORDS):
            inst.append(line.strip())
    return list(dict.fromkeys(inst))


def extract_education_majors(section_text, major_keywords):
    low = section_text.lower()
    return sorted({m for m in major_keywords if m in low})


# ============================================================
# SKILLS / TOOLS / PROJECTS / CERTIFICATIONS
# ============================================================

def extract_phrases_section(section_text, keywords):
    low = section_text.lower()
    return sorted({k for k in keywords if k in low})


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(raw_text):
    for line in raw_text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        parts = clean.split()
        if 1 <= len(parts) <= 4 and all(p[0].isupper() for p in parts if p[0].isalpha()):
            if not any(ch.isdigit() for ch in clean):
                return clean.title()
    return "Unknown"


# ============================================================
# KEYWORDS FROM RUBRIC (skills/tools/etc)
# ============================================================

def _collect_keywords_from_rubric(rubric):
    skills, tools, projects, certs, roles, majors = set(), set(), set(), set(), set(), set()

    for _, r in rubric.items():
        skills.update(s.lower() for s in r["skills"]["must"])
        skills.update(s.lower() for s in r["skills"]["nice"])

        tools.update(t.lower() for t in r["tools"]["core"])
        tools.update(t.lower() for t in r["tools"]["optional"])

        projects.update(p.lower() for p in r["signals"]["projects"])
        certs.update(c.lower() for c in r["signals"]["certifications"])

        roles.update(rr.lower() for rr in r["experience"]["roles"])

        majors.update(m.lower() for m in r["education"]["preferred_majors"])
        majors.update(m.lower() for m in r["education"]["optional_majors"])

    return {
        "skills": list(skills),
        "tools": list(tools),
        "projects": list(projects),
        "certs": list(certs),
        "roles": list(roles),
        "majors": list(majors),
    }


# ============================================================
# BUILD PROFILE — main extraction output for scoring
# ============================================================

def build_profile(raw_text, cleaned_text, rubric):
    sections = parse_sections(raw_text)
    vocab = _collect_keywords_from_rubric(rubric)

    profile = {
        "name": extract_name(raw_text),

        "skills": extract_phrases_section(sections["skills"], vocab["skills"]),
        "tools": extract_phrases_section(sections["skills"], vocab["tools"]),
        "projects": extract_phrases_section(sections["projects"], vocab["projects"]),
        "certifications": extract_phrases_section(sections["certifications"], vocab["certs"]),

        "experience_years": extract_experience_years(sections["experience"]),
        "experience_roles": extract_experience_roles(sections["experience"], vocab["roles"]),

        "education_level": extract_education_level(sections["education"]),
        "education_majors": extract_education_majors(sections["education"], vocab["majors"]),
        "education_institution": extract_education_institution(sections["education"]),
    }

    return profile
