"""
Optional demo-data script for the project viva / screenshots.

Creates 2 employers with 5 jobs and 3 candidates (with skills already filled in)
so the dashboards are not empty. Resumes still have to be uploaded manually to
demonstrate the real AI pipeline.

    python seed_data.py
"""
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import CandidateProfile, Company, Job, User, UserRole
from app.utils.security import hash_password

DEMO_PASSWORD = "Demo@12345"


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Job).count() > 0:
            print("Demo data already present - nothing to do.")
            return

        employers = [
            ("Rahul Sharma", "hr@techmindsolutions.com", "TechMind Solutions", "Noida", "IT Services"),
            ("Priya Nair", "careers@datanova.in", "DataNova Analytics", "Bengaluru", "Data & Analytics"),
        ]
        companies = []
        for name, email, company_name, location, industry in employers:
            user = User(name=name, email=email, password_hash=hash_password(DEMO_PASSWORD),
                        role=UserRole.employer, phone="9876543210")
            db.add(user)
            db.flush()
            company = Company(user_id=user.id, company_name=company_name, location=location,
                              industry=industry, website="https://example.com",
                              description=f"{company_name} builds software products for Indian clients.")
            db.add(company)
            db.flush()
            companies.append(company)

        jobs = [
            (0, "Python Backend Developer", "Build and maintain REST APIs with FastAPI and MySQL.",
             "python,fastapi,sql,git", "docker,aws", 1, "BCA", "Noida", "Full-time", "4-6 LPA"),
            (0, "React Frontend Developer", "Develop responsive dashboards using React and Bootstrap.",
             "react,javascript,html,css,bootstrap", "typescript,git", 1, "BCA", "Noida", "Full-time", "3.5-5 LPA"),
            (0, "Software Trainee", "Six month training programme for fresh graduates.",
             "python,sql,problem solving", "git,linux", 0, "BCA", "Remote", "Internship", "15k/month"),
            (1, "Data Analyst", "Analyse business data and build Power BI dashboards.",
             "excel,sql,power bi,data analysis", "python,pandas", 1, "BCA", "Bengaluru", "Full-time", "5-7 LPA"),
            (1, "Junior ML Engineer", "Work on NLP models for resume and document understanding.",
             "python,machine learning,nlp,numpy", "spacy,tensorflow", 2, "MCA", "Bengaluru", "Full-time", "8-12 LPA"),
        ]
        for idx, title, desc, req, pref, exp, edu, loc, etype, salary in jobs:
            db.add(Job(
                company_id=companies[idx].id, title=title, description=desc,
                required_skills=req, preferred_skills=pref, experience_required=exp,
                education_required=edu, location=loc, employment_type=etype,
                salary=salary, deadline=datetime.utcnow() + timedelta(days=30),
            ))

        candidates = [
            ("Aman Verma", "aman@student.com", "BCA", "Noida", "python,sql,git,html,css", 1.0),
            ("Sneha Gupta", "sneha@student.com", "BCA", "Bengaluru", "excel,sql,power bi,data analysis", 0.5),
            ("Vikas Yadav", "vikas@student.com", "MCA", "Delhi", "python,machine learning,nlp,numpy,git", 2.0),
        ]
        for name, email, edu, loc, skills, exp in candidates:
            user = User(name=name, email=email, password_hash=hash_password(DEMO_PASSWORD),
                        role=UserRole.candidate, phone="9000000000")
            db.add(user)
            db.flush()
            db.add(CandidateProfile(user_id=user.id, education=edu, location=loc,
                                    skills=skills, experience=exp,
                                    bio=f"{edu} student looking for an entry level role."))

        db.commit()
        print("Demo data created. Password for every demo account:", DEMO_PASSWORD)
    finally:
        db.close()


if __name__ == "__main__":
    main()
