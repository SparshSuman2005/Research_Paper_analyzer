from dotenv import load_dotenv
from reader import read_text
from chunker import chunk_text
import os,time
from sentence_transformers import SentenceTransformer

load_dotenv("../.env")

def embed_chunk():

    chunks = chunk_text(read_text())

    model = SentenceTransformer("all-MiniLM-L6-v2")
    

    vectors=model.encode(
        chunks,
        batch_size=32,
        show_progress_bar=True
    )

    print(len(vectors))
    print(len(vectors[0]))


embed_chunk()
