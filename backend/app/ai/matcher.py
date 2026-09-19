"""
Explainable candidate <-> job matching engine.

Used in two directions:
  * candidate side -> "recommended jobs"
  * employer side  -> "ranked applicants"

Both call compute_match() so a candidate and an employer always see the
same number for the same pair. The weighted formula is deliberately simple and
modular so it can later be swapped for embeddings / ML ranking.
"""
from app.ai.resume_analyzer import WEIGHTS

# Preferred skills are worth less than required skills.
PREFERRED_SKILL_WEIGHT = 0.4

EDUCATION_RANK = {
    "high school": 1, "diploma": 2, "bachelor": 3, "bca": 3, "b.tech": 3, "b.sc": 3,
    "master": 4, "mca": 4, "m.tech": 4, "mba": 4, "phd": 5, "any": 0, "": 0,
}


def _education_rank(text: str | None) -> int:
    if not text:
        return 0
    lowered = text.lower()
    for key, rank in EDUCATION_RANK.items():
        if key and key in lowered:
            return rank
    return 0


def _skill_component(candidate_skills: list[str], required: list[str], preferred: list[str]) -> tuple:
    candidate_set = {s.lower().strip() for s in candidate_skills}
    required_set = {s.lower().strip() for s in required}
    preferred_set = {s.lower().strip() for s in preferred} - required_set

    matched_required = sorted(candidate_set & required_set)
    missing_required = sorted(required_set - candidate_set)
    matched_preferred = sorted(candidate_set & preferred_set)
    missing_preferred = sorted(preferred_set - candidate_set)

    total_weight = len(required_set) + PREFERRED_SKILL_WEIGHT * len(preferred_set)
    if total_weight == 0:
        score = 100.0 if candidate_set else 0.0
    else:
        earned = len(matched_required) + PREFERRED_SKILL_WEIGHT * len(matched_preferred)
        score = (earned / total_weight) * 100

    return (round(score, 2), matched_required + matched_preferred,
            missing_required + missing_preferred)


def compute_match(
    candidate_skills: list[str],
    candidate_experience: float,
    candidate_education: str | None,
    candidate_location: str | None,
    job_required_skills: list[str],
    job_preferred_skills: list[str],
    job_experience_required: float,
    job_education_required: str | None,
    job_location: str | None,
) -> dict:
    """Return the full, explainable breakdown of one candidate/job pair."""

    skill_score, matching_skills, missing_skills = _skill_component(
        candidate_skills, job_required_skills, job_preferred_skills
    )

    # Experience: meeting the requirement = 100, otherwise proportional.
    required_years = job_experience_required or 0.0
    if required_years <= 0:
        experience_score = 100.0
    else:
        experience_score = min(candidate_experience / required_years, 1.0) * 100

    # Education: same level or higher = 100, one level below = 60, else 30.
    need = _education_rank(job_education_required)
    have = _education_rank(candidate_education)
    if need == 0:
        education_score = 100.0
    elif have >= need:
        education_score = 100.0
    elif have == need - 1:
        education_score = 60.0
    else:
        education_score = 30.0

    # Keyword / contextual relevance: location overlap + breadth of skill overlap.
    location_bonus = 0.0
    if job_location and candidate_location:
        if job_location.strip().lower() in candidate_location.strip().lower() or \
           candidate_location.strip().lower() in job_location.strip().lower():
            location_bonus = 100.0
        elif "remote" in job_location.lower():
            location_bonus = 100.0
        else:
            location_bonus = 40.0
    else:
        location_bonus = 60.0
    coverage = skill_score
    keyword_score = round(0.5 * location_bonus + 0.5 * coverage, 2)

    final = (
        skill_score * WEIGHTS["skills"]
        + experience_score * WEIGHTS["experience"]
        + education_score * WEIGHTS["education"]
        + keyword_score * WEIGHTS["keywords"]
    )

    return {
        "match_score": round(final, 2),
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "keyword_score": keyword_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "weights": WEIGHTS,
        "explanation": (
            f"Skills {skill_score:.0f}% x50, experience {experience_score:.0f}% x20, "
            f"education {education_score:.0f}% x10, relevance {keyword_score:.0f}% x20."
        ),
    }
