import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes.analyze import router as analyze_router
from src.api.routes.issue import router as issue_router
from src.api.routes.query import router as query_router
from src.rag.pipeline import load_index

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.index = None
    try:
        index, _ = load_index()
        app.state.index = index
    except Exception:
        logger.exception("Failed to build index during startup")
    yield


app = FastAPI(
    title="Sybol Compliance Engine",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(analyze_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(issue_router, prefix="/api")
