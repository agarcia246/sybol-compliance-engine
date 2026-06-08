import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routes import analyze, issue, query
from rag.pipeline import load_pipeline
from scoring.pipeline import load_scoring_pipeline

logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.index = None
    try:
        index, _, _ = load_pipeline()
        app.state.index = index
    except Exception as exc:
        logger.warning("RAG pipeline unavailable ( /query disabled ): %s", exc)

    load_scoring_pipeline()

    yield


app = FastAPI(
    title="Sybol Compliance Engine",
    version="0.1.0",
    lifespan=lifespan
)



app.include_router(analyze.router, prefix="/analyze", tags=["scoring"])
app.include_router(issue.router, prefix="/issue", tags=["rag"])
app.include_router(query.router, prefix="/query", tags=["credentials"])

@app.get("/health")
def health():
    return {"status":"ok"}



