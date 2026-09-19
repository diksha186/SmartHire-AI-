"""
SmartHire AI - FastAPI application entry point.

Run from the backend/ folder:
    uvicorn app.main:app --reload
Interactive API docs: http://127.0.0.1:8000/docs
"""
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import Base, engine
from app.models import models  # noqa: F401  (import registers the tables)
from app.routers import admin, applications, auth, candidates, employers, jobs

app = FastAPI(
    title="SmartHire AI",
    description="Smart Job Portal with AI Resume Screening & Job Recommendation System",
    version="1.0.0",
)

# --- CORS so the React dev server can call the API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create tables (if missing) and make sure the upload folder exists."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


# --- Global error handlers: always return meaningful JSON ---
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again."},
    )


# --- Routers ---
app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(employers.router)
app.include_router(applications.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {"app": "SmartHire AI", "status": "running", "docs": "/docs"}
