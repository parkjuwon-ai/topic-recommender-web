# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import auth, me, interest_categories, topics, sessions

settings = get_settings()

app = FastAPI(
    title="Bookend Topic Lab API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth, prefix="/auth", tags=["auth"])
app.include_router(me, prefix="/me", tags=["me"])
app.include_router(
    interest_categories,
    prefix="/interest-categories",
    tags=["interest-categories"],
)
app.include_router(topics, prefix="/topics", tags=["topics"])
app.include_router(sessions, prefix="/sessions", tags=["sessions"])
