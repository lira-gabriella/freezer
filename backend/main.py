"""CryoGuard FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
import backend.app.models  # noqa: F401 - ensure models are registered
from backend.app.routers.process_router import router as process_router
from backend.app.routers.vault_router import router as vault_router
from backend.app.routers.security_router import router as security_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CryoGuard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_router)
app.include_router(vault_router)
app.include_router(security_router)


@app.get("/health")
def health():
    return {"status": "ok"}
