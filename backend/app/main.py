from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from routers.auth import router as auth_router
from routers.candidates import router as candidates_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        host_sanitized
        for host in settings.cors_allowed_hosts.split(",")
        if (host_sanitized:=host.strip())
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(candidates_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "ok"}
