from downloader import downlaod_paper
from embedder import embed_chunk
from database import insert_chunks
from supabase_client import supabase


name = input("Enter the name of the paper: ")

downlaod_paper(name)

chunks, all_vector = embed_chunk()



insert_chunks(
    name,
    chunks,
    all_vector
)

