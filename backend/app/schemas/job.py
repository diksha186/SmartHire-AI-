"""Pydantic schemas for companies and jobs."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyUpdate(BaseModel):
    company_name: str | None = Field(default=None, max_length=160)
    description: str | None = None
    website: str | None = None
    location: str | None = None
    industry: str | None = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_name: str
    description: str | None = None
    website: str | None = None
    location: str | None = None
    industry: str | None = None


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=10)
    required_skills: str = Field(description="Comma separated list")
    preferred_skills: str | None = None
    experience_required: float = Field(default=0, ge=0, le=40)
    education_required: str | None = None
    location: str | None = None
    employment_type: str = "Full-time"
    salary: str | None = None
    deadline: datetime | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    required_skills: str | None = None
    preferred_skills: str | None = None
    experience_required: float | None = None
    education_required: str | None = None
    location: str | None = None
    employment_type: str | None = None
    salary: str | None = None
    deadline: datetime | None = None
    is_active: int | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    required_skills: str
    preferred_skills: str | None = None
    experience_required: float
    education_required: str | None = None
    location: str | None = None
    employment_type: str | None = None
    salary: str | None = None
    deadline: datetime | None = None
    is_active: int = 1
    created_at: datetime | None = None
    company_id: int
    company_name: str | None = None
    applicant_count: int | None = None
    already_applied: bool | None = None
    match_score: float | None = None


class RankedApplicantOut(BaseModel):
    application_id: int
    candidate_id: int
    name: str
    email: str
    education: str | None = None
    experience: float | None = None
    location: str | None = None
    resume_score: float | None = None
    match_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    application_status: str
    resume_file: str | None = None
    applied_at: datetime | None = None
