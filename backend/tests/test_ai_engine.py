"""
Basic unit tests for the AI layer (no database or server needed).

    cd backend
    pytest
"""
from app.ai.matcher import compute_match
from app.ai.resume_analyzer import analyze_resume, extract_education, extract_experience_years, extract_skills

SAMPLE_RESUME = """
Aman Verma
BCA Student, Bulandshahr

Summary: Backend developer with 2 years of experience building REST APIs.

Skills: Python, FastAPI, MySQL, Git, HTML, CSS, JavaScript, React

Experience: Developed and deployed a job portal that reduced manual screening time by 40%.
Internship at TechMind Solutions.

Projects: SmartHire AI - resume screening system using spaCy.
Education: Bachelor of Computer Applications (BCA), 2026.
Certification: Python for Everybody.
"""


def test_skill_extraction_finds_core_skills():
    skills = extract_skills(SAMPLE_RESUME.lower())
    for expected in ["python", "fastapi", "mysql", "git", "react"]:
        assert expected in skills


def test_education_detection():
    label, level = extract_education(SAMPLE_RESUME.lower())
    assert label == "Bachelor"
    assert level == 3


def test_experience_years_parsing():
    assert extract_experience_years(SAMPLE_RESUME.lower()) == 2.0


def test_resume_score_is_in_range_and_explainable():
    result = analyze_resume(SAMPLE_RESUME)
    assert 0 <= result["resume_score"] <= 100
    assert result["suggestions"]
    assert set(result["weights"]) == {"skills", "experience", "education", "keywords"}


def test_perfect_match_scores_higher_than_poor_match():
    good = compute_match(["python", "fastapi", "sql", "git"], 2, "BCA", "Noida",
                         ["python", "fastapi", "sql", "git"], [], 1, "BCA", "Noida")
    poor = compute_match(["photoshop"], 0, None, "Chennai",
                         ["python", "fastapi", "sql", "git"], [], 3, "MCA", "Noida")
    assert good["match_score"] > poor["match_score"]
    assert "python" in good["matching_skills"]
    assert "python" in poor["missing_skills"]
