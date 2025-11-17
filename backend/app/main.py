# app/main.py
from fastapi import FastAPI

from app.core.config import settings
from app.routers import health, auth, me, interests


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(interests.router)

    @app.get("/", tags=["root"])
    def root():
        return {"message": "Bookend Topic Recommender API is running"}

    return app


app = create_app()

