from dotenv import load_dotenv
from reader import read_text
from chunker import chunk_text
from database import insert_chunks
from sentence_transformers import SentenceTransformer
from supabase_client import supabase
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_chunk(name):
    model = get_model()
    if isinstance(name, str):
        name = [name]
    total_chunks = 0
    for paper_name in name:
        file = {"name": paper_name}
        raw_text = read_text(file)
        if not raw_text or not raw_text.strip():
            continue
        chunks = chunk_text(raw_text)
        if not chunks:
            continue
        vectors = model.encode(
            chunks,
            batch_size=32,
            show_progress_bar=False
        )
        count = insert_chunks(
            paper_name,
            chunks,
            vectors.tolist()
        )
        total_chunks += (count or len(chunks))
    return total_chunks

def embed_question(question):
    model = get_model()
    embedding = model.encode(question)
    return embedding.tolist()






