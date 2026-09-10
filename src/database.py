from supabase import create_client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")



supabase = create_client(url, key)
print("Done")

def insert_chunks(paper_name , chunk , vector):

    data =[]
    for chunk_t, vector_e in zip(chunk, vector):
        data.append({
                "paper_name": paper_name,
                "chunk_text": chunk_t,
                "embeddings": vector_e
            })
    response = supabase.table("chunks").insert(data).execute()
    return response
