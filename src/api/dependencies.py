from fastapi import Request
from llama_index.core import VectorStoreIndex

def get_index(request: Request) -> VectorStoreIndex:
    return request.app.state.index