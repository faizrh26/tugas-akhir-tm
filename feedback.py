# feedback.py

from typing import Dict, List, Tuple


def _classify_fit(best_pct: float) -> str:
    """Kategori fit berdasarkan skor persentase terbaik."""
    if best_pct >= 70:
        return "strong"
    elif best_pct >= 55:
        return "good"
    elif best_pct >= 40:
        return "borderline"
    else:
        return "weak"


def _gap_type(sorted_roles: List[Tuple[str, float]]) -> str:
    """
    sorted_roles: list [(role, pct)] sudah diurut desc.
    Return 'clear' jika gap role1-role2 >= 10,
           'hybrid' kalau < 10 atau cuma 1 role punya skor berarti.
    """
    if len(sorted_roles) < 2:
        return "clear"
    gap = sorted_roles[0][1] - sorted_roles[1][1]
    return "clear" if gap >= 10 else "hybrid"


def _role_label(role_key: str) -> str:
    return role_key.replace("_", " ").title()


def build_feedback(
    best_role: str,
    score_result: Dict,
    profile: Dict,
    rubric: Dict
) -> Dict:
    """
    Bangun feedback untuk kandidat & HRD berbasis skor dan profil.
    - best_role: role terbaik hasil rekomendasi (string, misal 'data_scientist')
    - score_result: output dari scorer.score_candidate
    - profile: output dari extraction.build_profile
    - rubric: rubrik_penilaian (dict)
    """
    percent = score_result["percent"]          # dict role -> pct
    best_role_label = _role_label(best_role)
    best_pct = percent[best_role]

    # urutkan role berdasarkan skor
    sorted_roles = sorted(percent.items(), key=lambda x: x[1], reverse=True)
    fit_level = _classify_fit(best_pct)
    gap_kind = _gap_type(sorted_roles)

    # ambil data rubrik utk role terbaik
    rconf = rubric[best_role]
    must_skills = set(s.lower() for s in rconf["skills"]["must"])
    nice_skills = set(s.lower() for s in rconf["skills"]["nice"])
    core_tools = set(t.lower() for t in rconf["tools"]["core"])
    opt_tools = set(t.lower() for t in rconf["tools"]["optional"])

    exp_conf = rconf.get("experience", {})
    pref_years = exp_conf.get("preferred_years")  # ⬅️ pakai .get, aman kalau key nggak ada


    # dari profil
    skills_have = set(s.lower() for s in profile.get("skills", []))
    tools_have = set(t.lower() for t in profile.get("tools", []))
    exp_years = profile.get("experience_years", 0.0) or 0.0
    edu_level = profile.get("education_level", "UNKNOWN")
    majors = [m.lower() for m in profile.get("education_majors", [])]

    # hitung kekuatan & kekurangan
    skills_strength = sorted(must_skills & skills_have)
    missing_must_skills = sorted(must_skills - skills_have)

    tools_strength = sorted(core_tools & tools_have)
    missing_core_tools = sorted(core_tools - tools_have)

    nice_covered = sorted(nice_skills & skills_have)
    opt_tools_have = sorted(opt_tools & tools_have)

    exp_ok = exp_years >= pref_years if pref_years is not None else True

    # ---------- FEEDBACK UNTUK KANDIDAT ----------
    user_summary = ""
    if fit_level == "strong":
        user_summary = (
            f"CV kamu menunjukkan kecocokan yang kuat untuk peran {best_role_label} "
            f"dengan skor sekitar {best_pct:.1f}%. Secara umum profilmu sudah cukup solid."
        )
    elif fit_level == "good":
        user_summary = (
            f"Kamu cukup cocok untuk peran {best_role_label} (skor sekitar {best_pct:.1f}%). "
            f"Ada beberapa hal yang bisa diperkuat supaya lebih kompetitif."
        )
    elif fit_level == "borderline":
        user_summary = (
            f"Kecocokanmu dengan peran {best_role_label} masih borderline "
            f"(sekitar {best_pct:.1f}%). Profil ini masih bisa dikembangkan "
            f"untuk memenuhi ekspektasi industri."
        )
    else:  # weak
        user_summary = (
            f"Saat ini CV kamu belum menunjukkan kecocokan yang kuat untuk peran {best_role_label} "
            f"(skor sekitar {best_pct:.1f}%). Ini bukan berarti kamu tidak bisa ke arah sana, "
            "tapi perlu cukup banyak penguatan skill dan pengalaman."
        )

    if gap_kind == "hybrid" and len(sorted_roles) >= 2:
        second_label = _role_label(sorted_roles[1][0])
        user_summary += (
            f" Selain itu, profilmu juga relatif dekat dengan peran {second_label}, "
            "jadi kamu bisa mengeksplor kedua jalur tersebut."
        )

    strengths = []
    if skills_strength:
        strengths.append(
            "Skill inti yang sudah kuat: " + ", ".join(skills_strength) + "."
        )
    if tools_strength:
        strengths.append(
            "Tools utama yang sudah kamu kuasai: " + ", ".join(tools_strength) + "."
        )
    if nice_covered or opt_tools_have:
        extra = []
        if nice_covered:
            extra.append("skill pendukung " + ", ".join(nice_covered))
        if opt_tools_have:
            extra.append("tools tambahan " + ", ".join(opt_tools_have))
        strengths.append("Kamu juga sudah punya " + " dan ".join(extra) + ".")

    improvements = []
    if missing_must_skills:
        improvements.append(
            "Perlu menambahkan atau menonjolkan skill inti berikut di CV: "
            + ", ".join(missing_must_skills) + "."
        )
    if missing_core_tools:
        improvements.append(
            "Perlu menguatkan pengalaman dengan tools utama: "
            + ", ".join(missing_core_tools) + "."
        )
    if not exp_ok and pref_years:
        improvements.append(
            f"Pengalamanmu (~{exp_years:.1f} tahun) masih di bawah preferensi umum "
            f"untuk role ini (~{pref_years} tahun). Pertimbangkan menambah project/praktik atau "
            "pengalaman kerja terkait."
        )
    if edu_level in ["UNKNOWN", "SMA", "D3"]:
        improvements.append(
            "Bagian pendidikan di CV bisa diperjelas (degree, jurusan, dan tahun lulus), "
            "agar HR lebih mudah menilai latar belakang akademikmu."
        )

    if not improvements:
        improvements.append(
            "Secara garis besar struktur CV sudah cukup baik. Fokus sekarang bisa dialihkan "
            "ke menambah depth pada project dan hasil yang terukur."
        )

    user_suggestions = (
        "• Tulis pengalaman dalam bentuk bullet yang mencantumkan impact (angka, hasil konkret).\n"
        "• Pertimbangkan untuk menambahkan section 'Projects' yang jelas terkait data.\n"
        "• Sesuaikan kata kunci di CV dengan deskripsi kerja (job description) yang dituju."
    )

    # ---------- FEEDBACK UNTUK HRD ----------
    hr_summary = (
        f"Kandidat ini memiliki profil yang paling mendekati peran {best_role_label} "
        f"dengan skor sekitar {best_pct:.1f}% dibanding rubrik internal."
    )
    if gap_kind == "hybrid" and len(sorted_roles) >= 2:
        second_label = _role_label(sorted_roles[1][0])
        hr_summary += (
            f" Skor untuk {second_label} juga cukup dekat, sehingga kandidat berpotensi hybrid."
        )

    if fit_level == "strong":
        hr_recommendation = "Direkomendasikan untuk dipertimbangkan ke tahap interview teknis."
    elif fit_level == "good":
        hr_recommendation = (
            "Layak dipertimbangkan, terutama jika kandidat lain terbatas. "
            "Perlu pendalaman dalam interview terkait area yang masih lemah."
        )
    elif fit_level == "borderline":
        hr_recommendation = (
            "Bisa dipertimbangkan sebagai kandidat cadangan atau untuk posisi junior/entry level."
        )
    else:
        hr_recommendation = (
            "Tidak direkomendasikan sebagai prioritas untuk role ini, "
            "kecuali jika terdapat konteks tambahan di luar CV."
        )

    hr_risks = []
    if missing_must_skills:
        hr_risks.append(
            "Belum terlihat bukti jelas untuk skill inti: " + ", ".join(missing_must_skills) + "."
        )
    if missing_core_tools:
        hr_risks.append(
            "Paparan ke tools utama terbatas: " + ", ".join(missing_core_tools) + "."
        )
    if not exp_ok and pref_years:
        hr_risks.append(
            f"Total pengalaman (~{exp_years:.1f} tahun) di bawah preferensi (~{pref_years} tahun)."
        )

    hr_questions = [
        "Minta kandidat menjelaskan project data paling kompleks yang pernah dikerjakan dan perannya.",
        "Gali kedalaman penggunaan skill/tools inti yang relevan dengan role.",
        "Tanyakan ekspektasi kandidat terhadap role (analyst vs scientist vs engineer) untuk melihat alignment."
    ]

    return {
        "for_candidate": {
            "role": best_role_label,
            "fit_level": fit_level,
            "summary": user_summary,
            "strengths": strengths,
            "improvements": improvements,
            "suggestions": user_suggestions,
        },
        "for_hr": {
            "role": best_role_label,
            "fit_level": fit_level,
            "summary": hr_summary,
            "recommendation": hr_recommendation,
            "risks": hr_risks,
            "questions": hr_questions,
        },
    }
