"""
One-time script that creates the first admin account securely.

Run once from the backend/ folder:
    python create_admin.py

Credentials come from the .env file (ADMIN_EMAIL / ADMIN_PASSWORD), so nothing
is hard-coded in the repository.
"""
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import User, UserRole
from app.utils.security import hash_password


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing:
            print(f"Admin already exists: {settings.ADMIN_EMAIL}")
            return
        admin = User(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        print(f"Admin created: {settings.ADMIN_EMAIL}")
        print("Log in through the normal login page and change this password later.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
