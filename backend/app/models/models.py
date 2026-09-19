"""
SQLAlchemy ORM models = the relational database design of SmartHire AI.

Relationships
-------------
User 1--1 CandidateProfile
User 1--1 Company
Company 1--N Job
Job 1--N Application
CandidateProfile 1--N Application
CandidateProfile 1--N ResumeAnalysis
CandidateProfile 1--N JobRecommendation  N--1 Job
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    candidate = "candidate"
    employer = "employer"
    admin = "admin"


class ApplicationStatus(str, enum.Enum):
    applied = "Applied"
    under_review = "Under Review"
    shortlisted = "Shortlisted"
    interview = "Interview"
    rejected = "Rejected"
    selected = "Selected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.candidate, index=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate_profile = relationship(
        "CandidateProfile", back_populates="user",
        uselist=False, cascade="all, delete-orphan",
    )
    company = relationship(
        "Company", back_populates="user",
        uselist=False, cascade="all, delete-orphan",
    )


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    education = Column(String(255), nullable=True)      # e.g. "BCA"
    location = Column(String(120), nullable=True)
    skills = Column(Text, nullable=True)                # comma separated: "python,sql,react"
    experience = Column(Float, default=0.0)             # years
    certifications = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    resume_file = Column(String(255), nullable=True)    # stored filename
    resume_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="candidate_profile")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    analyses = relationship("ResumeAnalysis", back_populates="candidate",
                            cascade="all, delete-orphan", order_by="ResumeAnalysis.analyzed_at.desc()")
    recommendations = relationship("JobRecommendation", back_populates="candidate",
                                   cascade="all, delete-orphan")

    @property
    def skill_list(self) -> list[str]:
        return [s.strip().lower() for s in (self.skills or "").split(",") if s.strip()]


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(200), nullable=True)
    location = Column(String(120), nullable=True)
    industry = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(160), nullable=False, index=True)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)      # comma separated
    preferred_skills = Column(Text, nullable=True)
    experience_required = Column(Float, default=0.0)
    education_required = Column(String(120), nullable=True)
    location = Column(String(120), nullable=True, index=True)
    employment_type = Column(String(60), default="Full-time")
    salary = Column(String(80), nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    recommendations = relationship("JobRecommendation", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_jobs_title_location", "title", "location"),)

    @property
    def required_skill_list(self) -> list[str]:
        return [s.strip().lower() for s in (self.required_skills or "").split(",") if s.strip()]

    @property
    def preferred_skill_list(self) -> list[str]:
        return [s.strip().lower() for s in (self.preferred_skills or "").split(",") if s.strip()]


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    resume_file = Column(String(255), nullable=True)   # snapshot of resume used
    match_score = Column(Float, nullable=True)         # AI score at apply time
    application_status = Column(Enum(ApplicationStatus), default=ApplicationStatus.applied, nullable=False)
    cover_note = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    candidate = relationship("CandidateProfile", back_populates="applications")

    # A candidate may apply to the same job only once.
    __table_args__ = (UniqueConstraint("job_id", "candidate_id", name="uq_job_candidate"),)


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    resume_score = Column(Float, nullable=False)
    extracted_skills = Column(Text, nullable=True)
    education_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    keyword_score = Column(Float, default=0.0)
    skills_score = Column(Float, default=0.0)
    suggestions = Column(Text, nullable=True)          # newline separated
    raw_text_preview = Column(Text, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("CandidateProfile", back_populates="analyses")


class JobRecommendation(Base):
    __tablename__ = "job_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, nullable=False)
    matching_skills = Column(Text, nullable=True)
    missing_skills = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("CandidateProfile", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")

    __table_args__ = (UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job_rec"),)
