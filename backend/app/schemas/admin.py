"""Pydantic schemas for the admin dashboard."""
from datetime import datetime

from pydantic import BaseModel


class AdminUserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: str | None = None
    is_active: int
    company_name: str | None = None
    created_at: datetime | None = None


class AdminJobOut(BaseModel):
    id: int
    title: str
    company_name: str
    location: str | None = None
    is_active: int
    applicant_count: int
    created_at: datetime | None = None


class AdminApplicationOut(BaseModel):
    id: int
    candidate_name: str
    job_title: str
    company_name: str
    application_status: str
    match_score: float | None = None
    applied_at: datetime | None = None


class StatisticsOut(BaseModel):
    total_candidates: int
    total_employers: int
    total_jobs: int
    active_jobs: int
    total_applications: int
    applications_by_status: dict[str, int]
    recent_registrations: list[AdminUserOut]
    recent_applications: list[AdminApplicationOut]
