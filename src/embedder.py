from dotenv import load_dotenv
from reader import read_text
from chunker import chunk_text
from sentence_transformers import SentenceTransformer
from supabase_client import supabase

def embed_chunk():
    files = (
        supabase
        .storage
        .from_("research_paper")
        .list()

    )
    for file in files:

        chunks = chunk_text(read_text(file))

        model = SentenceTransformer("all-MiniLM-L6-v2")
        

        vectors=model.encode(
            chunks,
            batch_size=32,
            show_progress_bar=True
        )

    return chunks,vectors.tolist()




