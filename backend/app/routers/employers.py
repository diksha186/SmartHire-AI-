"""
/api/employers - company profile, job CRUD and AI-ranked applicants.

Ownership is enforced everywhere: an employer can only touch jobs whose
company_id matches their own company.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Company, Job, User
from app.schemas.job import CompanyOut, CompanyUpdate, JobCreate, JobOut, JobUpdate, RankedApplicantOut
from app.services.recommendation_service import match_candidate_to_job
from app.utils.deps import get_current_company, require_employer
from app.utils.file_handler import resume_path

router = APIRouter(prefix="/api/employers", tags=["Employer"])


def _owned_job(job_id: int, company: Company, db: Session) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    if job.company_id != company.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only manage your own job postings")
    return job


@router.get("/profile", response_model=CompanyOut)
def get_company(company: Company = Depends(get_current_company)):
    return CompanyOut.model_validate(company)


@router.put("/profile", response_model=CompanyOut)
def update_company(
    payload: CompanyUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return CompanyOut.model_validate(company)


@router.get("/dashboard")
def employer_dashboard(company: Company = Depends(get_current_company), db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.company_id == company.id).all()
    job_ids = [j.id for j in jobs]
    applications = (
        db.query(Application).filter(Application.job_id.in_(job_ids)).all() if job_ids else []
    )
    status_counts: dict[str, int] = {}
    for app in applications:
        key = app.application_status.value
        status_counts[key] = status_counts.get(key, 0) + 1

    return {
        "company_name": company.company_name,
        "total_jobs": len(jobs),
        "active_jobs": sum(1 for j in jobs if j.is_active),
        "total_applications": len(applications),
        "status_counts": status_counts,
        "recent_jobs": [
            {"id": j.id, "title": j.title, "is_active": j.is_active,
             "applicants": sum(1 for a in applications if a.job_id == j.id)}
            for j in sorted(jobs, key=lambda x: x.created_at or 0, reverse=True)[:5]
        ],
    }


@router.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    job = Job(company_id=company.id, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    out = JobOut.model_validate(job)
    out.company_name = company.company_name
    out.applicant_count = 0
    return out


@router.get("/jobs", response_model=list[JobOut])
def my_jobs(company: Company = Depends(get_current_company), db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.company_id == company.id).order_by(Job.created_at.desc()).all()
    result = []
    for job in jobs:
        out = JobOut.model_validate(job)
        out.company_name = company.company_name
        out.applicant_count = db.query(Application).filter(Application.job_id == job.id).count()
        result.append(out)
    return result


@router.put("/jobs/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    payload: JobUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    job = _owned_job(job_id, company, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    out = JobOut.model_validate(job)
    out.company_name = company.company_name
    return out


@router.delete("/jobs/{job_id}", status_code=status.HTTP_200_OK)
def delete_job(
    job_id: int,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    job = _owned_job(job_id, company, db)
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully", "job_id": job_id}


@router.patch("/jobs/{job_id}/close", response_model=JobOut)
def close_job(
    job_id: int,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    job = _owned_job(job_id, company, db)
    job.is_active = 0
    db.commit()
    db.refresh(job)
    out = JobOut.model_validate(job)
    out.company_name = company.company_name
    return out


@router.get("/jobs/{job_id}/applicants", response_model=list[RankedApplicantOut])
def ranked_applicants(
    job_id: int,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """AI candidate ranking: every applicant scored against this job, best first."""
    job = _owned_job(job_id, company, db)
    applications = db.query(Application).filter(Application.job_id == job.id).all()

    ranked: list[RankedApplicantOut] = []
    for app in applications:
        profile = app.candidate
        user: User = profile.user
        match = match_candidate_to_job(profile, job)
        ranked.append(RankedApplicantOut(
            application_id=app.id,
            candidate_id=profile.id,
            name=user.name,
            email=user.email,
            education=profile.education,
            experience=profile.experience,
            location=profile.location,
            resume_score=profile.resume_score,
            match_score=match["match_score"],
            matching_skills=match["matching_skills"],
            missing_skills=match["missing_skills"],
            application_status=app.application_status.value,
            resume_file=app.resume_file,
            applied_at=app.applied_at,
        ))

    ranked.sort(key=lambda r: r.match_score, reverse=True)
    return ranked


@router.get("/applicants/{application_id}/resume")
def download_applicant_resume(
    application_id: int,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """An employer may only download resumes of people who applied to THEIR jobs."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if app is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    if app.job.company_id != company.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your applicant")
    if not app.resume_file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No resume attached")
    return FileResponse(resume_path(app.resume_file), filename=app.resume_file)
