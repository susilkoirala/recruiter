import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.auth import create_access_token  # noqa: E402
from app.models import Base, User, UserRole  # noqa: E402


@pytest.fixture()
def testing_session_factory(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(testing_session_factory):
    session = testing_session_factory()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def auth_headers(testing_session_factory):
    def make_headers(email: str, role: UserRole = UserRole.REVIEWER):
        db_session = testing_session_factory()
        user = User(
            email=email,
            hashed_password="unused-in-token-auth-tests",
            role=role,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        db_session.commit()

        token = create_access_token(
            subject=str(user.id),
            claims={"email": user.email, "role": user.role.value},
        )
        db_session.close()
        return {"Authorization": f"Bearer {token}"}, user

    return make_headers
