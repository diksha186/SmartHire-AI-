"""
/api/auth - registration, login and "who am I".

Admin accounts are never created here: use backend/create_admin.py instead.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CandidateProfile, Company, User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.utils.deps import get_current_user
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if payload.role == UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Admin accounts cannot be created through public registration")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    if payload.role == UserRole.employer and not payload.company_name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "company_name is required for employers")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),   # never store plain text
        role=payload.role,
        phone=payload.phone,
    )
    db.add(user)
    db.flush()          # get user.id before committing

    if payload.role == UserRole.candidate:
        db.add(CandidateProfile(user_id=user.id))
    else:
        db.add(Company(user_id=user.id, company_name=payload.company_name))

    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role.value, user.email)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Same message for both cases so attackers cannot enumerate emails.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been disabled")

    token = create_access_token(user.id, user.role.value, user.email)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
