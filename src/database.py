from sentence_transformers import SentenceTransformer
from supabase_client import supabase

def insert_chunks(paper_name , chunk , vector):

    data =[]
    for chunk_t, vector_e in zip(chunk, vector):
        data.append({
                "paper_name": paper_name,
                "chunk_text": chunk_t,
                "embeddings": vector_e
            })
    supabase.table("chunks").insert(data).execute()
    return 
