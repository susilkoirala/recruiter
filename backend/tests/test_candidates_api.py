import pytest
from fastapi import HTTPException

from app.auth import require_admin
from app.models import Candidate, Score, UserRole
from app.schemas import CandidateCreate
from routers.candidates import create_candidate, get_candidate, list_candidate_scores


def candidate_payload(email="sita.rai@example.com"):
    return {
        "name": "Sita Rai",
        "email": email,
        "role_applied": "Backend Engineer",
        "status": "new",
        "skills": ["Python", "FastAPI", "SQL"],
        "internal_notes": "Strong API fundamentals.",
    }


def create_candidate_record(db_session):
    candidate = Candidate(**candidate_payload())
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    db_session.commit()
    return candidate


def test_admin_can_create_candidate(db_session, auth_headers):
    _, admin = auth_headers("admin@example.com", UserRole.ADMIN)
    payload = CandidateCreate.model_validate(candidate_payload())

    candidate = create_candidate(payload, current_user=admin, db=db_session)

    assert candidate.id is not None
    assert candidate.name == "Sita Rai"
    assert candidate.email == "sita.rai@example.com"
    assert candidate.role_applied == "Backend Engineer"
    assert candidate.skills == ["Python", "FastAPI", "SQL"]


def test_reviewer_is_rejected_by_admin_dependency(auth_headers):
    _, reviewer = auth_headers("reviewer@example.com")

    with pytest.raises(HTTPException) as exc_info:
        require_admin(reviewer)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Admin access required"


def test_reviewer_only_sees_their_own_scores(db_session, auth_headers):
    candidate = create_candidate_record(db_session)
    _, reviewer = auth_headers("reviewer-one@example.com")
    _, other_reviewer = auth_headers("reviewer-two@example.com")
    db_session.add_all(
        [
            Score(
                candidate_id=candidate.id,
                reviewer_id=reviewer.id,
                category="Python",
                score=5,
                note="Excellent Python discussion.",
            ),
            Score(
                candidate_id=candidate.id,
                reviewer_id=other_reviewer.id,
                category="FastAPI",
                score=2,
                note="Different reviewer's private note.",
            ),
        ]
    )
    db_session.commit()

    scores = list_candidate_scores(candidate.id, current_user=reviewer, db=db_session)

    assert len(scores) == 1
    assert scores[0]["reviewer_id"] == reviewer.id
    assert scores[0]["category"] == "Python"
    assert scores[0]["reviewer_email"] is None


def test_admin_sees_all_reviewer_scores_in_candidate_detail(db_session, auth_headers):
    candidate = create_candidate_record(db_session)
    _, admin = auth_headers("admin@example.com", UserRole.ADMIN)
    _, reviewer = auth_headers("reviewer-one@example.com")
    _, other_reviewer = auth_headers("reviewer-two@example.com")
    db_session.add_all(
        [
            Score(
                candidate_id=candidate.id,
                reviewer_id=reviewer.id,
                category="Python",
                score=5,
                note="Excellent Python discussion.",
            ),
            Score(
                candidate_id=candidate.id,
                reviewer_id=other_reviewer.id,
                category="FastAPI",
                score=4,
                note="Solid framework understanding.",
            ),
        ]
    )
    db_session.commit()

    detail = get_candidate(candidate.id, current_user=admin, db=db_session)

    assert {score.reviewer_id for score in detail.scores} == {reviewer.id, other_reviewer.id}
    assert {score.reviewer_email for score in detail.scores} == {
        "reviewer-one@example.com",
        "reviewer-two@example.com",
    }
