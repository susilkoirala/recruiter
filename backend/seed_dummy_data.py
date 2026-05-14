from app.auth import hash_password
from app.database import SessionLocal, engine
from app.models import Base, Candidate, CandidateStatus, Score, User, UserRole


PASSWORD = "apple@pie"

USERS = [
    {
        "email": "root@example.com",
        "role": UserRole.ADMIN,
    },
    {
        "email": "reviewer1@techkraft.test",
        "role": UserRole.REVIEWER,
    },
    {
        "email": "reviewer2@techkraft.test",
        "role": UserRole.REVIEWER,
    },
    {
        "email": "reviewer3@techkraft.test",
        "role": UserRole.REVIEWER,
    },
]

CANDIDATES = [
    {
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "role_applied": "Backend Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["Python", "FastAPI", "SQL", "Docker"],
        "internal_notes": "Strong API fundamentals. Ask about database indexing.",
    },
    {
        "name": "Maya Gurung",
        "email": "maya.gurung@example.com",
        "role_applied": "Frontend Engineer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["React", "JavaScript", "TypeScript", "Communication"],
        "internal_notes": "Good product sense and clean UI examples.",
    },
    {
        "name": "Nischal Karki",
        "email": "nischal.karki@example.com",
        "role_applied": "DevOps Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["Docker", "AWS", "Testing", "Communication"],
        "internal_notes": "Has production incident response experience.",
    },
    {
        "name": "Sofia Rai",
        "email": "sofia.rai@example.com",
        "role_applied": "Finance Officer",
        "status": CandidateStatus.HIRED,
        "skills": ["Communication", "Leadership", "SQL"],
        "internal_notes": "Excellent attention to detail.",
    },
    {
        "name": "Rohan Thapa",
        "email": "rohan.thapa@example.com",
        "role_applied": "QA Engineer",
        "status": CandidateStatus.REJECTED,
        "skills": ["Testing", "Python", "Communication"],
        "internal_notes": "Good basics, but limited automation experience.",
    },
    {
        "name": "Anisha Adhikari",
        "email": "anisha.adhikari@example.com",
        "role_applied": "Full Stack Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["React", "Python", "FastAPI", "SQL"],
        "internal_notes": "Comfortable across frontend and backend.",
    },
    {
        "name": "Bibek Tamang",
        "email": "bibek.tamang@example.com",
        "role_applied": "Product Manager",
        "status": CandidateStatus.REVIEWED,
        "skills": ["Communication", "Leadership", "Testing"],
        "internal_notes": "Strong discovery and prioritization examples.",
    },
    {
        "name": "Elina Shrestha",
        "email": "elina.shrestha@example.com",
        "role_applied": "UI/UX Designer",
        "status": CandidateStatus.NEW,
        "skills": ["Communication", "React", "JavaScript"],
        "internal_notes": "Portfolio has clean dashboard work.",
    },
    {
        "name": "Prabin Lama",
        "email": "prabin.lama@example.com",
        "role_applied": "Data Analyst",
        "status": CandidateStatus.REVIEWED,
        "skills": ["SQL", "Python", "Communication"],
        "internal_notes": "Good SQL case-study answers.",
    },
    {
        "name": "Kriti Basnet",
        "email": "kriti.basnet@example.com",
        "role_applied": "HR Officer",
        "status": CandidateStatus.NEW,
        "skills": ["Communication", "Leadership"],
        "internal_notes": "Experienced with hiring coordination.",
    },
    {
        "name": "Sanjay Bista",
        "email": "sanjay.bista@example.com",
        "role_applied": "Backend Engineer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["Python", "Django", "SQL", "Testing"],
        "internal_notes": "Django-heavy background, learning FastAPI.",
    },
    {
        "name": "Ishika Maharjan",
        "email": "ishika.maharjan@example.com",
        "role_applied": "Frontend Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["React", "TypeScript", "JavaScript"],
        "internal_notes": "Good component design discussion.",
    },
    {
        "name": "Nabin Poudel",
        "email": "nabin.poudel@example.com",
        "role_applied": "DevOps Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["Docker", "AWS", "Python"],
        "internal_notes": "Has CI/CD and deployment experience.",
    },
    {
        "name": "Smriti Khadka",
        "email": "smriti.khadka@example.com",
        "role_applied": "QA Engineer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["Testing", "Python", "Communication"],
        "internal_notes": "Automation fundamentals are solid.",
    },
    {
        "name": "Amit Joshi",
        "email": "amit.joshi@example.com",
        "role_applied": "Finance Officer",
        "status": CandidateStatus.NEW,
        "skills": ["SQL", "Communication"],
        "internal_notes": "Good spreadsheet and reporting examples.",
    },
    {
        "name": "Puja KC",
        "email": "puja.kc@example.com",
        "role_applied": "Backend Engineer",
        "status": CandidateStatus.HIRED,
        "skills": ["Python", "FastAPI", "Docker", "AWS"],
        "internal_notes": "Strong systems thinking.",
    },
    {
        "name": "Ramesh Ale",
        "email": "ramesh.ale@example.com",
        "role_applied": "Full Stack Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["React", "Django", "SQL", "Docker"],
        "internal_notes": "Balanced experience, needs architecture deep-dive.",
    },
    {
        "name": "Meera Pandey",
        "email": "meera.pandey@example.com",
        "role_applied": "Product Manager",
        "status": CandidateStatus.REJECTED,
        "skills": ["Communication", "Leadership"],
        "internal_notes": "Less hands-on with internal tools than expected.",
    },
    {
        "name": "Kiran Shahi",
        "email": "kiran.shahi@example.com",
        "role_applied": "Data Analyst",
        "status": CandidateStatus.NEW,
        "skills": ["Python", "SQL", "Testing"],
        "internal_notes": "Promising data cleaning examples.",
    },
    {
        "name": "Sita Neupane",
        "email": "sita.neupane@example.com",
        "role_applied": "UI/UX Designer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["Communication", "JavaScript"],
        "internal_notes": "Good UX reasoning for admin workflows.",
    },
    {
        "name": "Dipesh Rana",
        "email": "dipesh.rana@example.com",
        "role_applied": "DevOps Engineer",
        "status": CandidateStatus.REJECTED,
        "skills": ["Docker", "AWS", "Communication"],
        "internal_notes": "Good operations experience, weaker coding round.",
    },
    {
        "name": "Laxmi Giri",
        "email": "laxmi.giri@example.com",
        "role_applied": "HR Officer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["Communication", "Leadership"],
        "internal_notes": "Strong process ownership.",
    },
    {
        "name": "Roshan Malla",
        "email": "roshan.malla@example.com",
        "role_applied": "Frontend Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["React", "TypeScript", "Testing"],
        "internal_notes": "Good accessibility awareness.",
    },
    {
        "name": "Tara Singh",
        "email": "tara.singh@example.com",
        "role_applied": "Backend Engineer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["Python", "Django", "FastAPI", "SQL"],
        "internal_notes": "Strong Python background.",
    },
    {
        "name": "Manoj Chaudhary",
        "email": "manoj.chaudhary@example.com",
        "role_applied": "QA Engineer",
        "status": CandidateStatus.NEW,
        "skills": ["Testing", "JavaScript", "Communication"],
        "internal_notes": "Manual QA background, growing automation skills.",
    },
    {
        "name": "Rekha Bhatt",
        "email": "rekha.bhatt@example.com",
        "role_applied": "Finance Officer",
        "status": CandidateStatus.NEW,
        "skills": ["SQL", "Communication", "Leadership"],
        "internal_notes": "Has finance ops and audit support experience.",
    },
    {
        "name": "Sagar Dhakal",
        "email": "sagar.dhakal@example.com",
        "role_applied": "Full Stack Engineer",
        "status": CandidateStatus.REVIEWED,
        "skills": ["React", "FastAPI", "Python", "Docker"],
        "internal_notes": "Good project walkthrough.",
    },
    {
        "name": "Namrata Shakya",
        "email": "namrata.shakya@example.com",
        "role_applied": "Product Manager",
        "status": CandidateStatus.NEW,
        "skills": ["Communication", "Leadership", "SQL"],
        "internal_notes": "Strong metrics mindset.",
    },
]


def get_or_create_user(db, email: str, role: UserRole) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    user = User(
        email=email,
        hashed_password=hash_password(PASSWORD),
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_candidate(db, data: dict) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.email == data["email"]).first()
    if candidate:
        return candidate

    candidate = Candidate(**data)
    db.add(candidate)
    db.flush()
    return candidate


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users_by_email = {
            user_data["email"]: get_or_create_user(db, **user_data)
            for user_data in USERS
        }
        candidates_by_email = {
            candidate_data["email"]: get_or_create_candidate(db, candidate_data)
            for candidate_data in CANDIDATES
        }

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("Dummy data seeded.")
    print("")
    print("Demo users:")
    for user in USERS:
        print(f"- {user['role'].value}: {user['email']} / {PASSWORD}")


if __name__ == "__main__":
    main()
