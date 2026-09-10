from dotenv import load_dotenv
from reader import read_text
from chunker import chunk_text
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

    return chunks,vectors.tolist()




