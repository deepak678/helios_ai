from sentence_transformers import SentenceTransformer

# Load model once for the service lifetime
MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(text_list):
    """Generate embeddings for a list of text strings."""
    if not text_list:
        return []
    return MODEL.encode(text_list, show_progress_bar=False, convert_to_numpy=True).tolist()
