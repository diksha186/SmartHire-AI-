"""
/api/applications - candidates track their applications,
employers update the status of applications on their own jobs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, CandidateProfile, Company, User, UserRole
from app.schemas.application import ApplicationOut, ApplicationStatusUpdate
from app.utils.deps import get_current_candidate_profile, get_current_user

router = APIRouter(prefix="/api/applications", tags=["Applications"])


def _application_out(app: Application) -> ApplicationOut:
    job = app.job
    company = job.company if job else None
    return ApplicationOut(
        id=app.id, job_id=app.job_id,
        job_title=job.title if job else "",
        company_name=company.company_name if company else "",
        location=job.location if job else None,
        application_status=app.application_status.value,
        match_score=app.match_score, cover_note=app.cover_note,
        applied_at=app.applied_at, updated_at=app.updated_at,
    )


@router.get("", response_model=list[ApplicationOut])
def my_applications(
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    db: Session = Depends(get_db),
):
    apps = (
        db.query(Application)
        .filter(Application.candidate_id == profile.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return [_application_out(a) for a in apps]


@router.get("/{application_id}", response_model=ApplicationOut)
def application_details(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Visible to the candidate who applied, the employer who owns the job, and admins."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if app is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")

    if current_user.role == UserRole.candidate:
        if app.candidate.user_id != current_user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This is not your application")
    elif current_user.role == UserRole.employer:
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        if company is None or app.job.company_id != company.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This application is not for your job")

    return _application_out(app)


@router.put("/{application_id}/status", response_model=ApplicationOut)
def update_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.employer, UserRole.admin):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only employers can update application status")

    app = db.query(Application).filter(Application.id == application_id).first()
    if app is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")

    if current_user.role == UserRole.employer:
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        if company is None or app.job.company_id != company.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "You can only update applications for your own jobs")

    app.application_status = payload.application_status
    db.commit()
    db.refresh(app)
    return _application_out(app)


@router.delete("/{application_id}")
def withdraw_application(
    application_id: int,
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    db: Session = Depends(get_db),
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if app is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    if app.candidate_id != profile.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This is not your application")
    db.delete(app)
    db.commit()
    return {"message": "Application withdrawn", "application_id": application_id}
