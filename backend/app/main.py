from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api.dependencies import build_game_service
from app.api.routers.game import router as game_router
from app.db.database import SessionLocal, create_tables
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize storage and the game instance for the application lifetime."""

    create_tables()
    db = SessionLocal()
    app.state.game_service = build_game_service(db)

    try:
        yield
    finally:
        db.close()


app = FastAPI(
    title="Moon Courier Crisis API",
    lifespan=lifespan,
)
app.include_router(game_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
