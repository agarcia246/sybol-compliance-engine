from dotenv import load_dotenv

load_dotenv()

from .embeder import get_embedding_model
from .indexer import build_index, load_index
from .ingest import REGULATIONS_DIR, chunk_documents, load_documents
from .query import query_regulations


def ingest_and_index(recreate_collection: bool = True):
    docs = load_documents()
    if not docs:
        raise FileNotFoundError(
            f"No regulation PDFs found in {REGULATIONS_DIR}. "
            "Add PDFs to research/regulations/ before indexing."
        )
    nodes = chunk_documents(docs)
    embed_model = get_embedding_model()
    index, client = build_index(
        nodes, embed_model, recreate_collection=recreate_collection
    )
    return index, embed_model, client


def load_pipeline():
    embed_model = get_embedding_model()
    index, client = load_index(embed_model)
    return index, embed_model, client


def build_pipeline():
    """Ingest PDFs and build the Qdrant index. Use for one-off indexing."""
    return ingest_and_index()
