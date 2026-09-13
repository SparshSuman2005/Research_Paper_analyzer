from downloader import downlaod_paper
from embedder import embed_chunk
from database import insert_chunks
from supabase import create_client
from dotenv import load_dotenv
import os


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")



supabase = create_client(url, key)
print("Done")


name = input("Enter the name of the paper: ")

downlaod_paper(name)

chunks, all_vector = embed_chunk()



insert_chunks(
    name,
    chunks,
    all_vector
)

