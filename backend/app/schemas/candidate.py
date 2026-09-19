"""Pydantic schemas for candidate profile, resume analysis and recommendations."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CandidateProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    education: str | None = None
    location: str | None = None
    skills: str | None = Field(default=None, description="Comma separated list")
    experience: float | None = Field(default=None, ge=0, le=50)
    certifications: str | None = None
    bio: str | None = None


class CandidateProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    education: str | None = None
    location: str | None = None
    skills: str | None = None
    experience: float | None = None
    certifications: str | None = None
    bio: str | None = None
    resume_file: str | None = None
    resume_score: float | None = None
    profile_completion: int = 0


class ResumeAnalysisOut(BaseModel):
    resume_score: float
    skills_score: float
    education_score: float
    experience_score: float
    keyword_score: float
    extracted_skills: list[str]
    education_detected: str | None = None
    experience_years: float = 0
    suggestions: list[str]
    analyzed_at: datetime | None = None


class RecommendationOut(BaseModel):
    job_id: int
    title: str
    company_name: str
    location: str | None = None
    employment_type: str | None = None
    salary: str | None = None
    match_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    explanation: str


class CandidateDashboardOut(BaseModel):
    name: str
    resume_score: float | None = None
    profile_completion: int
    total_applications: int
    status_counts: dict[str, int]
    top_recommendations: list[RecommendationOut]
    skills: list[str]
