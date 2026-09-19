"""
Explainable AI resume screening.

Pipeline:
    raw file -> text extraction -> cleaning -> spaCy NLP ->
    skill / education / experience / keyword detection -> weighted score -> suggestions

Weights (also used by the job matcher, see app/ai/matcher.py):
    skills 50% | experience 20% | education 10% | keywords 20%

Nothing here is a black box: every sub-score is returned to the user.
"""
import re

from app.ai.nlp_engine import clean_text, lemmatised_tokens
from app.ai.skills_db import (
    EDUCATION_LEVELS, EXPECTED_SECTIONS, QUALITY_KEYWORDS, SKILL_ALIASES,
)

WEIGHTS = {"skills": 0.50, "experience": 0.20, "education": 0.10, "keywords": 0.20}

# How many distinct skills count as a "full marks" resume.
SKILL_TARGET = 12


def extract_skills(cleaned_text: str) -> list[str]:
    """Dictionary matching against the skill database, alias aware."""
    padded = f" {cleaned_text} "
    found = []
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            # word-boundary match so 'r' does not match every word containing r
            pattern = r"(?<![a-zA-Z0-9\+\#])" + re.escape(alias.strip()) + r"(?![a-zA-Z0-9\+\#])"
            if re.search(pattern, padded):
                found.append(canonical)
                break
    return sorted(set(found))


def extract_education(cleaned_text: str) -> tuple[str | None, int]:
    """Return (highest education label, level 0-5)."""
    best_label, best_level = None, 0
    for label, level, keywords in EDUCATION_LEVELS:
        if any(kw in cleaned_text for kw in keywords) and level > best_level:
            best_label, best_level = label, level
    return best_label, best_level


def extract_experience_years(cleaned_text: str) -> float:
    """Find patterns such as '3 years of experience' or '2+ yrs'."""
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience",
        r"experience\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
    ]
    years = []
    for pattern in patterns:
        years += [float(m) for m in re.findall(pattern, cleaned_text)]
    if years:
        return min(max(years), 40.0)
    # Internships / training count as partial experience
    if "internship" in cleaned_text or "intern " in cleaned_text:
        return 0.5
    return 0.0


def extract_keywords(cleaned_text: str) -> list[str]:
    """Achievement / action words found via spaCy lemmatisation."""
    tokens = set(lemmatised_tokens(cleaned_text))
    return sorted({kw for kw in QUALITY_KEYWORDS
                   if kw in tokens or kw in cleaned_text})


def _build_suggestions(skills, education_label, years, keywords, cleaned_text) -> list[str]:
    suggestions: list[str] = []
    if len(skills) < 6:
        suggestions.append(
            "List more technical skills (languages, frameworks, databases, tools) "
            "in a dedicated 'Skills' section."
        )
    if education_label is None:
        suggestions.append("Add an 'Education' section with your degree, college and year of passing.")
    if years == 0:
        suggestions.append("Mention internships, training or freelance work to show practical experience.")
    if len(keywords) < 8:
        suggestions.append(
            "Use measurable action statements, e.g. 'Developed a REST API that reduced "
            "report time by 40%', instead of plain responsibilities."
        )
    missing_sections = [s for s in EXPECTED_SECTIONS if s not in cleaned_text]
    if missing_sections:
        suggestions.append("Missing common resume sections: " + ", ".join(missing_sections) + ".")
    if "project" not in cleaned_text:
        suggestions.append("Add 2-3 academic or personal projects with the technologies used.")
    if len(cleaned_text.split()) < 150:
        suggestions.append("Your resume looks short - aim for 300-600 words of meaningful content.")
    if not suggestions:
        suggestions.append("Strong resume. Keep it updated with your newest projects and certifications.")
    return suggestions


def analyze_resume(raw_text: str) -> dict:
    """
    Main entry point used by the /resume/upload and /resume/analyze endpoints.
    Returns a fully explainable analysis dictionary.
    """
    cleaned = clean_text(raw_text)
    if not cleaned:
        raise ValueError("No readable text found in the resume. "
                         "If it is a scanned image PDF, please upload a text-based file.")

    skills = extract_skills(cleaned)
    education_label, education_level = extract_education(cleaned)
    years = extract_experience_years(cleaned)
    keywords = extract_keywords(cleaned)

    skills_score = min(len(skills) / SKILL_TARGET, 1.0) * 100
    education_score = (education_level / 5) * 100
    experience_score = min(years / 3.0, 1.0) * 100          # 3+ years = full marks
    keyword_score = min(len(keywords) / len(QUALITY_KEYWORDS) * 2.5, 1.0) * 100

    final_score = (
        skills_score * WEIGHTS["skills"]
        + experience_score * WEIGHTS["experience"]
        + education_score * WEIGHTS["education"]
        + keyword_score * WEIGHTS["keywords"]
    )

    return {
        "resume_score": round(final_score, 2),
        "skills_score": round(skills_score, 2),
        "education_score": round(education_score, 2),
        "experience_score": round(experience_score, 2),
        "keyword_score": round(keyword_score, 2),
        "extracted_skills": skills,
        "education_detected": education_label,
        "experience_years": years,
        "keywords_found": keywords,
        "suggestions": _build_suggestions(skills, education_label, years, keywords, cleaned),
        "weights": WEIGHTS,
        "raw_text_preview": raw_text[:800],
    }
