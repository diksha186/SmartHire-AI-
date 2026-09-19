"""
Reusable FastAPI dependencies: current user extraction + Role Based Access Control.

Usage in a router:

    @router.get("/jobs", dependencies=[Depends(require_employer)])
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CandidateProfile, Company, User, UserRole
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication token missing")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer exists or is disabled")
    return user


def _role_guard(*allowed: UserRole):
    def guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"This endpoint requires role: {', '.join(r.value for r in allowed)}",
            )
        return current_user
    return guard


require_candidate = _role_guard(UserRole.candidate)
require_employer = _role_guard(UserRole.employer)
require_admin = _role_guard(UserRole.admin)
require_employer_or_admin = _role_guard(UserRole.employer, UserRole.admin)


def get_current_candidate_profile(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
) -> CandidateProfile:
    """Return the logged-in candidate's own profile (creating an empty one if needed)."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if profile is None:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_current_company(
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db),
) -> Company:
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company profile not created yet")
    return company
