"""
/api/admin - platform administration. Every route requires role == admin.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Application, ApplicationStatus, CandidateProfile, Company, Job, User, UserRole,
)
from app.schemas.admin import (
    AdminApplicationOut, AdminJobOut, AdminUserOut, StatisticsOut,
)
from app.utils.deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


def _user_out(user: User) -> AdminUserOut:
    return AdminUserOut(
        id=user.id, name=user.name, email=user.email, role=user.role.value,
        phone=user.phone, is_active=user.is_active,
        company_name=user.company.company_name if user.company else None,
        created_at=user.created_at,
    )


def _application_out(app: Application) -> AdminApplicationOut:
    return AdminApplicationOut(
        id=app.id,
        candidate_name=app.candidate.user.name if app.candidate and app.candidate.user else "",
        job_title=app.job.title if app.job else "",
        company_name=app.job.company.company_name if app.job and app.job.company else "",
        application_status=app.application_status.value,
        match_score=app.match_score,
        applied_at=app.applied_at,
    )


@router.get("/users", response_model=list[AdminUserOut])
def list_users(role: UserRole | None = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return [_user_out(u) for u in query.order_by(User.created_at.desc()).all()]


@router.patch("/users/{user_id}/toggle-active", response_model=AdminUserOut)
def toggle_user_active(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Admin accounts cannot be disabled")
    user.is_active = 0 if user.is_active else 1
    db.commit()
    db.refresh(user)
    return _user_out(user)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.role == UserRole.admin:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Admin accounts cannot be deleted here")
    db.delete(user)          # cascades to profile / company / jobs / applications
    db.commit()
    return {"message": "User deleted", "user_id": user_id}


@router.get("/jobs", response_model=list[AdminJobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [
        AdminJobOut(
            id=j.id, title=j.title,
            company_name=j.company.company_name if j.company else "",
            location=j.location, is_active=j.is_active,
            applicant_count=db.query(Application).filter(Application.job_id == j.id).count(),
            created_at=j.created_at,
        )
        for j in jobs
    ]


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job removed", "job_id": job_id}


@router.get("/applications", response_model=list[AdminApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    apps = db.query(Application).order_by(Application.applied_at.desc()).all()
    return [_application_out(a) for a in apps]


@router.get("/statistics", response_model=StatisticsOut)
def statistics(db: Session = Depends(get_db)):
    applications = db.query(Application).all()
    by_status = {s.value: 0 for s in ApplicationStatus}
    for app in applications:
        by_status[app.application_status.value] += 1

    recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    recent_apps = db.query(Application).order_by(Application.applied_at.desc()).limit(5).all()

    return StatisticsOut(
        total_candidates=db.query(User).filter(User.role == UserRole.candidate).count(),
        total_employers=db.query(User).filter(User.role == UserRole.employer).count(),
        total_jobs=db.query(Job).count(),
        active_jobs=db.query(Job).filter(Job.is_active == 1).count(),
        total_applications=len(applications),
        applications_by_status=by_status,
        recent_registrations=[_user_out(u) for u in recent_users],
        recent_applications=[_application_out(a) for a in recent_apps],
    )
