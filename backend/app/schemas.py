from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import CandidateStatus, UserRole


ROLE_OPTIONS = [
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "QA Engineer",
    "Product Manager",
    "UI/UX Designer",
    "Data Analyst",
    "Finance Officer",
    "HR Officer",
]

SKILL_OPTIONS = [
    "Python",
    "FastAPI",
    "Django",
    "React",
    "JavaScript",
    "TypeScript",
    "SQL",
    "Docker",
    "AWS",
    "Testing",
    "Communication",
    "Leadership",
]


def validate_role(value: str | None) -> str | None:
    if value is not None and value not in ROLE_OPTIONS:
        raise ValueError("role_applied must be one of the allowed options")
    return value


def validate_skills(value: list[str] | None) -> list[str] | None:
    if value is None:
        return value
    invalid = [skill for skill in value if skill not in SKILL_OPTIONS]
    if invalid:
        raise ValueError(f"Unsupported skills: {', '.join(invalid)}")
    return value


class UserRegister(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=3, max_length=255)
    role_applied: str = Field(..., min_length=1, max_length=120)
    skills: list[str] = Field(default_factory=list)
    internal_notes: str | None = None
    ai_summary: str | None = None

    _validate_role = field_validator("role_applied")(validate_role)
    _validate_skills = field_validator("skills")(validate_skills)


class CandidateCreate(CandidateBase):
    status: CandidateStatus = CandidateStatus.NEW


class CandidateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    role_applied: str | None = Field(default=None, min_length=1, max_length=120)
    status: CandidateStatus | None = None
    skills: list[str] | None = None
    internal_notes: str | None = None
    ai_summary: str | None = None

    _validate_role = field_validator("role_applied")(validate_role)
    _validate_skills = field_validator("skills")(validate_skills)


class CandidateRead(CandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: CandidateStatus
    ai_summary_generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ScoreBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=120)
    score: int = Field(..., ge=1, le=5)
    note: str | None = None


class ScoreCreate(ScoreBase):
    pass


class ScoreUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=120)
    score: int | None = Field(default=None, ge=1, le=5)
    note: str | None = None


class ScoreRead(ScoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    reviewer_id: int
    reviewer_email: str | None = None
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    detail: str


class CandidateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role_applied: str
    status: CandidateStatus
    skills: list[Any]
    created_at: datetime
    updated_at: datetime


class CandidateDetail(CandidateRead):
    scores: list[ScoreRead] = Field(default_factory=list)


class CandidateOptions(BaseModel):
    roles: list[str]
    skills: list[str]
    statuses: list[CandidateStatus]
