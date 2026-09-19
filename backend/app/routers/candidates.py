"""
/api/candidates - profile, resume upload + AI analysis, recommendations, dashboard.

Every endpoint uses get_current_candidate_profile(), so a candidate can only ever
read or modify their OWN data - that is the core of the RBAC design.
"""
import json
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.ai.resume_analyzer import analyze_resume
from app.ai.text_extractor import extract_text
from app.database import get_db
from app.models import Application, CandidateProfile, ResumeAnalysis, User
from app.schemas.candidate import (
    CandidateDashboardOut, CandidateProfileOut, CandidateProfileUpdate,
    RecommendationOut, ResumeAnalysisOut,
)
from app.services.recommendation_service import build_recommendations, profile_completion
from app.utils.deps import get_current_candidate_profile, require_candidate
from app.utils.file_handler import resume_path, save_resume

router = APIRouter(prefix="/api/candidates", tags=["Candidate"])


def _profile_out(profile: CandidateProfile, user: User) -> CandidateProfileOut:
    return CandidateProfileOut(
        id=profile.id, user_id=profile.user_id, name=user.name, email=user.email,
        phone=user.phone, education=profile.education, location=profile.location,
        skills=profile.skills, experience=profile.experience,
        certifications=profile.certifications, bio=profile.bio,
        resume_file=profile.resume_file, resume_score=profile.resume_score,
        profile_completion=profile_completion(profile),
    )


@router.get("/profile", response_model=CandidateProfileOut)
def get_profile(
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    current_user: User = Depends(require_candidate),
):
    return _profile_out(profile, current_user)


@router.put("/profile", response_model=CandidateProfileOut)
def update_profile(
    payload: CandidateProfileUpdate,
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)

    # name/phone live on the users table
    if data.get("name"):
        current_user.name = data.pop("name")
    if "phone" in data:
        current_user.phone = data.pop("phone")

    for field, value in data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    # Skills may have changed -> refresh the stored recommendations.
    build_recommendations(db, profile)
    return _profile_out(profile, current_user)


@router.post("/resume/upload", response_model=ResumeAnalysisOut, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    """
    Full AI pipeline:
    validate file -> save -> extract text -> NLP analysis -> store -> refresh recommendations.
    """
    stored_name, path = save_resume(file, current_user.id)

    try:
        raw_text = extract_text(path)
        analysis = analyze_resume(raw_text)
    except ValueError as exc:
        os.remove(path)                       # do not keep an unusable file
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))

    # Remove the previous resume file from disk to save space.
    if profile.resume_file:
        old = resume_path(profile.resume_file)
        if os.path.exists(old):
            os.remove(old)

    profile.resume_file = stored_name
    profile.resume_score = analysis["resume_score"]

    # Merge newly detected skills into the profile (candidate can still edit them).
    existing = set(profile.skill_list)
    merged = sorted(existing | set(analysis["extracted_skills"]))
    profile.skills = ",".join(merged)
    if analysis["experience_years"] and not profile.experience:
        profile.experience = analysis["experience_years"]
    if analysis["education_detected"] and not profile.education:
        profile.education = analysis["education_detected"]

    record = ResumeAnalysis(
        candidate_id=profile.id,
        resume_score=analysis["resume_score"],
        extracted_skills=",".join(analysis["extracted_skills"]),
        skills_score=analysis["skills_score"],
        education_score=analysis["education_score"],
        experience_score=analysis["experience_score"],
        keyword_score=analysis["keyword_score"],
        suggestions="\n".join(analysis["suggestions"]),
        raw_text_preview=analysis["raw_text_preview"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    build_recommendations(db, profile)

    return ResumeAnalysisOut(
        resume_score=record.resume_score,
        skills_score=record.skills_score,
        education_score=record.education_score,
        experience_score=record.experience_score,
        keyword_score=record.keyword_score,
        extracted_skills=analysis["extracted_skills"],
        education_detected=analysis["education_detected"],
        experience_years=analysis["experience_years"],
        suggestions=analysis["suggestions"],
        analyzed_at=record.analyzed_at,
    )


@router.get("/resume/analyze", response_model=ResumeAnalysisOut)
def latest_analysis(
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    db: Session = Depends(get_db),
):
    """Return the most recent stored analysis (no re-processing needed)."""
    record = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.candidate_id == profile.id)
        .order_by(ResumeAnalysis.analyzed_at.desc())
        .first()
    )
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No resume analysed yet. Please upload a resume.")

    return ResumeAnalysisOut(
        resume_score=record.resume_score,
        skills_score=record.skills_score,
        education_score=record.education_score,
        experience_score=record.experience_score,
        keyword_score=record.keyword_score,
        extracted_skills=[s for s in (record.extracted_skills or "").split(",") if s],
        education_detected=profile.education,
        experience_years=profile.experience or 0,
        suggestions=[s for s in (record.suggestions or "").split("\n") if s],
        analyzed_at=record.analyzed_at,
    )


@router.get("/resume/download")
def download_own_resume(profile: CandidateProfile = Depends(get_current_candidate_profile)):
    if not profile.resume_file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No resume uploaded")
    return FileResponse(resume_path(profile.resume_file), filename=profile.resume_file)


@router.get("/recommendations", response_model=list[RecommendationOut])
def recommendations(
    limit: int = 10,
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    db: Session = Depends(get_db),
):
    if not profile.skill_list:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Add skills to your profile or upload a resume to get recommendations",
        )
    return build_recommendations(db, profile, limit=limit)


@router.get("/dashboard", response_model=CandidateDashboardOut)
def dashboard(
    profile: CandidateProfile = Depends(get_current_candidate_profile),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    applications = db.query(Application).filter(Application.candidate_id == profile.id).all()
    status_counts: dict[str, int] = {}
    for app in applications:
        key = app.application_status.value
        status_counts[key] = status_counts.get(key, 0) + 1

    recs = build_recommendations(db, profile, limit=4) if profile.skill_list else []

    return CandidateDashboardOut(
        name=current_user.name,
        resume_score=profile.resume_score,
        profile_completion=profile_completion(profile),
        total_applications=len(applications),
        status_counts=status_counts,
        top_recommendations=recs,
        skills=profile.skill_list,
    )
