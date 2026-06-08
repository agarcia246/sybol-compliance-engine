from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routes import analyze, issue, query
from rag.pipeline import load_pipeline


load_dotenv()




@asynccontextmanager
async def lifespan(app: FastAPI):
    index, _, _ = load_pipeline()
    app.state.index = index

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



