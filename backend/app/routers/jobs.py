"""
/api/jobs - public job browsing, search & filtering, and applying to a job.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, CandidateProfile, Company, Job, User
from app.schemas.application import ApplicationCreate, ApplicationOut
from app.schemas.job import JobOut
from app.services.recommendation_service import match_candidate_to_job
from app.utils.deps import get_current_candidate_profile, get_current_user, require_candidate

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def _job_out(job: Job, db: Session, profile: CandidateProfile | None = None) -> JobOut:
    data = JobOut.model_validate(job)
    data.company_name = job.company.company_name if job.company else None
    data.applicant_count = db.query(Application).filter(Application.job_id == job.id).count()
    if profile is not None:
        data.already_applied = db.query(Application).filter(
            Application.job_id == job.id, Application.candidate_id == profile.id
        ).first() is not None
        data.match_score = match_candidate_to_job(profile, job)["match_score"]
    return data


@router.get("", response_model=list[JobOut])
def list_jobs(
    q: str | None = Query(default=None, description="Search in title / description / skills"),
    location: str | None = None,
    employment_type: str | None = None,
    min_experience: float | None = None,
    max_experience: float | None = None,
    skill: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Public endpoint: anyone can browse jobs (no token required)."""
    query = db.query(Job).filter(Job.is_active == 1)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title.like(like), Job.description.like(like),
                                 Job.required_skills.like(like)))
    if location:
        query = query.filter(Job.location.like(f"%{location}%"))
    if employment_type:
        query = query.filter(Job.employment_type == employment_type)
    if skill:
        query = query.filter(or_(Job.required_skills.like(f"%{skill}%"),
                                 Job.preferred_skills.like(f"%{skill}%")))
    if min_experience is not None:
        query = query.filter(Job.experience_required >= min_experience)
    if max_experience is not None:
        query = query.filter(Job.experience_required <= max_experience)

    jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    return [_job_out(job, db) for job in jobs]


@router.get("/{job_id}", response_model=JobOut)
def job_details(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return _job_out(job, db)


@router.get("/{job_id}/match", response_model=dict)
def job_match_for_me(
    job_id: int,
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    db: Session = Depends(get_db),
):
    """Explainable score for the logged-in candidate against one job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return match_candidate_to_job(profile, job)


@router.post("/{job_id}/apply", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: int,
    payload: ApplicationCreate,
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    if not job.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This job is closed")
    if job.deadline and job.deadline < datetime.utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The application deadline has passed")
    if not profile.resume_file:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Please upload your resume before applying")

    existing = db.query(Application).filter(
        Application.job_id == job_id, Application.candidate_id == profile.id
    ).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "You have already applied to this job")

    match = match_candidate_to_job(profile, job)
    application = Application(
        job_id=job.id,
        candidate_id=profile.id,
        resume_file=profile.resume_file,
        match_score=match["match_score"],
        cover_note=payload.cover_note,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    company: Company = job.company
    return ApplicationOut(
        id=application.id, job_id=job.id, job_title=job.title,
        company_name=company.company_name if company else "",
        location=job.location, application_status=application.application_status.value,
        match_score=application.match_score, cover_note=application.cover_note,
        applied_at=application.applied_at, updated_at=application.updated_at,
    )
