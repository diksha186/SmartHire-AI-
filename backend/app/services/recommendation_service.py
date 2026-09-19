"""
Business logic that sits between the routers and the AI layer.

Keeping it here means the same matching code is reused by:
  * candidate recommendations
  * employer applicant ranking
  * the score stored on an application at apply time
"""
from sqlalchemy.orm import Session

from app.ai.matcher import compute_match
from app.models import CandidateProfile, Company, Job, JobRecommendation


def match_candidate_to_job(profile: CandidateProfile, job: Job) -> dict:
    """Thin wrapper that unpacks the ORM objects for the AI matcher."""
    return compute_match(
        candidate_skills=profile.skill_list,
        candidate_experience=profile.experience or 0.0,
        candidate_education=profile.education,
        candidate_location=profile.location,
        job_required_skills=job.required_skill_list,
        job_preferred_skills=job.preferred_skill_list,
        job_experience_required=job.experience_required or 0.0,
        job_education_required=job.education_required,
        job_location=job.location,
    )


def build_recommendations(db: Session, profile: CandidateProfile, limit: int = 10) -> list[dict]:
    """
    Score every active job for this candidate, store the results in
    job_recommendations, and return the top `limit` matches.
    Called after a profile update or a resume upload so scores stay fresh.
    """
    jobs = db.query(Job).filter(Job.is_active == 1).all()
    results: list[dict] = []

    # Refresh: remove previous rows for this candidate.
    db.query(JobRecommendation).filter(
        JobRecommendation.candidate_id == profile.id
    ).delete(synchronize_session=False)

    for job in jobs:
        match = match_candidate_to_job(profile, job)
        company: Company = job.company
        results.append({
            "job_id": job.id,
            "title": job.title,
            "company_name": company.company_name if company else "Unknown",
            "location": job.location,
            "employment_type": job.employment_type,
            "salary": job.salary,
            "match_score": match["match_score"],
            "matching_skills": match["matching_skills"],
            "missing_skills": match["missing_skills"],
            "explanation": match["explanation"],
        })
        db.add(JobRecommendation(
            candidate_id=profile.id,
            job_id=job.id,
            match_score=match["match_score"],
            matching_skills=",".join(match["matching_skills"]),
            missing_skills=",".join(match["missing_skills"]),
        ))

    db.commit()
    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results[:limit]


def profile_completion(profile: CandidateProfile) -> int:
    """Percentage of the profile the candidate has filled in (used on the dashboard)."""
    fields = [
        profile.education, profile.location, profile.skills,
        profile.bio, profile.resume_file, profile.certifications,
    ]
    filled = sum(1 for f in fields if f)
    if profile.experience and profile.experience > 0:
        filled += 1
    return int(filled / (len(fields) + 1) * 100)
