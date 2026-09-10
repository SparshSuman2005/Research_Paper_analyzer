from downloader import downlaod_paper
from embedder import embed_chunk
from database import insert_chunks


name = input("Enter the name of the paper: ")

downlaod_paper(name)

chunks, all_vector = embed_chunk()

print("MAIN chunks:", len(chunks))
print("MAIN vectors:", len(all_vector))
print("MAIN first vector type:", type(all_vector[0]))
print("MAIN first vector length:", len(all_vector[0]))

response = insert_chunks(
    name,
    chunks,
    all_vector
)

print(response)