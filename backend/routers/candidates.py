import asyncio
import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import String, cast
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import decode_access_token, get_current_user, require_admin
from app.database import get_db
from app.models import Candidate, CandidateStatus, Score, User, UserRole
from app.schemas import (
    CandidateCreate,
    CandidateDetail,
    CandidateOptions,
    CandidateRead,
    CandidateSummary,
    CandidateUpdate,
    Message,
    ROLE_OPTIONS,
    ScoreCreate,
    ScoreRead,
    ScoreUpdate,
    SKILL_OPTIONS,
)
from services.candidate_service import generate_ai_summary


router = APIRouter(prefix="/candidates", tags=["candidates"])
score_streams: dict[int, list[asyncio.Queue[dict]]] = {}


def get_candidate_or_404(
    db: Session,
    candidate_id: int,
    *,
    include_deleted: bool = False,
) -> Candidate:
    query = db.query(Candidate).filter(Candidate.id == candidate_id)
    if not include_deleted:
        query = query.filter(Candidate.deleted_at.is_(None))

    candidate = query.first()
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    return candidate


def get_visible_scores_query(db: Session, candidate_id: int, current_user: User):
    query = db.query(Score).filter(Score.candidate_id == candidate_id)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Score.reviewer_id == current_user.id)
    return query


def build_candidate_detail(
    db: Session,
    candidate: Candidate,
    current_user: User,
) -> CandidateDetail:
    data = CandidateRead.model_validate(candidate).model_dump()
    if current_user.role != UserRole.ADMIN:
        data["internal_notes"] = None

    scores = (
        get_visible_scores_query(db, candidate.id, current_user)
        .order_by(Score.created_at.desc(), Score.id.desc())
        .all()
    )
    data["scores"] = [
        serialize_score(score, include_reviewer=current_user.role == UserRole.ADMIN)
        for score in scores
    ]
    return CandidateDetail.model_validate(data)


def serialize_score(score: Score, *, include_reviewer: bool):
    data = ScoreRead.model_validate(score).model_dump(mode="json")
    if not include_reviewer:
        data["reviewer_email"] = None
    return data


async def publish_score_event(candidate_id: int, event: dict):
    queues = score_streams.get(candidate_id, [])
    for queue in queues:
        await queue.put(event)


def get_user_from_stream_token(token: str, db: Session) -> User:
    payload = decode_access_token(token)
    subject = payload.get("sub")
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@router.get("/options", response_model=CandidateOptions)
def get_candidate_options(current_user: User = Depends(get_current_user)):
    return {
        "roles": ROLE_OPTIONS,
        "skills": SKILL_OPTIONS,
        "statuses": list(CandidateStatus),
    }


@router.get("", response_model=list[CandidateSummary])
def list_candidates(
    status_filter: CandidateStatus | None = Query(default=None, alias="status"),
    role_applied: str | None = None,
    skill: str | None = None,
    keyword: str | None = None,
    include_deleted: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Candidate)

    if not include_deleted:
        query = query.filter(Candidate.deleted_at.is_(None))
    if status_filter is not None:
        query = query.filter(Candidate.status == status_filter)
    if role_applied is not None:
        query = query.filter(Candidate.role_applied == role_applied)
    if keyword:
        keyword_like = f"%{keyword}%"
        query = query.filter(
            Candidate.name.ilike(keyword_like) | Candidate.email.ilike(keyword_like)
        )
    if skill:
        query = query.filter(cast(Candidate.skills, String).ilike(f"%{skill}%"))

    return (
        query.order_by(Candidate.created_at.desc(), Candidate.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("", response_model=CandidateRead, status_code=status.HTTP_201_CREATED)
def create_candidate(
    payload: CandidateCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    candidate = Candidate(**payload.model_dump())
    db.add(candidate)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate email already exists",
        ) from exc

    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=CandidateDetail)
def get_candidate(
    candidate_id: int,
    include_deleted: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_or_404(db, candidate_id, include_deleted=include_deleted)
    return build_candidate_detail(db, candidate, current_user)


@router.get("/{candidate_id}/stream")
async def stream_candidate_scores(
    candidate_id: int,
    token: str,
    db: Session = Depends(get_db),
):
    current_user = get_user_from_stream_token(token, db)
    get_candidate_or_404(db, candidate_id)
    queue: asyncio.Queue[dict] = asyncio.Queue()
    score_streams.setdefault(candidate_id, []).append(queue)

    async def event_generator():
        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=25)
                    if current_user.role != UserRole.ADMIN:
                        reviewer_id = event.get("score", {}).get("reviewer_id")
                        if reviewer_id != current_user.id:
                            continue
                    yield f"event: score_update\ndata: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield "event: heartbeat\ndata: {}\n\n"
        finally:
            queues = score_streams.get(candidate_id, [])
            if queue in queues:
                queues.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.patch("/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_or_404(db, candidate_id)
    updates = payload.model_dump(exclude_unset=True)

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    for field, value in updates.items():
        setattr(candidate, field, value)

    if updates.get("status") == CandidateStatus.ARCHIVED:
        candidate.deleted_at = candidate.deleted_at or datetime.now(UTC)
    elif "status" in updates and candidate.deleted_at is not None:
        candidate.deleted_at = None

    if "ai_summary" in updates:
        candidate.ai_summary_generated_at = datetime.now(UTC)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate email already exists",
        ) from exc

    db.refresh(candidate)
    return candidate


@router.delete("/{candidate_id}", response_model=Message)
def archive_candidate(
    candidate_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_or_404(db, candidate_id)
    candidate.deleted_at = datetime.now(UTC)
    candidate.status = CandidateStatus.ARCHIVED
    db.commit()
    return {"detail": "Candidate archived"}


@router.post("/{candidate_id}/summary", response_model=CandidateRead)
async def generate_candidate_summary(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_or_404(db, candidate_id)
    scores = get_visible_scores_query(db, candidate_id, current_user).all()
    try:
        candidate.ai_summary = await asyncio.to_thread(generate_ai_summary, candidate, scores)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI summary generation failed",
        ) from exc
    candidate.ai_summary_generated_at = datetime.now(UTC)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}/scores", response_model=list[ScoreRead])
def list_candidate_scores(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_candidate_or_404(db, candidate_id)
    scores = (
        get_visible_scores_query(db, candidate_id, current_user)
        .order_by(Score.created_at.desc(), Score.id.desc())
        .all()
    )
    return [
        serialize_score(score, include_reviewer=current_user.role == UserRole.ADMIN)
        for score in scores
    ]


@router.post(
    "/{candidate_id}/scores",
    response_model=ScoreRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_candidate_score(
    candidate_id: int,
    payload: ScoreCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_or_404(db, candidate_id)
    if payload.category not in (candidate.skills or []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score category must be one of the candidate skills",
        )

    score = Score(
        candidate_id=candidate_id,
        reviewer_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    await publish_score_event(
        candidate_id,
        {
            "type": "score_created",
            "score": serialize_score(
                score,
                include_reviewer=current_user.role == UserRole.ADMIN,
            ),
        },
    )
    return serialize_score(score, include_reviewer=current_user.role == UserRole.ADMIN)


@router.patch("/{candidate_id}/scores/{score_id}", response_model=ScoreRead)
async def update_candidate_score(
    candidate_id: int,
    score_id: int,
    payload: ScoreUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_or_404(db, candidate_id)
    if payload.category is not None and payload.category not in (candidate.skills or []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score category must be one of the candidate skills",
        )
    score = (
        get_visible_scores_query(db, candidate_id, current_user)
        .filter(Score.id == score_id)
        .first()
    )
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(score, field, value)

    db.commit()
    db.refresh(score)
    await publish_score_event(
        candidate_id,
        {
            "type": "score_updated",
            "score": serialize_score(
                score,
                include_reviewer=current_user.role == UserRole.ADMIN,
            ),
        },
    )
    return serialize_score(score, include_reviewer=current_user.role == UserRole.ADMIN)
