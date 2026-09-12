import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from app.api.dependencies import build_game_service
from app.api.routers.game import router as game_router
from app.db.database import SessionLocal, create_tables
from app.logging import configure_logging
from app.seeders.map_seeder import MapSeeder
from app.seeders.order_seeder import OrderSeeder
from app.seeders.rover_seeder import RoverSeeder
from fastapi import FastAPI, Request
from starlette.responses import Response

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize storage and the game instance for the application lifetime."""

    logger.info("Starting Moon Courier Crisis API")
    create_tables()
    db = SessionLocal()
    map_path = Path(__file__).resolve().parents[2] / "data" / "map.json"
    MapSeeder(db, map_path).seed()
    RoverSeeder(db, base_point_id=1).seed()
    OrderSeeder(db).seed()

    game_service = build_game_service(db)
    app.state.game_service = game_service
    game_service.initialize_game()
    logger.info("Database tables, starter mission, and game service are ready")

    try:
        yield
    finally:
        db.close()
        logger.info("Moon Courier Crisis API stopped")


app = FastAPI(
    title="Moon Courier Crisis API",
    lifespan=lifespan,
)
app.include_router(game_router)


@app.middleware("http")
async def log_request(request: Request, call_next) -> Response:
    """Log request completion without recording sensitive request contents."""

    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Request failed method=%s path=%s",
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "Request completed method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
