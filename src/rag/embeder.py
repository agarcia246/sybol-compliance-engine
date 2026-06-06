from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_embedding_model():
    return HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )