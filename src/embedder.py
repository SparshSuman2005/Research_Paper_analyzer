from dotenv import load_dotenv
from reader import read_text
from chunker import chunk_text
from database import insert_chunks
from sentence_transformers import SentenceTransformer
from supabase_client import supabase
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunk(name):
    for paper_name in name:
        file = {"name": paper_name}
        

        chunks = chunk_text(read_text(file))
        vectors=model.encode(
            chunks,
            batch_size=32,
            show_progress_bar=True
        )
        insert_chunks(
        paper_name,
        chunks,
        vectors.tolist()
        
        )
        
    return 




