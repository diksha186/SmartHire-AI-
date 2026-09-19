"""Pydantic schemas for job applications."""
from datetime import datetime

from pydantic import BaseModel

from app.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    cover_note: str | None = None


class ApplicationStatusUpdate(BaseModel):
    application_status: ApplicationStatus


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    company_name: str
    location: str | None = None
    application_status: str
    match_score: float | None = None
    cover_note: str | None = None
    applied_at: datetime | None = None
    updated_at: datetime | None = None
